from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse
import httpx
import io

router = APIRouter(tags=["tools"])
@router.post("/upscale", summary="Upscale Image")
async def upscale_image(image: UploadFile = File(...)):
    url = "https://api2.pixelcut.app/image/upscale/v1"

    img_bytes = await image.read()
    files = {
        "image": (image.filename, img_bytes, image.content_type),
        "scale": (None, "2")
    }
    headers = {
        "accept": "application/json",
        "x-client-version": "web"
    }

    try:
        async with httpx.AsyncClient(timeout=30) as client:
            # Kirim ke API Pixelcut
            response = await client.post(url, files=files, headers=headers)
            response.raise_for_status()
            data = response.json()
            result_url = data.get("result_url")

            if not result_url:
                raise HTTPException(status_code=500, detail="No result URL from API")
            img_response = await client.get(result_url)
            img_response.raise_for_status()
            return StreamingResponse(io.BytesIO(img_response.content), media_type="image/jpeg")

    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=f"Upscale API error: {e.response.text}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
