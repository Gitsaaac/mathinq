import React, { useState, useEffect } from "react";

function PracticeTab({ loading, error, problemUrl, answerUrl }) {
  const [showAnswer, setShowAnswer] = useState(false);

  // When a new problem arrives, hide the answer again
  useEffect(() => {
    setShowAnswer(false);
  }, [problemUrl, answerUrl]);

  const hasProblem = Boolean(problemUrl);

  return (
    <>
      {/* Output card only (no prompt here) */}
      <section className="card output-card">
        <div className="output-header">
          <h2 className="section-title">Practice Problem</h2>
          <p className="section-subtitle">
            Based on your latest lesson topic. Try it yourself, then reveal the answer.
          </p>
        </div>

        {error && (
          <div className="alert alert-error">
            <span className="alert-icon">⚠️</span>
            <span>{error}</span>
          </div>
        )}

        {loading && (
          <div className="output-loading">
            <div className="loading-orb" />
            <p className="loading-text">Generating your practice problem…</p>
          </div>
        )}

        {!loading && !hasProblem && !error && (
          <div className="output-placeholder">
            <div className="placeholder-video" />
            <p className="placeholder-text">
              Generate a lesson first, and your matching practice problem will appear here.
            </p>
          </div>
        )}

        {!loading && hasProblem && (
          <>
            <div className="practice-img-container">
              <img src={problemUrl} alt="Practice problem" />
            </div>

            {answerUrl && !showAnswer && (
              <div className="feedback-row" style={{ marginTop: "0.75rem" }}>
                <button
                  type="button"
                  className="primary-button"
                  onClick={() => setShowAnswer(true)}
                >
                  Show Answer
                </button>
              </div>
            )}

            {answerUrl && showAnswer && (
              <div className="practice-img-container answer-container">
                <img src={answerUrl} alt="Practice answer" />
              </div>
            )}
          </>
        )}
      </section>
    </>
  );
}

export default PracticeTab;
