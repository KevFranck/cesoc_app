"""Point d'entree de l'application desktop Windows."""

from client.app.ui.main_window import run


def main() -> int:
    """Lance l'application cliente."""
    return run()


if __name__ == "__main__":
    raise SystemExit(main())
