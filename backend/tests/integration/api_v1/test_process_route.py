import asyncio
from unittest.mock import patch

from app.adapters.ocr_provider import RawOcrSegment
from app.api.v1.process import process_image

from helpers import PNG_1X1_BYTES, StubOcrProvider, _request_with_body


def test_process_route_returns_envelope() -> None:
    with patch(
        "app.services.ocr_service.get_ocr_provider",
        return_value=StubOcrProvider([RawOcrSegment(text="你好", language="zh", confidence=0.9)]),
    ):
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


def test_process_route_valid_upload_returns_success_ocr_segments() -> None:
    with patch(
        "app.services.ocr_service.get_ocr_provider",
        return_value=StubOcrProvider(
            [
                RawOcrSegment(text="你好", language="zh", confidence=0.98),
                RawOcrSegment(text="hello", language="en", confidence=0.77),
            ]
        ),
    ):
        request = _request_with_body(PNG_1X1_BYTES, "image/png")
        response = asyncio.run(process_image(request))

    assert response.status == "success"
    assert response.request_id
    assert response.data is not None
    assert response.data.ocr is not None
    assert response.data.ocr.segments[0].text == "你好"
    assert response.data.ocr.segments[0].language == "zh"
    assert response.data.ocr.segments[0].confidence == 0.98


def test_process_route_ocr_no_text_returns_typed_ocr_error() -> None:
    with patch(
        "app.services.ocr_service.get_ocr_provider",
        return_value=StubOcrProvider([RawOcrSegment(text="hello", language="en", confidence=0.7)]),
    ):
        request = _request_with_body(PNG_1X1_BYTES, "image/png")
        response = asyncio.run(process_image(request))

    assert response.status == "error"
    assert response.error is not None
    assert response.error.category == "ocr"
    assert response.error.code == "ocr_no_text_detected"


def test_process_route_missing_file_returns_validation_error() -> None:
    request = _request_with_body(b"", "")
    response = asyncio.run(process_image(request))

    assert response.status == "error"
    assert response.error is not None
    assert response.error.category == "validation"
    assert response.error.code == "missing_file"
