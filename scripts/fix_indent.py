"""Normalize a Python file: tabs → 4 spaces, strip trailing whitespace."""
import sys
import io
from pathlib import Path


def fix_file(path: Path) -> bool:
    raw = path.read_bytes()

    # Detect encoding
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        text = raw.decode("utf-8-sig")

    # Normalize line endings
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    # Replace tabs with 4 spaces
    text = text.replace("\t", "    ")

    # Strip trailing whitespace per line
    lines = [line.rstrip() for line in text.split("\n")]
    text = "\n".join(lines)

    # Ensure single trailing newline
    if not text.endswith("\n"):
        text += "\n"

    path.write_text(text, encoding="utf-8")
    return True


if __name__ == "__main__":
    for arg in sys.argv[1:]:
        p = Path(arg)
        if not p.exists():
            print(f"SKIP: {p} (not found)")
            continue
        try:
            fix_file(p)
            print(f"FIXED: {p}")
        except Exception as e:
            print(f"ERROR: {p} → {e}")
