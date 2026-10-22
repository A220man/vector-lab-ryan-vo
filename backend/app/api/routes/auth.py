from fastapi import APIRouter

router = APIRouter(prefix="", tags=["auth"])


@router.get("/login")
async def login():
    # Redirect to Keycloak - placeholder
    return {"message": "Redirect to Keycloak login"}


@router.get("/callback")
async def callback():
    # Handle Keycloak callback - placeholder
    return {"message": "Auth callback"}


@router.post("/logout")
async def logout():
    return {"message": "Logged out"}