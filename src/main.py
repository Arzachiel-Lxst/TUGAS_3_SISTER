import os
import asyncio
from src.nodes.base_node import BaseNode
from dotenv import load_dotenv

load_dotenv()

node_id = os.getenv("NODE_ID", "node1")
cluster_nodes_raw = os.getenv("CLUSTER_NODES", "node1:8000,node2:8000,node3:8000")

peer_addresses = {}
for item in cluster_nodes_raw.split(","):
    nid, addr = item.split(":")
    if nid != node_id:
        peer_addresses[nid] = f"http://{addr}"

node = BaseNode(node_id, peer_addresses)
app = node.app

@app.on_event("startup")
async def startup_event():
    await node.start()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
