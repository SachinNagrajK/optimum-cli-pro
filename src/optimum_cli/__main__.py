"""Main entry point for the Optimum CLI Pro application."""

import sys
from optimum_cli.cli.main import app


def main():
    """Main entry point."""
    try:
        app()
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
