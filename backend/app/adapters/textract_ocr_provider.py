"""AWS Textract OCR provider.

The adapter uses an explicit LangGraph StateGraph to orchestrate OCR processing.
The graph replaces the previous RunnableLambda chain with named nodes and edges,
making each transformation step explicit, inspectable, and extensible as a
learning artifact.

Graph topology
--------------
START → filter_line_blocks → to_documents → to_segments → ocr_tool → llm_reasoning_node → END

Node responsibilities
---------------------
filter_line_blocks_node  – Keep only LINE-level Textract blocks with non-empty text.
to_documents_node        – Convert filtered blocks into LangChain Document instances
                           with confidence metadata.
to_segments_node         – Map Documents to RawOcrSegment values for service consumption.
                           Language is left as None because Textract DetectDocumentText
                           does not return a language tag; the OCR service layer
                           normalises it to "und" and the CJK filter determines usability.
ocr_tool_node            – Marks OCR extraction as complete; exposes the result as a
                           tool-style graph boundary for downstream LLM reasoning.
llm_reasoning_node       – Invokes gpt-5-mini with the OCR tool output for graph
                           reasoning. The LLM response is captured in state but does
                           NOT modify the segments; adapter contract is unchanged.

Environment variables
---------------------
OCR_PROVIDER=textract  Activates this provider (read by get_ocr_provider()).
AWS_REGION             AWS region for the Textract client (default: us-east-1).
AWS credentials        Standard boto3 resolution (env vars, ~/.aws, IAM role).
OPENAI_API_KEY         Required by the llm_reasoning_node in production.
"""

from __future__ import annotations

import os
from typing import Any, Callable

import boto3
from botocore.exceptions import BotoCoreError, ClientError
from langchain_core.documents import Document
from langgraph.graph import END, START, StateGraph
from typing_extensions import TypedDict

from app.adapters.ocr_provider import OcrExecutionError, ProviderUnavailableError, RawOcrSegment

# ---------------------------------------------------------------------------
# Graph state
# ---------------------------------------------------------------------------


class OcrGraphState(TypedDict):
    """Shared state flowing through the OCR LangGraph nodes."""

    response: dict[str, Any]       # Raw Textract API response dict.
    blocks: list[dict[str, Any]]   # Filtered LINE-level Textract blocks.
    documents: list[Document]      # LangChain Document wrappers with confidence.
    segments: list[RawOcrSegment]  # Final adapter output segments.
    llm_reasoning: str             # LLM reasoning output (not exposed in adapter result).


# ---------------------------------------------------------------------------
# Node functions
# ---------------------------------------------------------------------------


def filter_line_blocks_node(state: OcrGraphState) -> OcrGraphState:
    """Keep only LINE blocks with non-empty text from the Textract response.

    Isolates valid text lines from the raw Textract API response dict, discarding
    block types such as WORD, PAGE, TABLE, etc. that are not used downstream.
    """
    blocks: list[dict[str, Any]] = state["response"].get("Blocks", [])
    filtered = [
        block
        for block in blocks
        if block.get("BlockType") == "LINE" and block.get("Text")
    ]
    return {**state, "blocks": filtered}


def to_documents_node(state: OcrGraphState) -> OcrGraphState:
    """Convert filtered Textract blocks into LangChain Document instances.

    Wraps each LINE block in a LangChain Document so that later pipeline stages
    can be swapped in without touching the provider interface. Confidence metadata
    is propagated for downstream quality checks.
    """
    documents = [
        Document(
            page_content=block["Text"],
            metadata={"confidence": block.get("Confidence", 0.0)},
        )
        for block in state["blocks"]
    ]
    return {**state, "documents": documents}


def to_segments_node(state: OcrGraphState) -> OcrGraphState:
    """Map LangChain Documents to RawOcrSegment values for service consumption.

    Produces the normalised RawOcrSegment list that the service layer expects.
    Language is intentionally left as None; the OCR service normalises it to "und"
    and the CJK filter determines downstream usability.
    """
    segments = [
        RawOcrSegment(
            text=doc.page_content,
            language=None,  # Textract DetectDocumentText does not return language tags.
            confidence=doc.metadata["confidence"],
        )
        for doc in state["documents"]
    ]
    return {**state, "segments": segments}


def ocr_tool_node(state: OcrGraphState) -> OcrGraphState:
    """OCR tool boundary node – marks extraction complete for downstream reasoning.

    Encapsulates the OCR output as a tool-style graph boundary. The segments
    produced by to_segments_node are the 'tool result' that the llm_reasoning_node
    will consume. No transformation is applied; the node boundary itself is the
    meaningful learning artifact.
    """
    # The node boundary marks the tool contract; no data transformation needed.
    return state


