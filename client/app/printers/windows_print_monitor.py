"""Surveillance des jobs d'impression Windows."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from PySide6.QtCore import QObject, QTimer, Signal

try:
    import win32print  # type: ignore
except ImportError:  # pragma: no cover - environnement non-Windows ou dependance absente
    win32print = None


@dataclass(frozen=True)
class PrintJobSnapshot:
    """Etat simplifie d'un job detecte sur le spooler."""

    printer_name: str
    spool_job_id: int
    document_name: str
    total_pages: int


class WindowsPrintMonitor(QObject):
    """Observe les files d'impression locales par polling."""

    job_detected = Signal(dict)
    monitor_error = Signal(str)

    def __init__(self, interval_ms: int = 1500, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._timer = QTimer(self)
        self._timer.setInterval(interval_ms)
        self._timer.timeout.connect(self._poll_jobs)
        self._processed_keys: set[tuple[str, int]] = set()
        self._known_queue_keys: set[tuple[str, int]] = set()
        self._enabled = win32print is not None

    @property
    def is_supported(self) -> bool:
        """Indique si la surveillance Windows est disponible."""
        return self._enabled

    def start(self) -> None:
        """Demarre la surveillance."""
        if not self._enabled:
            self.monitor_error.emit(
                "La surveillance d'impression Windows n'est pas disponible sur ce poste."
            )
            return
        self._prime_existing_jobs()
        self._timer.start()

    def stop(self) -> None:
        """Arrete la surveillance et reinitialise les jobs connus."""
        self._timer.stop()
        self._processed_keys.clear()
        self._known_queue_keys.clear()

    def forget_processed_jobs(self) -> None:
        """Reinitialise la memoire locale des jobs deja vus."""
        self._processed_keys.clear()
        self._known_queue_keys.clear()

    def cancel_job(self, printer_name: str, spool_job_id: int) -> bool:
        """Supprime un job du spooler si possible."""
        if not self._enabled:
            return False

        handle = None
        try:
            handle = win32print.OpenPrinter(printer_name)
            win32print.SetJob(handle, spool_job_id, 0, None, win32print.JOB_CONTROL_DELETE)
            return True
        except Exception as exc:  # pragma: no cover - depend de l'etat du spooler
            self.monitor_error.emit(
                f"Impossible de bloquer l'impression {spool_job_id} sur {printer_name}: {exc}"
            )
            return False
        finally:
            if handle:
                win32print.ClosePrinter(handle)

    def _poll_jobs(self) -> None:
        if not self._enabled:
            return

        try:
            active_keys: set[tuple[str, int]] = set()
            for printer_name in self._list_printers():
                for job in self._list_jobs(printer_name):
                    key = (job.printer_name, job.spool_job_id)
                    active_keys.add(key)
                    if key in self._known_queue_keys:
                        continue
                    if key in self._processed_keys:
                        continue
                    self._known_queue_keys.add(key)
                    self._processed_keys.add(key)
                    self.job_detected.emit(
                        {
                            "printer_name": job.printer_name,
                            "spool_job_id": job.spool_job_id,
                            "document_name": job.document_name,
                            "pages": max(1, job.total_pages),
                        }
                    )
            self._known_queue_keys.intersection_update(active_keys)
        except Exception as exc:  # pragma: no cover - depend du spooler Windows
            self.monitor_error.emit(f"Erreur de surveillance des impressions: {exc}")

    def _prime_existing_jobs(self) -> None:
        """Ignore les jobs deja presents au moment ou la session CESOC commence."""
        try:
            existing_keys: set[tuple[str, int]] = set()
            for printer_name in self._list_printers():
                for job in self._list_jobs(printer_name):
                    existing_keys.add((job.printer_name, job.spool_job_id))
            self._known_queue_keys = existing_keys
        except Exception as exc:  # pragma: no cover - depend du spooler Windows
            self.monitor_error.emit(f"Impossible d'initialiser la surveillance d'impression: {exc}")
            self._known_queue_keys = set()

    def _list_printers(self) -> list[str]:
        flags = win32print.PRINTER_ENUM_LOCAL | win32print.PRINTER_ENUM_CONNECTIONS
        printers = win32print.EnumPrinters(flags)
        return [printer[2] for printer in printers]

    def _list_jobs(self, printer_name: str) -> list[PrintJobSnapshot]:
        handle = None
        try:
            handle = win32print.OpenPrinter(printer_name)
            jobs = win32print.EnumJobs(handle, 0, 999, 1)
            return [
                self._build_job_snapshot(printer_name, job)
                for job in jobs
                if self._should_track_job(job)
            ]
        finally:
            if handle:
                win32print.ClosePrinter(handle)

    def _build_job_snapshot(self, printer_name: str, job: dict[str, Any]) -> PrintJobSnapshot:
        total_pages = self._extract_total_pages(job)
        return PrintJobSnapshot(
            printer_name=printer_name,
            spool_job_id=int(job["JobId"]),
            document_name=str(job.get("pDocument") or "Document"),
            total_pages=total_pages,
        )

    def _extract_total_pages(self, job: dict[str, Any]) -> int:
        candidates = [
            job.get("TotalPages"),
            job.get("PagesPrinted"),
            job.get("Pages"),
        ]
        for value in candidates:
            try:
                parsed = int(value)
            except (TypeError, ValueError):
                continue
            if parsed > 0:
                return parsed
        return 1

    def _should_track_job(self, job: dict[str, Any]) -> bool:
        status_mask = int(job.get("Status", 0) or 0)
        tracked_statuses = (
            getattr(win32print, "JOB_STATUS_SPOOLING", 0),
            getattr(win32print, "JOB_STATUS_PRINTING", 0),
            getattr(win32print, "JOB_STATUS_PAUSED", 0),
            getattr(win32print, "JOB_STATUS_BLOCKED_DEVQ", 0),
            getattr(win32print, "JOB_STATUS_USER_INTERVENTION", 0),
        )
        if not status_mask:
            return True
        return any(status_mask & tracked for tracked in tracked_statuses if tracked)
