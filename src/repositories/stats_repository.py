import os
from functools import cached_property


class StatsRepository:
    def __init__(self, table_name: str | None = None, dynamodb_resource=None):
        self.table_name = table_name or os.environ["STATS_TABLE_NAME"]
        self._dynamodb_resource = dynamodb_resource

    @cached_property
    def table(self):
        if self._dynamodb_resource:
            return self._dynamodb_resource.Table(self.table_name)

        import boto3

        return boto3.resource("dynamodb").Table(self.table_name)

    def get_stats(self, code: str, from_date: str, to_date: str) -> list[dict]:
        from boto3.dynamodb.conditions import Key

        response = self.table.query(
            KeyConditionExpression=Key("codigo").eq(code) & Key("fecha").between(from_date, to_date)
        )
        return response.get("Items", [])
