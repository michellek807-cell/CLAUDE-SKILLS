#!/usr/bin/env bash
# project_doc.sh - regenerate projects/<job>/PROJECT.md (the resume doc).
set -eu
. "$(cd "$(dirname "$0")/../lib" && pwd -P)/common.sh"
DIR=$(vs_require_job "${1:-}")
vs_py "$VS_SCRIPTS/project_doc.py" --job-dir "$DIR"
