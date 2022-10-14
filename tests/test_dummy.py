from mo_smtp.smtp_agent import settings


def test_initial() -> None:
    print(settings)
    assert None is None
