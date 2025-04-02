import networkx as nx
from typing import List, Dict

class KnowledgeGraphBuilder:
    def __init__(self):
        """Initialize an empty knowledge graph"""
        self.graph = nx.DiGraph()
        
    def add_entities(self, entities: List[Dict]) -> None:
        """Add entities to the knowledge graph"""
        for entity in entities:  # این خط باید تو رفته باشد
            entity_id = self._normalize_text(entity["text"])
            if not self.graph.has_node(entity_id):
                self.graph.add_node(
                    entity_id,
                    label=entity["text"],
                    type=entity["label"],
                    count=1
                )
            else:
                # Update count for existing entity
                self.graph.nodes[entity_id]["count"] += 1
    
    def add_relations(self, relations: List[Dict], confidence_threshold: float = 0.5) -> None:
        """Add relations to the knowledge graph with confidence threshold"""
        for relation in relations:  # این خط باید تو رفته باشد
            if relation["confidence"] < confidence_threshold:
                continue
                
            subject_id = self._normalize_text(relation["subject"])
            object_id = self._normalize_text(relation["object"])
            
            # Ensure nodes exist
            if not self.graph.has_node(subject_id):
                self.graph.add_node(
                    subject_id,
                    label=relation["subject"],
                    type=relation["subject_type"],
                    count=1
                )
                
            if not self.graph.has_node(object_id):
                self.graph.add_node(
                    object_id,
                    label=relation["object"],
                    type=relation["object_type"],
                    count=1
                )
            
            # Add or update edge
            if self.graph.has_edge(subject_id, object_id):
                self.graph[subject_id][object_id]["weight"] += 1
                current_conf = self.graph[subject_id][object_id]["confidence"]
                count = self.graph[subject_id][object_id]["weight"]
                new_conf = (current_conf * (count - 1) + relation["confidence"]) / count
                self.graph[subject_id][object_id]["confidence"] = new_conf
            else:
                self.graph.add_edge(
                    subject_id,
                    object_id,
                    predicate=relation["predicate"],
                    weight=1,
                    confidence=relation["confidence"]
                )
    
    def get_graph(self) -> nx.DiGraph:
        """Return the knowledge graph"""
        return self.graph
    
    def get_node_data(self) -> List[Dict]:
        """Get node data for visualization"""
        nodes = []
        for node, data in self.graph.nodes(data=True):  # این خط باید تو رفته باشد
            nodes.append({
                "id": node,
                "label": data.get("label", node),
                "type": data.get("type", "Unknown"),
                "count": data.get("count", 1)
            })
        return nodes
    
    def get_edge_data(self) -> List[Dict]:
        """Get edge data for visualization"""
        edges = []
        for source, target, data in self.graph.edges(data=True):  # این خط باید تو رفته باشد
            edges.append({
                "source": source,
                "target": target,
                "predicate": data.get("predicate", "related_to"),
                "weight": data.get("weight", 1),
                "confidence": data.get("confidence", 0.5)
            })
        return edges
    
    def calculate_metrics(self) -> Dict:
        """Calculate graph metrics"""
        return {
            "num_entities": self.graph.number_of_nodes(),
            "num_relations": self.graph.number_of_edges(),
            "density": nx.density(self.graph),
            "connected_components": nx.number_connected_components(nx.Graph(self.graph))
        }
    
    def _normalize_text(self, text: str) -> str:
        """Normalize text for node IDs"""
        return text.lower().replace(" ", "_")