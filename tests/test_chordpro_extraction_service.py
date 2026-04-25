from app.application.services.chordpro_extraction_service import ChordproExtractionService
from app.domain.enums.extraction_status import ExtractionStatus
from app.domain.enums.source_type import SourceType


def test_extracts_chordpro_from_text_file(tmp_path):
    text_file = tmp_path / "cifra.txt"
    text_file.write_text(
        "        E                         B/D#\n"
        "Quando eu digo que deixei de te amar\n",
        encoding="utf-8",
    )

    result = ChordproExtractionService().extract(
        file_path=str(text_file),
        filename="cifra.txt",
        mime_type="text/plain",
        file_size_bytes=text_file.stat().st_size,
        request_id="test-request",
    )

    assert result.status == ExtractionStatus.DONE
    assert result.source_type == SourceType.TEXT_FILE
    assert result.chordpro is not None
    assert result.chordpro.startswith("[E]Quando")
    assert "[B/D#]" in result.chordpro
