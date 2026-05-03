import asyncio
import random
import time
import logging
from enum import Enum
from typing import List, Dict, Any, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class State(Enum):
    FOLLOWER = 1
    CANDIDATE = 2
    LEADER = 3

class RaftNode:
    def __init__(self, node_id: str, peers: List[str], messenger: Any):
        self.node_id = node_id
        self.peers = peers
        self.messenger = messenger
        
        self.state = State.FOLLOWER
        self.current_term = 0
        self.voted_for = None
        self.log = []
        
        self.commit_index = 0
        self.last_applied = 0
        
        self.next_index = {}
        self.match_index = {}
        
        self.election_timeout = random.uniform(1.5, 3.0)
        self.last_heartbeat = time.time()
        
        self.lock = asyncio.Lock()
        self.running = True

    async def run(self):
        while self.running:
            if self.state == State.FOLLOWER or self.state == State.CANDIDATE:
                if time.time() - self.last_heartbeat > self.election_timeout:
                    await self.start_election()
            elif self.state == State.LEADER:
                await self.send_heartbeats()
            await asyncio.sleep(0.1)

    async def start_election(self):
        async with self.lock:
            self.state = State.CANDIDATE
            self.current_term += 1
            self.voted_for = self.node_id
            self.last_heartbeat = time.time()
            self.election_timeout = random.uniform(1.5, 3.0)
            
            votes = 1
            logger.info(f"Node {self.node_id} starting election for term {self.current_term}")
            
            for peer in self.peers:
                asyncio.create_task(self.request_vote(peer))

    async def request_vote(self, peer: str):
        # Placeholder for actual network call
        # In real implementation, this would use self.messenger
        pass

    async def handle_request_vote(self, term: int, candidate_id: str, last_log_index: int, last_log_term: int):
        async with self.lock:
            if term > self.current_term:
                self.current_term = term
                self.state = State.FOLLOWER
                self.voted_for = None
            
            if term == self.current_term and (self.voted_for is None or self.voted_for == candidate_id):
                # Simplified log check
                self.voted_for = candidate_id
                self.last_heartbeat = time.time()
                return True, self.current_term
            return False, self.current_term

    async def send_heartbeats(self):
        for peer in self.peers:
            # Send AppendEntries with empty log
            pass

    async def handle_append_entries(self, term: int, leader_id: str, prev_log_index: int, prev_log_term: int, entries: List, leader_commit: int):
        async with self.lock:
            if term >= self.current_term:
                self.current_term = term
                self.state = State.FOLLOWER
                self.last_heartbeat = time.time()
                return True, self.current_term
            return False, self.current_term
