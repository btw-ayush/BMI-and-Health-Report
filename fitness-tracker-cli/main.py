"""Entry point: python main.py"""
import sys

from fitness_tracker.cli import FitnessTrackerCLI
from fitness_tracker.logger import setup_logging
from fitness_tracker.storage import HistoryStore


def main() -> int:
    logger = setup_logging()
    logger.info("Application started")
    try:
        FitnessTrackerCLI(HistoryStore()).run()
    except (KeyboardInterrupt, EOFError):
        print("\nExiting. Goodbye!")
    except Exception:  # last-resort safety net
        logger.exception("Unhandled error")
        print("An unexpected error occurred. See logs/app.log for details.")
        return 1
    logger.info("Application closed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
