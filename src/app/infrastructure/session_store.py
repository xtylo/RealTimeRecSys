from collections import defaultdict, deque


class InMemorySessionStore:
    """Keeps the last N interactions per session. WARNING: lives in the process memory."""

    def __init__(self, max_events: int = 20):
        self._sessions: dict[str, deque] = defaultdict(lambda: deque(maxlen=max_events))

    def add(self, session_id: str, product_id: int, event_type: str) -> None:
        self._sessions[session_id].append((product_id, event_type))

    def get(self, session_id: str) -> list[tuple[int, str]]:
        return list(self._sessions.get(session_id, []))
