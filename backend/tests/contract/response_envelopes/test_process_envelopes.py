import asyncio
from collections.abc import Mapping
from unittest.mock import AsyncMock, patch

from starlette.requests import Request

from app.api.v1.process import process_image
from app.schemas.process import ProcessData, ProcessError, ProcessResponse, ProcessWarning

PNG_1X1_BYTES = (
    b"\x89PNG\r\n\x1a\n"
    b"\x00\x00\x00\rIHDR"
    b"\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00"
    b"\x90wS\xde"
    b"\x00\x00\x00\x0cIDATx\x9cc\xf8\xff\xff?\x00\x05\xfe\x02\xfeA\xe2$\x8f"
    b"\x00\x00\x00\x00IEND\xaeB`\x82"
)


def _request_with_body(body: bytes, content_type: str) -> Request:
    sent = False

    async def receive() -> dict[str, object]:
        nonlocal sent
        if sent:
            return {"type": "http.disconnect"}
        sent = True
        return {"type": "http.request", "body": body, "more_body": False}

    scope = {
        "type": "http",
        "asgi": {"version": "3.0"},
        "http_version": "1.1",
        "method": "POST",
        "scheme": "http",
        "path": "/v1/process",
        "raw_path": b"/v1/process",
        "query_string": b"",
        "headers": [(b"content-type", content_type.encode("ascii"))],
        "client": ("testclient", 123),
        "server": ("testserver", 80),
    }
    return Request(scope, receive)


def assert_process_envelope(envelope: Mapping[str, object]) -> None:
    assert "status" in envelope
    assert envelope["status"] in {"success", "partial", "error"}

    assert "request_id" in envelope
    assert isinstance(envelope["request_id"], str)
    assert envelope["request_id"]

    # Contract is strict snake_case with stable top-level keys.
    assert "requestId" not in envelope
    assert "payload" not in envelope

    status = envelope["status"]
    if status == "success":
        assert "data" in envelope
        assert isinstance(envelope["data"], Mapping)
        assert "warnings" not in envelope
        assert "error" not in envelope
    elif status == "partial":
        assert "data" in envelope
        assert isinstance(envelope["data"], Mapping)
        assert "warnings" in envelope
        assert isinstance(envelope["warnings"], list)
        assert "error" not in envelope
    else:
        assert "error" in envelope
        assert isinstance(envelope["error"], Mapping)
        assert "category" in envelope["error"]
        assert "data" not in envelope


def test_process_endpoint_success_envelope_contract() -> None:
    response = asyncio.run(process_image(_request_with_body(PNG_1X1_BYTES, "image/png")))
    assert_process_envelope(response.model_dump(exclude_none=True))


def test_process_endpoint_partial_envelope_contract() -> None:
    partial_response = ProcessResponse(
        status="partial",
        request_id="req-partial-contract",
        data=ProcessData(message="partially-processed"),
        warnings=[ProcessWarning(code="ocr-low-confidence", message="Low confidence score")],
    )
    with patch(
        "app.api.v1.process._build_process_response",
        new=AsyncMock(return_value=partial_response),
    ):
        response = asyncio.run(process_image(_request_with_body(PNG_1X1_BYTES, "image/png")))
    assert_process_envelope(response.model_dump(exclude_none=True))


def test_process_endpoint_error_envelope_contract() -> None:
    error_response = ProcessResponse(
        status="error",
        request_id="req-error-contract",
        error=ProcessError(
            category="validation",
            code="invalid-image",
            message="Image could not be processed",
        ),
    )
    with patch(
        "app.api.v1.process._build_process_response",
        new=AsyncMock(return_value=error_response),
    ):
        response = asyncio.run(process_image(_request_with_body(PNG_1X1_BYTES, "image/png")))
    assert_process_envelope(response.model_dump(exclude_none=True))


def test_process_endpoint_validation_error_contract() -> None:
    response = asyncio.run(process_image(_request_with_body(b"nope", "image/png")))
    payload = response.model_dump(exclude_none=True)
    assert payload["status"] == "error"
    assert payload["error"]["category"] == "validation"
    assert payload["error"]["code"] == "image_decode_failed"
    assert "requestId" not in payload
    assert "payload" not in payload
