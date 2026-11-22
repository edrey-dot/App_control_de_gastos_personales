import os
import tempfile
from pathlib import Path

import pytest

_test_database_directory = tempfile.TemporaryDirectory(prefix="app-gastos-tests-")
_test_database_path = Path(_test_database_directory.name, "test.db")

os.environ["DATABASE_URL"] = f"sqlite:///{_test_database_path.as_posix()}"
os.environ.setdefault("SECRET_KEY", "pytest-only-secret-key-not-for-production")


@pytest.hookimpl(trylast=True)
def pytest_sessionfinish(session, exitstatus):
    from app.db.session import engine

    engine.dispose()
    _test_database_directory.cleanup()
