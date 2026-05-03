import asyncio
from enum import Enum
from typing import Dict, Any, Optional

class MESIState(Enum):
    MODIFIED = "M"
    EXCLUSIVE = "E"
    SHARED = "S"
    INVALID = "I"

class CacheLine:
    def __init__(self, data: Any = None, state: MESIState = MESIState.INVALID):
        self.data = data
        self.state = state

class DistributedCacheNode:
    def __init__(self, node_id: str, messenger: Any):
        self.node_id = node_id
        self.messenger = messenger
        self.cache: Dict[str, CacheLine] = {}
        self.lock = asyncio.Lock()

    async def read(self, key: str) -> Any:
        async with self.lock:
            line = self.cache.get(key, CacheLine())
            
            if line.state == MESIState.INVALID:
                # Cache Miss: Need to fetch from other nodes or main memory
                data, state = await self.messenger.broadcast_read_request(key, self.node_id)
                line.data = data
                line.state = state
                self.cache[key] = line
            
            return line.data

    async def write(self, key: str, data: Any):
        async with self.lock:
            line = self.cache.get(key, CacheLine())
            
            if line.state == MESIState.MODIFIED:
                line.data = data
            elif line.state == MESIState.EXCLUSIVE:
                line.data = data
                line.state = MESIState.MODIFIED
            else:
                # Need to invalidate others
                await self.messenger.broadcast_invalidate(key, self.node_id)
                line.data = data
                line.state = MESIState.MODIFIED
            
            self.cache[key] = line

    async def handle_remote_read(self, key: str) -> (Any, MESIState):
        async with self.lock:
            line = self.cache.get(key)
            if not line or line.state == MESIState.INVALID:
                return None, MESIState.INVALID
            
            if line.state == MESIState.MODIFIED:
                # Downgrade to Shared and provide data
                line.state = MESIState.SHARED
                return line.data, MESIState.SHARED
            
            if line.state == MESIState.EXCLUSIVE:
                line.state = MESIState.SHARED
                return line.data, MESIState.SHARED
                
            return line.data, MESIState.SHARED

    async def handle_remote_invalidate(self, key: str):
        async with self.lock:
            if key in self.cache:
                self.cache[key].state = MESIState.INVALID
