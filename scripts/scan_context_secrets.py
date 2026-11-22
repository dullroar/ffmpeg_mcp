#!/usr/bin/env python3
"""Scan context files using the previous command name. Usage: scan_context_secrets.py [ROOT]

Run me when: I use an existing command that calls this name for scan_secrets.py.
"""
from __future__ import annotations

import sys

from scan_secrets import main


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
