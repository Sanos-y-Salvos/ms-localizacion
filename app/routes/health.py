from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
def health():
    return {"status": "ok", "microservicio": "ms-localizacion", "version": "1.0.0"}
