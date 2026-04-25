from __future__ import annotations

from typing import Optional

from app.domain.models.extracted_line import ExtractedLine
from app.domain.models.extracted_token import ExtractedToken
from app.infrastructure.chordpro.diagram_filter import (
    remove_final_chord_diagram_block,
)


def token(text: str, x: float, y: float = 0, width: Optional[float] = None):
    return ExtractedToken(
        text=text,
        x=x,
        y=y,
        width=width or max(len(text) * 8, 8),
        height=12,
        confidence=1.0,
    )


def line(texts: list[str], y: float, page_number: int = 1):
    tokens = [
        token(text=value, x=index * 35, y=y)
        for index, value in enumerate(texts)
    ]

    for item in tokens:
        item.page_number = page_number

    return ExtractedLine(
        page_number=page_number,
        y=y,
        text=" ".join(texts),
        tokens=tokens,
    )


def test_removes_final_chord_diagram_block():
    lines = [
        line(["{section:", "Final}"], y=0, page_number=1),
        line(["E7M", "Gº", "G#m7", "C#7(9)"], y=20, page_number=1),
        line(["Dizem", "que", "o", "amor", "atrai"], y=40, page_number=1),
        line(["A#m7(5-)", "A7M", "B7(13)", "B7(2)", "B7(9)"], y=0, page_number=2),
        line(["1", "1", "4ª"], y=20, page_number=2),
        line(["2", "3", "2", "3", "2", "3", "4"], y=40, page_number=2),
        line(["3", "4"], y=60, page_number=2),
    ]

    result = remove_final_chord_diagram_block(lines)

    assert result.removed_diagram_block is True
    assert [item.text for item in result.lines] == [
        "{section: Final}",
        "E7M Gº G#m7 C#7(9)",
        "Dizem que o amor atrai",
    ]


def test_does_not_remove_regular_tablature():
    lines = [
        line(["Parte", "1", "de", "2"], y=0),
        line(["E7M", "Gº", "G#m7", "C#7(9)"], y=20),
        line(["E|-4-----x-4--------------------------------|"], y=40),
        line(["B|-4-----x-4-2-----2-x-2-4-----x-4-4--------|"], y=60),
    ]

    result = remove_final_chord_diagram_block(lines)

    assert result.removed_diagram_block is False
    assert result.lines == lines


def test_does_not_remove_song_chord_lines_with_lyrics_after():
    lines = [
        line(["E7M", "Gº", "G#m7", "C#7(9)"], y=0),
        line(["Crescei", "luar", "pra"], y=20),
        line(["A7M", "G7M", "F#m7", "B7(9)"], y=40),
        line(["As", "trevas", "fundas", "da", "paixão"], y=60),
    ]

    result = remove_final_chord_diagram_block(lines)

    assert result.removed_diagram_block is False
    assert result.lines == lines


def test_does_not_remove_lyrics_with_occasional_numbers():
    lines = [
        line(["Verso", "2"], y=0),
        line(["Hoje", "são", "3", "da", "manhã"], y=20),
        line(["E", "eu", "não", "dormi"], y=40),
    ]

    result = remove_final_chord_diagram_block(lines)

    assert result.removed_diagram_block is False
    assert result.lines == lines
