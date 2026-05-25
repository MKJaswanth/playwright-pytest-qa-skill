# Cleanup Reference

Full implementation of the two cleanup utility files.

---

## utils/cleanup_registry.py

```python
from __future__ import annotations
import threading
from typing import Any

_lock = threading.Lock()
_registry: list[dict[str, Any]] = []

def register(resource_type: str, resource_id: Any) -> None:
    """Call immediately after creating any test resource."""
    with _lock:
        _registry.append({"type": resource_type, "id": str(resource_id)})

def pop_all() -> list[dict[str, Any]]:
    """Drain and return full registry — called by autoclean fixture."""
    with _lock:
        items = list(_registry)
        _registry.clear()
        return items

def clear() -> None:
    with _lock:
        _registry.clear()
```

---

## utils/cleanup_client.py

```python
from __future__ import annotations
import logging
import requests
from config.config import Config

logger = logging.getLogger(__name__)

RESOURCE_DELETE_PATHS: dict[str, str] = {
    "role":        "/roles/{id}",
    "user":        "/users/{id}",
    "permission":  "/permissions/{id}",
    "country":     "/masters/countries/{id}",
    "state":       "/masters/states/{id}",
    "city":        "/masters/cities/{id}",
    "lead_source": "/masters/lead-sources/{id}",
    "team":        "/masters/teams/{id}",
    "project":     "/masters/projects/{id}",
    "lead":        "/leads/{id}",
}

BULK_CLEANUP_PATH = "/api/test/cleanup"


class CleanupClient:
    def __init__(self):
        self.base    = Config.API_BASE_URL
        self.token   = Config.SUPER_ADMIN_TOKEN
        self.mode    = getattr(Config, "CLEANUP_MODE", "per_resource")
        self.timeout = 15

    def delete_all(self, items: list[dict]) -> None:
        if not items:
            return
        logger.info("[Cleanup] %d resource(s) to delete", len(items))
        if self.mode == "bulk":
            self._bulk_delete(items)
        else:
            for item in items:
                self._single_delete(item["type"], item["id"])

    def _headers(self):
        return {
            "Content-Type":  "application/json",
            "Authorization": f"Bearer {self.token}",
        }

    def _bulk_delete(self, items):
        try:
            resp = requests.post(
                f"{self.base}{BULK_CLEANUP_PATH}",
                json=items, headers=self._headers(), timeout=self.timeout)
            if resp.status_code not in (200, 204):
                logger.warning("[Cleanup] Bulk delete %s: %s", resp.status_code, resp.text[:200])
        except requests.RequestException as exc:
            logger.error("[Cleanup] Bulk delete failed: %s", exc)

    def _single_delete(self, resource_type, resource_id):
        path_template = RESOURCE_DELETE_PATHS.get(resource_type)
        if not path_template:
            logger.warning("[Cleanup] Unknown type '%s' id=%s", resource_type, resource_id)
            return
        url = f"{self.base}{path_template.format(id=resource_id)}"
        try:
            resp = requests.delete(url, headers=self._headers(), timeout=self.timeout)
            logger.info("[Cleanup] DELETE %s → %s", url, resp.status_code)
        except requests.RequestException as exc:
            logger.error("[Cleanup] DELETE %s failed: %s", url, exc)
```
