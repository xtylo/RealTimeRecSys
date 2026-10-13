"""Build the recommender artifacts from a sample of the REES46 dataset."""

import itertools
import json
from collections import Counter, defaultdict
from pathlib import Path

import pandas as pd

RAW = Path("data/raw/2019-Oct.csv")
PROCESSED = Path("data/processed")
ARTIFACTS = Path("artifacts")
SAMPLE_ROWS = 200_000
EVENT_WEIGHTS = {"view": 1, "cart": 3, "purchase": 5}


def main() -> None:
    PROCESSED.mkdir(parents=True, exist_ok=True)
    ARTIFACTS.mkdir(exist_ok=True)

    # nrows avoids loading the full ~5 GB file
    df = pd.read_csv(RAW, nrows=SAMPLE_ROWS).dropna(subset=["user_session"])
    df.to_parquet(PROCESSED / "events.parquet", index=False)
    (
        df[["product_id", "category_code", "brand", "price"]]
        .drop_duplicates("product_id")
        .to_parquet(PROCESSED / "products.parquet", index=False)
    )

    # 1) Popular items: weighted sum by event type
    df["weight"] = df["event_type"].map(EVENT_WEIGHTS)
    popular = df.groupby("product_id")["weight"].sum().nlargest(100).index
    (ARTIFACTS / "popular.json").write_text(json.dumps([int(p) for p in popular]))

    # 2) Co-occurrence: products seen in the same session
    cooc: dict[int, Counter] = defaultdict(Counter)
    sessions = df.groupby("user_session")["product_id"].apply(lambda s: list(dict.fromkeys(s)))
    for items in sessions:
        for a, b in itertools.permutations(items[:30], 2):
            cooc[a][b] += 1
    related = {str(a): [int(b) for b, _ in c.most_common(20)] for a, c in cooc.items()}
    (ARTIFACTS / "related.json").write_text(json.dumps(related))

    print(f"events={len(df):,} products_with_related={len(related):,}")


if __name__ == "__main__":
    main()
