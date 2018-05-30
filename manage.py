#!/usr/bin/env python
import os
import sys

from load_env import read_env

if __name__ == "__main__":

    read_env()  # it is important to load env before setting settings

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "{{ project_name }}.settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)
