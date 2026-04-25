from app.infrastructure.chordpro.chord_detector import is_chord


def test_accepts_common_brazilian_chord_notation():
    valid_chords = [
        "E",
        "E5+",
        "A",
        "F#m",
        "A/B",
        "E/G#",
        "C#m7",
        "E7(9)",
        "C°",
        "B/D#",
        "F7M",
        "Bm7(b5)",
    ]

    for chord in valid_chords:
        assert is_chord(chord), chord


def test_rejects_regular_words():
    invalid_values = ["Quando", "amor", "Primeira", "", "Aquela"]

    for value in invalid_values:
        assert not is_chord(value), value
