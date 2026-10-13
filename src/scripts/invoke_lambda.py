"""Send an HTTP-like request to the Lambda function running locally in Docker.

The AWS Lambda base image ships the Runtime Interface Emulator (RIE). The RIE does
not speak plain HTTP like API Gateway does: it expects the raw Lambda *event*.
This script builds the same event API Gateway (HTTP API, payload v2) would send,
invokes the function and prints the response.

Usage:
    uv run python src/scripts/invoke_lambda.py GET /health
    uv run python src/scripts/invoke_lambda.py GET "/recommendations?session_id=s1&k=5"
    uv run python src/scripts/invoke_lambda.py POST /events --body-file event.json
"""

import argparse
import json
import sys
import time
import urllib.request
from pathlib import Path
from urllib.parse import urlsplit

DEFAULT_URL = "http://localhost:9000/2015-03-31/functions/function/invocations"


def build_event(method: str, path: str, body: str | None = None) -> dict:
    """Build an API Gateway HTTP API (payload format 2.0) event."""
    parts = urlsplit(path)
    return {
        "version": "2.0",
        "routeKey": "$default",
        "rawPath": parts.path,
        "rawQueryString": parts.query,
        "headers": {"content-type": "application/json", "host": "localhost"},
        "requestContext": {
            "accountId": "000000000000",
            "apiId": "local",
            "domainName": "localhost",
            "requestId": "local-request",
            "routeKey": "$default",
            "stage": "$default",
            "timeEpoch": int(time.time() * 1000),
            "http": {
                "method": method.upper(),
                "path": parts.path,
                "protocol": "HTTP/1.1",
                "sourceIp": "127.0.0.1",
                "userAgent": "invoke_lambda.py",
            },
        },
        "body": body,
        "isBase64Encoded": False,
    }


def invoke(event: dict, url: str = DEFAULT_URL) -> dict:
    request = urllib.request.Request(
        url,
        data=json.dumps(event).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=120) as response:
        return json.loads(response.read())


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("method", help="HTTP method, e.g. GET or POST")
    parser.add_argument("path", help='Path with optional query string, e.g. "/recommendations?session_id=s1"')
    body = parser.add_mutually_exclusive_group()
    body.add_argument("--body", help="JSON request body as a string")
    body.add_argument("--body-file", type=Path, help="File with the JSON request body (easier on Windows)")
    parser.add_argument("--url", default=DEFAULT_URL, help="Lambda RIE invocation URL")
    args = parser.parse_args()

    payload = args.body_file.read_text(encoding="utf-8") if args.body_file else args.body
    start = time.perf_counter()
    try:
        result = invoke(build_event(args.method, args.path, payload), args.url)
    except OSError as error:
        sys.exit(f"Could not reach the local Lambda at {args.url}: {error}\n"
                 "Is it running? docker compose --profile lambda up -d lambda")
    elapsed_ms = (time.perf_counter() - start) * 1000

    print(f"HTTP {result.get('statusCode')}  ({elapsed_ms:.0f} ms)")
    response_body = result.get("body") or ""
    try:
        print(json.dumps(json.loads(response_body), indent=2))
    except json.JSONDecodeError:
        print(response_body if response_body else json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
