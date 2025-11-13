# proxy_balancer.py
import time
from typing import Dict, Optional

from proxy_config import (
    get_pool_size, get_current_index, get_current_proxy, rotate_proxy
)


class ProxyBalancer:
    def __init__(self):
        n = get_pool_size()
        # usage считаем по индексам реального пула
        self.proxy_usage_count = {i: 0 for i in range(n)}
        self.user_proxy_index = {}  # user_id -> pool_index
        self.last_reset_time = time.time()
        self.reset_interval = 3600  # сек

    def _tick_reset(self):
        if time.time() - self.last_reset_time > self.reset_interval:
            n = get_pool_size()
            self.proxy_usage_count = {i: 0 for i in range(n)}
            self.last_reset_time = time.time()

    def _mark_used(self, pool_index: int):
        # безопасно инкрементим (индекс может поменяться после ресайза)
        if pool_index not in self.proxy_usage_count:
            self.proxy_usage_count[pool_index] = 0
        self.proxy_usage_count[pool_index] += 1

    def get_proxy_for_user(self, user_id: str) -> Dict:
        self._tick_reset()
        if user_id in self.user_proxy_index:
            idx = self.user_proxy_index[user_id]
            self._mark_used(idx)
            # вернуть актуальный прокси на этом индексе
            # (если пул перетасовали/пересобрали — поведение детерминированно в рамках жизни процесса)
            return get_current_proxy() if idx == get_current_index() else rotate_proxy()

        # иначе — отдаём текущий и закрепляем
        idx = get_current_index()
        self.user_proxy_index[user_id] = idx
        self._mark_used(idx)
        return get_current_proxy()

    def get_proxy_for_store(self, store_tag: str) -> Dict:
        """Для магазинов просто крутим round-robin."""
        self._tick_reset()
        p = rotate_proxy()
        self._mark_used(get_current_index())
        return p

    def get_balanced_proxy(self, identifier: Optional[str] = None) -> Dict:
        if identifier and "@" in identifier:
            return self.get_proxy_for_user(identifier)  # выглядит как email → закрепляем
        return self.get_proxy_for_store(identifier or "generic")

    def get_stats(self) -> Dict:
        total = sum(self.proxy_usage_count.values())
        return {
            "total_requests": total,
            "pool_size": get_pool_size(),
            "usage": self.proxy_usage_count,
            "time_to_reset": max(0, self.reset_interval - (time.time() - self.last_reset_time)),
        }


proxy_balancer = ProxyBalancer()
