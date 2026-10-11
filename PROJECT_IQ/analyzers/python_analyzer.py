"""
PROJECTIQ - Python Analyzer

Uses Python's built-in `ast` module to statically parse .py files.
Files are NEVER executed - only parsed into a syntax tree and inspected.
Files that fail to parse (syntax errors, unsupported grammar) are
skipped gracefully rather than crashing the pipeline.
"""

import ast
from dataclasses import dataclass, field
from typing import Dict, List

from analyzers.file_scanner import ScanResult

ML_MODEL_NAMES = {
    "RandomForestClassifier", "RandomForestRegressor", "LogisticRegression",
    "LinearRegression", "SVC", "SVR", "KMeans", "DecisionTreeClassifier",
    "GradientBoostingClassifier", "XGBClassifier", "Sequential", "Model",
    "AutoModel", "AutoTokenizer", "SentenceTransformer", "KNeighborsClassifier",
}

API_DECORATOR_HINTS = {"app.get", "app.post", "app.put", "app.delete", "app.patch",
                        "router.get", "router.post", "router.put", "router.delete"}


@dataclass
class PythonFileReport:
    path: str
    imports: List[str] = field(default_factory=list)
    functions: List[str] = field(default_factory=list)
    classes: List[str] = field(default_factory=list)
    routes: List[str] = field(default_factory=list)
    ml_models_used: List[str] = field(default_factory=list)
    has_syntax_error: bool = False


def _decorator_name(dec: ast.expr) -> str:
    if isinstance(dec, ast.Call):
        dec = dec.func
    if isinstance(dec, ast.Attribute):
        base = dec.value.id if isinstance(dec.value, ast.Name) else ""
        return f"{base}.{dec.attr}"
    if isinstance(dec, ast.Name):
        return dec.id
    return ""


def analyze_python_file(path: str, content: str) -> PythonFileReport:
    report = PythonFileReport(path=path)
    try:
        tree = ast.parse(content)
    except SyntaxError:
        report.has_syntax_error = True
        return report

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                report.imports.append(alias.name)
        elif isinstance(node, ast.ImportFrom) and node.module:
            report.imports.append(node.module)
        elif isinstance(node, ast.FunctionDef):
            report.functions.append(node.name)
            for dec in node.decorator_list:
                dname = _decorator_name(dec)
                if any(hint in dname for hint in API_DECORATOR_HINTS):
                    report.routes.append(f"{dname} -> {node.name}")
        elif isinstance(node, ast.ClassDef):
            report.classes.append(node.name)
        elif isinstance(node, ast.Call):
            fname = ""
            if isinstance(node.func, ast.Name):
                fname = node.func.id
            elif isinstance(node.func, ast.Attribute):
                fname = node.func.attr
            if fname in ML_MODEL_NAMES:
                report.ml_models_used.append(fname)

    return report


def analyze_python_files(scan: ScanResult) -> Dict:
    reports: List[PythonFileReport] = []
    for f in scan.by_extension(".py"):
        if f.content:
            reports.append(analyze_python_file(f.relative_path, f.content))

    all_imports = sorted({imp for r in reports for imp in r.imports})
    all_routes = [route for r in reports for route in r.routes]
    all_ml_models = sorted({m for r in reports for m in r.ml_models_used})
    syntax_errors = [r.path for r in reports if r.has_syntax_error]

    return {
        "file_count": len(reports),
        "total_functions": sum(len(r.functions) for r in reports),
        "total_classes": sum(len(r.classes) for r in reports),
        "imports": all_imports,
        "api_routes": all_routes,
        "ml_models_detected": all_ml_models,
        "files_with_syntax_errors": syntax_errors,
        "reports": reports,
    }
