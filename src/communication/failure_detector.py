import asyncio
import logging
from typing import List, Set

logger = logging.getLogger(__name__)

class FailureDetector:
    def __init__(self, messenger, peers: List[str], interval: float = 1.0):
        self.messenger = messenger
        self.peers = peers
        self.interval = interval
        self.alive_nodes: Set[str] = set(peers)
        self.running = False

    async def start(self):
        self.running = True
        while self.running:
            for peer in self.peers:
                res = await self.messenger.send_message(peer, "health", {"from": self.messenger.node_id})
                if res:
                    if peer not in self.alive_nodes:
                        logger.info(f"Node {peer} is BACK ONLINE")
                        self.alive_nodes.add(peer)
                else:
                    if peer in self.alive_nodes:
                        logger.warning(f"Node {peer} detected as FAILED")
                        self.alive_nodes.remove(peer)
            await asyncio.sleep(self.interval)

    def is_alive(self, node_id: str) -> bool:
        return node_id in self.alive_nodes
