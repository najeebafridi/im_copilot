"""Cleanup scheduler for expired conversations."""

from __future__ import annotations

from threading import Event, Thread

from app.core.config import get_settings
from app.services.conversation.service import ConversationService, get_conversation_service


class ConversationCleanupScheduler:
    """Run conversation cleanup on a lightweight background loop."""

    def __init__(self, service: ConversationService, interval_minutes: int) -> None:
        self._service = service
        self._interval_seconds = max(1, interval_minutes * 60)
        self._stop_event = Event()
        self._thread: Thread | None = None

    def start(self) -> None:
        """Start the cleanup loop if it is not already running."""

        if self._thread and self._thread.is_alive():
            return

        self._stop_event.clear()
        self._thread = Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        """Stop the cleanup loop."""

        self._stop_event.set()

    def run_once(self) -> int:
        """Run one cleanup cycle."""

        return self._service.cleanup_expired_conversations()

    def _run(self) -> None:
        while not self._stop_event.wait(self._interval_seconds):
            self._service.cleanup_expired_conversations()


_scheduler: ConversationCleanupScheduler | None = None


def get_conversation_cleanup_scheduler() -> ConversationCleanupScheduler:
    """Return the singleton cleanup scheduler."""

    global _scheduler
    if _scheduler is None:
        settings = get_settings()
        _scheduler = ConversationCleanupScheduler(
            service=get_conversation_service(),
            interval_minutes=settings.CHAT_CLEANUP_INTERVAL_MINUTES,
        )
    return _scheduler
