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
    copies: int


@dataclass
class TrackedPrintJob:
    """Etat local d'un job en cours de suivi."""

    printer_name: str
    spool_job_id: int
    document_name: str
    max_pages_seen: int
    emitted_pages: int = 0
    paused_once: bool = False


class WindowsPrintMonitor(QObject):
    """Observe les files d'impression locales par polling."""

    job_detected = Signal(dict)
    monitor_error = Signal(str)

    def __init__(self, interval_ms: int = 1500, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._timer = QTimer(self)
        self._timer.setInterval(interval_ms)
        self._timer.timeout.connect(self._poll_jobs)
        self._known_queue_keys: set[tuple[str, int]] = set()
        self._tracked_jobs: dict[tuple[str, int], TrackedPrintJob] = {}
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
        self._known_queue_keys.clear()
        self._tracked_jobs.clear()

    def forget_processed_jobs(self) -> None:
        """Reinitialise la memoire locale des jobs deja vus."""
        self._known_queue_keys.clear()
        self._tracked_jobs.clear()

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

    def pause_job(self, printer_name: str, spool_job_id: int) -> bool:
        """Met un job en pause pour laisser le temps a CESOC de decider."""
        if not self._enabled:
            return False

        handle = None
        try:
            handle = win32print.OpenPrinter(printer_name)
            win32print.SetJob(handle, spool_job_id, 0, None, win32print.JOB_CONTROL_PAUSE)
            return True
        except Exception:
            return False
        finally:
            if handle:
                win32print.ClosePrinter(handle)

    def resume_job(self, printer_name: str, spool_job_id: int) -> bool:
        """Relance un job precedemment mis en pause."""
        if not self._enabled:
            return False

        handle = None
        try:
            handle = win32print.OpenPrinter(printer_name)
            win32print.SetJob(handle, spool_job_id, 0, None, win32print.JOB_CONTROL_RESUME)
            return True
        except Exception:
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
                        self._update_tracked_job(key, job)
                        continue
                    self._known_queue_keys.add(key)
                    self._tracked_jobs[key] = TrackedPrintJob(
                        printer_name=job.printer_name,
                        spool_job_id=job.spool_job_id,
                        document_name=job.document_name,
                        max_pages_seen=max(1, job.total_pages),
                        emitted_pages=0,
                        paused_once=False,
                    )
                    tracked = self._tracked_jobs[key]
                    tracked.paused_once = self.pause_job(job.printer_name, job.spool_job_id)
                    self._emit_new_pages(key)
            self._known_queue_keys.intersection_update(active_keys)
            stale_keys = set(self._tracked_jobs.keys()) - active_keys
            for stale_key in stale_keys:
                self._tracked_jobs.pop(stale_key, None)
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
            self._tracked_jobs = {}

    def _list_printers(self) -> list[str]:
        flags = win32print.PRINTER_ENUM_LOCAL | win32print.PRINTER_ENUM_CONNECTIONS
        printers = win32print.EnumPrinters(flags)
        return [printer[2] for printer in printers]

    def _list_jobs(self, printer_name: str) -> list[PrintJobSnapshot]:
        handle = None
        try:
            handle = win32print.OpenPrinter(printer_name)
            try:
                jobs = win32print.EnumJobs(handle, 0, 999, 2)
            except Exception:
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
        copies = self._extract_copies(job)
        total_pages = self._extract_total_pages(job, copies)
        return PrintJobSnapshot(
            printer_name=printer_name,
            spool_job_id=int(job["JobId"]),
            document_name=str(job.get("pDocument") or "Document"),
            total_pages=total_pages,
            copies=copies,
        )

    def _extract_total_pages(self, job: dict[str, Any], copies: int) -> int:
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
                return parsed * max(1, copies)
        return 1

    def _extract_copies(self, job: dict[str, Any]) -> int:
        candidates = [
            job.get("Copies"),
        ]

        devmode = job.get("pDevMode")
        if devmode is not None:
            for attr_name in ("Copies", "dmCopies"):
                try:
                    candidates.append(getattr(devmode, attr_name))
                except Exception:
                    continue

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

    def _update_tracked_job(self, key: tuple[str, int], snapshot: PrintJobSnapshot) -> None:
        tracked = self._tracked_jobs.get(key)
        if not tracked:
            self._tracked_jobs[key] = TrackedPrintJob(
                printer_name=snapshot.printer_name,
                spool_job_id=snapshot.spool_job_id,
                document_name=snapshot.document_name,
                max_pages_seen=max(1, snapshot.total_pages),
                emitted_pages=0,
                paused_once=False,
            )
            tracked = self._tracked_jobs[key]
            tracked.paused_once = self.pause_job(snapshot.printer_name, snapshot.spool_job_id)
            self._emit_new_pages(key)
            return

        tracked.max_pages_seen = max(tracked.max_pages_seen, max(1, snapshot.total_pages))
        if snapshot.document_name:
            tracked.document_name = snapshot.document_name
        self._emit_new_pages(key)

    def _emit_new_pages(self, key: tuple[str, int]) -> None:
        tracked = self._tracked_jobs.get(key)
        if not tracked:
            return

        pages_delta = tracked.max_pages_seen - tracked.emitted_pages
        if pages_delta <= 0:
            return

        tracked.emitted_pages += pages_delta
        self.job_detected.emit(
            {
                "printer_name": tracked.printer_name,
                "spool_job_id": tracked.spool_job_id,
                "document_name": tracked.document_name,
                "pages": pages_delta,
                "pages_total_seen": tracked.max_pages_seen,
                "paused_once": tracked.paused_once,
            }
        )
