import pytest
from app.database import Base, make_engine, make_session_factory


@pytest.fixture
def session_factory(tmp_path):
    db_path = tmp_path / "test.db"
    engine = make_engine(f"sqlite:///{db_path}")
    Base.metadata.create_all(engine)
    factory = make_session_factory(engine)
    yield factory
    engine.dispose()
