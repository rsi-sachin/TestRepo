"""
Phase 2 unit tests — Spec Parsing Pipeline

Covers:
  - PDF/DOCX ingestion (PdfParser, DocxParser)
  - Clause extraction (TestClauseExtractor)
  - HTTP info extraction from clause text
  - Cross-reference and enrichment (SpecParserService)
  - Conflict detection and persistence
"""

import json
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
from io import BytesIO

from app.parsers.pdf_parser import PdfParser
from app.parsers.docx_parser import DocxParser
from app.parsers.test_clause_extractor import TestClauseExtractor
from app.models.oran import SpecType, HttpMethod, ScenarioType
from app.services.spec_parser_service import SpecParserService


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

SAMPLE_SPEC_TEXT = """
--- Page 1 ---
ETSI TS 103 989 V4.2.0 (2024-01)
A1 Test Specification

--- Page 5 ---
5.2.1 Test Purpose
Test purpose: Verify that the A1-P Producer responds correctly to a GET request.
Pre-condition: A1 interface is available.
Test procedure: Send GET /policytypes to the A1-P Producer.
Expected result: HTTP 200 OK with empty array [].

--- Page 6 ---
5.2.2 Policy Creation Test
Test purpose: Verify that PUT /policytypes/{policyTypeId}/policies/{policyId} returns 201.
Pre-condition: Policy type is registered.
Test procedure: Send PUT request with valid PolicyObject body.
Expected result: HTTP 201 Created with Location header.

--- Page 7 ---
5.3.1 Interoperability Test
Test purpose: Verify interoperability between Non-RT RIC and Near-RT RIC.
Pre-condition: Both systems connected.
Test procedure: Initiate A1 policy exchange.
Expected result: Policy acknowledged.
"""

SAMPLE_PROTOCOL_TEXT = """
--- Page 10 ---
5.2.3 List policy type identifiers
Test purpose: GET /a1-p/policytypes returns list of identifiers.
Expected result: HTTP 200 OK.
"""


# ---------------------------------------------------------------------------
# PdfParser (mocked — no real PDF file required)
# ---------------------------------------------------------------------------

class TestPdfParser:
    def test_raises_file_not_found(self, tmp_path):
        parser = PdfParser()
        with pytest.raises(FileNotFoundError):
            parser.parse_file(tmp_path / "nonexistent.pdf")

    def test_parse_file_returns_text(self, tmp_path):
        """Mock pypdf.PdfReader to verify extraction logic."""
        mock_page = MagicMock()
        mock_page.extract_text.return_value = "Sample page text"
        mock_reader = MagicMock()
        mock_reader.pages = [mock_page, mock_page]

        pdf_path = tmp_path / "test.pdf"
        pdf_path.write_bytes(b"%PDF mock")

        with patch("app.parsers.pdf_parser.pypdf.PdfReader", return_value=mock_reader):
            text = PdfParser.parse_file(pdf_path)

        assert "Sample page text" in text
        assert "Page 1" in text
        assert "Page 2" in text

    def test_get_page_count(self, tmp_path):
        mock_reader = MagicMock()
        mock_reader.pages = [MagicMock()] * 7
        pdf_path = tmp_path / "test.pdf"
        pdf_path.write_bytes(b"%PDF mock")

        with patch("app.parsers.pdf_parser.pypdf.PdfReader", return_value=mock_reader):
            count = PdfParser.get_page_count(pdf_path)

        assert count == 7


# ---------------------------------------------------------------------------
# DocxParser (mocked — no real DOCX file required)
# ---------------------------------------------------------------------------

class TestDocxParser:
    def test_raises_file_not_found(self, tmp_path):
        with pytest.raises(FileNotFoundError):
            DocxParser.parse_file(tmp_path / "nonexistent.docx")

    def test_parse_file_returns_paragraphs(self, tmp_path):
        mock_para = MagicMock()
        mock_para.text = "Paragraph text"
        mock_doc = MagicMock()
        mock_doc.paragraphs = [mock_para, mock_para]

        docx_path = tmp_path / "test.docx"
        docx_path.write_bytes(b"PK mock")

        with patch("app.parsers.docx_parser.Document", return_value=mock_doc):
            text = DocxParser.parse_file(docx_path)

        assert "Paragraph text" in text


# ---------------------------------------------------------------------------
# TestClauseExtractor
# ---------------------------------------------------------------------------

class TestTestClauseExtractor:
    def setup_method(self):
        self.extractor = TestClauseExtractor()

    def test_extracts_test_clauses_from_sample_text(self):
        clauses = self.extractor.extract_clauses(SAMPLE_SPEC_TEXT, SpecType.TS_103_989)
        assert len(clauses) >= 2
        clause_numbers = [c.clause_number for c in clauses]
        assert "5.2.1" in clause_numbers or "5.2.2" in clause_numbers

    def test_clause_has_required_fields(self):
        clauses = self.extractor.extract_clauses(SAMPLE_SPEC_TEXT, SpecType.TS_103_989)
        for clause in clauses:
            assert clause.clause_number
            assert clause.title
            assert clause.spec_type == SpecType.TS_103_989

    def test_max_tests_limit_is_respected(self):
        clauses = self.extractor.extract_clauses(SAMPLE_SPEC_TEXT, SpecType.TS_103_989, max_tests=1)
        assert len(clauses) <= 1

    def test_scenario_type_interoperability_detected(self):
        clauses = self.extractor.extract_clauses(SAMPLE_SPEC_TEXT, SpecType.TS_103_989)
        inter_clauses = [c for c in clauses if "Interoperability" in c.title]
        if inter_clauses:
            assert inter_clauses[0].scenario_type == ScenarioType.INTEROPERABILITY

    def test_scenario_type_conformance_default_for_ts_103_989(self):
        clauses = self.extractor.extract_clauses(SAMPLE_SPEC_TEXT, SpecType.TS_103_989)
        conformance_clauses = [c for c in clauses if c.title and "Interoperability" not in c.title]
        for clause in conformance_clauses:
            assert clause.scenario_type == ScenarioType.CONFORMANCE


