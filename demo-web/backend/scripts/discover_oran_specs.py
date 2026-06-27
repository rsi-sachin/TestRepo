"""
CLI wrapper for ORAN spec discovery endpoint.

Usage:
  python scripts/discover_oran_specs.py
  python scripts/discover_oran_specs.py --base-url http://localhost:8000/api/oran
  python scripts/discover_oran_specs.py --no-candidates
"""

import argparse
import sys
from typing import Dict, List

import requests


def _build_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Discover ORAN specs and select latest versions")
    parser.add_argument(
        "--base-url",
        default="http://localhost:8000/api/oran",
        help="Base ORAN API URL",
    )
    parser.add_argument(
        "--no-candidates",
        action="store_true",
        help="Hide full candidate lists in output",
    )
    return parser.parse_args()


def _print_spec_block(spec_type: str, payload: Dict[str, object]) -> None:
    status = payload.get("status", "unknown")
    title = payload.get("title", "")
    print(f"\n[{spec_type}] {title}")
    print(f"  Status: {status}")

    selected = payload.get("selected")
    if not selected:
        print("  Selected: None")
        return

    print(f"  Selected: {selected.get('filename')}")
    print(f"  Version: {selected.get('version_tag') or 'n/a'}")
    print(f"  Type: {selected.get('document_type')} ({selected.get('document_type_confidence')})")
    print(f"  Modified: {selected.get('modified_time')}")

    candidates = payload.get("candidates")
    if not isinstance(candidates, list):
        return

    print(f"  Candidates ({len(candidates)}):")
    selected_name = selected.get("filename")
    for candidate in candidates:
        marker = "*" if candidate.get("filename") == selected_name else "-"
        print(
            f"    {marker} {candidate.get('filename')} "
            f"version={candidate.get('version_tag') or 'n/a'} "
            f"modified={candidate.get('modified_time')}"
        )


def main() -> int:
    args = _build_args()
    endpoint = f"{args.base_url.rstrip('/')}/specs/discover-latest"
    params = {"include_candidates": str(not args.no_candidates).lower()}

    try:
        response = requests.get(endpoint, params=params, timeout=30)
    except Exception as exc:
        print(f"Request failed: {exc}")
        return 1

    if response.status_code != 200:
        print(f"Request failed with HTTP {response.status_code}")
        print(response.text[:500])
        return 1

    data = response.json()
    summary = data.get("summary", {})
    specs = data.get("specs", {})

    print("ORAN Spec Discovery")
    print("===================")
    print(f"Docs Path: {data.get('docs_path')}")
    print(f"Scanned Files: {data.get('scanned_file_count')}")
    print(f"Resolved Specs: {summary.get('resolved_specs')}")

    missing_specs = summary.get("missing_specs")
    if isinstance(missing_specs, list) and missing_specs:
        print(f"Missing Specs: {', '.join(missing_specs)}")

    if isinstance(specs, dict):
        ordered_specs: List[str] = ["TS_103_989", "TS_103_987", "TS_103_988", "TS_103_983"]
        for spec_type in ordered_specs:
            payload = specs.get(spec_type)
            if isinstance(payload, dict):
                _print_spec_block(spec_type, payload)

    return 0


if __name__ == "__main__":
    sys.exit(main())
