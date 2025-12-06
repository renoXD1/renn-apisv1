from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
import httpx
import io

router = APIRouter(tags=["random"])

@router.get("/random-waifu")
async def get_random_waifu():
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("https://api.waifu.pics/sfw/waifu")
            response.raise_for_status()
            data = response.json()
            image_url = data["url"]
            
            image_response = await client.get(image_url)
            image_response.raise_for_status()
            
            image_bytes = io.BytesIO(image_response.content)
            return StreamingResponse(image_bytes, media_type="image/png")
            
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=f"Failed to fetch waifu: {e.response.text}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))