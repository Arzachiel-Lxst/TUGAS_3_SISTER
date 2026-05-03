import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    NODE_ID = os.getenv("NODE_ID", "node1")
    REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
    CLUSTER_NODES = os.getenv("CLUSTER_NODES", "node1:8001,node2:8002,node3:8003")
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

    @classmethod
    def get_peer_addresses(cls):
        peer_addresses = {}
        for item in cls.CLUSTER_NODES.split(","):
            nid, addr = item.split(":")
            if nid != cls.NODE_ID:
                peer_addresses[nid] = f"http://{addr}"
        return peer_addresses
