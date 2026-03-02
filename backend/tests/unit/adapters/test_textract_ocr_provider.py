"""Unit tests for the AWS Textract OCR provider adapter (LangGraph-based).

All Textract API calls and LLM calls are mocked via unittest.mock so these
tests run without AWS credentials, network access, or an OpenAI API key.

Test structure
--------------
  Node unit tests   – Test each graph node function in isolation.
  Graph integration – Test TextractOcrProvider.extract() end-to-end with mocked
                      Textract and LLM clients. Verifies node output parity,
                      invocation sequence, and failure-path handling.
"""

from unittest.mock import MagicMock, patch

import pytest

from app.adapters.ocr_provider import OcrExecutionError, RawOcrSegment
from app.adapters.textract_ocr_provider import (
    OcrGraphState,
    TextractOcrProvider,
    _make_llm_reasoning_node,
    filter_line_blocks_node,
    ocr_tool_node,
    to_documents_node,
    to_segments_node,
)

# ---------------------------------------------------------------------------
# Shared fixtures / helpers
# ---------------------------------------------------------------------------

_TEXTRACT_TWO_LINE_RESPONSE = {
    "Blocks": [
        {"BlockType": "LINE", "Text": "你好", "Confidence": 92.0},
        {"BlockType": "LINE", "Text": "hello", "Confidence": 80.0},
        # WORD blocks must be excluded from output
        {"BlockType": "WORD", "Text": "你好", "Confidence": 91.0},
    ]
}


def _mock_llm_client(content: str = "extraction looks valid") -> MagicMock:
    """Return a minimal mock OpenAI client whose completions return *content*."""
    mock_llm = MagicMock()
    mock_llm.chat.completions.create.return_value = MagicMock(
        choices=[MagicMock(message=MagicMock(content=content))]
    )
    return mock_llm


def _make_provider(
    response: dict,
    llm_client: MagicMock | None = None,
) -> TextractOcrProvider:
    """Return a TextractOcrProvider with stubbed Textract + LLM clients."""
    if llm_client is None:
        llm_client = _mock_llm_client()
    with patch("app.adapters.textract_ocr_provider.boto3.client") as mock_factory:
        mock_boto = MagicMock()
        mock_boto.detect_document_text.return_value = response
        mock_factory.return_value = mock_boto
        provider = TextractOcrProvider(region_name="us-east-1", llm_client=llm_client)
        provider._client = mock_boto  # keep stub active outside the patch context
    return provider


def _base_state(**overrides: object) -> OcrGraphState:
    """Return a minimal OcrGraphState for node-level unit tests."""
    state: OcrGraphState = {
        "response": {},
        "blocks": [],
        "documents": [],
        "segments": [],
        "llm_reasoning": "",
    }
    state.update(overrides)  # type: ignore[typeddict-item]
    return state


# ---------------------------------------------------------------------------
# Node: filter_line_blocks_node
# ---------------------------------------------------------------------------


class TestFilterLineBlocksNode:
    def test_keeps_line_blocks_with_text(self) -> None:
        state = _base_state(response=_TEXTRACT_TWO_LINE_RESPONSE)
        result = filter_line_blocks_node(state)
        assert len(result["blocks"]) == 2
        assert all(b["BlockType"] == "LINE" for b in result["blocks"])

    def test_excludes_word_blocks(self) -> None:
        state = _base_state(response=_TEXTRACT_TWO_LINE_RESPONSE)
        result = filter_line_blocks_node(state)
        assert not any(b["BlockType"] == "WORD" for b in result["blocks"])

    def test_excludes_empty_text_blocks(self) -> None:
        state = _base_state(
            response={
                "Blocks": [
                    {"BlockType": "LINE", "Text": "", "Confidence": 90.0},
                    {"BlockType": "LINE", "Confidence": 85.0},  # no "Text" key
                ]
            }
        )
        result = filter_line_blocks_node(state)
        assert result["blocks"] == []

    def test_handles_empty_blocks_list(self) -> None:
        state = _base_state(response={"Blocks": []})
        result = filter_line_blocks_node(state)
        assert result["blocks"] == []

    def test_handles_missing_blocks_key(self) -> None:
        state = _base_state(response={})
        result = filter_line_blocks_node(state)
        assert result["blocks"] == []

    def test_preserves_other_state_fields(self) -> None:
        state = _base_state(response={"Blocks": []}, llm_reasoning="prev")
        result = filter_line_blocks_node(state)
        assert result["llm_reasoning"] == "prev"


