import json

from una_autonomous_learning_v0_1 import CandidateLearningStore, learn


def test_learning_records_source_and_stays_candidate(tmp_path):
    source = tmp_path / "lesson.md"
    source.write_text("Memory is retrieved by subject.\nUnrelated line.\n", encoding="utf-8")
    records = learn(tmp_path, "memory", [source])
    assert len(records) == 1
    record = records[0]
    assert record["schema"] == "UNA_CANDIDATE_LEARNING_RECORD_V0_1"
    assert record["excerpts"] == ["Memory is retrieved by subject."]
    assert record["memory_promoted"] is False
    assert record["model_weights_changed"] is False
    assert record["network_access"] is False

    recalled = CandidateLearningStore(tmp_path).recall("memory")
    assert recalled[0]["record_sha256"] == record["record_sha256"]


def test_corrupt_lines_are_ignored(tmp_path):
    store = CandidateLearningStore(tmp_path)
    store.path.parent.mkdir(parents=True)
    store.path.write_text("not-json\n", encoding="utf-8")
    assert store.recall() == []
