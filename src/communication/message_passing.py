import aiohttp
import asyncio
import json
import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class Messenger:
    def __init__(self, node_id: str, peer_addresses: Dict[str, str]):
        self.node_id = node_id
        self.peer_addresses = peer_addresses # node_id -> "http://host:port"
        self.session: Optional[aiohttp.ClientSession] = None

    async def start(self):
        self.session = aiohttp.ClientSession()

    async def stop(self):
        if self.session:
            await self.session.close()

    async def send_message(self, target_id: str, endpoint: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        if target_id not in self.peer_addresses:
            return None
        
        url = f"{self.peer_addresses[target_id]}/{endpoint}"
        try:
            async with self.session.post(url, json=data, timeout=2) as response:
                if response.status == 200:
                    return await response.json()
        except Exception as e:
            logger.error(f"Error sending message to {target_id}: {e}")
        return None

    async def broadcast(self, endpoint: str, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        tasks = [self.send_message(peer_id, endpoint, data) for peer_id in self.peer_addresses]
        results = await asyncio.gather(*tasks)
        return [r for r in results if r is not None]

class FailureDetector:
    def __init__(self, messenger: Messenger, peers: List[str], interval: float = 1.0):
        self.messenger = messenger
        self.peers = peers
        self.interval = interval
        self.alive_nodes = set(peers)
        self.running = False

    async def start(self):
        self.running = True
        while self.running:
            for peer in self.peers:
                res = await self.messenger.send_message(peer, "health", {"from": self.messenger.node_id})
                if res:
                    self.alive_nodes.add(peer)
                else:
                    if peer in self.alive_nodes:
                        logger.warning(f"Node {peer} detected as FAILED")
                        self.alive_nodes.remove(peer)
            await asyncio.sleep(self.interval)

    def is_alive(self, node_id: str) -> bool:
        return node_id in self.alive_nodes
