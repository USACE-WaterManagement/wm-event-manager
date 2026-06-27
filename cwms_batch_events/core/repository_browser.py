from pathlib import Path

from cwms_batch_events.core.models import (
    RepositoryBrowserEntry,
    RepositoryBrowserResponse,
)
from cwms_batch_events.core.settings import settings


RUNTIME_SCRIPT_TYPES: dict[str, list[str]] = {
    "python": [".py"],
    "node": [".js", ".mjs", ".cjs", ".ts"],
    "java": [".java", ".jar"],
    "shell": [".sh", ".bash", ".zsh", "extensionless"],
}

SKIPPED_DIRECTORIES = {
    ".git",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".venv",
    "__pycache__",
    "node_modules",
}


def _normalized_directory(directory: str) -> str:
    return directory.strip().strip("/\\")


def _is_relative_to(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
    except ValueError:
        return False
    return True


def _script_types_for_runtime(runtime: str) -> list[str]:
    return RUNTIME_SCRIPT_TYPES.get(runtime.lower(), [])


def _runtime_match(path: Path, runtime: str) -> bool:
    script_types = _script_types_for_runtime(runtime)
    suffix = path.suffix.lower()
    if suffix and suffix in script_types:
        return True
    return "extensionless" in script_types and not suffix


def browse_repository_paths(
    directory: str = "",
    runtime: str = "python",
    include_all_files: bool = False,
) -> RepositoryBrowserResponse:
    script_types = _script_types_for_runtime(runtime)
    root_setting = settings.script_repository_root.strip()
    if not root_setting:
        return RepositoryBrowserResponse(
            directory="",
            configured=False,
            script_types=script_types,
            entries=[],
        )

    root = Path(root_setting).resolve()
    requested_directory = _normalized_directory(directory)
    target = (root / requested_directory).resolve()
    if not _is_relative_to(target, root):
        raise ValueError("directory must stay within the configured repository root")
    if not target.exists() or not target.is_dir():
        return RepositoryBrowserResponse(
            directory=requested_directory,
            configured=True,
            script_types=script_types,
            entries=[],
        )

    entries: list[RepositoryBrowserEntry] = []
    for child in sorted(
        target.iterdir(), key=lambda path: (not path.is_dir(), path.name.lower())
    ):
        if child.name.startswith(".") and child.name != ".github":
            continue
        if child.is_dir() and child.name in SKIPPED_DIRECTORIES:
            continue

        relative_path = child.relative_to(root).as_posix()
        if child.is_dir():
            entries.append(
                RepositoryBrowserEntry(
                    name=child.name,
                    path=relative_path,
                    entry_type="directory",
                    selectable=False,
                    runtime_match=False,
                )
            )
            continue

        runtime_match = _runtime_match(child, runtime)
        if include_all_files or runtime_match:
            entries.append(
                RepositoryBrowserEntry(
                    name=child.name,
                    path=relative_path,
                    entry_type="file",
                    selectable=True,
                    runtime_match=runtime_match,
                )
            )

    return RepositoryBrowserResponse(
        directory=requested_directory,
        configured=True,
        script_types=script_types,
        entries=entries,
    )
