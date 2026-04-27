"""Client HTTP pour le desktop CESOC."""

import json
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

    def login(self, email: str, password: str, workstation_name: str) -> dict[str, Any]:
        """Ouvre une session utilisateur."""
        response = self._request(
            "POST",
            "/auth/login",
            json={"email": email, "password": password, "workstation_name": workstation_name},
        )
        return response.json()

    def register(self, email: str, first_name: str, last_name: str, password: str) -> dict[str, Any]:
        """Inscrit un utilisateur client."""
        response = self._request(
            "POST",
            "/auth/register",
            json={
                "email": email,
                "first_name": first_name,
                "last_name": last_name,
                "password": password,
            },
        )
        return response.json()

    def change_password(self, email: str, current_password: str, new_password: str) -> dict[str, Any]:
        """Modifie le mot de passe d'un utilisateur."""
        response = self._request(
            "POST",
            "/auth/change-password",
            json={
                "email": email,
                "current_password": current_password,
                "new_password": new_password,
            },
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

    def submit_print(self, email: str, workstation_name: str, pages: int) -> dict[str, Any]:
        """Soumet une demande d'impression."""
        response = self._request(
            "POST",
            "/prints",
            json={
                "email": email,
                "workstation_name": workstation_name,
                "pages": pages,
            },
        )
        return response.json()

    def get_print_quota(self, email: str) -> dict[str, Any]:
        """Retourne l'etat du quota d'impression de l'usager."""
        response = self._request(
            "GET",
            "/prints/quota",
            params={"email": email},
        )
        return response.json()

    def observe_print_job(
        self,
        email: str,
        workstation_name: str,
        pages: int,
        printer_name: str | None = None,
        document_name: str | None = None,
        spool_job_id: int | None = None,
        total_pages_seen: int | None = None,
    ) -> dict[str, Any]:
        """Journalise un job detecte par le spooler Windows."""
        response = self._request(
            "POST",
            "/prints/observe",
            json={
                "email": email,
                "workstation_name": workstation_name,
                "pages": pages,
                "printer_name": printer_name,
                "document_name": document_name,
                "spool_job_id": spool_job_id,
                "total_pages_seen": total_pages_seen,
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
            raise RuntimeError(self._extract_error_message(exc.response)) from exc
        except httpx.HTTPError as exc:
            raise RuntimeError(
                "Impossible de joindre l'API CESOC. Verifie que le serveur tourne."
            ) from exc

    def _extract_error_message(self, response: httpx.Response) -> str:
        """Retourne un message d'erreur presentable pour l'interface."""
        try:
            payload = response.json()
        except (json.JSONDecodeError, ValueError):
            text = response.text.strip()
            return text or f"Erreur API {response.status_code}."

        detail = payload.get("detail")
        if isinstance(detail, str) and detail.strip():
            return detail.strip()

        if isinstance(detail, list) and detail:
            first_error = detail[0]
            if isinstance(first_error, dict):
                msg = first_error.get("msg")
                if isinstance(msg, str) and msg.strip():
                    return msg.strip()

        return f"Erreur API {response.status_code}."
