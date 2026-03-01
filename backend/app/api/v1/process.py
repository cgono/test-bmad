from uuid import uuid4

from fastapi import APIRouter, File, UploadFile

from app.schemas.process import ProcessPayload, ProcessResponse

router = APIRouter()


@router.post('/process', response_model=ProcessResponse)
async def process_image(file: UploadFile | None = File(default=None)) -> ProcessResponse:
    _ = file  # Reserved for OCR pipeline in later stories.
    return ProcessResponse(
        status='success',
        request_id=str(uuid4()),
        payload=ProcessPayload(
            message='processing-not-implemented',
            job_id=None,
        ),
    )
