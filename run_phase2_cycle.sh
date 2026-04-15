#!/usr/bin/env bash
# Phase 2 Cron Job Wrapper
# Deploy to crontab for automatic multi-cycle execution

# Configuration
LOG_DIR="${HOME}/PyAgent/phase2_logs"
LOG_FILE="${LOG_DIR}/phase2_$(date +%Y%m%d_%H%M%S).log"
STATE_FILE="${HOME}/PyAgent/PHASE2_EXECUTION_STATE.json"

# Create log directory
mkdir -p "$LOG_DIR"

# Run executor
cd ~/PyAgent

echo "======================================" >> "$LOG_FILE"
echo "Phase 2 Execution - $(date)" >> "$LOG_FILE"
echo "======================================" >> "$LOG_FILE"

python3 phase2_executor.py >> "$LOG_FILE" 2>&1

# Print status
python3 phase2_executor.py --status >> "$LOG_FILE" 2>&1

# Archive old logs (keep last 100)
ls -1t "$LOG_DIR"/phase2_*.log | tail -n +101 | xargs -r rm

echo "" >> "$LOG_FILE"
echo "Cycle completed at $(date)" >> "$LOG_FILE"

# Exit with status (0 = success, 1 = errors)
if grep -q "\[!\]" "$LOG_FILE"; then
    exit 1
else
    exit 0
fi
