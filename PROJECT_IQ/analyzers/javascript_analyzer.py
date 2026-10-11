"""
PROJECTIQ - JavaScript / TypeScript Analyzer

Uses regular-expression based static analysis (no code execution) since
a full JS AST parser is not part of the Python standard library. Signals
are intentionally conservative - they favor missing an edge case over
producing false confidence.
"""

import re
from typing import Dict, List

from analyzers.file_scanner import ScanResult

IMPORT_PATTERN = re.compile(r"""import\s+.*?from\s+['"]([^'"]+)['"]|require\(['"]([^'"]+)['"]\)""")
COMPONENT_PATTERN = re.compile(r"""(?:function|const)\s+([A-Z][A-Za-z0-9_]*)\s*(?:=|\()""")
ROUTE_PATTERN = re.compile(r"""(?:app|router)\.(get|post|put|delete|patch)\(\s*['"]([^'"]+)['"]""")
HOOK_PATTERN = re.compile(r"\buse[A-Z][A-Za-z0-9_]*\(")
ROUTER_PATH_PATTERN = re.compile(r"""<Route\s+path=['"]([^'"]+)['"]""")


def analyze_js_files(scan: ScanResult) -> Dict:
    files = scan.by_extension(".js", ".jsx", ".ts", ".tsx")

    all_imports: set = set()
    components: set = set()
    routes: List[str] = []
    hooks_used: set = set()
    frontend_routes: set = set()

    for f in files:
        if not f.content:
            continue
        for match in IMPORT_PATTERN.finditer(f.content):
            module = match.group(1) or match.group(2)
            if module:
                all_imports.add(module)
        for match in COMPONENT_PATTERN.finditer(f.content):
            components.add(match.group(1))
        for method, path in ROUTE_PATTERN.findall(f.content):
            routes.append(f"{method.upper()} {path}")
        for match in HOOK_PATTERN.finditer(f.content):
            hooks_used.add(match.group(0).rstrip("("))
        for path in ROUTER_PATH_PATTERN.findall(f.content):
            frontend_routes.add(path)

    return {
        "file_count": len(files),
        "imports": sorted(all_imports),
        "components_detected": sorted(components),
        "backend_routes": routes,
        "hooks_used": sorted(hooks_used),
        "frontend_routes": sorted(frontend_routes),
    }
