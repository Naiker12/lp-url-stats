import json
from datetime import UTC, date, datetime, timedelta
from http import HTTPStatus

from models.stats_model import DailyEntry, StatsResponse
from repositories.stats_repository import StatsRepository


DEFAULT_RANGE_DAYS = 30
DATE_FORMAT = "%Y-%m-%d"


class StatsService:
    def __init__(
        self,
        repository: StatsRepository | None = None,
        today: date | None = None,
    ):
        self.repository = repository or StatsRepository()
        self.today = today or datetime.now(UTC).date()

    def get_stats(self, code: str | None, from_date: str | None = None, to_date: str | None = None) -> dict:
        if not code:
            return self._response(HTTPStatus.BAD_REQUEST, {"message": "codigo is required"})

        date_range = self._resolve_date_range(from_date, to_date)
        if date_range is None:
            return self._response(
                HTTPStatus.BAD_REQUEST,
                {"message": "from and to must use YYYY-MM-DD and from must be less than or equal to to"},
            )

        if not self.repository.url_exists(code):
            return self._response(HTTPStatus.NOT_FOUND, {"message": "codigo not found", "code": code})

        start_date, end_date = date_range
        items = self.repository.get_stats(code, start_date.isoformat(), end_date.isoformat())
        daily = [
            DailyEntry(fecha=item["fecha"], clicks=int(item.get("clicks", 0)))
            for item in items
        ]
        total_clicks = sum(entry.clicks for entry in daily)

        return self._response(
            HTTPStatus.OK,
            StatsResponse(codigo=code, total_clicks=total_clicks, daily=daily).to_dict(),
        )

    def _resolve_date_range(self, from_date: str | None, to_date: str | None) -> tuple[date, date] | None:
        if not from_date and not to_date:
            return self.today - timedelta(days=DEFAULT_RANGE_DAYS - 1), self.today

        if not from_date or not to_date:
            return None

        start_date = self._parse_date(from_date)
        end_date = self._parse_date(to_date)

        if start_date is None or end_date is None or start_date > end_date:
            return None

        return start_date, end_date

    @staticmethod
    def _parse_date(value: str) -> date | None:
        try:
            return datetime.strptime(value, DATE_FORMAT).date()
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _response(status_code: HTTPStatus, payload: dict) -> dict:
        return {
            "statusCode": int(status_code),
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
            },
            "body": json.dumps(payload),
        }
