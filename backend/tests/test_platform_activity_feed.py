from backend.platform.activity_feed import ActivityFeedQuery, ActivityFeedStore
from backend.platform.platform_event_model import build_event


def make_event(sequence: int, correlation_id: str = "corr-1"):
    return build_event(
        event_type="task.updated",
        source="founder-os",
        occurred_at=f"2026-08-20T18:58:0{sequence}+05:30",
        correlation_id=correlation_id,
        sequence=sequence,
        subject_id="task-1",
        payload={"status": "running"},
    )


def test_activity_feed_deduplicates_and_preserves_order():
    store = ActivityFeedStore(maximum_events=5)
    first = make_event(1)
    second = make_event(2)
    store.extend([first, first, second])
    result = store.query()
    assert result.events == (first, second)
    assert result.total_matches == 2
    assert result.returned_events == 2


def test_activity_feed_filters_by_correlation_and_sequence():
    store = ActivityFeedStore()
    store.extend([make_event(1), make_event(2), make_event(3, "corr-2")])
    result = store.query(ActivityFeedQuery(correlation_id="corr-1", after_sequence=1))
    assert [event.sequence for event in result.events] == [2]
