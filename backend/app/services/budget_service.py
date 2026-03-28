import os

from app.schemas.diagnostics import CostEstimate

_GCV_USD_PER_IMAGE = 0.0015
_USD_TO_SGD = 1.35


def estimate_request_cost(*, file_size_bytes: int) -> CostEstimate:  # noqa: ARG001
    """Estimate the processing cost for a single request.

    Provider is determined from the OCR_PROVIDER environment variable.
    file_size_bytes is accepted for future per-size cost models; not used by GCV.
    """
    provider = os.environ.get("OCR_PROVIDER", "").strip().lower()

    if provider == "google_vision":
        estimated_sgd = round(_GCV_USD_PER_IMAGE * _USD_TO_SGD, 6)
        return CostEstimate(
            estimated_usd=_GCV_USD_PER_IMAGE,
            estimated_sgd=estimated_sgd,
            confidence="full",
        )

    return CostEstimate(confidence="unavailable")