# ---------------------------------------------------------------------------
# Node: to_documents_node
# ---------------------------------------------------------------------------


class TestToDocumentsNode:
    def test_converts_blocks_to_documents(self) -> None:
        from langchain_core.documents import Document

        state = _base_state(
            blocks=[
                {"BlockType": "LINE", "Text": "你好", "Confidence": 92.0},
                {"BlockType": "LINE", "Text": "hello", "Confidence": 80.0},
            ]
        )
        result = to_documents_node(state)
        assert len(result["documents"]) == 2
        assert isinstance(result["documents"][0], Document)
        assert result["documents"][0].page_content == "你好"
        assert result["documents"][0].metadata["confidence"] == 92.0
        assert result["documents"][1].page_content == "hello"
        assert result["documents"][1].metadata["confidence"] == 80.0

    def test_empty_blocks_returns_empty_documents(self) -> None:
        state = _base_state(blocks=[])
        result = to_documents_node(state)
        assert result["documents"] == []

    def test_defaults_confidence_to_zero_when_missing(self) -> None:
        state = _base_state(blocks=[{"BlockType": "LINE", "Text": "test"}])
        result = to_documents_node(state)
        assert result["documents"][0].metadata["confidence"] == 0.0

    def test_preserves_other_state_fields(self) -> None:
        state = _base_state(blocks=[], llm_reasoning="prev")
        result = to_documents_node(state)
        assert result["llm_reasoning"] == "prev"


# ---------------------------------------------------------------------------
# Node: to_segments_node
# ---------------------------------------------------------------------------


class TestToSegmentsNode:
    def test_maps_documents_to_segments(self) -> None:
        from langchain_core.documents import Document

        state = _base_state(
            documents=[
                Document(page_content="你好", metadata={"confidence": 92.0}),
                Document(page_content="hello", metadata={"confidence": 80.0}),
            ]
        )
        result = to_segments_node(state)
        assert len(result["segments"]) == 2
        assert result["segments"][0].text == "你好"
        assert result["segments"][0].confidence == 92.0
        assert result["segments"][0].language is None  # Textract provides no language tag
        assert result["segments"][1].text == "hello"

    def test_empty_documents_returns_empty_segments(self) -> None:
        state = _base_state(documents=[])
        result = to_segments_node(state)
        assert result["segments"] == []

    def test_language_is_always_none(self) -> None:
        """Language must be None for all segments; service normalises to 'und'."""
        from langchain_core.documents import Document

        state = _base_state(
            documents=[Document(page_content="text", metadata={"confidence": 90.0})]
        )
        result = to_segments_node(state)
        assert result["segments"][0].language is None

    def test_preserves_other_state_fields(self) -> None:
        state = _base_state(documents=[], llm_reasoning="prev")
        result = to_segments_node(state)
        assert result["llm_reasoning"] == "prev"


# ---------------------------------------------------------------------------
# Node: ocr_tool_node
# ---------------------------------------------------------------------------


class TestOcrToolNode:
    def test_passes_state_through_unchanged(self) -> None:
        segments = [RawOcrSegment(text="你好", language=None, confidence=92.0)]
        state = _base_state(segments=segments)
        result = ocr_tool_node(state)
        assert result is state  # identity – no copy made

    def test_does_not_modify_segments(self) -> None:
        segments = [RawOcrSegment(text="hello", language=None, confidence=80.0)]
        state = _base_state(segments=segments)
        result = ocr_tool_node(state)
        assert result["segments"] is segments


# ---------------------------------------------------------------------------
# Node: llm_reasoning_node (via _make_llm_reasoning_node factory)
# ---------------------------------------------------------------------------


