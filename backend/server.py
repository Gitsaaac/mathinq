from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import uuid
import os

from backend import pipeline  # your pipeline function

app = FastAPI()

# CORS so your frontend can call the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/generate")
def generate(query: str):
    """
    Run the AI+Manim pipeline and return URLs for:
    - the raw video (mp4)
    - the generated audio (mp3)
    """

    try:
        print("🎬 Running pipeline...")

        video_path, audio_path = pipeline(query)

        # Validate output
        if not video_path or not os.path.exists(video_path):
            raise HTTPException(status_code=500, detail="Pipeline failed: No video created.")

        if not audio_path or not os.path.exists(audio_path):
            raise HTTPException(status_code=500, detail="Pipeline failed: No audio created.")

        # Generate unique public filenames
        video_id = f"{uuid.uuid4()}.mp4"
        audio_id = f"{uuid.uuid4()}.mp3"

        public_video_path = f"outputs/{video_id}"
        public_audio_path = f"outputs/{audio_id}"

        os.rename(video_path, public_video_path)
        os.rename(audio_path, public_audio_path)

        print("✅ Returning file URLs…")

        return {
            "video_url": f"/video/{video_id}",
            "audio_url": f"/audio/{audio_id}"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Serve video
@app.get("/video/{filename}")
def serve_video(filename: str):
    path = f"outputs/{filename}"
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="Video not found")
    return FileResponse(path, media_type="video/mp4", filename=filename)


# Serve audio
@app.get("/audio/{filename}")
def serve_audio(filename: str):
    path = f"outputs/{filename}"
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="Audio not found")
    return FileResponse(path, media_type="audio/mpeg", filename=filename)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)