from app.retrieval import LexicalRetriever


def test_staff_password_reset_ranks_correct_policy():
    assert LexicalRetriever().retrieve("reset a staff password", 1)[0].id == "password_reset"


def test_student_access_is_distinct():
    assert LexicalRetriever().retrieve("student account access ticket", 1)[0].id == "account_access"
