"""Services de lancement d'applications locales."""

from __future__ import annotations

import os
import shutil
import subprocess
import webbrowser
from pathlib import Path


class AppLauncher:
    """Ouvre des applications et ressources locales pour les tests."""

    def __init__(self, word_executable: str) -> None:
        self.word_executable = word_executable
        self._tracked_processes: list[subprocess.Popen] = []

    def open_browser(self, url: str) -> None:
        """Ouvre le navigateur par defaut sur une URL."""
        success = webbrowser.open(url)
        if not success:
            raise RuntimeError("Impossible d'ouvrir le navigateur web.")

    def open_word(self) -> None:
        """Ouvre Microsoft Word si disponible."""
        executable = shutil.which(self.word_executable) or self.word_executable
        try:
            process = subprocess.Popen([executable], creationflags=subprocess.CREATE_NO_WINDOW)
            self._tracked_processes.append(process)
        except FileNotFoundError as exc:
            raise RuntimeError(
                "Microsoft Word est introuvable sur ce poste. Verifie winword.exe."
            ) from exc
        except OSError as exc:
            raise RuntimeError("Impossible de lancer Microsoft Word.") from exc

    def open_path(self, target: Path) -> None:
        """Ouvre un dossier ou un fichier avec l'application par defaut."""
        if not target.exists():
            raise RuntimeError(f"Chemin introuvable : {target}")
        if target.is_dir():
            process = subprocess.Popen(["explorer.exe", str(target)])
            self._tracked_processes.append(process)
            return
        os.startfile(target)

    def cleanup_finished_processes(self) -> None:
        """Supprime les processus deja termines de la liste de suivi."""
        self._tracked_processes = [
            process for process in self._tracked_processes if process.poll() is None
        ]

    def tracked_process_count(self) -> int:
        """Retourne le nombre de processus encore suivis."""
        self.cleanup_finished_processes()
        return len(self._tracked_processes)

    def close_tracked_processes(self) -> int:
        """Ferme les processus lances par l'application quand c'est possible."""
        self.cleanup_finished_processes()
        closed_count = 0
        for process in list(self._tracked_processes):
            try:
                process.terminate()
                process.wait(timeout=5)
                closed_count += 1
            except OSError:
                continue
            except subprocess.TimeoutExpired:
                try:
                    process.kill()
                    process.wait(timeout=2)
                    closed_count += 1
                except OSError:
                    continue
                except subprocess.TimeoutExpired:
                    continue
        self.cleanup_finished_processes()
        return closed_count
