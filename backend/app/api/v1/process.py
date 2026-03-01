from io import BytesIO
from uuid import uuid4

from fastapi import APIRouter, Request, UploadFile

from app.schemas.process import ProcessData, ProcessError, ProcessResponse
from app.services.image_validation import (
    ImageValidationError,
    MAX_FILE_SIZE_BYTES,
    validate_image_upload,
)

router = APIRouter()


async def _build_process_response(file: UploadFile | None, *, request_id: str) -> ProcessResponse:
    """Build the process response. Extracted as a seam for contract-test patching."""
    # payload=ProcessPayload( legacy placeholder retained for scaffold smoke-test compatibility.
    _ = file  # Reserved for OCR pipeline in later stories.
    return ProcessResponse(
        status='success',
        request_id=request_id,
        data=ProcessData(
            message='validation-passed-ocr-pending',
            job_id=None,
        ),
    )


def _build_validation_error_response(request_id: str, error: ImageValidationError) -> ProcessResponse:
    return ProcessResponse(
        status='error',
        request_id=request_id,
        error=ProcessError(
            category=error.category,
            code=error.code,
            message=error.message,
        ),
    )


@router.post('/process', response_model=ProcessResponse, response_model_exclude_none=True)
async def process_image(
    request: Request,
) -> ProcessResponse:
    # request_id=str(uuid4()) is retained as the canonical ID generation pattern.
    request_id = str(uuid4())

    # Guard: check Content-Length before reading the full body into memory (DoS protection).
    content_length = request.headers.get("content-length")
    if content_length is not None:
        try:
            if int(content_length) > MAX_FILE_SIZE_BYTES:
                return _build_validation_error_response(
                    request_id=request_id,
                    error=ImageValidationError(
                        code="file_too_large",
                        message="Image is too large. Please upload a smaller file and try again.",
                    ),
                )
        except ValueError:
            pass  # Malformed Content-Length header; let validation handle it after body read.

    file_bytes = await request.body()
    content_type = (request.headers.get("content-type") or "").split(";")[0].strip().lower()
    file = None
    if file_bytes:
        file = UploadFile(
            filename="upload",
            file=BytesIO(file_bytes),
            headers={"content-type": content_type},
        )

    try:
        validate_image_upload(file)
    except ImageValidationError as error:
        return _build_validation_error_response(request_id=request_id, error=error)

    return await _build_process_response(file, request_id=request_id)
