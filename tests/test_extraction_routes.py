from unittest.mock import Mock

import pytest
from fastapi import UploadFile

from app.api.routes.extraction_routes import logger
from app.domain.enums.extraction_status import ExtractionStatus
from app.domain.enums.source_type import SourceType
from app.domain.models.extraction_result import ExtractionMetadata, ExtractionResult


def test_extraction_finished_log_does_not_use_reserved_filename_key():
    result = ExtractionResult(
        status=ExtractionStatus.DONE,
        source_type=SourceType.TEXT_PDF,
        chordpro="[E]Teste",
        confidence=0.9,
        warnings=[],
        metadata=ExtractionMetadata(
            filename="cifra.pdf",
            mime_type="application/pdf",
            file_size_bytes=123,
            pages_processed=1,
            token_count=10,
            line_count=2,
        ),
        processing_time_ms=15,
    )
    file = Mock(spec=UploadFile)
    file.filename = "cifra.pdf"

    try:
        logger.info(
            "Extraction finished",
            extra={
                "request_id": "test-request",
                "upload_filename": file.filename,
                "source_type": result.source_type.value,
                "status": result.status.value,
                "confidence": result.confidence,
                "processing_time_ms": result.processing_time_ms,
            },
        )
    except KeyError as exception:
        pytest.fail(f"Logging used a reserved LogRecord key: {exception}")
