import time
from typing import Any

import aiohttp
import requests

from .enums import API_URL, REPORT_URL
from .exceptions import (
    FssaAnnouncementException,
    FssaDocumentException,
    FssaEventException,
    FssaLogException,
)
from .objects import (
    Announcement,
    Document,
    Event,
    InclusionProof,
    LogEntry,
    LogKey,
    LogStatus,
)

DEFAULT_TIMEOUT = 30.0
ALLOWED_CODES = (200, 201, 202, 204)


def _build_url(route: str) -> str:
    """把相對路徑接到 API 主機，絕對 URL 則原樣回傳。"""
    if route.startswith(("http://", "https://")):
        return route
    return f"{API_URL.rstrip('/')}/{route.lstrip('/')}"


def _log_url(route: str) -> str:
    return f"{REPORT_URL.rstrip('/')}/{route.lstrip('/')}"


class AsyncClient:
    """以 aiohttp 實作的非同步 client。"""

    def __init__(self, cache: bool = False, timeout: float = DEFAULT_TIMEOUT):
        self._session: aiohttp.ClientSession | None = None
        self._update_time: float | None = None
        self._cache = cache
        self._timeout = timeout

    @property
    def session(self) -> aiohttp.ClientSession | None:
        return self._session

    @property
    def closed(self) -> bool:
        return self._session is None or self._session.closed

    @property
    def update_time(self) -> float | None:
        return self._update_time

    async def _init(self, *, force: bool = False) -> None:
        if not self.closed and not force:
            return
        if self._session is not None:
            await self.close()
        self._session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=self._timeout)
        )
        self._update_time = time.time()

    def _cleanup(self) -> None:
        self._session = None
        self._update_time = None

    async def close(self) -> None:
        if self._session is not None and not self._session.closed:
            await self._session.close()
        self._cleanup()

    async def __aenter__(self) -> "AsyncClient":
        await self._init()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        await self.close()

    async def _send_request(self, route: str, **kwargs: Any) -> Any:
        await self._init()
        session = self._session
        if session is None:
            raise RuntimeError("Session was not initialised")
        async with session.get(_build_url(route), **kwargs) as resp:
            if resp.status not in ALLOWED_CODES:
                raise aiohttp.ClientResponseError(
                    resp.request_info,
                    resp.history,
                    status=resp.status,
                    message=await resp.text(),
                )
            if resp.status == 204:
                return None
            return await resp.json()

    async def get_announcements(self) -> list[Announcement]:
        try:
            payload = await self._send_request("/announcements")
            return [Announcement.from_payload(item) for item in payload or []]
        except aiohttp.ClientResponseError as exc:
            raise FssaAnnouncementException("Unable to get announcements") from exc

    async def get_events(self) -> list[Event]:
        try:
            payload = await self._send_request("/events")
            return [Event.from_payload(item) for item in payload or []]
        except aiohttp.ClientResponseError as exc:
            raise FssaEventException("Unable to get events") from exc

    async def get_documents(self) -> list[Document]:
        try:
            payload = await self._send_request("/documents")
            return [Document.from_payload(item) for item in payload or []]
        except aiohttp.ClientResponseError as exc:
            raise FssaDocumentException("Unable to get documents") from exc

    # ---- 透明日誌 (report.fssakh.org) --------------------------------

    async def _log_request(self, route: str, **kwargs: Any) -> Any:
        try:
            return await self._send_request(_log_url(route), **kwargs)
        except aiohttp.ClientResponseError as exc:
            raise FssaLogException(f"Unable to get log data from {route}") from exc

    async def get_log_size(self) -> dict:
        return await self._log_request("/log/size")

    async def get_log_stats(self) -> LogStatus:
        payload = await self._log_request("/log/stats")
        return LogStatus.from_payload(payload)

    async def get_log_keys(self) -> list[LogKey]:
        payload = await self._log_request("/log/keys")
        keys = payload.get("keys", []) if isinstance(payload, dict) else payload
        return [LogKey.from_payload(item) for item in keys or []]

    async def get_log_entries(
        self, from_index: int = 0, limit: int = 100
    ) -> list[LogEntry]:
        """取得日誌條目。索引從 1 開始，伺服器會把 0 視為 1。"""
        if from_index < 0 or limit <= 0:
            raise ValueError("Expected from_index >= 0 and limit > 0")
        payload = await self._log_request(
            "/log/entries", params={"from": from_index, "limit": limit}
        )
        entries = payload.get("entries", []) if isinstance(payload, dict) else payload
        return [LogEntry.from_payload(item) for item in entries or []]

    async def get_log_entry(self, idx: int) -> LogEntry:
        if idx < 1:
            raise ValueError("idx must be >= 1")
        payload = await self._log_request(f"/log/entry/{idx}")
        return LogEntry.from_payload(payload)

    async def get_log_consistency(self, from_size: int, to_size: int) -> dict:
        if from_size < 1 or to_size < from_size:
            raise ValueError("Expected 1 <= from_size <= to_size")
        return await self._log_request(
            "/log/consistency", params={"from": from_size, "to": to_size}
        )

    async def get_log_inclusion(
        self, idx: int, tree_size: int | None = None
    ) -> InclusionProof:
        """取得 Merkle inclusion proof。idx 從 1 開始。"""
        if idx < 1:
            raise ValueError("idx must be >= 1")
        params: dict[str, int] = {}
        if tree_size is not None:
            params["tree_size"] = tree_size
        payload = await self._log_request(f"/log/proof/{idx}", params=params or None)
        return InclusionProof.from_payload(payload)


