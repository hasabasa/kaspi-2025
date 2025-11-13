# proxy_config.py
import os
import random
from typing import Dict, List

INSTANCE_INDEX = int(os.getenv("INSTANCE_INDEX", "0"))
INSTANCE_COUNT = int(os.getenv("INSTANCE_COUNT", "1"))

# Базовая запись провайдера + диапазон портов
PROVIDER = {
    'host': 'dc.decodo.com',
    'user': 'spzj0ldhjp',
    'pass': 'snOe90h0g~Y3jWChqe',
    'from': 10001,
    'to':   10999,   # включительно
}

def expand_pool(p: Dict) -> List[Dict]:
    start, end = int(p['from']), int(p['to'])
    return [
        {'host': p['host'], 'port': port, 'user': p['user'], 'pass': p['pass']}
        for port in range(start, end + 1)
    ]

def shard_slice(items: List[Dict], shard_idx: int, shard_cnt: int) -> List[Dict]:
    if shard_cnt <= 1:
        return items
    return [p for i, p in enumerate(items) if i % shard_cnt == shard_idx]

# 1) Полный пул (200 портов)
FULL_PROXY_POOL: List[Dict] = expand_pool(PROVIDER)

# 2) Срез пулa для текущего шарда
PROXY_POOL: List[Dict] = shard_slice(FULL_PROXY_POOL, INSTANCE_INDEX, INSTANCE_COUNT)

# На всякий случай перетасуем, чтобы разные шарды начинали с разных IP
random.shuffle(PROXY_POOL)

# Глобальный индекс текущего прокси в пуле шарда
_CURRENT_IDX = 0

def _ensure_pool():
    if not PROXY_POOL:
        raise RuntimeError("PROXY_POOL пуст. Проверь диапазон портов и переменные INSTANCE_INDEX/COUNT.")

def get_current_proxy() -> Dict:
    _ensure_pool()
    return PROXY_POOL[_CURRENT_IDX % len(PROXY_POOL)]

def rotate_proxy() -> Dict:
    global _CURRENT_IDX
    _ensure_pool()
    _CURRENT_IDX = (_CURRENT_IDX + 1) % len(PROXY_POOL)
    return PROXY_POOL[_CURRENT_IDX]

def get_current_index() -> int:
    return _CURRENT_IDX

def get_pool_size() -> int:
    return len(PROXY_POOL)

def get_proxy_config(proxy: Dict | None = None) -> Dict[str, str]:
    """Конфиг для aiohttp/requests."""
    if not is_proxy_enabled():
        return {}
    if proxy is None:
        proxy = get_current_proxy()
    auth = f"{proxy['user']}:{proxy['pass']}@"
    proxy_url = f"http://{auth}{proxy['host']}:{proxy['port']}"
    return {'http': proxy_url, 'https': proxy_url}

def is_proxy_enabled() -> bool:
    return os.getenv('USE_PROXY', 'true').lower() == 'true'
