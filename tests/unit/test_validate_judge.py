import pytest

from evals.validate_judge import validate


def test_null_human_labels_refused():
    with pytest.raises(ValueError, match="personally"):
        validate([{"human_grounded": None}], object(), "judge-v1")
