"""
PROJECTIQ - README / Documentation Analyzer
"""

import re
from typing import Dict

from analyzers.file_scanner import ScanResult

SETUP_KEYWORDS = ["install", "setup", "getting started", "run the", "npm ", "pip install", "requirements"]
USAGE_KEYWORDS = ["usage", "how to use", "example"]


def analyze_readme(scan: ScanResult) -> Dict:
    readmes = scan.find_by_name("readme.md", "readme.txt", "readme")
    if not readmes:
        return {
            "present": False,
            "word_count": 0,
            "has_setup_instructions": False,
            "has_usage_section": False,
            "headings": [],
            "summary_text": "",
        }

    content = readmes[0].content
    headings = re.findall(r"^#{1,3}\s+(.*)$", content, re.MULTILINE)
    lowered = content.lower()

    return {
        "present": True,
        "word_count": len(content.split()),
        "has_setup_instructions": any(k in lowered for k in SETUP_KEYWORDS),
        "has_usage_section": any(k in lowered for k in USAGE_KEYWORDS),
        "headings": headings[:15],
        "summary_text": " ".join(content.split()[:60]),
    }
