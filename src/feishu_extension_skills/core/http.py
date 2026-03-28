from __future__ import annotations

from typing import Any, Mapping

import httpx

from .config import AppConfig
from .errors import FeishuAPIError


class HttpClient:
    def __init__(
        self,
        *,
        base_url: str,
        timeout_seconds: float = 10.0,
        headers: Mapping[str, str] | None = None,
        transport: httpx.BaseTransport | None = None,
    ) -> None:
        self._client = httpx.Client(
            base_url=base_url.rstrip("/"),
            timeout=timeout_seconds,
            headers=dict(headers or {}),
            transport=transport,
        )

    def close(self) -> None:
        self._client.close()

    def request(
        self,
        method: str,
        path: str,
        *,
        headers: Mapping[str, str] | None = None,
        params: Mapping[str, Any] | None = None,
        json: Any | None = None,
    ) -> httpx.Response:
        try:
            response = self._client.request(
                method,
                path,
                headers=dict(headers or {}),
                params=params,
                json=json,
            )
        except httpx.RequestError as exc:
            raise FeishuAPIError(
                code="http_error",
                message=str(exc),
                details={"method": method, "path": path},
            ) from exc
        return response

    def request_json(
        self,
        method: str,
        path: str,
        *,
        headers: Mapping[str, str] | None = None,
        params: Mapping[str, Any] | None = None,
        json: Any | None = None,
    ) -> dict[str, Any]:
        response = self.request(method, path, headers=headers, params=params, json=json)
        payload = _parse_json(response)
        _raise_for_error(response, payload)
        return payload


def build_http_client(
    config: AppConfig | None = None,
    *,
    base_url: str | None = None,
    timeout_seconds: float | None = None,
    headers: Mapping[str, str] | None = None,
    transport: httpx.BaseTransport | None = None,
) -> HttpClient:
    resolved_base_url = base_url
    resolved_timeout_seconds = timeout_seconds
    if config is not None:
        resolved_base_url = config.base_url
        resolved_timeout_seconds = config.timeout_seconds
    return HttpClient(
        base_url=(resolved_base_url or "https://open.feishu.cn").rstrip("/"),
        timeout_seconds=resolved_timeout_seconds or 10.0,
        headers=headers,
        transport=transport,
    )


def _parse_json(response: httpx.Response) -> dict[str, Any]:
    try:
        payload = response.json()
    except ValueError as exc:
        raise FeishuAPIError(
            code="invalid_json",
            message="feishu response is not valid JSON",
            status_code=response.status_code,
            details={"response_text": response.text},
        ) from exc
    if not isinstance(payload, dict):
        raise FeishuAPIError(
            code="invalid_json",
            message="feishu response must be a JSON object",
            status_code=response.status_code,
            details={"response_type": type(payload).__name__},
        )
    return payload


def _raise_for_error(response: httpx.Response, payload: dict[str, Any]) -> None:
    status_code = response.status_code
    request_id = (
        response.headers.get("x-tt-logid")
        or response.headers.get("x-request-id")
        or payload.get("request_id")
    )
    code = payload.get("code")
    if status_code < 200 or status_code >= 300:
        raise FeishuAPIError(
            code=str(code or "http_error"),
            message=str(payload.get("msg") or payload.get("message") or response.reason_phrase),
            status_code=status_code,
            request_id=request_id,
            details=payload,
        )
    if code not in (None, 0, "0"):
        raise FeishuAPIError(
            code=str(code),
            message=str(payload.get("msg") or payload.get("message") or "feishu api error"),
            status_code=status_code,
            request_id=request_id,
            details=payload,
        )
