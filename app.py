import streamlit as st
import networkx as nx
import pandas as pd
import os # Import os if needed elsewhere, though not strictly required by this version

# Update imports to use the new function and base classes/functions
from src.data_ingestion.ingest import process_uploaded_file, scrape_url # Removed process_file, kept scrape_url
# from src.data_ingestion.ingest import scrape_url_with_selenium # Uncomment if adding Selenium option
from src.nlp_processing.extractor import EntityRelationExtractor
from src.graph_construction.builder import KnowledgeGraphBuilder
from src.visualization.visualizer import prepare_agraph_nodes_edges
from streamlit_agraph import agraph, Node, Edge, Config # Make sure all imports are correct

def main():
    # تنظیمات صفحه Streamlit
    st.set_page_config(
        page_title="Knowledge Graph Builder",
        page_icon="🧠",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    st.title("Knowledge Graph Builder for Unstructured Data")

    # Initialize session state variables if they don't exist
    if 'text_content' not in st.session_state:
        st.session_state['text_content'] = None
    if 'graph_built' not in st.session_state:
        st.session_state['graph_built'] = False
    if 'nodes' not in st.session_state:
        st.session_state['nodes'] = []
    if 'edges' not in st.session_state:
        st.session_state['edges'] = []
    if 'node_data' not in st.session_state:
         st.session_state['node_data'] = []
    if 'edge_data' not in st.session_state:
         st.session_state['edge_data'] = []
    if 'graph_metrics' not in st.session_state:
        st.session_state['graph_metrics'] = {}


    # Sidebar برای انتخاب منبع داده
    st.sidebar.header("Controls")

    upload_option = st.sidebar.radio(
        "Select Data Source",
        ["Upload Files", "Enter URL", "Paste Text"],
        key="data_source_option" # Add a key for state management
    )

    # --- Data Input Section ---
    # Reset state if input method changes or no input is given yet
    # This logic might need refinement depending on desired behavior
    # For now, we process based on button clicks within each section

    if upload_option == "Upload Files":
        uploaded_files = st.sidebar.file_uploader(
            "Upload Documents (.pdf, .txt, .docx)",
            accept_multiple_files=True,
            type=["pdf", "txt", "docx"],
            key="file_uploader" # Add key
        )
        if st.sidebar.button("Process Uploaded Files", key="process_files_button", disabled=not uploaded_files):
            if uploaded_files:
                st.session_state['text_content'] = None # Reset previous text
                st.session_state['graph_built'] = False # Reset graph state
                st.info(f"Processing {len(uploaded_files)} files...")
                all_texts = []
                error_messages = []
                with st.spinner("Extracting text from files..."):
                    for uploaded_file in uploaded_files:
                        # Use the new function that handles file objects
                        extracted_content = process_uploaded_file(uploaded_file)
                        if extracted_content:
                            # Check if it's an error message returned by the function
                            if extracted_content.startswith("Error:"):
                                error_messages.append(f"{uploaded_file.name}: {extracted_content}")
                            else:
                                all_texts.append(extracted_content)
                        else:
                            # Handle case where None is returned unexpectedly
                            error_messages.append(f"{uploaded_file.name}: Failed to extract text (returned None).")

                if error_messages:
                    for msg in error_messages:
                        st.warning(msg) # Show warnings for files that failed

                if all_texts:
                    st.session_state['text_content'] = "\n\n".join(all_texts) # Join texts with a separator
                    st.success("Text extraction complete for processable files.")
                    # Optional: Show a preview
                    with st.expander("Show Extracted Text Preview (First 2000 Chars)"):
                         st.text_area("", st.session_state['text_content'][:2000], height=200, key="text_preview_files")
                elif not error_messages:
                     st.warning("No files were uploaded or selected for processing.")
                elif not all_texts and error_messages:
                     st.error("Text extraction failed for all uploaded files.")


    elif upload_option == "Enter URL":
        url = st.sidebar.text_input("Enter URL", key="url_input")
        # use_selenium = st.sidebar.checkbox("Use Selenium (slower, for dynamic sites)", key="use_selenium_checkbox") # Optional Selenium toggle

        if st.sidebar.button("Fetch and Process URL", key="fetch_url_button", disabled=not url):
            if url:
                st.session_state['text_content'] = None # Reset previous text
                st.session_state['graph_built'] = False # Reset graph state
                st.info(f"Fetching content from: {url}")
                with st.spinner("Scraping URL..."):
                    # if use_selenium:
                    #     st.session_state['text_content'] = scrape_url_with_selenium(url)
                    # else:
                    st.session_state['text_content'] = scrape_url(url)

                if st.session_state['text_content']:
                    st.success("Content fetched successfully.")
                    with st.expander("Show Fetched Text Preview (First 2000 Chars)"):
                         st.text_area("", st.session_state['text_content'][:2000], height=200, key="text_preview_url")
                else:
                    st.error("Failed to fetch or extract meaningful content from URL. The site might be inaccessible, protected, dynamic (try Selenium if available), or contain no extractable text.")
            else:
                st.warning("Please enter a URL.")


    elif upload_option == "Paste Text":
        text_input = st.sidebar.text_area("Paste your text here", height=250, key="paste_text_area")
        if st.sidebar.button("Process Pasted Text", key="process_text_button", disabled=not text_input):
            if text_input:
                st.session_state['text_content'] = None # Reset previous text
                st.session_state['graph_built'] = False # Reset graph state
                st.info("Processing pasted text...")
                with st.spinner("Processing..."):
                    st.session_state['text_content'] = text_input # Assign the pasted text
                st.success("Text processed.")
                with st.expander("Show Input Text Preview (First 2000 Chars)"):
                         st.text_area("", st.session_state['text_content'][:2000], height=200, key="text_preview_paste")

            else:
                st.warning("Please paste text into the text area.")

    # --- Processing and Graph Building Section ---
    # This section runs if text_content was successfully populated by one of the methods above
    # We use session state to avoid reprocessing on every interaction

    if st.session_state['text_content'] and not st.session_state['graph_built']:
        st.write("---") # Separator
        st.header("Processing Text and Building Graph")
        text_to_process = st.session_state['text_content']
        print(f"Processing text content of length: {len(text_to_process)}") # Debugging print to console

        # Initialize components
        try:
            extractor = EntityRelationExtractor() # Consider adding model loading feedback/error handling
            graph_builder = KnowledgeGraphBuilder()

            # Extract entities and relations
            st.write("Step 1: Extracting Entities...")
            with st.spinner("Identifying entities..."):
                 entities = extractor.extract_entities(text_to_process)
            st.write(f"Found {len(entities)} entities.")

            st.write("Step 2: Extracting Relations...")
            with st.spinner("Identifying potential relations..."):
                 relations = extractor.extract_relations(text_to_process)
            st.write(f"Found {len(relations)} potential relations.")

            if not entities and not relations:
                st.warning("No entities or relations could be extracted from the provided text. The graph will be empty.")
                # Set empty data in session state
                st.session_state['node_data'] = []
                st.session_state['edge_data'] = []
                st.session_state['nodes'] = []
                st.session_state['edges'] = []
                st.session_state['graph_metrics'] = {"num_entities": 0, "num_relations": 0, "density": 0.0}

            else:
                st.write("Step 3: Building Knowledge Graph...")
                with st.spinner("Constructing graph structure..."):
                    # Add to graph
                    graph_builder.add_entities(entities)
                    # You might want to make the confidence threshold configurable via sidebar slider
                    confidence_threshold = st.sidebar.slider("Relation Confidence Threshold", 0.0, 1.0, 0.5, 0.05)
                    graph_builder.add_relations(relations, confidence_threshold=confidence_threshold)

                    # Get data for visualization and metrics
                    st.session_state['node_data'] = graph_builder.get_node_data()
                    st.session_state['edge_data'] = graph_builder.get_edge_data()

                    # Prepare nodes and edges for agraph
                    st.session_state['nodes'], st.session_state['edges'] = prepare_agraph_nodes_edges(
                         st.session_state['node_data'], st.session_state['edge_data']
                    )

                    # Calculate metrics
                    num_entities = len(st.session_state['nodes'])
                    num_relations = len(st.session_state['edges'])
                    density = 0.0
                    # Ensure graph object is retrieved for density calculation
                    actual_graph = graph_builder.get_graph()
                    if actual_graph and actual_graph.number_of_nodes() > 1:
                         density = round(nx.density(actual_graph), 4)

                    st.session_state['graph_metrics'] = {
                         "num_entities": num_entities,
                         "num_relations": num_relations,
                         "density": density
                    }

                st.success("Knowledge graph built successfully!")

            st.session_state['graph_built'] = True # Mark graph as built

        except Exception as e:
            st.error(f"An error occurred during NLP processing or graph building: {e}")
            # Print stack trace to console for detailed debugging
            import traceback
            traceback.print_exc()
            # Reset state on error
            st.session_state['graph_built'] = False
            st.session_state['text_content'] = None


    # --- Display Section ---
    # Display graph and tables if data exists in session state

    st.write("---") # Separator
    st.header("Knowledge Graph Visualization & Data")

    if not st.session_state.get('graph_built', False) and not st.session_state.get('text_content', None):
         st.info("Please select a data source and process it using the sidebar controls to build and view the knowledge graph.")
    elif not st.session_state.get('nodes', []) and not st.session_state.get('edges', []):
         st.warning("The graph is empty. No entities or relations were found in the processed text, or processing failed.")
    else:
        tab1, tab2 = st.tabs(["📊 Interactive Graph", "📄 Tabular View"])

        with tab1:
            st.subheader("Interactive Graph View")
            if st.session_state['nodes'] or st.session_state['edges']:
                # Configure graph appearance
                config = Config(width=800, # Adjust size as needed
                                height=600,
                                directed=True,
                                physics=st.checkbox("Enable physics simulation", True, key="physics_toggle"), # Toggle physics
                                hierarchical=False,
                                # Add more customization: https://visjs.github.io/vis-network/docs/network/
                                node={'labelProperty':'label'}, # Show label inside node
                                edge={'labelProperty':'label'}, # Show label on edge
                                )
                agraph(nodes=st.session_state['nodes'],
                       edges=st.session_state['edges'],
                       config=config)
            else:
                # This case should be covered by the outer warning, but included for safety
                st.info("Graph is empty.")

        with tab2:
            st.subheader("Entities (Nodes)")
            if st.session_state['node_data']:
                # Create DataFrame for display
                entity_df = pd.DataFrame(st.session_state['node_data'])
                st.dataframe(entity_df)
            else:
                st.info("No entity data available.")

            st.subheader("Relationships (Edges)")
            if st.session_state['edge_data']:
                # Create DataFrame for display
                edge_df = pd.DataFrame(st.session_state['edge_data'])
                st.dataframe(edge_df)
            else:
                st.info("No relationship data available.")

    # --- Graph Analytics Section ---
    st.write("---") # Separator
    st.header("Graph Analytics")

    if st.session_state.get('graph_built', False) and st.session_state.get('graph_metrics', {}):
        metrics = st.session_state['graph_metrics']
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Entities (Nodes)", metrics.get("num_entities", 0))
        col2.metric("Total Relationships (Edges)", metrics.get("num_relations", 0))
        col3.metric("Graph Density", f"{metrics.get('density', 0.0):.4f}") # Format density
    else:
        st.info("No analytics available. Process data to generate graph metrics.")


if __name__ == "__main__":
    # Note: It's generally recommended to have spacy model downloaded outside the script run
    # E.g., run `python -m spacy download en_core_web_lg` in your terminal once.
    # You could add a check here, but it might slow down startup.
    main()
