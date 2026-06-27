"""
ORAN specification discovery service.

Finds ETSI TS spec files in ORAN/docs, groups candidates by canonical spec type,
and picks the latest version per spec using filename version tags.
"""

from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from app.parsers.docx_parser import DocxParser
from app.services.document_classifier_service import DocumentClassifier


class OranSpecDiscoveryService:
    """Discover and resolve canonical ORAN specs from a docs folder."""

    # Canonical spec map used by Feature-1 and Feature-2 handoff.
    SPEC_DEFINITIONS: Dict[str, Dict[str, object]] = {
        "TS_103_989": {
            "ts_number": "TS 103 989",
            "title": "A1 Test Specification",
            "number_token": "103989",
        },
        "TS_103_987": {
            "ts_number": "TS 103 987",
            "title": "A1 Application Protocol",
            "number_token": "103987",
        },
        "TS_103_988": {
            "ts_number": "TS 103 988",
            "title": "A1 Type Definitions",
            "number_token": "103988",
        },
        "TS_103_983": {
            "ts_number": "TS 103 983",
            "title": "A1 General Principles",
            "number_token": "103983",
        },
    }

    _VERSION_RE = re.compile(r"v(?P<digits>\d{6,8})(?:p|d)?", re.IGNORECASE)

    def __init__(self) -> None:
        self._docx_parser = DocxParser()

    def discover_latest_specs(self, docs_path: Path, include_candidates: bool = True) -> Dict[str, object]:
        """
        Discover all supported ORAN specs and resolve the latest version of each.

        Args:
            docs_path: Folder containing source specs.
            include_candidates: Include full per-spec candidate list in response.

        Returns:
            Structured discovery payload.
        """
        if not docs_path.exists() or not docs_path.is_dir():
            raise FileNotFoundError(f"Docs path is missing or invalid: {docs_path}")

        all_files = self._list_spec_files(docs_path)
        grouped: Dict[str, List[Dict[str, object]]] = {spec: [] for spec in self.SPEC_DEFINITIONS.keys()}

        for file_path in all_files:
            matched_spec = self._match_spec_type(file_path)
            if not matched_spec:
                continue

            grouped[matched_spec].append(self._build_candidate_record(file_path, docs_path))

        specs_payload: Dict[str, Dict[str, object]] = {}
        resolved = 0

        for spec_type, spec_info in self.SPEC_DEFINITIONS.items():
            candidates = grouped.get(spec_type, [])
            if not candidates:
                specs_payload[spec_type] = {
                    "spec_type": spec_type,
                    "ts_number": str(spec_info["ts_number"]),
                    "title": str(spec_info["title"]),
                    "status": "missing",
                    "selected": None,
                    "candidates": [] if include_candidates else None,
                }
                continue

            selected = self._select_latest_candidate(candidates)
            if selected:
                selected = dict(selected)
                selected["document_type"], selected["document_type_confidence"] = self._classify_document(
                    Path(str(selected["full_path"]))
                )
                resolved += 1

            specs_payload[spec_type] = {
                "spec_type": spec_type,
                "ts_number": str(spec_info["ts_number"]),
                "title": str(spec_info["title"]),
                "status": "resolved" if selected else "missing",
                "selected": selected,
                "candidates": candidates if include_candidates else None,
            }

        missing_specs = [k for k, v in specs_payload.items() if v["status"] == "missing"]

        return {
            "docs_path": str(docs_path.resolve()),
            "scanned_file_count": len(all_files),
            "supported_specs": list(self.SPEC_DEFINITIONS.keys()),
            "specs": specs_payload,
            "summary": {
                "resolved_specs": resolved,
                "missing_specs": missing_specs,
                "discovered_at": datetime.utcnow().isoformat(),
            },
        }

    def _list_spec_files(self, docs_path: Path) -> List[Path]:
        files: List[Path] = []
        for ext in ("*.pdf", "*.docx"):
            files.extend(sorted(docs_path.glob(ext)))
        return files

    def _match_spec_type(self, file_path: Path) -> Optional[str]:
        normalized = re.sub(r"[^a-z0-9]", "", file_path.stem.lower())
        for spec_type, spec_info in self.SPEC_DEFINITIONS.items():
            token = str(spec_info["number_token"])
            if token in normalized:
                return spec_type
        return None

    def _parse_version(self, file_path: Path) -> Tuple[str, Tuple[int, int, int]]:
        stem_lower = file_path.stem.lower()
        match = self._VERSION_RE.search(stem_lower)
        if not match:
            return ("", (0, 0, 0))

        digits = match.group("digits")
        if len(digits) < 6:
            return (match.group(0), (0, 0, 0))

        major = int(digits[0:2])
        minor = int(digits[2:4])
        patch = int(digits[4:6])
        return (match.group(0), (major, minor, patch))

    def _build_candidate_record(self, file_path: Path, docs_path: Path) -> Dict[str, object]:
        version_tag, version_tuple = self._parse_version(file_path)
        stat = file_path.stat()
        return {
            "filename": file_path.name,
            "relative_path": str(file_path.relative_to(docs_path)).replace("\\", "/"),
            "full_path": str(file_path.resolve()),
            "file_extension": file_path.suffix.lower(),
            "version_tag": version_tag,
            "version_tuple": list(version_tuple),
            "modified_time": datetime.fromtimestamp(stat.st_mtime).isoformat(),
            "size_bytes": stat.st_size,
        }

    def _select_latest_candidate(self, candidates: List[Dict[str, object]]) -> Optional[Dict[str, object]]:
        if not candidates:
            return None

        def ext_priority(ext: str) -> int:
            return 2 if ext == ".pdf" else 1

        def sort_key(item: Dict[str, object]) -> Tuple[int, int, int, float, int]:
            version_tuple = item.get("version_tuple") or [0, 0, 0]
            major, minor, patch = int(version_tuple[0]), int(version_tuple[1]), int(version_tuple[2])
            modified_time = datetime.fromisoformat(str(item["modified_time"]))
            return (
                major,
                minor,
                patch,
                modified_time.timestamp(),
                ext_priority(str(item.get("file_extension", ""))),
            )

        selected = max(candidates, key=sort_key)
        return selected

    def _classify_document(self, file_path: Path) -> Tuple[str, float]:
        if file_path.suffix.lower() == ".pdf":
            doc_type, confidence = DocumentClassifier.classify_document(file_path)
            return doc_type.value, round(confidence, 2)

        if file_path.suffix.lower() == ".docx":
            text = self._docx_parser.parse_file(file_path)
            doc_type, confidence = DocumentClassifier.classify_from_text(text)
            return doc_type.value, round(confidence, 2)

        return ("UNKNOWN", 0.0)
