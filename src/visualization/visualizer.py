import networkx as nx
import plotly.graph_objects as go
from streamlit_agraph import Node, Edge

def prepare_agraph_nodes_edges(node_data, edge_data):
    """Prepare nodes and edges for streamlit-agraph"""
    nodes = []
    edges = []
    
    # Create nodes
    for node in node_data:
        size = 10 + (node["count"] * 2)  # Size based on count
        nodes.append(Node(
            id=node["id"],
            label=node["label"],
            size=size,
            color=get_node_color(node["type"])
        ))
    
    # Create edges
    for edge in edge_data:
        edges.append(Edge(
            source=edge["source"],
            target=edge["target"],
            label=edge["predicate"],
            # Color or width could be based on confidence
            color=get_edge_color(edge["confidence"])
        ))
    
    return nodes, edges

def get_node_color(node_type):
    """Get color based on node type"""
    color_map = {
        "PERSON": "#FF5733",
        "ORG": "#33A8FF",
        "GPE": "#33FF57",
        "DATE": "#FF33A8",
        "SCIENTIFIC_CONCEPT": "#A833FF",
        "METHOD": "#FFD700",
        "UNKNOWN": "#AAAAAA"
    }
    return color_map.get(node_type, "#AAAAAA")

def get_edge_color(confidence):
    """Get edge color based on confidence"""
    # Higher confidence = darker color
    if confidence > 0.8:
        return "#000000"  # Black
    elif confidence > 0.6:
        return "#555555"  # Dark Gray
    else:
        return "#AAAAAA"  # Light Gray