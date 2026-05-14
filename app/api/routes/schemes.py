from fastapi import APIRouter

router = APIRouter()

# Placeholder for future REST APIs to manage schemes directly

@router.get("/schemes")
async def list_schemes():
    """
    Placeholder endpoint for listing all available schemes.
    """
    return {"message": "Endpoint not implemented yet"}
