import json
import re
import warnings

def parse_scores(text: str):
    """
    Extract the JSON scores block from Claude response.
    Looks specifically for the scores structure to avoid
    grabbing unrelated JSON blocks. Returns None and warns
    if parsing fails so the caller is always informed.
    """
    match = re.search(r'{"scores"\s*:\s*{[\s\S]*?"overall"\s*:\s*\d+[\s\S]*?}', text)
    if not match:
        match = re.search(r'{[\s\S]*?"overall"\s*:\s*\d+[\s\S]*?}', text)
    if not match:
        warnings.warn(
            "parse_scores: No scores JSON found in Claude response. "
            "Scores will not be displayed.",
            stacklevel=2,
        )
        return None
    try:
        data = json.loads(match.group(0))
        if "scores" in data and isinstance(data["scores"], dict):
            data["scores"] = {
                k: max(0, min(100, int(v)))
                for k, v in data["scores"].items()
            }
        if "overall" in data:
            data["overall"] = max(0, min(100, int(data["overall"])))
        return data
    except (json.JSONDecodeError, ValueError, TypeError) as e:
        warnings.warn(
            f"parse_scores: JSON found but failed to parse — {e}.",
            stacklevel=2,
        )
        return None

def interpret_score(score: int) -> tuple:
    """Return (rating_label, description) for a 0-100 score."""
    score = max(0, min(100, int(score)))
    if score >= 80:
        return "Excellent", "World-class — sustain and innovate"
    elif score >= 60:
        return "Good", "Above average — targeted improvements needed"
    elif score >= 40:
        return "Fair", "Moderate gaps — structured improvement required"
    else:
        return "At Risk", "Significant underperformance — immediate action needed"

def print_score_bar(domain: str, score: int):
    """Print a visual ASCII score bar to the terminal."""
    score  = max(0, min(100, int(score)))
    filled = score // 5
    bar    = "█" * filled + "░" * (20 - filled)
    rating, _ = interpret_score(score)
    print(f"  {domain:<18} [{bar}] {score:>3}/100  {rating}")
