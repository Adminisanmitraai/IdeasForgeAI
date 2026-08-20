from backend import ideasforge_chat_api as chat_api
from backend.platform.activity_feed import ActivityFeedQuery, ActivityFeedStore


def test_chat_platform_wrapper_preserves_bytes_and_records_order(monkeypatch):
    store = ActivityFeedStore()
    monkeypatch.setattr(chat_api, "activity_feed", store)
    monkeypatch.setattr(
        chat_api,
        "_stream_openai",
        lambda req, attachments=None: iter((b"hello ", b"world")),
    )
    req = chat_api.IdeasForgeChatRequest(message="hi")
    output = list(
        chat_api._stream_openai_with_platform_events(
            req, [], "chat-corr-1"
        )
    )
    assert output == [b"hello ", b"world"]
    result = store.query(ActivityFeedQuery(correlation_id="chat-corr-1"))
    assert [event.sequence for event in result.events] == [1, 2]
    assert [event.payload["text"] for event in result.events] == ["hello ", "world"]
    assert all(event.event_type == "chat.delta" for event in result.events)
