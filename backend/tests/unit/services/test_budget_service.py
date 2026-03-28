import pytest

from app.services.budget_service import estimate_request_cost


def test_google_vision_provider_returns_full_estimate(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("OCR_PROVIDER", "google_vision")

    result = estimate_request_cost(file_size_bytes=50_000)

    assert result.confidence == "full"
    assert result.estimated_usd == pytest.approx(0.0015)
    assert result.estimated_sgd == pytest.approx(0.002025)


def test_unset_provider_returns_unavailable(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("OCR_PROVIDER", raising=False)

    result = estimate_request_cost(file_size_bytes=50_000)

    assert result.confidence == "unavailable"
    assert result.estimated_usd is None
    assert result.estimated_sgd is None


def test_textract_provider_returns_unavailable(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("OCR_PROVIDER", "textract")

    result = estimate_request_cost(file_size_bytes=50_000)

    assert result.confidence == "unavailable"
    assert result.estimated_usd is None
    assert result.estimated_sgd is None


def test_provider_name_with_surrounding_whitespace_is_normalized(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("OCR_PROVIDER", " google_vision ")

    result = estimate_request_cost(file_size_bytes=50_000)

    assert result.confidence == "full"
