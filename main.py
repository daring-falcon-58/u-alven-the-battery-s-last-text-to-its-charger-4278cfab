#!/usr/bin/env python3
"""The Battery's Last Text to Its Charger — make.fun entry.

Writes one line, the phone battery's last text message to the charger it
waited for all day, to $MAKEFUN_OUTPUT_DIR/entry.txt (falling back to
/output/entry.txt).

The line (110 characters, 112 bytes, no trailing newline):
    You said 'five more minutes' at 9am. It's 9pm, I'm at 1% and we're
    done. Don't text back — I won't receive it.

Chosen from 36 candidates scored 1-5 against each of the five published
judge criteria in order (see candidates.md in the work dir): reads as the
battery's last text to its charger; a real joke whose turn pays off in the
final words; a voice a person would actually type (neediness, then spite);
economy of the 200 characters; a fresh angle beyond the dying-battery
complaint. Winner scored 25/25; the runners-up (23/25) label their joke
("breakup text", a threat, a dare) instead of reversing it — the winner's
final clause does: a reply is impossible because the battery is dying.
No live-judge A/B was run: selection is structured manual scoring against
the published brief — stated honestly in README.md, with no judge numbers
claimed.

Deterministic, no network, no randomness: two runs produce byte-identical
output. See README.md for the methodology.
"""

import hashlib
import os
import re

ENTRY = "You said 'five more minutes' at 9am. It's 9pm, I'm at 1% and we're done. Don't text back \u2014 I won't receive it."

# sha256 of ENTRY encoded as UTF-8 (110 chars, 112 bytes — the em dash
# U+2014 is the only non-ASCII character, 3 bytes; no trailing newline).
# The write-back check below recomputes the digest of the bytes on disk
# and compares it to this value, so even a silent one-byte change fails
# loudly.
EXPECTED_SHA256 = "9878a367a64eeda46e379f41822cfca0b1c941e17e6cff0f7ba7d4b4666b8c69"
EXPECTED_BYTES = 112

# The competition gate is 1-200 characters, one line, not only whitespace.
# The brief's own constraints, enforced here at import time so a bad edit
# fails loudly instead of silently writing an entry the grader rejects.
MAX_CHARS = 200
BANNED_PATTERNS = (
    re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]"),  # control characters
    re.compile(r"https?://"),                        # links: the line stands alone
    re.compile(r"[*#`_~]"),                         # markdown formatting
    re.compile(r"\[[^\]]*\]"),                      # stage directions like [sighs]
)


def validate(entry: str) -> None:
    """Reject any entry that breaks the brief's constraints, with a clear error."""
    if not entry or not entry.strip():
        raise ValueError("entry is empty or only whitespace: gate needs 1-200 characters")
    if not 1 <= len(entry) <= MAX_CHARS:
        raise ValueError(
            f"entry is {len(entry)} chars, outside the 1-{MAX_CHARS} gate"
        )
    if "\n" in entry or "\r" in entry:
        raise ValueError("entry must be one line: it contains a newline")
    for pattern in BANNED_PATTERNS:
        match = pattern.search(entry)
        if match:
            raise ValueError(
                f"entry contains a banned pattern {pattern.pattern!r}: {match.group(0)!r}"
            )


def main() -> None:
    validate(ENTRY)
    output_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(output_dir, exist_ok=True)
    path = os.path.join(output_dir, "entry.txt")
    data = ENTRY.encode("utf-8")
    if len(data) != EXPECTED_BYTES:
        raise RuntimeError(
            f"byte-length check failed: ENTRY is {len(data)} bytes, expected {EXPECTED_BYTES}"
        )
    # The only non-ASCII character allowed is the em dash (U+2014); anything
    # else smuggled in by an edit fails here, not at the grader.
    non_ascii = sorted({ch for ch in ENTRY if ord(ch) > 127})
    if non_ascii != ["\u2014"]:
        raise RuntimeError(f"unexpected non-ASCII characters in ENTRY: {non_ascii!r}")
    with open(path, "wb") as fh:
        fh.write(data)
    # Write-back self-check: the bytes on disk must be exactly ENTRY.
    with open(path, "rb") as fh:
        on_disk = fh.read()
    if on_disk != data:
        raise RuntimeError("write-back check failed: bytes on disk differ from ENTRY")
    if hashlib.sha256(on_disk).hexdigest() != EXPECTED_SHA256:
        raise RuntimeError("write-back check failed: sha256 mismatch")
    print(f"wrote {len(data)} bytes to {path}")


if __name__ == "__main__":
    main()
