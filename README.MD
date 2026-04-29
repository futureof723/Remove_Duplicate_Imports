# remove_duplicate_imports

A lightweight Python script that scans `.py` files for duplicate import statements and removes them, keeping the first occurrence of each.

## Requirements

- Python 3.10+
- No external dependencies (uses the standard library only)

## Usage

```bash
# Fix a single file
python remove_duplicate_imports.py path/to/yourfile.py

# Recursively fix all .py files in a directory
python remove_duplicate_imports.py path/to/your/project/

# Preview what would change without modifying any files
python remove_duplicate_imports.py path/to/your/project/ --dry-run
```

## Example

Given a file with duplicate imports:

```python
import os
import sys
from pathlib import Path
import os                    # duplicate
from pathlib import Path     # duplicate
import json
from os.path import join
from os.path import join     # duplicate
```

Running the script produces:

```
  [FIX]  yourfile.py — removed duplicate imports on lines: [4, 5, 8]

Done. 1/1 file(s) were modified.
```

And the cleaned file becomes:

```python
import os
import sys
from pathlib import Path
import json
from os.path import join
```

## What counts as a duplicate

The script uses Python's `ast` module to parse imports properly, so it correctly detects duplicates across all import styles:

| Style | Example |
|---|---|
| Simple import | `import os` |
| Multi-module import | `import os, sys` |
| From import | `from pathlib import Path` |
| Aliased import | `import numpy as np` |
| Relative import | `from . import utils` |
| Multi-line import | `from module import (a, b, c)` |

Two imports are considered duplicates if they import the same module, the same names, and use the same aliases.

## Flags

| Flag | Description |
|---|---|
| `--dry-run` | Print what would be changed without modifying any files |

## Notes

- Files with syntax errors are skipped and reported, leaving them untouched.
- The script always keeps the **first** occurrence of a duplicate and removes later ones.
- Only `.py` files are scanned when a directory is provided.