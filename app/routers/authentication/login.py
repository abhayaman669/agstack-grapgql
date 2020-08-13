from fastapi import APIRouter


router = APIRouter()


@router.get("/")
async def login():
    return "Yep this is working"
