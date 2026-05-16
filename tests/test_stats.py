import json
import sys
import types
import unittest
from datetime import date
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))

from repositories.stats_repository import StatsRepository
from router import route
from services.stats_service import StatsService


def parse_body(response: dict) -> dict:
    return json.loads(response["body"])


def build_event(code: str | None = "Ab3xY9", method: str = "GET", query_params: dict | None = None) -> dict:
    event = {"httpMethod": method, "queryStringParameters": query_params}
    if code is not None:
        event["pathParameters"] = {"codigo": code}
    return event


class StatsServiceTest(unittest.TestCase):
    def test_valid_range_returns_total_and_daily_entries(self):
        repository = MagicMock()
        repository.get_stats.return_value = [
            {"codigo": "Ab3xY9", "fecha": "2026-05-14", "clicks": 3},
            {"codigo": "Ab3xY9", "fecha": "2026-05-15", "clicks": 5},
        ]

        response = StatsService(repository=repository).get_stats(
            "Ab3xY9",
            from_date="2026-05-14",
            to_date="2026-05-15",
        )

        self.assertEqual(response["statusCode"], 200)
        self.assertEqual(
            parse_body(response),
            {
                "codigo": "Ab3xY9",
                "total_clicks": 8,
                "daily": [
                    {"fecha": "2026-05-14", "clicks": 3},
                    {"fecha": "2026-05-15", "clicks": 5},
                ],
            },
        )
        repository.get_stats.assert_called_once_with("Ab3xY9", "2026-05-14", "2026-05-15")

    def test_without_dates_uses_last_30_days(self):
        repository = MagicMock()
        repository.get_stats.return_value = []

        response = StatsService(repository=repository, today=date(2026, 5, 16)).get_stats("Ab3xY9")

        self.assertEqual(response["statusCode"], 200)
        self.assertEqual(parse_body(response), {"codigo": "Ab3xY9", "total_clicks": 0, "daily": []})
        repository.get_stats.assert_called_once_with("Ab3xY9", "2026-04-17", "2026-05-16")

    def test_code_without_visits_returns_empty_daily_array(self):
        repository = MagicMock()
        repository.get_stats.return_value = []

        response = StatsService(repository=repository).get_stats(
            "NoHits",
            from_date="2026-05-01",
            to_date="2026-05-16",
        )

        self.assertEqual(response["statusCode"], 200)
        self.assertEqual(parse_body(response), {"codigo": "NoHits", "total_clicks": 0, "daily": []})

    def test_invalid_range_returns_bad_request_before_repository_call(self):
        repository = MagicMock()

        response = StatsService(repository=repository).get_stats(
            "Ab3xY9",
            from_date="2026-05-16",
            to_date="2026-05-01",
        )

        self.assertEqual(response["statusCode"], 400)
        repository.get_stats.assert_not_called()

    def test_router_extracts_code_and_query_parameters(self):
        repository = MagicMock()
        repository.get_stats.return_value = [{"codigo": "Ab3xY9", "fecha": "2026-05-16", "clicks": 2}]

        original_init = StatsService.__init__

        def init_with_repository(self):
            original_init(self, repository=repository)

        StatsService.__init__ = init_with_repository
        try:
            response = route(build_event(query_params={"from": "2026-05-16", "to": "2026-05-16"}))
        finally:
            StatsService.__init__ = original_init

        self.assertEqual(response["statusCode"], 200)
        repository.get_stats.assert_called_once_with("Ab3xY9", "2026-05-16", "2026-05-16")

    def test_repository_queries_dynamodb_by_code_and_date_range(self):
        class FakeCondition:
            def __init__(self, value):
                self.value = value

            def __and__(self, other):
                return FakeCondition(("and", self.value, other.value))

        class FakeKey:
            def __init__(self, name: str):
                self.name = name

            def eq(self, value: str):
                return FakeCondition(("eq", self.name, value))

            def between(self, start: str, end: str):
                return FakeCondition(("between", self.name, start, end))

        table = MagicMock()
        table.query.return_value = {"Items": [{"codigo": "Ab3xY9", "fecha": "2026-05-16", "clicks": 2}]}
        dynamodb = MagicMock()
        dynamodb.Table.return_value = table

        repository = StatsRepository(table_name="url_stats", dynamodb_resource=dynamodb)
        fake_conditions = types.SimpleNamespace(Key=FakeKey)
        fake_dynamodb = types.SimpleNamespace(conditions=fake_conditions)
        fake_boto3 = types.SimpleNamespace(dynamodb=fake_dynamodb)

        with patch.dict(
            sys.modules,
            {
                "boto3": fake_boto3,
                "boto3.dynamodb": fake_dynamodb,
                "boto3.dynamodb.conditions": fake_conditions,
            },
        ):
            items = repository.get_stats("Ab3xY9", "2026-05-01", "2026-05-16")

        dynamodb.Table.assert_called_once_with("url_stats")
        table.query.assert_called_once()
        self.assertEqual(items, [{"codigo": "Ab3xY9", "fecha": "2026-05-16", "clicks": 2}])

    def test_non_get_method_returns_method_not_allowed(self):
        response = route(build_event(method="POST"))

        self.assertEqual(response["statusCode"], 405)
        self.assertEqual(parse_body(response), {"message": "Method not allowed"})


if __name__ == "__main__":
    unittest.main()
