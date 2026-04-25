"""Client HTTP pour le desktop CESOC."""

from typing import Any

import httpx


class ApiClient:
    """Encapsule les appels a l'API CESOC."""

    def __init__(self, base_url: str) -> None:
        self.base_url = base_url.rstrip("/")

    def list_users(self) -> list[dict[str, Any]]:
        """Retourne les utilisateurs disponibles."""
        response = self._request("GET", "/catalog/users")
        return response.json()

    def list_workstations(self) -> list[dict[str, Any]]:
        """Retourne les postes disponibles."""
        response = self._request("GET", "/catalog/workstations")
        return response.json()

    def login(self, external_id: str, workstation_name: str) -> dict[str, Any]:
        """Ouvre une session utilisateur."""
        response = self._request(
            "POST",
            "/auth/login",
            json={"external_id": external_id, "workstation_name": workstation_name},
        )
        return response.json()

    def list_active_sessions(self) -> list[dict[str, Any]]:
        """Liste les sessions actives."""
        response = self._request("GET", "/sessions/active")
        return response.json()

    def close_session(self, session_id: int) -> dict[str, Any]:
        """Ferme une session."""
        response = self._request("POST", f"/sessions/{session_id}/close")
        return response.json()

    def submit_print(self, external_id: str, workstation_name: str, pages: int) -> dict[str, Any]:
        """Soumet une demande d'impression."""
        response = self._request(
            "POST",
            "/prints",
            json={
                "external_id": external_id,
                "workstation_name": workstation_name,
                "pages": pages,
            },
        )
        return response.json()

    def get_print_quota(self, external_id: str) -> dict[str, Any]:
        """Retourne l'etat du quota d'impression de l'usager."""
        response = self._request(
            "GET",
            "/prints/quota",
            params={"external_id": external_id},
        )
        return response.json()

    def observe_print_job(
        self,
        external_id: str,
        workstation_name: str,
        pages: int,
        printer_name: str | None = None,
        document_name: str | None = None,
        spool_job_id: int | None = None,
    ) -> dict[str, Any]:
        """Journalise un job detecte par le spooler Windows."""
        response = self._request(
            "POST",
            "/prints/observe",
            json={
                "external_id": external_id,
                "workstation_name": workstation_name,
                "pages": pages,
                "printer_name": printer_name,
                "document_name": document_name,
                "spool_job_id": spool_job_id,
            },
        )
        return response.json()

    def get_daily_report(self) -> dict[str, Any]:
        """Retourne le rapport du jour."""
        response = self._request("GET", "/reports/daily")
        return response.json()

    def _request(self, method: str, path: str, **kwargs: Any) -> httpx.Response:
        """Execute une requete HTTP avec timeout et messages d'erreur propres."""
        url = f"{self.base_url}{path}"
        try:
            with httpx.Client(timeout=10.0) as client:
                response = client.request(method, url, **kwargs)
                response.raise_for_status()
                return response
        except httpx.HTTPStatusError as exc:
            detail = exc.response.text
            raise RuntimeError(f"Erreur API {exc.response.status_code}: {detail}") from exc
        except httpx.HTTPError as exc:
            raise RuntimeError(
                "Impossible de joindre l'API CESOC. Verifie que le serveur tourne."
            ) from exc
