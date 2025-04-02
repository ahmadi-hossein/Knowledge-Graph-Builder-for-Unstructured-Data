import argparse
import os
import streamlit
from src.data_ingestion.ingest import process_file, scrape_url
from src.nlp_processing.extractor import EntityRelationExtractor
from src.graph_construction.builder import KnowledgeGraphBuilder

def process_data(data_source, source_type):
    """Process data from a file or URL"""
    # Initialize components
    extractor = EntityRelationExtractor()
    graph_builder = KnowledgeGraphBuilder()
    
    # Extract text from source
    text = ""
    if source_type == "file":
        text = process_file(data_source)
    elif source_type == "url":
        text = scrape_url(data_source)
    elif source_type == "text":
        text = data_source
    
    if not text:
        return None
    
    # Extract entities and relations
    entities = extractor.extract_entities(text)
    relations = extractor.extract_relations(text)
    
    # Build knowledge graph
    graph_builder.add_entities(entities)
    graph_builder.add_relations(relations)
    
    return graph_builder

def main():
    parser = argparse.ArgumentParser(description="Knowledge Graph Builder")
    parser.add_argument("--input", help="Input file or URL")
    parser.add_argument("--type", choices=["file", "url"], help="Input type")
    parser.add_argument("--streamlit", action="store_true", help="Launch Streamlit app")
    
    args = parser.parse_args()
    
    if args.streamlit:
        # Launch Streamlit app
        os.system("streamlit run app.py")
    elif args.input and args.type:
        # Process input file or URL
        graph_builder = process_data(args.input, args.type)
        if graph_builder:
            print(f"Built knowledge graph with {graph_builder.graph.number_of_nodes()} nodes and {graph_builder.graph.number_of_edges()} edges")
        else:
            print("Failed to process input")
    else:
        parser.print_help()

if __name__ == "__main__":
    main()