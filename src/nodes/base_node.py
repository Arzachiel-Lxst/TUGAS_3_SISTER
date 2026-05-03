import asyncio
import os
from fastapi import FastAPI, Request
from src.communication.message_passing import Messenger, FailureDetector
from src.consensus.raft import RaftNode
from src.nodes.lock_manager import DistributedLockManager
from src.nodes.queue_node import DistributedQueue
from src.nodes.cache_node import DistributedCacheNode
from src.utils.metrics import MetricsCollector

class BaseNode:
    def __init__(self, node_id: str, peer_addresses: dict):
        self.node_id = node_id
        self.peer_addresses = peer_addresses
        self.app = FastAPI(title=f"Node {node_id}")
        
        self.messenger = Messenger(node_id, peer_addresses)
        self.metrics = MetricsCollector()
        
        # Initialize components
        self.raft = RaftNode(node_id, list(peer_addresses.keys()), self.messenger)
        self.lock_manager = DistributedLockManager(self.raft)
        self.queue = DistributedQueue(node_id)
        self.cache = DistributedCacheNode(node_id, self.messenger)
        self.failure_detector = FailureDetector(self.messenger, list(peer_addresses.keys()))
        
        self.setup_routes()

    def setup_routes(self):
        @self.app.get("/health")
        async def health():
            return {"status": "ok", "node_id": self.node_id}

        @self.app.post("/raft/append_entries")
        async def append_entries(req: Request):
            data = await req.json()
            return await self.raft.handle_append_entries(**data)

        @self.app.post("/raft/request_vote")
        async def request_vote(req: Request):
            data = await req.json()
            return await self.raft.handle_request_vote(**data)

        @self.app.get("/metrics")
        async def get_metrics():
            return self.metrics.get_report()

        # Add more routes for Lock, Queue, and Cache...

    async def start(self):
        await self.messenger.start()
        asyncio.create_task(self.raft.run())
        asyncio.create_task(self.failure_detector.start())
        # Start uvicorn server here or externally
