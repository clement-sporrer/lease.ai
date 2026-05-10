"""Standard API response envelope: {data, meta, errors}."""
from typing import Any


def ok(data: Any = None, meta: dict | None = None) -> dict:
    return {"data": data, "meta": meta or {}, "errors": []}


def page(items: list, page_num: int = 1, page_size: int = 20, total: int | None = None) -> dict:
    if total is None:
        total = len(items)
    return {
        "data": items,
        "meta": {"page": page_num, "page_size": page_size, "total": total},
        "errors": [],
    }


def err(code: str, message: str, details: dict | None = None) -> dict:
    return {
        "data": None,
        "meta": {},
        "errors": [{"code": code, "message": message, "details": details or {}}],
    }
