import React, { useState, useRef, useEffect} from "react";
import "./App.css";

const BACKEND_URL = "http://localhost:8000"; // change if your backend is on a different host/port

function App() {
  const [prompt, setPrompt] = useState("");
  const [videoUrl, setVideoUrl] = useState("");
  const [audioUrl, setAudioUrl] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const videoRef = useRef(null);
  const audioRef = useRef(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setVideoUrl("");
    setAudioUrl("");

    if (!prompt.trim()) {
      setError("Please enter a prompt.");
      return;
    }

    try {
      setLoading(true);

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
    } catch (err) {
      console.error(err);
      setError(err.message || "Something went wrong.");
    } finally {
      setLoading(false);
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

  // Keep audio tightly synced to video while playing
  const handleVideoTimeUpdate = () => {
    if (!videoRef.current || !audioRef.current) return;
    const v = videoRef.current;
    const a = audioRef.current;
    const diff = Math.abs(a.currentTime - v.currentTime);

    // Adjust only if they drift more than a tiny threshold
    if (diff > 0.1) {
      a.currentTime = v.currentTime;
    }
  };

    useEffect(() => {
    if (audioRef.current) {
      audioRef.current.playbackRate = 1.5;   // 🔥 default 1.5× audio speed
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
                  className={`primary-button ${loading ? "is-loading" : ""}`}
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
                  Your explainer video will appear here after you submit a topic above.
                </p>
              </div>
            )}

            {/* Actual video once ready */}
            {!loading && videoUrl && (
              <div className="video-wrapper">
                <video
                  ref={videoRef}
                  src={videoUrl}
                  controls
                  muted = {true}
                  onPlay={handleVideoPlay}
                  onPause={handleVideoPause}
                  // onTimeUpdate={handleVideoTimeUpdate}
                />
              </div>
            )}

            {/* Hidden audio used only for sync */}
            {audioUrl && <audio ref={audioRef} src={audioUrl} />}
          </section>
        </main>

        <footer className="app-footer">
          <span className="footer-text">Powered by Manim</span>
        </footer>
      </div>
    </div>
  );
}

export default App;
