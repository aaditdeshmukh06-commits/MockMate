#!/usr/bin/env python3
"""
Import checker for MockMate Lambda handlers.
Verifies that all handler modules can be imported without errors.
Run from the repository root or scripts directory.
"""
import sys
import os

repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ai_dir = os.path.join(repo_root, "ai")
package_dir = os.path.join(ai_dir, "package")

# For Lambda, handlers/ and shared/ are at the same level in the zip root.
# So we need to add the parent directory of handlers/ (which is ai/ or package/)
# to sys.path, and then import handlers.xxx
# The key is that shared/ must be importable as a sibling package.

# We'll check against the source first
# Add ai's parent so we can import ai.handlers, ai.shared
# But handlers use `from shared.xxx import ...` which means shared must be at the same level
# So we add ai_dir to path and import handlers directly

def check_imports(path_to_check, label):
    """Check imports from a specific path."""
    sys.path.insert(0, path_to_check)
    modules = [
        "handlers.start_interview",
        "handlers.submit_answer",
        "handlers.get_report",
        "handlers.list_interviews",
        "handlers.save_report",
    ]
    failed = False
    for mod in modules:
        try:
            # Clear any cached modules
            for cached in list(sys.modules.keys()):
                if cached.startswith("handlers") or cached.startswith("shared"):
                    del sys.modules[cached]
            __import__(mod)
            print(f"  OK: {mod}")
        except Exception as e:
            print(f"  FAIL: {mod} - {e}")
            failed = True
    return failed


def main():
    print(f"Checking imports from source ({ai_dir})...")
    failed = check_imports(ai_dir, "source")

    if os.path.exists(package_dir):
        print(f"\nChecking imports from package ({package_dir})...")
        # Need to clear modules again
        for cached in list(sys.modules.keys()):
            if cached.startswith("handlers") or cached.startswith("shared"):
                del sys.modules[cached]
        failed = check_imports(package_dir, "package") or failed

    if failed:
        print("\nSome imports failed!")
        return 1
    print("\nAll imports OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())