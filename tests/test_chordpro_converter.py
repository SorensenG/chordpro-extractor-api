from __future__ import annotations

from typing import Optional

from app.domain.models.extracted_line import ExtractedLine
from app.domain.models.extracted_token import ExtractedToken
from app.infrastructure.chordpro.chordpro_converter import convert_lines_to_chordpro


def token(text: str, x: float, y: float = 0, width: Optional[float] = None):
    return ExtractedToken(
        text=text,
        x=x,
        y=y,
        width=width or max(len(text) * 8, 8),
        height=12,
        confidence=1.0,
    )


def line(tokens: list[ExtractedToken], y: float):
    return ExtractedLine(
        y=y,
        text=" ".join(item.text for item in tokens),
        tokens=tokens,
    )


def test_converts_section_line():
    result = convert_lines_to_chordpro(
        [
            line([token("[Primeira", 0), token("Parte]", 64)], y=0),
            line([token("Intro", 0)], y=20),
        ]
    )

    assert result.startswith("{section: Primeira Parte}")


def test_merges_chords_with_lyrics_by_estimated_character_position():
    chord_line = line(
        [
            token("E", 0, y=0),
            token("B/D#", 255, y=0),
        ],
        y=0,
    )
    lyric_line = line(
        [
            token("Quando", 0, y=20),
            token("eu", 58, y=20),
            token("digo", 88, y=20),
            token("que", 132, y=20),
            token("deixei", 166, y=20),
            token("de", 224, y=20),
            token("te", 252, y=20),
            token("amar", 280, y=20),
        ],
        y=20,
    )

    result = convert_lines_to_chordpro([chord_line, lyric_line])

    assert result.startswith("[E]Quando")
    assert "[B/D#]" in result
    assert "amar" in result


def test_collapses_overprinted_chords_from_pdf_text_layer():
    chord_line = line(
        [
            token("E7M", 78.7, y=0),
            token("E7M", 79.0, y=0),
            token("E7M", 79.3, y=0),
            token("Gº", 111.0, y=0),
            token("Gº", 111.4, y=0),
        ],
        y=0,
    )

    result = convert_lines_to_chordpro([chord_line])

    assert result == "[E7M] [Gº]"


def test_does_not_merge_chord_line_into_tablature_line():
    chord_line = line([token("E7M", 47, y=0), token("Gº", 111, y=0)], y=0)
    tab_line = line([token("E|-4-----x-4--------------------------------|", 0, y=20)], y=20)

    result = convert_lines_to_chordpro([chord_line, tab_line])

    assert result.splitlines() == [
        "[E7M] [Gº]",
        "E|-4-----x-4--------------------------------|",
    ]


def test_does_not_merge_chord_line_into_section_title():
    chord_line = line([token("E7M", 47, y=0), token("Gº", 111, y=0)], y=0)
    section_line = line(
        [token("[Tab", 0, y=20), token("-", 35, y=20), token("Intro]", 55, y=20)],
        y=20,
    )

    result = convert_lines_to_chordpro([chord_line, section_line])

    assert result.splitlines() == ["[E7M] [Gº]", "{section: Tab - Intro}"]


def test_keeps_metadata_lines_readable():
    result = convert_lines_to_chordpro(
        [
            line(
                [
                    token("Tom:", 0, y=0),
                    token("C#m", 50, y=0),
                    token("C#m", 50.4, y=0),
                    token("C#m", 50.8, y=0),
                ],
                y=0,
            )
        ]
    )

    assert result == "Tom: C#m"
