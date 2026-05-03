from src.nodes.queue_node import ConsistentHash

def test_consistent_hash_distribution():
    nodes = ["node1", "node2", "node3"]
    ch = ConsistentHash(nodes)
    
    # Test mapping
    node_a = ch.get_node("key1")
    node_b = ch.get_node("key2")
    
    assert node_a in nodes
    assert node_b in nodes

def test_node_removal():
    nodes = ["node1", "node2", "node3"]
    ch = ConsistentHash(nodes)
    
    ch.remove_node("node2")
    for i in range(100):
        assert ch.get_node(f"key{i}") != "node2"
