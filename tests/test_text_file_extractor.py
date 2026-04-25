from app.infrastructure.extractors.text_file_extractor import extract_tokens_from_text_file


def test_extracts_tokens_from_text_file_preserving_horizontal_position(tmp_path):
    text_file = tmp_path / "cifra.txt"
    text_file.write_text(
        "        E                         B/D#\nQuando eu digo\n",
        encoding="utf-8",
    )

    tokens = extract_tokens_from_text_file(str(text_file))

    assert [token.text for token in tokens] == ["E", "B/D#", "Quando", "eu", "digo"]
    assert tokens[0].x > 0
    assert tokens[1].x > tokens[0].x
    assert tokens[2].y > tokens[0].y
