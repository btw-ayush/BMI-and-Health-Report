"""Module 3a - Persistent history with full CRUD (JSON file storage)."""
import json
import os
import tempfile
from pathlib import Path
from typing import List, Optional

from fitness_tracker import config
from fitness_tracker.logger import get_logger
from fitness_tracker.models import Assessment

log = get_logger("storage")


class StorageError(Exception):
    """Raised when history cannot be saved."""


class HistoryStore:
    def __init__(self, path: Optional[Path] = None):
        self.path = Path(path) if path else config.get_history_path()

    # ---------- internal helpers ----------
    def _read(self) -> List[dict]:
        if not self.path.exists():
            return []
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
            if not isinstance(data, list):
                raise ValueError("history root must be a list")
            return data
        except (json.JSONDecodeError, ValueError, UnicodeDecodeError) as exc:
            backup = self.path.with_suffix(".corrupt")
            log.error("Corrupt history file (%s); moved to %s", exc, backup)
            try:
                os.replace(self.path, backup)
            except OSError:
                pass
            return []
        except OSError as exc:
            raise StorageError(f"Cannot read history: {exc}") from exc

    def _write(self, records: List[dict]) -> None:
        """Atomic write: temp file then rename, so a crash never corrupts data."""
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            fd, tmp = tempfile.mkstemp(dir=self.path.parent, suffix=".tmp")
            with os.fdopen(fd, "w", encoding="utf-8") as fh:
                json.dump(records, fh, indent=2)
            os.replace(tmp, self.path)
        except OSError as exc:
            log.error("Write failed: %s", exc)
            raise StorageError(f"Cannot save history: {exc}") from exc

    # ---------- CRUD ----------
    def add(self, assessment: Assessment) -> Assessment:
        records = self._read()
        assessment.id = max((r.get("id", 0) for r in records), default=0) + 1
        records.append(assessment.to_dict())
        self._write(records)
        log.info("Added assessment id=%s", assessment.id)
        return assessment

    def list_all(self) -> List[Assessment]:
        items = []
        for rec in self._read():
            try:
                items.append(Assessment.from_dict(rec))
            except (TypeError, KeyError) as exc:
                log.warning("Skipping malformed record: %s", exc)
        return items

    def get(self, record_id: int) -> Optional[Assessment]:
        return next((a for a in self.list_all() if a.id == record_id), None)

    def update_note(self, record_id: int, note: str) -> bool:
        records = self._read()
        for rec in records:
            if rec.get("id") == record_id:
                rec["note"] = note
                self._write(records)
                log.info("Updated note id=%s", record_id)
                return True
        return False

    def delete(self, record_id: int) -> bool:
        records = self._read()
        remaining = [r for r in records if r.get("id") != record_id]
        if len(remaining) == len(records):
            return False
        self._write(remaining)
        log.info("Deleted assessment id=%s", record_id)
        return True

    def clear(self) -> None:
        self._write([])
        log.info("History cleared")
