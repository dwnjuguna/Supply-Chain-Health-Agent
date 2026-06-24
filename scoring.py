import json
import re
import warnings


def _coerce_scores(data):
    """Validate shape and clamp domain/overall scores to 0–100. Returns the
    cleaned dict, or None if the object is not a usable scores block."""
    if not (isinstance(data, dict) and ("scores" in data or "overall" in data)):
        return None
    try:
        if isinstance(data.get("scores"), dict):
            data["scores"] = {
                k: max(0, min(100, int(v)))
                for k, v in data["scores"].items()
            }
        if "overall" in data:
            data["overall"] = max(0, min(100, int(data["overall"])))
    except (ValueError, TypeError):
        return None
    return data


def parse_scores(text: str):
    """
    Extract the JSON scores block from a Claude response.

    Tolerant of markdown code fences and negative integers, with a
    best-effort fallback that scans for any valid JSON object containing
    the scores/overall structure. Returns None and warns if no usable
    scores block can be parsed, so the caller is always informed.
    """
    # (1) Strip markdown code fences (```json ... ```) Claude sometimes adds.
    cleaned = re.sub(r'```[a-zA-Z]*', '', text)

    # Build candidate JSON strings in priority order.
    # (2) Accept negative integers (-?\d+) for the "overall" anchor so a
    #     malformed negative score does not defeat extraction.
    candidates = []
    primary = re.search(r'{"scores"\s*:\s*{[\s\S]*?"overall"\s*:\s*-?\d+[\s\S]*?}', cleaned)
    if primary:
        candidates.append(primary.group(0))
    secondary = re.search(r'{[\s\S]*?"overall"\s*:\s*-?\d+[\s\S]*?}', cleaned)
    if secondary:
        candidates.append(secondary.group(0))
    # (3) Fallback — try json.loads() on any {...} block: outermost first,
    #     then the smallest individual blocks.
    greedy = re.search(r'\{[\s\S]*\}', cleaned)
    if greedy:
        candidates.append(greedy.group(0))
    candidates.extend(re.findall(r'\{[\s\S]*?\}', cleaned))

    for blob in candidates:
        try:
            data = json.loads(blob)
        except (json.JSONDecodeError, ValueError, TypeError):
            continue
        result = _coerce_scores(data)
        if result is not None:
            return result

    warnings.warn(
        "parse_scores: No scores JSON found in Claude response. "
        "Scores will not be displayed.",
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
