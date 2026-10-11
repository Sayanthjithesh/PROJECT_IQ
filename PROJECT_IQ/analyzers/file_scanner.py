"""
PROJECTIQ - File Scanner

Performs a STATIC, READ-ONLY walk of an extracted project directory.
No file is ever executed. Files above MAX_FILE_SIZE_BYTES have their
content skipped (but are still counted) to keep analysis fast and safe.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List

from config import IGNORED_DIRECTORIES, IGNORED_FILE_EXTENSIONS, MAX_FILE_SIZE_BYTES

TEXT_READ_EXTENSIONS = {
    ".py", ".js", ".jsx", ".ts", ".tsx", ".json", ".md", ".txt", ".yml",
    ".yaml", ".toml", ".cfg", ".ini", ".html", ".css", ".scss", ".env",
    ".sql", ".sh", ".bat", ".dockerfile", ".gitignore", ".xml",
}


@dataclass
class ScannedFile:
    relative_path: str
    extension: str
    size_bytes: int
    content: str = ""  # empty if binary / too large / unreadable


@dataclass
class ScanResult:
    root: Path
    files: List[ScannedFile] = field(default_factory=list)
    total_files: int = 0
    total_size_bytes: int = 0
    directories: List[str] = field(default_factory=list)

    def by_extension(self, *extensions: str) -> List[ScannedFile]:
        exts = {e.lower() for e in extensions}
        return [f for f in self.files if f.extension.lower() in exts]

    def find_by_name(self, *names: str) -> List[ScannedFile]:
        wanted = {n.lower() for n in names}
        return [f for f in self.files if Path(f.relative_path).name.lower() in wanted]

    def full_path(self, scanned_file: ScannedFile) -> Path:
        return self.root / scanned_file.relative_path


def _is_ignored_dir(parts) -> bool:
    return any(p in IGNORED_DIRECTORIES for p in parts)


def scan_project(root: Path) -> ScanResult:
    result = ScanResult(root=root)
    seen_dirs = set()

    for path in root.rglob("*"):
        try:
            rel = path.relative_to(root)
        except ValueError:
            continue
        parts = rel.parts
        if _is_ignored_dir(parts):
            continue

        if path.is_dir():
            seen_dirs.add(str(rel))
            continue

        if path.name == "_upload.zip":
            continue

        ext = path.suffix.lower()
        if ext in IGNORED_FILE_EXTENSIONS:
            continue

        try:
            size = path.stat().st_size
        except OSError:
            continue

        content = ""
        if ext in TEXT_READ_EXTENSIONS and size <= MAX_FILE_SIZE_BYTES:
            try:
                content = path.read_text(encoding="utf-8", errors="ignore")
            except (OSError, UnicodeDecodeError):
                content = ""

        result.files.append(ScannedFile(
            relative_path=str(rel).replace("\\", "/"),
            extension=ext,
            size_bytes=size,
            content=content,
        ))
        result.total_files += 1
        result.total_size_bytes += size

    result.directories = sorted(seen_dirs)
    return result


def language_distribution(scan: ScanResult) -> Dict[str, int]:
    """Rough file-count-based language distribution used for charts."""
    mapping = {
        ".py": "Python", ".js": "JavaScript", ".jsx": "JavaScript",
        ".ts": "TypeScript", ".tsx": "TypeScript", ".html": "HTML",
        ".css": "CSS", ".scss": "CSS", ".sql": "SQL", ".sh": "Shell",
        ".java": "Java", ".go": "Go", ".rb": "Ruby", ".php": "PHP",
    }
    counts: Dict[str, int] = {}
    for f in scan.files:
        lang = mapping.get(f.extension)
        if lang:
            counts[lang] = counts.get(lang, 0) + 1
    return dict(sorted(counts.items(), key=lambda kv: kv[1], reverse=True))
