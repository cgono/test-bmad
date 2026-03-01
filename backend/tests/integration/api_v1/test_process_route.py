import asyncio

from starlette.requests import Request

from app.api.v1.process import process_image

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


def test_process_route_returns_envelope() -> None:
    request = _request_with_body(PNG_1X1_BYTES, "image/png")
    response = asyncio.run(process_image(request))

    assert response.status in {"success", "partial", "error"}
    assert isinstance(response.request_id, str)
    assert response.request_id
    assert response.data is not None or response.error is not None


def test_process_route_invalid_upload_returns_validation_error() -> None:
    request = _request_with_body(b"not-an-image", "image/png")
    response = asyncio.run(process_image(request))

    assert response.status == "error"
    assert response.error is not None
    assert response.error.category == "validation"
    assert response.error.code == "image_decode_failed"
    assert isinstance(response.error.message, str)


def test_process_route_valid_upload_returns_success_progress_message() -> None:
    request = _request_with_body(PNG_1X1_BYTES, "image/png")
    response = asyncio.run(process_image(request))

    assert response.status == "success"
    assert response.request_id
    assert response.data is not None
    assert response.data.message == "validation-passed-ocr-pending"


def test_process_route_missing_file_returns_validation_error() -> None:
    request = _request_with_body(b"", "")
    response = asyncio.run(process_image(request))

    assert response.status == "error"
    assert response.error is not None
    assert response.error.category == "validation"
    assert response.error.code == "missing_file"
