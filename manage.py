#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'wellesuedwest.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Django konnte nicht importiert werden. Ist es installiert und "
            "in der PYTHONPATH-Umgebungsvariable verfügbar? Hast du dein "
            "virtuelles Environment aktiviert?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
