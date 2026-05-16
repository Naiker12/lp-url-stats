from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class DailyEntry:
    fecha: str
    clicks: int


@dataclass(frozen=True)
class StatsResponse:
    codigo: str
    total_clicks: int
    daily: list[DailyEntry]

    def to_dict(self) -> dict:
        return asdict(self)
