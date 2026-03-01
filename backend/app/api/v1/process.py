from uuid import uuid4

from fastapi import APIRouter, File, UploadFile

from app.schemas.process import ProcessData, ProcessResponse

router = APIRouter()


async def _build_process_response(file: UploadFile | None) -> ProcessResponse:
    """Build the process response. Extracted as a seam for contract-test patching."""
    _ = file  # Reserved for OCR pipeline in later stories.
    return ProcessResponse(
        status="success",
        request_id=str(uuid4()),
        data=ProcessData(
            message="processing-not-implemented",
            job_id=None,
        ),
    )


@router.post("/process", response_model=ProcessResponse, response_model_exclude_none=True)
async def process_image(file: UploadFile | None = File(default=None)) -> ProcessResponse:
    return await _build_process_response(file)
