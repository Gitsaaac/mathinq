import React, { useState } from "react";

const BACKEND_URL = "http://localhost:8000"; // change if your backend is on a different host/port

function App() {
  const [prompt, setPrompt] = useState("");
  const [videoUrl, setVideoUrl] = useState("");
  const [audioUrl, setAudioUrl] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

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

      // Your FastAPI endpoint expects `query: str`, taken from the query params
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
      // Backend returns: { video_url: "/video/...", audio_url: "/audio/..." }
      setVideoUrl(`${BACKEND_URL}${data.video_url}`);
      setAudioUrl(`${BACKEND_URL}${data.audio_url}`);
    } catch (err) {
      console.error(err);
      setError(err.message || "Something went wrong.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div
      style={{
        minHeight: "100vh",
        padding: "2rem",
        backgroundColor: "#0f172a",
        color: "#e5e7eb",
        fontFamily: "system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
      }}
    >
      <div
        style={{
          maxWidth: "800px",
          margin: "0 auto",
          padding: "2rem",
          backgroundColor: "#020617",
          borderRadius: "1rem",
          boxShadow: "0 10px 40px rgba(0,0,0,0.4)",
        }}
      >
        <h1 style={{ fontSize: "2rem", marginBottom: "1rem" }}>
          🧠 Math → 🎬 Manim → 🎧 Voiceover
        </h1>
        <p style={{ marginBottom: "1.5rem", color: "#9ca3af" }}>
          Type what you need help with (e.g. <em>"systems of linear equations"</em>),
          and the backend will generate a Manim video and a voiceover.
        </p>

        <form onSubmit={handleSubmit} style={{ marginBottom: "1.5rem" }}>
          <textarea
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            rows={3}
            placeholder="What do you need help with?"
            style={{
              width: "100%",
              padding: "0.75rem 1rem",
              borderRadius: "0.75rem",
              border: "1px solid #1f2937",
              backgroundColor: "#020617",
              color: "#e5e7eb",
              resize: "vertical",
              outline: "none",
              marginBottom: "1rem",
            }}
          />
          <button
            type="submit"
            disabled={loading}
            style={{
              padding: "0.6rem 1.4rem",
              borderRadius: "999px",
              border: "none",
              background: loading ? "#4b5563" : "#22c55e",
              color: "#020617",
              fontWeight: 600,
              cursor: loading ? "not-allowed" : "pointer",
              transition: "transform 0.1s ease, box-shadow 0.1s ease",
              boxShadow: loading
                ? "none"
                : "0 10px 20px rgba(34,197,94,0.25)",
            }}
          >
            {loading ? "Generating..." : "Generate Video & Audio"}
          </button>
        </form>

        {error && (
          <div
            style={{
              marginBottom: "1.5rem",
              padding: "0.75rem 1rem",
              borderRadius: "0.75rem",
              backgroundColor: "#7f1d1d",
              color: "#fee2e2",
              fontSize: "0.9rem",
            }}
          >
            ⚠️ {error}
          </div>
        )}

        {videoUrl && (
          <div style={{ marginBottom: "1.5rem" }}>
            <h2 style={{ marginBottom: "0.5rem", fontSize: "1.2rem" }}>
              🎬 Generated Video
            </h2>
            <video
              src={videoUrl}
              controls
              style={{
                width: "100%",
                borderRadius: "0.75rem",
                border: "1px solid #1f2937",
                backgroundColor: "black",
              }}
            />
          </div>
        )}

        {audioUrl && (
          <div>
            <h2 style={{ marginBottom: "0.5rem", fontSize: "1.2rem" }}>
              🎧 Generated Audio
            </h2>
            <audio
              src={audioUrl}
              controls
              style={{
                width: "100%",
              }}
            />
          </div>
        )}

        {!loading && !videoUrl && !audioUrl && !error && (
          <p style={{ marginTop: "1rem", color: "#6b7280", fontSize: "0.9rem" }}>
            After you click <strong>Generate</strong>, the video and audio will
            appear here.
          </p>
        )}
      </div>
    </div>
  );
}

export default App;
