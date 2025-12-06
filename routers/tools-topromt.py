from fastapi import APIRouter, UploadFile, File, HTTPException
import httpx

router = APIRouter(tags=["tools"])


@router.post("/topromt", summary="Image To Promt")
async def image_to_prompt(image: UploadFile = File(...)):
    url = "https://www.reliablesoft.net/wp-admin/admin-ajax.php"

    try:
        img_bytes = await image.read()

        files = {
            "action": (None, "openai_process"),
            "shortcode_action": (None, "image-to-prompt-generator"),
            "image_file": (image.filename, img_bytes, image.content_type)
        }

        headers = {
            "accept": "*/*",
            "x-requested-with": "XMLHttpRequest",
            "referer": "https://www.reliablesoft.net/ai-text-generator-tools/image-to-prompt-generator/"
        }

        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(url, files=files, headers=headers)
            response.raise_for_status()
            data = response.json()

            return {"prompt": data.get("data", {}).get("data")}

    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=f"API error: {e.response.text}")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))