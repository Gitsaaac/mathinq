import React, { useState, useRef, useEffect } from "react";
import "./App.css";
import PracticeTab from "./practicetab";

const BACKEND_URL = "http://localhost:8000"; // change if your backend is on a different host/port

function App() {
  const [prompt, setPrompt] = useState("");
  const [videoUrl, setVideoUrl] = useState("");
  const [audioUrl, setAudioUrl] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [sampleId, setSampleId] = useState(null);
  const [feedbackSubmitted, setFeedbackSubmitted] = useState(false);
  const [activeTab, setActiveTab] = useState("lesson"); // "lesson" | "practice"

  // Practice-problem state (comes from the SAME query as the lesson)
  const [practiceProblemUrl, setPracticeProblemUrl] = useState("");
  const [practiceAnswerUrl, setPracticeAnswerUrl] = useState("");
  const [practiceLoading, setPracticeLoading] = useState(false);
  const [practiceError, setPracticeError] = useState("");

  const videoRef = useRef(null);
  const audioRef = useRef(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setVideoUrl("");
    setAudioUrl("");
    setSampleId(null);
    setFeedbackSubmitted(false);

    // reset practice state for this new query
    setPracticeProblemUrl("");
    setPracticeAnswerUrl("");
    setPracticeError("");

    if (!prompt.trim()) {
      setError("Please enter a prompt.");
      return;
    }

    try {
      setLoading(true);

      // 1) Generate lesson video/audio
      const res = await fetch(
        `${BACKEND_URL}/generate?query=${encodeURIComponent(prompt)}`,
        {
          method: "POST",
        }
      );

      if (!res.ok) {
        const errData = await res.json().catch(() => ({}));
        throw new Error(errData.detail || "Failed to generate video/audio");
      }

      const data = await res.json();
      setVideoUrl(`${BACKEND_URL}${data.video_url}`);
      setAudioUrl(`${BACKEND_URL}${data.audio_url}`);
      setSampleId(data.sample_id || null);

      // 2) In parallel (or right after), generate practice problem for the SAME query
      try {
        setPracticeLoading(true);
        const pRes = await fetch(
          `${BACKEND_URL}/practice?query=${encodeURIComponent(prompt)}`,
          {
            method: "POST",
          }
        );

        if (!pRes.ok) {
          const pErrData = await pRes.json().catch(() => ({}));
          throw new Error(
            pErrData.detail || "Failed to generate practice problem"
          );
        }

        const pData = await pRes.json();
        setPracticeProblemUrl(`${BACKEND_URL}${pData.problem_url}`);
        setPracticeAnswerUrl(`${BACKEND_URL}${pData.answer_url}`);
      } catch (pErr) {
        console.error("Practice error:", pErr);
        setPracticeError(
          pErr.message || "Failed to generate practice problem."
        );
      } finally {
        setPracticeLoading(false);
      }
    } catch (err) {
      console.error(err);
      setError(err.message || "Something went wrong.");
    } finally {
      setLoading(false);
    }
  };

  const handleFeedback = async (rating) => {
    if (!sampleId) return;

    try {
      await fetch(`${BACKEND_URL}/feedback`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          sample_id: sampleId,
          rating, // +1 or -1
          comment: null,
        }),
      });

      setFeedbackSubmitted(true);
    } catch (err) {
      console.error("Failed to send feedback:", err);
    }
  };

  // --- Sync helpers: video is the "master" ---

  const handleVideoPlay = () => {
    if (!videoRef.current || !audioRef.current) return;
    try {
      audioRef.current.currentTime = videoRef.current.currentTime;
      audioRef.current.play();
    } catch (err) {
      console.error("Audio play error:", err);
    }
  };

  const handleVideoPause = () => {
    if (!audioRef.current) return;
    audioRef.current.pause();
  };

  // Default 1.5x speed for audio
  useEffect(() => {
    if (audioRef.current) {
      audioRef.current.playbackRate = 1.5;
    }
  }, [audioUrl]);

  const hasMedia = Boolean(videoUrl || audioUrl);

  return (
    <div className="app-root">
      <div className="app-gradient" />

      <div className="app-shell">
        <header className="app-header">
          <div>
            <h1 className="app-title">MathInq</h1>
            <p className="app-subtitle">Redefining mathematical education</p>
          </div>
          <div className="badge beta-badge">Beta</div>
        </header>

        <main className="app-main">
          {/* Tab row */}
          <div className="tab-row">
            <button
              type="button"
              className={`tab-button ${
                activeTab === "lesson" ? "tab-button-active" : ""
              }`}
              onClick={() => setActiveTab("lesson")}
            >
              Lesson
            </button>
            <button
              type="button"
              className={`tab-button ${
                activeTab === "practice" ? "tab-button-active" : ""
              }`}
              onClick={() => setActiveTab("practice")}
            >
              Practice Problems
            </button>
          </div>

          {activeTab === "lesson" && (
            <>
              {/* Top input card */}
              <section className="card prompt-card">
                <form onSubmit={handleSubmit} className="prompt-form">
                  <label className="field-label" htmlFor="prompt">
                    What do you want explained?
                  </label>
                  <textarea
                    id="prompt"
                    value={prompt}
                    onChange={(e) => setPrompt(e.target.value)}
                    rows={3}
                    placeholder='e.g. "Explain the difference between mean, median, and mode"'
                    className="prompt-input"
                  />
                  <div className="prompt-footer">
                    <button
                      type="submit"
                      disabled={loading}
                      className={`primary-button ${
                        loading ? "is-loading" : ""
                      }`}
                    >
                      {loading ? (
                        <>
                          <span className="spinner" />
                          Generating…
                        </>
                      ) : (
                        "Generate Video & Audio"
                      )}
                    </button>
                  </div>
                </form>

                {error && (
                  <div className="alert alert-error">
                    <span className="alert-icon">⚠️</span>
                    <span>{error}</span>
                  </div>
                )}
              </section>

              {/* Bottom output card: always visible */}
              <section className="card output-card">
                <div className="output-header">
                  <h2 className="section-title">Your Generated Lesson</h2>
                  <p className="section-subtitle">
                    MathInq creates a Manim animation with audio custom for you
                  </p>
                </div>

                {/* Loading state */}
                {loading && (
                  <div className="output-loading">
                    <div className="loading-orb" />
                    <p className="loading-text">Generating your lesson…</p>
                    <p className="loading-subtext">
                      Building the animation and syncing the voiceover.
                    </p>
                  </div>
                )}

                {/* Placeholder before any generation */}
                {!loading && !hasMedia && !error && (
                  <div className="output-placeholder">
                    <div className="placeholder-video" />
                    <p className="placeholder-text">
                      Your explainer video will appear here after you submit a
                      topic above.
                    </p>
                  </div>
                )}

                {/* Actual video once ready */}
                {!loading && videoUrl && (
                  <>
                    <div className="video-wrapper">
                      <video
                        ref={videoRef}
                        src={videoUrl}
                        controls
                        muted={true}
                        onPlay={handleVideoPlay}
                        onPause={handleVideoPause}
                      />
                    </div>

                    {sampleId && !feedbackSubmitted && (
                      <div className="feedback-row">
                        <button
                          type="button"
                          className="secondary-button feedback-button"
                          onClick={() => handleFeedback(1)}
                        >
                          👍 Helpful
                        </button>
                        <button
                          type="button"
                          className="secondary-button feedback-button"
                          onClick={() => handleFeedback(-1)}
                        >
                          👎 Not helpful
                        </button>
                      </div>
                    )}

                    {sampleId && feedbackSubmitted && (
                      <p className="feedback-thanks">
                        Thanks for your feedback 💚
                      </p>
                    )}
                  </>
                )}

                {/* Hidden audio used only for sync */}
                {audioUrl && <audio ref={audioRef} src={audioUrl} />}
              </section>
            </>
          )}

          {activeTab === "practice" && (
            <PracticeTab
              loading={practiceLoading}
              error={practiceError}
              problemUrl={practiceProblemUrl}
              answerUrl={practiceAnswerUrl}
            />
          )}
        </main>

        <footer className="app-footer">
          <span className="footer-text">Powered by Manim</span>
        </footer>
      </div>
    </div>
  );
}

export default App;
