"""V0.1 uses a fixed curriculum. Progress is descriptive, not a mastery model."""
def summarize_attempts(attempts: list[dict]) -> dict:
    scored = [r for r in attempts if r.get("score") is not None]
    return {
        "attempts": len(scored),
        "average_score": sum(r["score"] for r in scored) / len(scored) if scored else None,
        "confident_errors": sum(r["score"] == 0 and r["confidence"] == 4 for r in scored),
    }
