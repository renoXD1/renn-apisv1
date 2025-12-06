from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
import httpx
import io

router = APIRouter(tags=["tools"])


@router.get("/ssweb", summary="Ss Web")
async def ssweb(
    url: str,
    width: int = 1280,
    height: int = 720,
    full_page: bool = False,
    device_scale: int = 1
):
    if not url.startswith("https://"):
        raise HTTPException(status_code=400, detail="Invalid URL")

    payload = {
        "url": url,
        "browserWidth": int(width),
        "browserHeight": int(height),
        "fullPage": bool(full_page),
        "deviceScaleFactor": int(device_scale),
        "format": "png"
    }

    headers = {
        "content-type": "application/json",
        "referer": "https://imagy.app/full-page-screenshot-taker/",
        "user-agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Mobile Safari/537.36"
    }

    try:
        async with httpx.AsyncClient(timeout=30) as client:
            res = await client.post(
                "https://gcp.imagy.app/screenshot/createscreenshot",
                json=payload,
                headers=headers
            )

            data = res.json()
            file_url = data.get("fileUrl")

            if not file_url:
                raise HTTPException(status_code=500, detail="Gagal mengambil screenshot")

            img_res = await client.get(file_url)
            img_res.raise_for_status()

            return StreamingResponse(
                io.BytesIO(img_res.content),
                media_type="image/png"
            )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))