import pytest

from governance.holdout import load_holdout
from governance.upstream import ensure_upstream


@pytest.fixture(scope="session")
def holdout():
    ensure_upstream()
    return load_holdout()
