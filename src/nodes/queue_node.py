import hashlib
import bisect
import asyncio
import json
import os
from typing import List, Dict, Any, Optional

class ConsistentHash:
    def __init__(self, nodes: List[str] = None, replicas: int = 3):
        self.replicas = replicas
        self.ring = {}
        self.sorted_keys = []
        if nodes:
            for node in nodes:
                self.add_node(node)

    def _hash(self, key: str) -> int:
        return int(hashlib.md5(key.encode()).hexdigest(), 16)

    def add_node(self, node: str):
        for i in range(self.replicas):
            key = self._hash(f"{node}:{i}")
            self.ring[key] = node
            bisect.insort(self.sorted_keys, key)

    def remove_node(self, node: str):
        for i in range(self.replicas):
            key = self._hash(f"{node}:{i}")
            del self.ring[key]
            self.sorted_keys.remove(key)

    def get_node(self, key: str) -> str:
        if not self.ring:
            return None
        h = self._hash(key)
        idx = bisect.bisect(self.sorted_keys, h)
        if idx == len(self.sorted_keys):
            idx = 0
        return self.ring[self.sorted_keys[idx]]

class DistributedQueue:
    def __init__(self, node_id: str, storage_path: str = "/tmp/queue_data"):
        self.node_id = node_id
        self.storage_path = storage_path
        os.makedirs(storage_path, exist_ok=True)
        self.queue = []
        self.lock = asyncio.Lock()
        self._load_persistence()

    def _load_persistence(self):
        file_path = os.path.join(self.storage_path, f"{self.node_id}_queue.json")
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                self.queue = json.load(f)

    async def _save_persistence(self):
        file_path = os.path.join(self.storage_path, f"{self.node_id}_queue.json")
        with open(file_path, 'w') as f:
            json.dump(self.queue, f)

    async def enqueue(self, message: Any):
        async with self.lock:
            self.queue.append({
                "id": hashlib.sha256(str(message).encode()).hexdigest(),
                "data": message,
                "timestamp": asyncio.get_event_loop().time()
            })
            await self._save_persistence()
            return True

    async def dequeue(self) -> Optional[Any]:
        async with self.lock:
            if not self.queue:
                return None
            msg = self.queue.pop(0)
            await self._save_persistence()
            return msg