# ---------------------------------------------------------------------------
# extract_http_info
# ---------------------------------------------------------------------------

class TestExtractHttpInfo:
    def setup_method(self):
        self.extractor = TestClauseExtractor()

    def test_extracts_get_method(self):
        result = self.extractor.extract_http_info("Send GET /policytypes to producer")
        assert result["method"] == "GET"

    def test_extracts_put_method(self):
        result = self.extractor.extract_http_info("Send PUT /policies/{id} with body")
        assert result["method"] == "PUT"

    def test_extracts_delete_method(self):
        result = self.extractor.extract_http_info("Send DELETE /policies/{id}")
        assert result["method"] == "DELETE"

    def test_extracts_endpoint_path(self):
        result = self.extractor.extract_http_info("Send GET /a1-p/policytypes to server")
        assert result["endpoint"] is not None
        assert "/a1-p/policytypes" in result["endpoint"]

    def test_extracts_status_code_201(self):
        result = self.extractor.extract_http_info("Expected result: HTTP 201 Created")
        assert result["status_code"] == 201

    def test_extracts_status_code_200(self):
        result = self.extractor.extract_http_info("Expected result: HTTP 200 OK")
        assert result["status_code"] == 200

    def test_returns_none_for_empty_text(self):
        result = self.extractor.extract_http_info("")
        assert result["method"] is None
        assert result["endpoint"] is None
        assert result["status_code"] is None


# ---------------------------------------------------------------------------
# SpecParserService — cross-reference and conflict detection
# ---------------------------------------------------------------------------

class TestSpecParserService:
    def setup_method(self, tmp_path_factory):
        self.spec_dir = Path(".")  # not used in unit tests — we pass text directly
        self.service = SpecParserService(spec_dir=Path("."))

    def _make_clauses(self, spec_type: SpecType, count: int = 2):
        from app.models.oran import TestClause
        clauses = []
        for i in range(count):
            clauses.append(
                TestClause(
                    clause_number=f"5.{i+1}.1",
                    title=f"Test Clause {i+1}",
                    description=f"Verify A1 policy operation {i+1}",
                    methodology="Send GET /policytypes",
                    expected_result="HTTP 200 OK",
                    spec_type=spec_type,
                    page_number=5 + i,
                    raw_text="Send GET /policytypes Expected result: HTTP 200 OK",
                )
            )
        return clauses

    def test_cross_reference_returns_enriched_cases(self):
        clauses = {
            SpecType.TS_103_989: self._make_clauses(SpecType.TS_103_989, 3),
            SpecType.TS_103_987: self._make_clauses(SpecType.TS_103_987, 2),
        }
        enriched = self.service.cross_reference_specs(clauses)
        assert len(enriched) == 3  # driven by TS_103_989 base clauses

    def test_cross_reference_enrichment_sources_populated(self):
        clauses = {
            SpecType.TS_103_989: self._make_clauses(SpecType.TS_103_989, 1),
        }
        enriched = self.service.cross_reference_specs(clauses)
        assert enriched[0].enrichment_sources
        assert "base" in enriched[0].enrichment_sources

    def test_cross_reference_empty_ts989_produces_no_cases(self):
        clauses = {
            SpecType.TS_103_989: [],
            SpecType.TS_103_987: self._make_clauses(SpecType.TS_103_987, 3),
        }
        enriched = self.service.cross_reference_specs(clauses)
        assert enriched == []

    def test_detect_conflicts_returns_list(self):
        clauses = {SpecType.TS_103_989: self._make_clauses(SpecType.TS_103_989, 2)}
        enriched = self.service.cross_reference_specs(clauses)
        conflicts = self.service.detect_conflicts(enriched)
        assert isinstance(conflicts, list)

    def test_save_conflicts_writes_json(self, tmp_path):
        from app.models.oran import SpecConflict
        self.service.conflicts = [
            SpecConflict(
                conflict_id="CONF-001",
                field="endpoint",
                spec1=SpecType.TS_103_989,
                value1="/policytypes",
                spec2=SpecType.TS_103_987,
                value2="/a1-p/policytypes",
                resolution="priority_order",
            )
        ]
        output_path = tmp_path / "conflicts.json"
        self.service.save_conflicts(output_path)
        assert output_path.exists()
        data = json.loads(output_path.read_text())
        assert len(data) == 1
        assert data[0]["field"] == "endpoint"

    def test_determine_complexity_basic(self):
        from app.models.oran import TestClause
        clause = TestClause(
            clause_number="5.1.1",
            title="Simple test",
            description="Short description",
            spec_type=SpecType.TS_103_989,
        )
        assert self.service._determine_complexity(clause) == "BASIC"

    def test_determine_complexity_advanced(self):
        from app.models.oran import TestClause
        long_text = "validate verify sequence workflow multiple " * 30
        clause = TestClause(
            clause_number="5.1.1",
            title="Complex test",
            description=long_text,
            methodology=long_text,
            spec_type=SpecType.TS_103_989,
        )
        assert self.service._determine_complexity(clause) in ("INTERMEDIATE", "ADVANCED")
