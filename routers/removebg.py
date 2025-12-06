from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse
import httpx, io

router = APIRouter(tags=["tools"])

@router.post("/removebg")
async def remove_background(image: UploadFile = File(...)):
    url = "https://api2.pixelcut.app/image/matte/v1"
    try:
        img_bytes = await image.read()
        files = {
            "format": (None, "png"),
            "model": (None, "v1"),
            "image": (image.filename, img_bytes, image.content_type)
        }
        headers = {"x-client-version": "web"}
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(url, files=files, headers=headers)
            response.raise_for_status()
            result_bytes = response.content
            return StreamingResponse(io.BytesIO(result_bytes), media_type="image/png")
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=f"RemoveBG API error: {e.response.text}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))