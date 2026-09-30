from fitness_tracker.cli import FitnessTrackerCLI
from fitness_tracker.storage import HistoryStore


def run_cli(tmp_path, inputs):
    it = iter(inputs)
    out = []
    cli = FitnessTrackerCLI(HistoryStore(tmp_path / "h.json"), input_fn=lambda _p: next(it),
                            output_fn=out.append, use_color=False)
    cli.run()
    return "\n".join(out), cli.store


def test_full_flow_with_retry_on_invalid_input(tmp_path):
    inputs = ["1", "Asha", "abc", "25", "f", "165", "60", "3", "6"]  # 'abc' triggers re-prompt
    text, store = run_cli(tmp_path, inputs)
    assert "Age must be a number" in text
    assert "NORMAL" in text and "Saved as record #1" in text
    assert len(store.list_all()) == 1


def test_cancel_returns_to_menu(tmp_path):
    text, store = run_cli(tmp_path, ["1", "Asha", "cancel", "6"])
    assert "Cancelled." in text and store.list_all() == []


def test_invalid_menu_choice(tmp_path):
    text, _ = run_cli(tmp_path, ["9", "6"])
    assert "Invalid choice" in text


def test_progress_with_no_data(tmp_path):
    text, _ = run_cli(tmp_path, ["3", "6"])
    assert "No records yet" in text


def test_delete_flow_and_confirmation(tmp_path):
    add = ["1", "Ravi", "30", "m", "175", "70", "2"]
    text, store = run_cli(tmp_path, add + ["5", "1", "n", "5", "1", "y", "6"])
    assert "Cancelled." in text and "Record deleted." in text
    assert store.list_all() == []


def test_note_flow(tmp_path):
    add = ["1", "Ravi", "30", "m", "175", "70", "2"]
    text, store = run_cli(tmp_path, add + ["4", "1", "leg day", "4", "9", "hi", "6"])
    assert store.get(1).note == "leg day"
    assert "Record #9 not found." in text
