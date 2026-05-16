import json
from http import HTTPStatus

from services.stats_service import StatsService


def route(event):
    method = event.get("httpMethod") or event.get("requestContext", {}).get("http", {}).get("method")

    if method == "GET":
        code = (event.get("pathParameters") or {}).get("codigo")
        query_params = event.get("queryStringParameters") or {}
        return StatsService().get_stats(
            code,
            from_date=query_params.get("from"),
            to_date=query_params.get("to"),
        )

    if method == "OPTIONS":
        return {
            "statusCode": HTTPStatus.NO_CONTENT,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Content-Type",
                "Access-Control-Allow-Methods": "GET,OPTIONS",
            },
        }

    return {
        "statusCode": HTTPStatus.METHOD_NOT_ALLOWED,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
        },
        "body": json.dumps({"message": "Method not allowed"}),
    }
