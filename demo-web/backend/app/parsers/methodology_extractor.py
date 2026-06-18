"""
Methodology extraction utilities for ETSI O-RAN specification documents.

This module provides a lightweight machine-intelligence style pipeline that:
1. Identifies Test Methodology sections.
2. Extracts distinct Test Module candidates from that context.
3. Generates distinct test-title candidates from the same context.

The implementation is hybrid: deterministic section parsing plus heuristic
semantic scoring for phrase clustering and naming.
"""

from __future__ import annotations

import re
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class MethodologySection:
    section_number: str
    title: str
    page_number: Optional[int]
    depth: int
    text: str
    evidence: List[str] = field(default_factory=list)


@dataclass
class ModuleCandidate:
    module_name: str
    module_id: str
    source_section: str
    source_title: str
    confidence: float
    evidence: List[str] = field(default_factory=list)
    keywords: List[str] = field(default_factory=list)


@dataclass
class TestTitleCandidate:
    title: str
    module_id: str
    source_section: str
    confidence: float
    evidence: List[str] = field(default_factory=list)


class MethodologyExtractor:
    """Extract methodology sections and derive module/title candidates."""

    SECTION_RE = re.compile(r"^(?P<num>\d+(?:\.\d+)*)\s+(?P<title>.+)$", re.MULTILINE)
    PAGE_RE = re.compile(r"---\s*Page\s+(\d+)\s*---")

    METHODOLOGY_HINTS = (
        "test methodology",
        "test method",
        "testing methodology",
        "testing method",
        "test procedure",
        "test procedures",
        "test setup",
        "test configuration",
        "test environment",
        "test architecture",
        "test strategy",
        "abstract test suite",
        "test suite",
        "conformance test",
        "verification method",
    )

    ACTION_VERBS = ("validate", "verify", "check", "confirm", "ensure", "assess", "measure")

    STOP_WORDS = {
        "a", "an", "and", "or", "the", "to", "of", "in", "for", "on", "with", "by", "from",
        "test", "testing", "method", "methodology", "procedures", "procedure", "suite", "cases",
        "case", "section", "specification", "document", "documents", "shall", "should", "must",
        "may", "can", "will", "is", "are", "be", "been", "this", "that", "these", "those",
    }

    DOMAIN_HINTS: Dict[str, str] = {
        "policy": "Policy Management",
        "policies": "Policy Management",
        "subscription": "Subscription Management",
        "notification": "Notification Handling",
        "notify": "Notification Handling",
        "heartbeat": "Heartbeat Monitoring",
        "security": "Security Verification",
        "auth": "Authentication",
        "error": "Error Handling",
        "fault": "Fault Management",
        "performance": "Performance Testing",
        "load": "Load Testing",
        "conformance": "Conformance Verification",
        "interoperability": "Interoperability Testing",
        "interface": "Interface Verification",
        "protocol": "Protocol Conformance",
        "request": "Request Handling",
        "response": "Response Validation",
        "create": "Resource Creation",
        "update": "Resource Update",
        "delete": "Resource Deletion",
        "retrieve": "Resource Retrieval",
        "query": "Query Operations",
        "setup": "Test Setup",
        "environment": "Test Environment",
        "architecture": "Test Architecture",
        "workflow": "Test Workflow",
        "message": "Message Exchange",
    }

    GENERIC_BLOCKLIST = {
        "expected result",
        "expected results",
        "configuration",
        "configurations used",
        "return code",
        "return code 200 ok",
        "all three configurations listed",
        "requirements it",
        "result",
        "methodology",
        "test methodology",
        "a1-ei related it",
        "a1-p related it",
        "device under requirements",
        "dut scenarios clause",
    }

    def extract_methodology_sections(self, text: str) -> List[MethodologySection]:
        """Find likely methodology sections and preserve evidence."""
        sections = self._split_sections(text)
        methodology_sections: List[MethodologySection] = []

        for section in sections:
            if self._is_methodology_section(section["title"], section["text"]):
                methodology_sections.append(
                    MethodologySection(
                        section_number=section["number"],
                        title=section["title"],
                        page_number=section["page"],
                        depth=section["depth"],
                        text=section["text"],
                        evidence=self._build_evidence(section["text"], section["title"]),
                    )
                )

        return methodology_sections

    def generate_module_candidates(
        self,
        methodology_sections: List[MethodologySection],
        full_text: str,
        max_modules: int = 12,
    ) -> List[ModuleCandidate]:
        """Generate distinct module names from methodology context."""
        scored_phrases: Dict[str, Dict[str, object]] = {}

        for section in methodology_sections:
            self._score_phrase(scored_phrases, section.title, section.section_number, section.title, 2.0)

        ranked = sorted(
            scored_phrases.values(),
            key=lambda item: (-float(item["score"]), str(item["name"])),
        )

        modules: List[ModuleCandidate] = []
        seen_ids = set()
        for item in ranked:
            name = str(item["name"])
            module_id = self._to_module_id(name)
            if not module_id or module_id in seen_ids:
                continue
            seen_ids.add(module_id)
            modules.append(
                ModuleCandidate(
                    module_name=name,
                    module_id=module_id,
                    source_section=str(item["source_section"]),
                    source_title=str(item["source_title"]),
                    confidence=min(0.99, round(float(item["score"]) / 4.0, 2)),
                    evidence=list(dict.fromkeys(item["evidence"])),
                    keywords=list(dict.fromkeys(item["keywords"])),
                )
            )
            if len(modules) >= max_modules:
                break

        if not modules:
            modules = self._fallback_modules(full_text)

        return modules

    def generate_test_title_candidates(
        self,
        modules: List[ModuleCandidate],
        methodology_sections: List[MethodologySection],
        max_titles_per_module: int = 2,
    ) -> List[TestTitleCandidate]:
        """Generate distinct test-title candidates from methodology context."""
        titles: List[TestTitleCandidate] = []
        seen = set()

        section_lookup = {section.section_number: section for section in methodology_sections}

        for module in modules:
            section = section_lookup.get(module.source_section)
            evidence_source = section.evidence if section else module.evidence

            # Prefer concise module-derived titles; fall back to short evidence phrases.
            title_phrases = [module.module_name]
            title_phrases.extend(self._extract_title_phrases(module.source_title or ""))
            title_phrases.extend(self._extract_title_phrases(" ".join(evidence_source[:2]) if evidence_source else ""))
            if not title_phrases:
                title_phrases = [f"Validate {module.module_name}", f"Verify {module.module_name}"]

            count = 0
            for phrase in title_phrases:
                title = self._normalize_title(phrase)
                if not title:
                    continue
                key = title.lower()
                if key in seen:
                    continue
                seen.add(key)
                titles.append(
                    TestTitleCandidate(
                        title=title,
                        module_id=module.module_id,
                        source_section=module.source_section,
                        confidence=max(0.5, min(0.95, module.confidence)),
                        evidence=module.evidence[:3],
                    )
                )
                count += 1
                if count >= max_titles_per_module:
                    break

        return titles

    def extract_context_plan(self, text: str) -> Dict[str, object]:
        """Return sections, modules and title candidates in one response payload."""
        sections = self.extract_methodology_sections(text)
        modules = self.generate_module_candidates(sections, text)
        titles = self.generate_test_title_candidates(modules, sections)
        return {
            "methodology_sections": sections,
            "modules": modules,
            "titles": titles,
        }

    def _split_sections(self, text: str) -> List[Dict[str, object]]:
        sections: List[Dict[str, object]] = []
        lines = text.splitlines()
        current: Optional[Dict[str, object]] = None
        body_lines: List[str] = []
        current_page = 1

        for line in lines:
            page_match = self.PAGE_RE.search(line)
            if page_match:
                current_page = int(page_match.group(1))
                continue

            match = self.SECTION_RE.match(line.strip())
            if match:
                if current is not None:
                    current["text"] = "\n".join(body_lines).strip()
                    sections.append(current)
                current = {
                    "number": match.group("num"),
                    "title": self._clean_title(match.group("title")),
                    "depth": match.group("num").count(".") + 1,
                    "page": current_page,
                    "text": "",
                }
                body_lines = []
            elif current is not None:
                body_lines.append(line)

        if current is not None:
            current["text"] = "\n".join(body_lines).strip()
            sections.append(current)

        return sections

    def _is_methodology_section(self, title: str, text: str) -> bool:
        title_l = title.lower()
        body_l = text.lower()

        if any(hint in title_l for hint in self.METHODOLOGY_HINTS):
            return True

        body_hits = sum(1 for hint in self.METHODOLOGY_HINTS if hint in body_l)
        return body_hits >= 2 or (
            body_hits >= 1 and any(keyword in body_l for keyword in ("input", "output", "expected", "steps", "procedure"))
        )

    def _extract_candidate_phrases(self, text: str) -> List[str]:
        phrases: List[str] = []

        bullet_patterns = [
            r"^\s*[-•\*]\s+(.+)$",
            r"^\s*\d+[.)]\s+(.+)$",
            r"^\s*[a-z]\)\s+(.+)$",
        ]
        for pattern in bullet_patterns:
            for match in re.finditer(pattern, text, flags=re.MULTILINE):
                candidate = self._strip_trailing_clauses(match.group(1))
                if candidate:
                    phrases.append(candidate)

        action_patterns = [
            r"\b(?:test|verify|validate|check|ensure|confirm|measure)\s+([^.;\n]{4,120})",
            r"\bfor\s+([^.;\n]{4,80})",
            r"\b(?:module|component|function|workflow|scenario|procedure)\s+([^.;\n]{3,80})",
        ]
        for pattern in action_patterns:
            for match in re.finditer(pattern, text, flags=re.IGNORECASE):
                candidate = self._strip_trailing_clauses(match.group(1))
                if candidate and 2 <= len(candidate.split()) <= 10:
                    phrases.append(candidate)

        return list(dict.fromkeys(phrases))

    def _extract_title_phrases(self, text: str) -> List[str]:
        title_phrases = []
        for match in re.finditer(r"\b(?:verify|validate|test|check|ensure|confirm)\s+([^.;\n]{4,120})", text, flags=re.IGNORECASE):
            phrase = self._strip_trailing_clauses(match.group(1))
            if phrase and 2 <= len(phrase.split()) <= 10:
                title_phrases.append(phrase)
        return list(dict.fromkeys(title_phrases))

    def _score_phrase(
        self,
        scored_phrases: Dict[str, Dict[str, object]],
        phrase: str,
        source_section: str,
        source_title: str,
        base_score: float,
    ) -> None:
        normalized = self._normalize_phrase(phrase)
        if not normalized:
            return

        lower = normalized.lower()
        if lower in self.GENERIC_BLOCKLIST:
            return
        if len(lower.split()) == 1 and lower not in {"policy", "notification", "interface", "protocol"}:
            return
        score = base_score
        keywords = self._keywords(lower)

        if source_title:
            score += 0.5
        if self._looks_semantic(normalized):
            score += 0.5
        if len(keywords) >= 2:
            score += 0.5
        if len(normalized.split()) >= 2:
            score += 0.25
        if len(normalized) > 50:
            score -= 0.25

        for hint, mapped in self.DOMAIN_HINTS.items():
            if hint in lower:
                normalized = mapped
                score += 0.75
                keywords.extend(hint.split())
                break

        item = scored_phrases.setdefault(
            normalized,
            {
                "name": normalized,
                "score": 0.0,
                "source_section": source_section,
                "source_title": source_title,
                "evidence": [],
                "keywords": [],
            },
        )
        item["score"] = float(item["score"]) + score
        if source_section and not item["source_section"]:
            item["source_section"] = source_section
        if source_title and not item["source_title"]:
            item["source_title"] = source_title
        item["evidence"].append(phrase.strip())
        item["keywords"].extend(keywords)

    def _fallback_modules(self, full_text: str) -> List[ModuleCandidate]:
        modules: List[ModuleCandidate] = []
        lower = full_text.lower()
        for hint, mapped in self.DOMAIN_HINTS.items():
            if hint in lower:
                module_id = self._to_module_id(mapped)
                modules.append(
                    ModuleCandidate(
                        module_name=mapped,
                        module_id=module_id,
                        source_section="",
                        source_title="keyword-scan",
                        confidence=0.45,
                        evidence=[hint],
                        keywords=[hint],
                    )
                )
        return modules[:12]

    def _build_evidence(self, text: str, title: str) -> List[str]:
        evidence = [title]
        evidence.extend(self._extract_candidate_phrases(text)[:4])
        return list(dict.fromkeys([item for item in evidence if item]))

    @staticmethod
    def _clean_title(title: str) -> str:
        title = re.sub(r"\s*\.{2,}.*$", "", title)
        title = re.sub(r"\s+", " ", title).strip()
        return title

    @staticmethod
    def _strip_trailing_clauses(text: str) -> str:
        cleaned = re.sub(r"\s+", " ", text).strip()
        cleaned = re.split(r"\b(?:shall|should|must|will|may|can)\b", cleaned, maxsplit=1, flags=re.IGNORECASE)[0]
        cleaned = cleaned.strip(" :-;,.\t")
        return cleaned

    def _normalize_phrase(self, phrase: str) -> str:
        phrase = re.sub(r"[^\w\s/-]", " ", phrase)
        words = [word for word in phrase.split() if word.lower() not in self.STOP_WORDS]
        if not words:
            return ""
        candidate = " ".join(words)
        candidate = re.sub(r"\s+", " ", candidate).strip()
        if len(candidate) < 3:
            return ""
        return candidate

    def _looks_semantic(self, phrase: str) -> bool:
        lower = phrase.lower()
        return any(hint in lower for hint in self.DOMAIN_HINTS) or len(lower.split()) >= 2

    def _keywords(self, phrase: str) -> List[str]:
        return [word for word in re.findall(r"[a-z0-9]+", phrase.lower()) if word not in self.STOP_WORDS]

    @staticmethod
    def _to_module_id(name: str) -> str:
        module_id = re.sub(r"[^A-Z0-9]+", "_", name.upper()).strip("_")
        return module_id

    def _normalize_title(self, text: str) -> str:
        normalized = self._normalize_phrase(text)
        if not normalized:
            return ""
        if normalized.lower() in self.GENERIC_BLOCKLIST:
            return ""
        words = []
        for word in normalized.split():
            if word.isupper() and len(word) <= 5:
                words.append(word)
            else:
                words.append(word[:1].upper() + word[1:])
        return " ".join(words)