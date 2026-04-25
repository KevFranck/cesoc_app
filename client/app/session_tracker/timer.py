"""Minuterie locale de session."""

from __future__ import annotations

from datetime import datetime, timedelta

from PySide6.QtCore import QObject, QTimer, Signal


class SessionTimer(QObject):
    """Calcule et diffuse le temps restant de la session."""

    tick = Signal(int, int, str)
    warning = Signal(int)
    expired = Signal()

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._timer = QTimer(self)
        self._timer.setInterval(1000)
        self._timer.timeout.connect(self._emit_tick)
        self._started_at: datetime | None = None
        self._limit_minutes = 0
        self._expired_emitted = False
        self._warning_thresholds: list[int] = []
        self._warning_emitted: set[int] = set()

    def start(self, started_at: datetime, limit_minutes: int, warning_thresholds: list[int] | None = None) -> None:
        """Demarre la minuterie."""
        self._started_at = started_at
        self._limit_minutes = limit_minutes
        self._expired_emitted = False
        self._warning_thresholds = warning_thresholds or []
        self._warning_emitted = set()
        self._emit_tick()
        self._timer.start()

    def stop(self) -> None:
        """Arrete la minuterie."""
        self._timer.stop()
        self._started_at = None
        self._limit_minutes = 0
        self._expired_emitted = False
        self._warning_thresholds = []
        self._warning_emitted = set()

    def _emit_tick(self) -> None:
        if self._started_at is None:
            return

        elapsed = datetime.now() - self._started_at
        remaining = timedelta(minutes=self._limit_minutes) - elapsed
        total_seconds = max(int(remaining.total_seconds()), 0)
        elapsed_minutes = max(int(elapsed.total_seconds() // 60), 0)
        remaining_minutes = total_seconds // 60

        hours, remainder = divmod(total_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        formatted = f"{hours:02d}:{minutes:02d}:{seconds:02d}"

        self.tick.emit(elapsed_minutes, remaining_minutes, formatted)

        for threshold in self._warning_thresholds:
            if remaining_minutes <= threshold and threshold not in self._warning_emitted and total_seconds > 0:
                self._warning_emitted.add(threshold)
                self.warning.emit(threshold)

        if total_seconds == 0 and not self._expired_emitted:
            self._expired_emitted = True
            self.expired.emit()
