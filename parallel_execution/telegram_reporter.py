"""Telegram reporter for real-time updates."""

import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class TelegramReporter:
    """Sends real-time updates to Telegram."""
    
    def __init__(self, chat_id: Optional[str] = None, api_token: Optional[str] = None):
        self.chat_id = chat_id or self._get_chat_id()
        self.api_token = api_token or self._get_token()
        self.enabled = bool(self.chat_id and self.api_token)
    
    def _get_chat_id(self) -> Optional[str]:
        """Get chat ID from environment or config."""
        import os
        return os.getenv("TELEGRAM_CHAT_ID")
    
    def _get_token(self) -> Optional[str]:
        """Get API token from environment or config."""
        import os
        return os.getenv("TELEGRAM_BOT_TOKEN")
    
    def send_progress_report(self, metrics: Dict[str, Any]) -> bool:
        """Send cycle completion report."""
        if not self.enabled:
            logger.warning("Telegram not configured, skipping report")
            return False
        
        message = self._format_progress_message(metrics)
        return self._send_message(message)
    
    def send_milestone_alert(self, milestone: str, metrics: Dict[str, Any]) -> bool:
        """Send milestone notification."""
        if not self.enabled:
            return False
        
        message = f"""
🎉 **MILESTONE REACHED: {milestone}**

📊 Current Status:
• Ideas: {metrics.get('ideas_processed', 0):,}
• Projects: {metrics.get('projects_created', 0):,}
• Files: {metrics.get('files_generated', 0):,}
• LOC: {metrics.get('lines_of_code', 0):,}

⏱️ ETA to completion: {metrics.get('eta_hours', '?')} hours
"""
        return self._send_message(message)
    
    def send_error_alert(self, shard_id: int, error: str) -> bool:
        """Send error notification."""
        if not self.enabled:
            return False
        
        message = f"""
❌ **SHARD ERROR**

Shard: SHARD_{shard_id:04d}
Error: {error[:200]}
"""
        return self._send_message(message)
    
    def _format_progress_message(self, metrics: Dict[str, Any]) -> str:
        """Format metrics into a nice Telegram message."""
        return f"""
📈 **Parallel Execution Progress**

**Shards:** {metrics.get('shards_completed', 0)}/419
**Ideas:** {metrics.get('ideas_processed', 0):,}
**Projects:** {metrics.get('projects_created', 0):,}
**Files:** {metrics.get('files_generated', 0):,}
**LOC:** {metrics.get('lines_of_code', 0):,}

**Quality:**
• Pass rate: {metrics.get('quality_pass_rate', 0):.1f}%
• Violations: {metrics.get('quality_violations', 0)}

**Performance:**
• Shards/hour: {metrics.get('velocity_shards_per_hour', 0):.1f}
• Ideas/hour: {metrics.get('velocity_ideas_per_hour', 0):,.0f}
• ETA: {metrics.get('eta_hours', '?')} hours

🟢 Status: {metrics.get('status', 'RUNNING')}
"""
    
    def _send_message(self, message: str) -> bool:
        """Send message to Telegram. (Stub - requires hermes integration)."""
        try:
            logger.info(f"Would send Telegram message:\n{message}")
            # In production: use python-telegram-bot or requests to send
            # For now, just log it
            return True
        except Exception as e:
            logger.error(f"Error sending Telegram message: {e}")
            return False
