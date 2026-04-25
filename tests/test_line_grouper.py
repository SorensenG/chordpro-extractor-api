from app.domain.models.extracted_token import ExtractedToken
from app.infrastructure.chordpro.line_grouper import group_tokens_by_lines


def test_groups_tokens_by_page_and_y_position():
    tokens = [
        ExtractedToken(text="mundo", x=50, y=10, width=40, height=10, page_number=1),
        ExtractedToken(text="Olá", x=0, y=11, width=30, height=10, page_number=1),
        ExtractedToken(text="Fim", x=0, y=10, width=30, height=10, page_number=2),
    ]

    lines = group_tokens_by_lines(tokens)

    assert len(lines) == 2
    assert lines[0].text == "Olá mundo"
    assert lines[0].page_number == 1
    assert lines[1].text == "Fim"
    assert lines[1].page_number == 2
