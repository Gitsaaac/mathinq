from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import uuid
import os
from pydantic import BaseModel
from rlhf import init_db, log_sample, log_feedback

from backend import pipeline  # your pipeline function
from practice_problems import prob_ans_pipeline


app = FastAPI()
init_db() #only creates if not exist

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

        sample_id = log_sample(
            prompt=query,
            manim_code="",           # we aren't passing code right now
            narration_text=None,     # not needed yet
            video_path=public_video_path,
            audio_path=public_audio_path,
            meta={"source": "api"},  # optional
        )

        print("✅ Returning file URLs…")

        return {
            "video_url": f"/video/{video_id}",
            "audio_url": f"/audio/{audio_id}",
            "sample_id": sample_id,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@app.post("/practice")
def practice(query: str):
    """
    Generate a practice problem and answer as LaTeX images.
    Returns URLs for:
    - problem image (PNG)
    - answer image (PNG)
    """
    try:
        prob_path, ans_path = prob_ans_pipeline(query)

        if not prob_path or not os.path.exists(prob_path):
            raise HTTPException(status_code=500, detail="No practice problem image created.")
        if not ans_path or not os.path.exists(ans_path):
            raise HTTPException(status_code=500, detail="No practice answer image created.")

        problem_id = f"{uuid.uuid4()}.png"
        answer_id = f"{uuid.uuid4()}.png"

        public_problem_path = f"outputs/{problem_id}"
        public_answer_path = f"outputs/{answer_id}"

        os.rename(prob_path, public_problem_path)
        os.rename(ans_path, public_answer_path)

        return {
            "problem_url": f"/practice/problem/{problem_id}",
            "answer_url": f"/practice/answer/{answer_id}",
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

@app.get("/practice/problem/{filename}")
def serve_practice_problem(filename: str):
    path = f"outputs/{filename}"
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="Problem image not found")
    return FileResponse(path, media_type="image/png", filename=filename)


@app.get("/practice/answer/{filename}")
def serve_practice_answer(filename: str):
    path = f"outputs/{filename}"
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="Answer image not found")
    return FileResponse(path, media_type="image/png", filename=filename)



class FeedbackIn(BaseModel):
    sample_id: str
    rating: int            # +1 for thumbs up, -1 for thumbs down
    comment: str | None = None


@app.post("/feedback")
def feedback(data: FeedbackIn):
    if data.rating not in (1, -1):
        raise HTTPException(status_code=400, detail="rating must be +1 or -1")

    log_feedback(
        sample_id=data.sample_id,
        rating=data.rating,
        comment=data.comment,
        meta={"source": "frontend"},
    )
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)