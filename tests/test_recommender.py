from app.domain.recommender import Recommender


def test_empty_history_returns_popular():
    rec = Recommender(related={}, popular=[9, 8, 7])
    assert [p for p, _ in rec.recommend([], k=2)] == [9, 8]


def test_cart_weighs_more_than_view():
    rec = Recommender(related={"1": [10], "2": [20]}, popular=[])
    result = rec.recommend([(1, "cart"), (2, "view")], k=2)
    assert result[0][0] == 10


def test_does_not_recommend_seen_items():
    rec = Recommender(related={"1": [2, 3]}, popular=[])
    result = rec.recommend([(1, "view"), (2, "view")], k=5)
    assert 2 not in [p for p, _ in result]