class SyncClient:
    """以 requests 實作的同步 client，方法與 :class:`AsyncClient` 對應。"""

    def __init__(self, cache: bool = False, timeout: float = DEFAULT_TIMEOUT):
        self._session: requests.Session | None = None
        self._update_time: float | None = None
        self._cache = cache
        self._timeout = timeout

    @property
    def session(self) -> requests.Session | None:
        return self._session

    @property
    def closed(self) -> bool:
        return self._session is None

    @property
    def update_time(self) -> float | None:
        return self._update_time

    def _init(self, *, force: bool = False) -> None:
        if not self.closed and not force:
            return
        if self._session is not None:
            self.close()
        self._session = requests.Session()
        self._update_time = time.time()

    def close(self) -> None:
        if self._session is not None:
            self._session.close()
        self._session = None
        self._update_time = None

    def __enter__(self) -> "SyncClient":
        self._init()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.close()

    def _send_request(self, route: str, **kwargs: Any) -> Any:
        self._init()
        session = self._session
        if session is None:
            raise RuntimeError("Session was not initialised")
        resp = session.get(_build_url(route), timeout=self._timeout, **kwargs)
        if resp.status_code not in ALLOWED_CODES:
            raise requests.HTTPError(
                f"{resp.status_code} {resp.reason}: {resp.text}", response=resp
            )
        if resp.status_code == 204:
            return None
        return resp.json()

    def get_announcements(self) -> list[Announcement]:
        try:
            payload = self._send_request("/announcements")
            return [Announcement.from_payload(item) for item in payload or []]
        except requests.HTTPError as exc:
            raise FssaAnnouncementException("Unable to get announcements") from exc

    def get_events(self) -> list[Event]:
        try:
            payload = self._send_request("/events")
            return [Event.from_payload(item) for item in payload or []]
        except requests.HTTPError as exc:
            raise FssaEventException("Unable to get events") from exc

    def get_documents(self) -> list[Document]:
        try:
            payload = self._send_request("/documents")
            return [Document.from_payload(item) for item in payload or []]
        except requests.HTTPError as exc:
            raise FssaDocumentException("Unable to get documents") from exc

    # ---- 透明日誌 (report.fssakh.org) --------------------------------

    def _log_request(self, route: str, **kwargs: Any) -> Any:
        try:
            return self._send_request(_log_url(route), **kwargs)
        except requests.HTTPError as exc:
            raise FssaLogException(f"Unable to get log data from {route}") from exc

    def get_log_size(self) -> dict:
        return self._log_request("/log/size")

    def get_log_stats(self) -> LogStatus:
        payload = self._log_request("/log/stats")
        return LogStatus.from_payload(payload)

    def get_log_keys(self) -> list[LogKey]:
        payload = self._log_request("/log/keys")
        keys = payload.get("keys", []) if isinstance(payload, dict) else payload
        return [LogKey.from_payload(item) for item in keys or []]

    def get_log_entries(self, from_index: int = 0, limit: int = 100) -> list[LogEntry]:
        if from_index < 0 or limit <= 0:
            raise ValueError("Expected from_index >= 0 and limit > 0")
        payload = self._log_request(
            "/log/entries", params={"from": from_index, "limit": limit}
        )
        entries = payload.get("entries", []) if isinstance(payload, dict) else payload
        return [LogEntry.from_payload(item) for item in entries or []]

    def get_log_entry(self, idx: int) -> LogEntry:
        if idx < 1:
            raise ValueError("idx must be >= 1")
        payload = self._log_request(f"/log/entry/{idx}")
        return LogEntry.from_payload(payload)

    def get_log_consistency(self, from_size: int, to_size: int) -> dict:
        if from_size < 1 or to_size < from_size:
            raise ValueError("Expected 1 <= from_size <= to_size")
        return self._log_request(
            "/log/consistency", params={"from": from_size, "to": to_size}
        )

    def get_log_inclusion(
        self, idx: int, tree_size: int | None = None
    ) -> InclusionProof:
        if idx < 1:
            raise ValueError("idx must be >= 1")
        params: dict[str, int] = {}
        if tree_size is not None:
            params["tree_size"] = tree_size
        payload = self._log_request(f"/log/proof/{idx}", params=params or None)
        return InclusionProof.from_payload(payload)

