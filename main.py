import sys

INTERACTIVE = False

if INTERACTIVE and sys.stdin.isatty():
    __import__("interactive")
else:
    if INTERACTIVE:
        # User tried to use interactive mode but failed
        print("=== FALLBACK TO LEGACY MODE")
        print("Your terminal does not support interactive mode, so we've automatically switched to legacy mode for you.")
    else:
        print("=== SWITCHED TO LEGACY MODE")
    __import__("legacy")