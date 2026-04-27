"""Utilitaires de date/heure applicatifs."""

from datetime import date, datetime, time, timedelta, timezone
from functools import lru_cache
from zoneinfo import ZoneInfo

from server.app.core.config import get_settings


@lru_cache
def get_app_timezone() -> ZoneInfo:
    """Retourne le fuseau horaire applicatif."""
    return ZoneInfo(get_settings().app_timezone)


def get_local_now() -> datetime:
    """Retourne la date/heure locale du service, sans information de fuseau."""
    return datetime.now(get_app_timezone()).replace(tzinfo=None)


def get_local_today() -> date:
    """Retourne la date locale du service."""
    return get_local_now().date()


def get_utc_now_naive() -> datetime:
    """Retourne l'instant courant en UTC naif pour les horodatages stockes en UTC naive."""
    return datetime.now(timezone.utc).replace(tzinfo=None)


def get_local_day_bounds(target_date: date) -> tuple[datetime, datetime]:
    """Retourne les bornes locales naives d'une journee donnee."""
    start = datetime.combine(target_date, time.min)
    end = start + timedelta(days=1)
    return start, end


def get_utc_naive_bounds_for_local_date(target_date: date) -> tuple[datetime, datetime]:
    """Retourne les bornes UTC naives correspondant a une journee locale."""
    tz = get_app_timezone()
    local_start = datetime.combine(target_date, time.min, tzinfo=tz)
    local_end = local_start + timedelta(days=1)
    utc_start = local_start.astimezone(timezone.utc).replace(tzinfo=None)
    utc_end = local_end.astimezone(timezone.utc).replace(tzinfo=None)
    return utc_start, utc_end
