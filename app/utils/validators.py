def validate_query(query: str) -> bool:
    """
    Basic validation for an input query.
    Ensures it's not empty and meets basic length requirements.
    """
    if not query or not query.strip():
        return False
    if len(query.strip()) < 3:
        return False
    return True
