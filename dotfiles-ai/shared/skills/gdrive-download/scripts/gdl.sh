#!/usr/bin/env bash
# gdl - Google Drive Download wrapper
# Wraps gdown for easy file/folder downloads from Google Drive
# Usage: gdl <url_or_id> [output_path] [options]

set -euo pipefail

GDOWN_BIN="${GDOWN:-$(command -v gdown 2>/dev/null || echo "$HOME/.local/bin/gdown")}"

usage() {
    cat <<'EOF'
gdl - Google Drive Download

Usage:
  gdl <url_or_id> [output_path] [options]

Arguments:
  url_or_id       Google Drive URL (any format) or bare file/folder ID
  output_path     Destination path (file or directory). Default: current directory

Options:
  -f, --folder    Download entire folder
  -r, --resume    Resume partial download
  -q, --quiet     Suppress progress output
  --fuzzy         Fuzzy extract file ID from URL
  --id            Treat url_or_id as a bare file/folder ID
  -h, --help      Show this help

URL formats supported:
  https://drive.google.com/file/d/<ID>/view
  https://drive.google.com/uc?id=<ID>
  https://drive.google.com/open?id=<ID>
  https://drive.google.com/drive/folders/<ID>
  <bare file ID>

Examples:
  gdl https://drive.google.com/file/d/1abc123/view /tmp/downloads/
  gdl 1abc123 /tmp/output.zip
  gdl https://drive.google.com/drive/folders/1xyz789 /tmp/folder --folder
  gdl https://drive.google.com/file/d/1abc123/view --resume
EOF
    exit "${1:-0}"
}

# Defaults
FOLDER=false
RESUME=false
QUIET=false
FUZZY=false
ID_MODE=false
URL=""
OUTPUT=""

# Parse arguments
while [[ $# -gt 0 ]]; do
    case "$1" in
        -h|--help)    usage 0 ;;
        -f|--folder)  FOLDER=true; shift ;;
        -r|--resume)  RESUME=true; shift ;;
        -q|--quiet)   QUIET=true; shift ;;
        --fuzzy)      FUZZY=true; shift ;;
        --id)         ID_MODE=true; shift ;;
        -*)
            echo "Error: unknown option: $1" >&2
            usage 1
            ;;
        *)
            if [[ -z "$URL" ]]; then
                URL="$1"
            elif [[ -z "$OUTPUT" ]]; then
                OUTPUT="$1"
            else
                echo "Error: unexpected argument: $1" >&2
                usage 1
            fi
            shift
            ;;
    esac
done

if [[ -z "$URL" ]]; then
    echo "Error: URL or file ID required" >&2
    usage 1
fi

# Check gdown is available
if [[ ! -x "$GDOWN_BIN" ]] && ! command -v gdown &>/dev/null; then
    echo "Error: gdown not found. Install with: pip install gdown" >&2
    exit 1
fi

# Build gdown command
CMD=("$GDOWN_BIN")

if $FOLDER; then
    CMD+=(--folder)
fi

if $RESUME; then
    CMD+=(--continue)
fi

if $QUIET; then
    CMD+=(-q)
fi

if $FUZZY; then
    CMD+=(--fuzzy)
fi

if $ID_MODE; then
    CMD+=(--id)
fi

CMD+=("$URL")

# Handle output path
if [[ -n "$OUTPUT" ]]; then
    # If output ends with / or is an existing directory, use as directory
    if [[ "$OUTPUT" == */ ]] || [[ -d "$OUTPUT" ]]; then
        mkdir -p "$OUTPUT"
        CMD+=(-O "$OUTPUT")
    else
        # Ensure parent directory exists
        PARENT="$(dirname "$OUTPUT")"
        if [[ "$PARENT" != "." ]]; then
            mkdir -p "$PARENT"
        fi
        CMD+=(-O "$OUTPUT")
    fi
fi

# Execute
if ! $QUIET; then
    echo "Downloading: $URL" >&2
    [[ -n "$OUTPUT" ]] && echo "To: $OUTPUT" >&2
    echo "---" >&2
fi

"${CMD[@]}"
EXIT_CODE=$?

if [[ $EXIT_CODE -eq 0 ]] && ! $QUIET; then
    echo "---" >&2
    echo "Done." >&2
fi

exit $EXIT_CODE
