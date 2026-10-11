"""
PROJECTIQ - Dependency Analyzer

Parses manifest files to extract declared dependencies. This is combined
with import-statement scanning in technology_detector.py so detection
never relies on a single signal.
"""

import json
import re
from typing import Dict, List

from analyzers.file_scanner import ScanResult


def parse_requirements_txt(content: str) -> List[str]:
    packages = []
    for line in content.splitlines():
        line = line.strip()
        if not line or line.startswith("#") or line.startswith("-"):
            continue
        name = re.split(r"[=<>!~\[; ]", line, maxsplit=1)[0].strip()
        if name:
            packages.append(name.lower())
    return packages


def parse_package_json(content: str) -> Dict[str, List[str]]:
    try:
        data = json.loads(content)
    except json.JSONDecodeError:
        return {"dependencies": [], "devDependencies": []}
    return {
        "dependencies": sorted((data.get("dependencies") or {}).keys()),
        "devDependencies": sorted((data.get("devDependencies") or {}).keys()),
    }


def parse_pyproject_toml(content: str) -> List[str]:
    """Lightweight best-effort dependency extraction without a TOML parser
    dependency - looks for a `dependencies = [...]` block."""
    packages = []
    match = re.search(r"dependencies\s*=\s*\[(.*?)\]", content, re.DOTALL)
    if match:
        for entry in re.findall(r'"([^"]+)"', match.group(1)):
            name = re.split(r"[=<>!~\[; ]", entry, maxsplit=1)[0].strip()
            if name:
                packages.append(name.lower())
    return packages


def analyze_dependencies(scan: ScanResult) -> Dict:
    """Returns a consolidated dependency report across every manifest found."""
    report = {
        "python_packages": [],
        "node_dependencies": [],
        "node_dev_dependencies": [],
        "manifests_found": [],
    }

    for f in scan.find_by_name("requirements.txt"):
        report["python_packages"].extend(parse_requirements_txt(f.content))
        report["manifests_found"].append(f.relative_path)

    for f in scan.find_by_name("pyproject.toml"):
        report["python_packages"].extend(parse_pyproject_toml(f.content))
        report["manifests_found"].append(f.relative_path)

    for f in scan.find_by_name("package.json"):
        parsed = parse_package_json(f.content)
        report["node_dependencies"].extend(parsed["dependencies"])
        report["node_dev_dependencies"].extend(parsed["devDependencies"])
        report["manifests_found"].append(f.relative_path)

    report["python_packages"] = sorted(set(report["python_packages"]))
    report["node_dependencies"] = sorted(set(report["node_dependencies"]))
    report["node_dev_dependencies"] = sorted(set(report["node_dev_dependencies"]))
    return report
