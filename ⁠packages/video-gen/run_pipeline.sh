#!/usr/bin/env bash
# ==============================================================================
# BUG-Bounty-Xterminator: Veo 3 Automated Video Generation Pipeline
# ==============================================================================
set -euo pipefail

# Configuration Defaults (Override via environment variables)
START_IDX="${START_IDX:-1}"
END_IDX="${END_IDX:-40}"
CONCURRENCY="${CONCURRENCY:-30}"
BATCH_OUTPUT="${BATCH_OUTPUT:-batch_jobs.json}"
DOWNLOAD_DIR="${DOWNLOAD_DIR:-packages/video-gen/downloads}"
POLL_INTERVAL="${POLL_INTERVAL:-15}"

# Formatting & Colors
GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

log_info() {
    echo -e "${CYAN}[PIPELINE]${NC} $(date +'%H:%M:%S') - $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $(date +'%H:%M:%S') - $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $(date +'%H:%M:%S') - $1" >&2
    exit 1
}

# 1. Environment & Pre-flight Checks
log_info "Verifying execution environment..."

if [[ -z "${GOOGLE_API_KEY:-}" ]]; then
    log_error "GOOGLE_API_KEY environment variable is not set. Export your key before running."
fi

if ! command -v python3 &> /dev/null; then
    log_error "python3 is required but could not be found."
fi

# 2. Step 1: Batch Submission
log_info "Initiating batch submissions for scripts ${START_IDX} through ${END_IDX} (Concurrency: ${CONCURRENCY})..."

python3 packages/video-gen/run_batch.py \
    --start "${START_IDX}" \
    --end "${END_IDX}" \
    --concurrency "${CONCURRENCY}" \
    --output "${BATCH_OUTPUT}"

if [[ ! -f "${BATCH_OUTPUT}" ]]; then
    log_error "Batch submission manifest '${BATCH_OUTPUT}' was not created."
fi

log_success "Batch job handles successfully generated in '${BATCH_OUTPUT}'."

# 3. Step 2: Automated Polling & Download
log_info "Kicking off polling worker for video rendering and retrieval..."

python3 packages/video-gen/poll_and_download.py \
    --input "${BATCH_OUTPUT}" \
    --output-dir "${DOWNLOAD_DIR}" \
    --interval "${POLL_INTERVAL}"

log_success "Pipeline complete! All generated MP4 clips are saved in '${DOWNLOAD_DIR}'."