class TestLlmReasoningNode:
    def test_calls_gpt5_mini_model(self) -> None:
        mock_llm = _mock_llm_client("ok")
        node_fn = _make_llm_reasoning_node(llm_client=mock_llm)
        state = _base_state(
            segments=[RawOcrSegment(text="你好", language=None, confidence=92.0)]
        )
        node_fn(state)
        create_kwargs = mock_llm.chat.completions.create.call_args.kwargs
        assert create_kwargs["model"] == "gpt-5-mini"

    def test_prompt_contains_segment_texts(self) -> None:
        mock_llm = _mock_llm_client("all good")
        node_fn = _make_llm_reasoning_node(llm_client=mock_llm)
        state = _base_state(
            segments=[
                RawOcrSegment(text="你好", language=None, confidence=92.0),
                RawOcrSegment(text="hello", language=None, confidence=80.0),
            ]
        )
        node_fn(state)
        prompt: str = mock_llm.chat.completions.create.call_args.kwargs["messages"][0]["content"]
        assert "你好" in prompt
        assert "hello" in prompt

    def test_stores_llm_response_in_state(self) -> None:
        node_fn = _make_llm_reasoning_node(llm_client=_mock_llm_client("confirmed"))
        state = _base_state(segments=[])
        result = node_fn(state)
        assert result["llm_reasoning"] == "confirmed"

    def test_segments_not_modified_by_llm_node(self) -> None:
        segments = [RawOcrSegment(text="你好", language=None, confidence=92.0)]
        node_fn = _make_llm_reasoning_node(llm_client=_mock_llm_client())
        state = _base_state(segments=segments)
        result = node_fn(state)
        assert result["segments"] is segments

    def test_gracefully_handles_llm_failure(self) -> None:
        mock_llm = MagicMock()
        mock_llm.chat.completions.create.side_effect = RuntimeError("API down")
        node_fn = _make_llm_reasoning_node(llm_client=mock_llm)
        state = _base_state(segments=[])
        result = node_fn(state)
        assert result["llm_reasoning"] == "<llm-reasoning-unavailable>"

    def test_segments_are_intact_after_llm_failure(self) -> None:
        mock_llm = MagicMock()
        mock_llm.chat.completions.create.side_effect = RuntimeError("API down")
        node_fn = _make_llm_reasoning_node(llm_client=mock_llm)
        segments = [RawOcrSegment(text="text", language=None, confidence=90.0)]
        state = _base_state(segments=segments)
        result = node_fn(state)
        assert result["segments"] is segments  # contract preserved


# ---------------------------------------------------------------------------
# Graph integration: TextractOcrProvider end-to-end
# ---------------------------------------------------------------------------


