from app.db.session import SessionLocal


def get_db():
    """Provide a transactional database session for request handling.

    This function creates a new SQLAlchemy SessionLocal instance, yields it for use, and
    ensures that the session is properly closed after the calling context is finished.

    Yields:
        Session: A SQLAlchemy session bound to the configured database engine.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()