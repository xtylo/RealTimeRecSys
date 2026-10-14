from collections import Counter

EVENT_WEIGHTS = {"view": 1.0, "cart": 3.0, "purchase": 5.0}
RECENCY_DECAY = 0.8  # the most recent event weighs the most


class Recommender:
    def __init__(self, related: dict[str, list[int]], popular: list[int]):
        self._related = related
        self._popular = popular

    def recommend(self, history: list[tuple[int, str]], k: int = 10) -> list[tuple[int, float]]:
        seen = {pid for pid, _ in history}
        scores: Counter[int] = Counter()

        for age, (pid, event_type) in enumerate(reversed(history)):
            weight = EVENT_WEIGHTS[event_type] * (RECENCY_DECAY**age)
            for rank, candidate in enumerate(self._related.get(str(pid), [])):
                if candidate not in seen:
                    scores[candidate] += weight / (rank + 1)

        result = [(pid, round(score, 4)) for pid, score in scores.most_common(k)]

        # Fill with popular items (also the cold-start answer when there is no history)
        for pid in self._popular:
            if len(result) >= k:
                break
            if pid not in seen and pid not in scores:
                result.append((pid, 0.0))
        return result
