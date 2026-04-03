---
name: gdrive-download
description: Download files and folders from Google Drive via the terminal. Use when a user provides a Google Drive link or file ID and wants to download it to this server. Handles large files, virus scan bypass, folder downloads, and resume support.
---

# gdrive-download

## Dependencies
- `gdown` (Python CLI) — installed at `~/.local/bin/gdown`
- Python 3

## Quick Start

### Using the wrapper script (recommended)
```bash
# Download a file to a specific path
./scripts/gdl.sh "https://drive.google.com/file/d/FILE_ID/view" /path/to/output/

# Download with bare file ID
./scripts/gdl.sh "1l_5RK28JRL19wpT22B-DY9We3TVXnnQQ" /tmp/model.npz

# Download entire folder
./scripts/gdl.sh "https://drive.google.com/drive/folders/FOLDER_ID" /tmp/output/ --folder

# Resume interrupted download
./scripts/gdl.sh "https://drive.google.com/file/d/FILE_ID/view" /tmp/output.zip --resume

# Quiet mode
./scripts/gdl.sh "https://drive.google.com/file/d/FILE_ID/view" /tmp/ --quiet
```

### Using gdown directly
```bash
# File (auto-detects URL format)
~/.local/bin/gdown "https://drive.google.com/uc?id=FILE_ID" -O /path/to/output

# Fuzzy URL extraction (any Google Drive link format)
~/.local/bin/gdown --fuzzy "https://drive.google.com/file/d/FILE_ID/view?usp=sharing" -O /tmp/file.zip

# Folder
~/.local/bin/gdown --folder "https://drive.google.com/drive/folders/FOLDER_ID" -O /tmp/folder/

# Resume partial download
~/.local/bin/gdown --continue "https://drive.google.com/uc?id=FILE_ID" -O /tmp/large_file.tar.gz

# Pipe to stdout (for compression)
~/.local/bin/gdown "https://drive.google.com/uc?id=FILE_ID" -O - --quiet | tar xzf -
```

## URL Formats
All formats are accepted — gdown handles extraction:
- `https://drive.google.com/file/d/<ID>/view?usp=sharing`
- `https://drive.google.com/uc?id=<ID>`
- `https://drive.google.com/open?id=<ID>`
- `https://drive.google.com/drive/folders/<ID>`
- Bare `<ID>` string

## Large Files
Google blocks direct downloads for large files (>100MB) with a virus scan warning. `gdown` handles this automatically. If it fails:
1. Download `cookies.txt` via browser extension (Get cookies.txt LOCALLY)
2. Place at `~/.cache/gdown/cookies.txt`
3. Retry

## Output Path Rules
- Ends with `/` → treat as directory, keep original filename
- No trailing `/` → treat as full file path
- Parent directories are created automatically

## Workflow
1. Extract file/folder ID from the Google Drive URL
2. Determine output path (user-specified or current directory)
3. Run `gdown` or `scripts/gdl.sh` with appropriate flags
4. For large downloads, use `--resume` flag
5. Verify download completed successfully
