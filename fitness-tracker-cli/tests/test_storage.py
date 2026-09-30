from fitness_tracker.storage import HistoryStore


def test_add_list_get(tmp_path, assessment):
    store = HistoryStore(tmp_path / "h.json")
    saved = store.add(assessment)
    assert saved.id == 1
    assert len(store.list_all()) == 1
    assert store.get(1).profile.name == "Asha"
    assert store.get(99) is None


def test_ids_increment_and_not_reused(tmp_path, assessment):
    store = HistoryStore(tmp_path / "h.json")
    store.add(assessment)
    store.add(assessment)
    store.delete(1)
    assert store.add(assessment).id == 3


def test_update_note(tmp_path, assessment):
    store = HistoryStore(tmp_path / "h.json")
    store.add(assessment)
    assert store.update_note(1, "felt great") is True
    assert store.get(1).note == "felt great"
    assert store.update_note(42, "x") is False


def test_delete_and_clear(tmp_path, assessment):
    store = HistoryStore(tmp_path / "h.json")
    store.add(assessment)
    assert store.delete(1) is True
    assert store.delete(1) is False
    store.add(assessment)
    store.clear()
    assert store.list_all() == []


def test_missing_file_returns_empty(tmp_path):
    assert HistoryStore(tmp_path / "nope.json").list_all() == []


def test_corrupt_file_recovers(tmp_path, assessment):
    path = tmp_path / "h.json"
    path.write_text("{not valid json")
    store = HistoryStore(path)
    assert store.list_all() == []
    assert path.with_suffix(".corrupt").exists()
    store.add(assessment)  # still usable afterwards
    assert len(store.list_all()) == 1


def test_wrong_root_type_recovers(tmp_path):
    path = tmp_path / "h.json"
    path.write_text('{"a": 1}')
    assert HistoryStore(path).list_all() == []


def test_malformed_record_skipped(tmp_path, assessment):
    store = HistoryStore(tmp_path / "h.json")
    store.add(assessment)
    (tmp_path / "h.json").write_text('[{"id": 1, "bogus": true}]')
    assert store.list_all() == []
