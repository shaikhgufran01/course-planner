"""Academic terms: January, May, September."""
from datetime import date

NAMES = ["January", "May", "September"]


def term_index(d: date) -> int:
    slot = 0 if d.month < 5 else 1 if d.month < 9 else 2
    return d.year * 3 + slot


def label(idx: int) -> str:
    return f"{NAMES[idx % 3]} {idx // 3}"


def code(idx: int) -> str:
    return f"F{idx % 3 + 1}-{idx // 3}"


def upcoming(n: int = 8, today: date | None = None) -> list[str]:
    cur = term_index(today or date.today())
    return [label(cur + 1 + i) for i in range(n)]


def label_to_index(lbl: str) -> int | None:
    """Convert a label like 'January 2025' back to its term index."""
    try:
        parts = lbl.rsplit(" ", 1)
        name, year = parts[0], int(parts[1])
        slot = NAMES.index(name)
        return year * 3 + slot
    except (ValueError, IndexError):
        return None


def term_range(
    start: date = date(2026, 5, 1),
    end: date = date(2030, 9, 1),
) -> list[str]:
    """Return every term label from *start* to *end* inclusive."""
    first = term_index(start)
    last = term_index(end)
    return [label(i) for i in range(first, last + 1)]
