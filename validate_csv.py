#!/usr/bin/env python3

from pathlib import Path

import pandas as pd


def column_names(df: pd.DataFrame):
    columns = frozenset(df.columns)
    assert "time" in columns
    assert "band" in columns
    assert columns.issuperset({"mag", "magerr"}) or columns.issuperset({"flux", "fluxerr"})


def validate(df: pd.DataFrame):
    column_names(df)


def test_all_csv(subtests):
    project_dir = Path(__file__).parent

    for folder in ["from-issues", "RRLyrae/light-curves", "SNIa/light-curves"]:
        base = project_dir / folder
        for csv_path in base.glob("**/*.csv"):
            path = base / csv_path
            df = pd.read_csv(path)
            with subtests.test("CSV validation test", path=path):
                validate(df)


def main():
    from contextlib import nullcontext

    class MockPytestSubtests:
        def test(self, *args, **kwargs):
            return nullcontext()

    test_all_csv(MockPytestSubtests())


if __name__ == "__main__":
    main()
