"""
remove_duplicate_imports.py

Recursively scans a Python file or directory for duplicate import statements
and removes them, keeping the first occurrence of each.

Usage:
    python remove_duplicate_imports.py <path>

    <path> can be a single .py file or a directory (scanned recursively).
"""

import ast
import sys
from pathlib import Path


def get_import_key(node):
    """Return a hashable key representing an import statement."""
    if isinstance(node, ast.Import):
        # e.g. "import os, sys" -> frozenset of (name, asname) tuples
        return ("import", frozenset((a.name, a.asname) for a in node.names))
    elif isinstance(node, ast.ImportFrom):
        # e.g. "from os.path import join as j"
        return (
            "from",
            node.module,
            node.level,  # handles relative imports like "from . import x"
            frozenset((a.name, a.asname) for a in node.names),
        )


def remove_duplicate_imports(source: str) -> tuple[str, list[int]]:
    """
    Parse source, find duplicate import lines, and remove them.

    Returns:
        (cleaned_source, list_of_removed_line_numbers)
    """
    try:
        tree = ast.parse(source)
    except SyntaxError as e:
        raise SyntaxError(f"Could not parse file: {e}")

    lines = source.splitlines(keepends=True)

    seen_keys = set()
    lines_to_remove = set()  # 0-indexed line numbers

    for node in ast.walk(tree):
        if not isinstance(node, (ast.Import, ast.ImportFrom)):
            continue

        key = get_import_key(node)
        if key in seen_keys:
            # Mark every line this node spans for removal (ast lines are 1-indexed)
            for lineno in range(node.lineno - 1, node.end_lineno):
                lines_to_remove.add(lineno)
        else:
            seen_keys.add(key)

    if not lines_to_remove:
        return source, []

    cleaned_lines = [
        line for i, line in enumerate(lines) if i not in lines_to_remove
    ]

    removed_1indexed = sorted(i + 1 for i in lines_to_remove)
    return "".join(cleaned_lines), removed_1indexed


def process_file(path: Path, dry_run: bool = False) -> bool:
    """Process a single file. Returns True if changes were made."""
    source = path.read_text(encoding="utf-8")

    try:
        cleaned, removed = remove_duplicate_imports(source)
    except SyntaxError as e:
        print(f"  [SKIP] {path}: {e}")
        return False

    if not removed:
        print(f"  [OK]   {path} — no duplicates found")
        return False

    print(f"  [FIX]  {path} — removed duplicate imports on lines: {removed}")
    if not dry_run:
        path.write_text(cleaned, encoding="utf-8")
    return True


def main():
    if len(sys.argv) < 2:
        print("Usage: python remove_duplicate_imports.py <file_or_directory> [--dry-run]")
        sys.exit(1)

    target = Path(sys.argv[1])
    dry_run = "--dry-run" in sys.argv

    if dry_run:
        print("=== DRY RUN — no files will be modified ===\n")

    if not target.exists():
        print(f"Error: '{target}' does not exist.")
        sys.exit(1)

    files = [target] if target.is_file() else sorted(target.rglob("*.py"))

    if not files:
        print("No Python files found.")
        sys.exit(0)

    total_fixed = 0
    for f in files:
        if process_file(f, dry_run=dry_run):
            total_fixed += 1

    print(f"\nDone. {total_fixed}/{len(files)} file(s) {'would be' if dry_run else 'were'} modified.")


if __name__ == "__main__":
    main()