def _make_llm_reasoning_node(
    llm_client: Any | None = None,
) -> Callable[[OcrGraphState], OcrGraphState]:
    """Factory producing an llm_reasoning_node with an injectable LLM client.

    The returned node calls gpt-5-mini with the OCR tool output and stores the
    reasoning in state. The segments are NOT modified; the LLM response is an
    explanatory artifact captured for graph transparency and extensibility.

    Args:
        llm_client: Optional OpenAI-compatible client. When None, an ``openai.OpenAI``
                    client is constructed at call time (requires OPENAI_API_KEY).
                    Pass a mock in tests to avoid real API calls.
    """

    def llm_reasoning_node(state: OcrGraphState) -> OcrGraphState:
        """Call gpt-5-mini using OCR tool output to produce a graph reasoning step."""
        client = llm_client
        if client is None:
            import openai  # deferred import – only required when OPENAI_API_KEY is set

            client = openai.OpenAI()

        segment_texts = [seg.text for seg in state["segments"]]
        prompt = (
            f"OCR extracted {len(segment_texts)} text segment(s). "
            f"Segments: {segment_texts}. "
            "Briefly confirm the extraction looks valid."
        )
        try:
            chat_response = client.chat.completions.create(
                model="gpt-5-mini",
                messages=[{"role": "user", "content": prompt}],
            )
            reasoning: str = chat_response.choices[0].message.content or ""
        except Exception:  # LLM reasoning is non-critical – adapter contract must hold.
            reasoning = "<llm-reasoning-unavailable>"

        return {**state, "llm_reasoning": reasoning}

    return llm_reasoning_node


# ---------------------------------------------------------------------------
# Graph builder
# ---------------------------------------------------------------------------


def _build_ocr_graph(llm_client: Any | None = None):
    """Construct and compile the OCR LangGraph StateGraph.

    Edges:
        START → filter_line_blocks → to_documents → to_segments → ocr_tool
              → llm_reasoning_node → END

    Args:
        llm_client: Optional injectable LLM client forwarded to llm_reasoning_node.
    """
    graph: StateGraph = StateGraph(OcrGraphState)

    graph.add_node("filter_line_blocks", filter_line_blocks_node)
    graph.add_node("to_documents", to_documents_node)
    graph.add_node("to_segments", to_segments_node)
    graph.add_node("ocr_tool", ocr_tool_node)
    graph.add_node("llm_reasoning_node", _make_llm_reasoning_node(llm_client=llm_client))

    graph.add_edge(START, "filter_line_blocks")
    graph.add_edge("filter_line_blocks", "to_documents")
    graph.add_edge("to_documents", "to_segments")
    graph.add_edge("to_segments", "ocr_tool")
    graph.add_edge("ocr_tool", "llm_reasoning_node")
    graph.add_edge("llm_reasoning_node", END)

    return graph.compile()


# ---------------------------------------------------------------------------
# Provider
# ---------------------------------------------------------------------------


class TextractOcrProvider:
    """AWS Textract implementation of the OcrProvider protocol.

    Reads image bytes via Textract's DetectDocumentText API, then orchestrates
    the result through an explicit LangGraph StateGraph to produce normalised
    RawOcrSegment values.  The graph makes each transformation step inspectable
    and extensible as a learning artifact.

    Args:
        region_name: AWS region for the Textract client (default: us-east-1).
        llm_client:  Injectable OpenAI-compatible client for the gpt-5-mini node.
                     Defaults to ``openai.OpenAI()`` constructed at call time when
                     None.  Pass a mock in tests to avoid real API calls.
    """

    def __init__(
        self,
        region_name: str | None = None,
        llm_client: Any | None = None,
    ) -> None:
        region = region_name or os.environ.get("AWS_REGION", "us-east-1")
        try:
            self._client = boto3.client("textract", region_name=region)
        except Exception as exc:  # boto3 setup errors (credentials shape, etc.)
            raise ProviderUnavailableError(
                "Could not initialise Textract client. Check AWS credentials and region."
            ) from exc
        self._graph = _build_ocr_graph(llm_client=llm_client)

    def extract(self, *, image_bytes: bytes, content_type: str) -> list[RawOcrSegment]:
        """Call Textract and return normalised segments via the LangGraph graph."""
        try:
            response = self._client.detect_document_text(Document={"Bytes": image_bytes})
        except (BotoCoreError, ClientError) as exc:
            raise OcrExecutionError(f"Textract API error: {exc}") from exc
        except Exception as exc:
            raise OcrExecutionError(f"Unexpected Textract error: {exc}") from exc

        initial_state: OcrGraphState = {
            "response": response,
            "blocks": [],
            "documents": [],
            "segments": [],
            "llm_reasoning": "",
        }
        final_state: OcrGraphState = self._graph.invoke(initial_state)
        return final_state["segments"]
