import pytest

from sre.psi import calculate_psi


def test_calm_and_alert():
    ref = list(range(1, 101))
    assert calculate_psi(ref, ref).verdict == "calm"
    assert calculate_psi(ref, list(range(1000, 1100))).verdict == "alert"


def test_moderate_with_custom_thresholds():
    result = calculate_psi(list(range(100)), list(range(10, 110)), moderate=0.001, alert=100)
    assert result.verdict == "moderate"


def test_duplicate_heavy():
    result = calculate_psi([1] * 90 + [2] * 10, [1] * 80 + [2] * 20)
    assert result.buckets_used <= 3


@pytest.mark.parametrize(
    ("ref", "cur", "buckets"), [([], [1], 10), ([1], [], 10), ([1], [1], 1), ([float("nan")], [1], 10)]
)
def test_invalid(ref, cur, buckets):
    with pytest.raises(ValueError):
        calculate_psi(ref, cur, buckets)
