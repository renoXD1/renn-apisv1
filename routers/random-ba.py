from fastapi import APIRouter, HTTPException
from fastapi.responses import RedirectResponse
import httpx
import random

router = APIRouter(tags=["random"])

@router.get("/blue-arcive", summary="Random Image Blue Archive")
async def get_random_image():
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get('https://raw.githubusercontent.com/rynxzyy/blue-archive-r-img/refs/heads/main/links.json')
            response.raise_for_status()
            image_data = response.json()
            if image_data:
                random_image = random.choice(image_data)
                return RedirectResponse(url=random_image)
            raise HTTPException(status_code=404, detail="No images found")
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=f"Failed to fetch images: {e.response.text}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))