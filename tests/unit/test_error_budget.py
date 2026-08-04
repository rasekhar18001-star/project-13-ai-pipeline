import pytest

from sre.error_budget import calculate


@pytest.mark.parametrize(
    ("total", "bad", "verdict"),
    [(1000, 2, "healthy"), (1000, 8, "high-burn"), (1000, 12, "exhausted"), (0, 0, "healthy")],
)
def test_verdicts(total, bad, verdict):
    assert calculate(0.99, total, bad).verdict == verdict


@pytest.mark.parametrize(("slo", "total", "bad"), [(0, 1, 0), (1.1, 1, 0), (0.99, -1, 0), (0.99, 1, 2)])
def test_invalid(slo, total, bad):
    with pytest.raises(ValueError):
        calculate(slo, total, bad)
