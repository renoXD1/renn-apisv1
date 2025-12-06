from fastapi import APIRouter, HTTPException
import httpx
import uuid

router = APIRouter(tags=["downloader"])

headers = {
    "origin": "https://spotdown.org",
    "referer": "https://spotdown.org/",
    "user-agent": "Mozilla/5.0 (Linux; Android 15; SM-F958 Build/AP3A.240905.015) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.6723.86 Mobile Safari/537.36"
}


async def upload_uguu(buffer: bytes, filename: str):
    try:
        multipart = {
            "files[]": (filename, buffer, "audio/mpeg")
        }

        async with httpx.AsyncClient(timeout=40) as client:
            r = await client.post("https://uguu.se/upload.php", files=multipart)
            data = r.json()

            if "files" not in data or not data["files"]:
                raise Exception("Upload gagal")

            f = data["files"][0]

            name = f.get("name", filename)
            url = f.get("url")
            size = f.get("size", "Unknown")

            if not url:
                raise Exception("Gagal mendapatkan URL dari Uguu")

            return {
                "name": name,
                "url": url,
                "size": size
            }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/Spotify", summary="Get MP3 Spotify")
async def spotify_dl(input: str):
    if not input:
        raise HTTPException(status_code=400, detail="Input is required")

    try:
        async with httpx.AsyncClient(timeout=40) as client:

            res = await client.get(
                f"https://spotdown.org/api/song-details?url={input}",
                headers=headers
            )

            j = res.json()

            if "songs" not in j or not j["songs"]:
                raise HTTPException(status_code=404, detail="Track not found")

            song = j["songs"][0]

            audio_res = await client.post(
                "https://spotdown.org/api/download",
                json={"url": song["url"]},
                headers=headers
            )

            if audio_res.status_code != 200:
                raise HTTPException(status_code=500, detail="Failed to download audio")

            audio_bytes = audio_res.content

            filename = song["title"].replace(" ", "_") + ".mp3"

            upload_res = await upload_uguu(audio_bytes, filename)

            return {
                "metadata": {
                    "title": song["title"],
                    "artist": song["artist"],
                    "duration": song["duration"],
                    "cover": song["thumbnail"],
                    "url": song["url"]
                },
                "audio": upload_res
            }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))