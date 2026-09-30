"""Interactive command-line interface (workflow controller)."""
from typing import Callable

from fitness_tracker import advice, analytics, formatter, services, validators
from fitness_tracker.logger import get_logger
from fitness_tracker.models import UserProfile
from fitness_tracker.storage import HistoryStore, StorageError

log = get_logger("cli")

MENU = """
========== BMI & Fitness Tracker ==========
 1. New assessment
 2. View history
 3. Progress report
 4. Add / edit note on a record
 5. Delete a record
 6. Exit
"""


class CancelInput(Exception):
    """Raised when the user types 'cancel' at any prompt."""


class FitnessTrackerCLI:
    def __init__(self, store: HistoryStore, input_fn: Callable = input,
                 output_fn: Callable = print, use_color: bool = None):
        self.store = store
        self.input_fn = input_fn
        self.out = output_fn
        self.color = formatter.supports_color() if use_color is None else use_color

    # ---------- helpers ----------
    def ask(self, label: str, validator: Callable):
        """Prompt until valid. Type 'cancel' to abort."""
        while True:
            raw = self.input_fn(f"{label}: ")
            if raw.strip().lower() == "cancel":
                raise CancelInput
            try:
                return validator(raw)
            except validators.ValidationError as exc:
                self.out(formatter.colorize(f"  ! {exc}", "red", self.color))

    # ---------- actions ----------
    def new_assessment(self) -> None:
        self.out("Enter your details (type 'cancel' to go back).")
        name = self.ask("Name", validators.validate_name)
        age = self.ask("Age (years)", validators.validate_age)
        sex = self.ask("Sex (m/f)", validators.validate_sex)
        height = self.ask("Height (cm)", validators.validate_height_cm)
        weight = self.ask("Weight (kg)", validators.validate_weight_kg)
        self.out("Activity level:\n" + formatter.activity_menu())
        activity = self.ask("Choose 1-5", validators.validate_activity)

        profile = UserProfile(name, age, sex, height, weight, activity)
        assessment = services.build_assessment(profile)
        self.out("\n" + formatter.render_assessment(assessment, self.color))
        self.out("\n" + formatter.render_advice(
            advice.get_advice(assessment.category, activity), self.color))
        saved = self.store.add(assessment)
        self.out(f"\nSaved as record #{saved.id}.")

    def view_history(self) -> None:
        self.out(formatter.render_history(self.store.list_all(), self.color))

    def progress_report(self) -> None:
        summary = analytics.summarize_progress(self.store.list_all())
        self.out(formatter.render_progress(summary, self.color))

    def edit_note(self) -> None:
        self.view_history()
        rid = self.ask("Record ID", validators.validate_record_id)
        note = self.ask("Note", validators.validate_note)
        ok = self.store.update_note(rid, note)
        self.out("Note updated." if ok else f"Record #{rid} not found.")

    def delete_record(self) -> None:
        self.view_history()
        rid = self.ask("Record ID to delete", validators.validate_record_id)
        confirm = self.input_fn(f"Delete record #{rid}? (y/N): ").strip().lower()
        if confirm != "y":
            self.out("Cancelled.")
            return
        self.out("Record deleted." if self.store.delete(rid) else f"Record #{rid} not found.")

    # ---------- main loop ----------
    def run(self) -> None:
        actions = {
            "1": self.new_assessment, "2": self.view_history, "3": self.progress_report,
            "4": self.edit_note, "5": self.delete_record,
        }
        while True:
            self.out(MENU)
            choice = self.input_fn("Choose an option: ").strip()
            if choice == "6":
                self.out("Stay healthy! Goodbye.")
                return
            action = actions.get(choice)
            if action is None:
                self.out(formatter.colorize("Invalid choice, enter 1-6.", "red", self.color))
                continue
            try:
                action()
            except CancelInput:
                self.out("Cancelled.")
            except StorageError as exc:
                log.error("Storage error: %s", exc)
                self.out(formatter.colorize(f"Storage problem: {exc}", "red", self.color))