class TestTextractOcrProviderGraphIntegration:
    # -- Output parity tests (verify graph produces same results as old chain) --

    def test_extract_returns_line_level_segments_only(self) -> None:
        provider = _make_provider(_TEXTRACT_TWO_LINE_RESPONSE)
        segments = provider.extract(image_bytes=b"fake-image", content_type="image/png")
        # Only LINE blocks → 2 segments; WORD block is excluded.
        assert len(segments) == 2
        assert segments[0].text == "你好"
        assert segments[0].confidence == 92.0
        assert segments[0].language is None

    def test_extract_maps_confidence_from_textract_float(self) -> None:
        provider = _make_provider(
            {"Blocks": [{"BlockType": "LINE", "Text": "世界", "Confidence": 99.5}]}
        )
        segments = provider.extract(image_bytes=b"fake-image", content_type="image/jpeg")
        assert segments[0].confidence == 99.5

    def test_extract_excludes_blocks_with_no_text(self) -> None:
        provider = _make_provider(
            {
                "Blocks": [
                    {"BlockType": "LINE", "Text": "", "Confidence": 90.0},
                    {"BlockType": "LINE", "Confidence": 85.0},  # no "Text" key
                    {"BlockType": "PAGE", "Confidence": 99.0},
                ]
            }
        )
        segments = provider.extract(image_bytes=b"fake-image", content_type="image/png")
        assert segments == []

    def test_extract_returns_empty_list_for_empty_blocks(self) -> None:
        provider = _make_provider({"Blocks": []})
        segments = provider.extract(image_bytes=b"fake-image", content_type="image/png")
        assert segments == []

    # -- Failure-path tests (verify OcrExecutionError mapping) --

    def test_extract_raises_ocr_execution_error_on_client_error(self) -> None:
        from botocore.exceptions import ClientError

        provider = _make_provider({})
        provider._client.detect_document_text.side_effect = ClientError(
            {"Error": {"Code": "InvalidDocumentException", "Message": "Invalid document"}},
            "DetectDocumentText",
        )
        with pytest.raises(OcrExecutionError):
            provider.extract(image_bytes=b"bad-image", content_type="image/png")

    def test_extract_raises_ocr_execution_error_on_unexpected_exception(self) -> None:
        provider = _make_provider({})
        provider._client.detect_document_text.side_effect = RuntimeError("network blip")
        with pytest.raises(OcrExecutionError):
            provider.extract(image_bytes=b"bad-image", content_type="image/png")

    def test_boto_core_error_surfaces_as_ocr_execution_error(self) -> None:
        from botocore.exceptions import BotoCoreError

        provider = _make_provider({})
        provider._client.detect_document_text.side_effect = BotoCoreError()
        with pytest.raises(OcrExecutionError):
            provider.extract(image_bytes=b"bad-image", content_type="image/png")

    # -- Graph execution path tests --

    def test_ocr_tool_node_invoked_before_llm_reasoning(self) -> None:
        """Verify ocr_tool runs before llm_reasoning via LLM prompt inspection.

        The llm_reasoning_node prompt includes segment texts; if ocr_tool ran
        first (pass-through), those segments were produced before the LLM call.
        This indirectly validates the declared edge order.
        """
        captured: dict[str, object] = {}

        mock_llm = MagicMock()

        def capture_create(**kwargs: object) -> MagicMock:
            captured["messages"] = kwargs.get("messages", [])
            return MagicMock(choices=[MagicMock(message=MagicMock(content="ok"))])

        mock_llm.chat.completions.create.side_effect = capture_create

        provider = _make_provider(_TEXTRACT_TWO_LINE_RESPONSE, llm_client=mock_llm)
        provider.extract(image_bytes=b"fake-image", content_type="image/png")

        # LLM was called and its prompt contains the OCR segment texts,
        # proving the pipeline executed in order up to and through ocr_tool.
        assert mock_llm.chat.completions.create.called
        prompt: str = captured["messages"][0]["content"]  # type: ignore[index]
        assert "你好" in prompt
        assert "hello" in prompt

    def test_llm_reasoning_invoked_with_ocr_tool_output(self) -> None:
        """Verify the LLM node is called and receives a non-empty prompt."""
        mock_llm = _mock_llm_client()
        provider = _make_provider(_TEXTRACT_TWO_LINE_RESPONSE, llm_client=mock_llm)
        provider.extract(image_bytes=b"fake-image", content_type="image/png")
        mock_llm.chat.completions.create.assert_called_once()

    def test_llm_failure_does_not_break_adapter_contract(self) -> None:
        """LLM node exception must not propagate; segments must still be returned."""
        mock_llm = MagicMock()
        mock_llm.chat.completions.create.side_effect = RuntimeError("LLM down")
        provider = _make_provider(_TEXTRACT_TWO_LINE_RESPONSE, llm_client=mock_llm)
        segments = provider.extract(image_bytes=b"fake-image", content_type="image/png")
        assert len(segments) == 2

    # -- Empty / invalid Textract block handling --

    def test_handles_blocks_with_none_confidence(self) -> None:
        provider = _make_provider(
            {"Blocks": [{"BlockType": "LINE", "Text": "test", "Confidence": None}]}
        )
        segments = provider.extract(image_bytes=b"fake-image", content_type="image/png")
        assert segments[0].confidence is None

    def test_handles_response_with_only_non_line_blocks(self) -> None:
        provider = _make_provider(
            {
                "Blocks": [
                    {"BlockType": "PAGE", "Confidence": 99.0},
                    {"BlockType": "WORD", "Text": "word", "Confidence": 90.0},
                ]
            }
        )
        segments = provider.extract(image_bytes=b"fake-image", content_type="image/png")
        assert segments == []
