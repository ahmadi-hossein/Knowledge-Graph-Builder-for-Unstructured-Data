import streamlit as st
import networkx as nx
import pandas as pd
from src.data_ingestion.ingest import process_file, scrape_url
from src.nlp_processing.extractor import EntityRelationExtractor
from src.graph_construction.builder import KnowledgeGraphBuilder
from src.visualization.visualizer import prepare_agraph_nodes_edges
from streamlit_agraph import agraph, Node, Edge, Config  # وارد کردن توابع و کلاس‌های مورد نیاز

def main():
    # تنظیمات صفحه Streamlit
    st.set_page_config(
        page_title="Knowledge Graph Builder",
        page_icon="🧠",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    
    st.title("Knowledge Graph Builder for Unstructured Data")
    
    # Sidebar برای انتخاب منبع داده
    st.sidebar.header("Controls")
    
    upload_option = st.sidebar.radio(
        "Select Data Source",
        ["Upload Files", "Enter URL", "Paste Text"]
    )
    
    text = None  # متغیری برای ذخیره متن استخراج‌شده
    
    # بخش ورودی داده
    if upload_option == "Upload Files":
        uploaded_files = st.sidebar.file_uploader("Upload Documents", 
                                        accept_multiple_files=True,
                                        type=["pdf", "txt", "docx"])
        if uploaded_files:
            st.write(f"Uploaded {len(uploaded_files)} files")
            # پردازش فایل‌ها
            text = ""
            for uploaded_file in uploaded_files:
                file_path = f"./data/{uploaded_file.name}"
                with open(file_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                text += process_file(file_path)
                
    elif upload_option == "Enter URL":
        url = st.sidebar.text_input("Enter URL")
        if st.sidebar.button("Fetch"):
            if url:
                st.write(f"Fetching content from: {url}")
                text = scrape_url(url)
                
    elif upload_option == "Paste Text":
        text_input = st.sidebar.text_area("Paste your text here", height=250)
        if st.sidebar.button("Process"):
            if text_input:
                st.write("Processing text input...")
                text = text_input
    
    # بررسی اینکه آیا متن استخراج شده است یا خیر
    if text:
        # مراحل پردازش داده‌ها و ساخت گراف
        extractor = EntityRelationExtractor()
        graph_builder = KnowledgeGraphBuilder()
        
        # استخراج موجودیت‌ها و روابط
        entities = extractor.extract_entities(text)
        relations = extractor.extract_relations(text)
        
        # افزودن موجودیت‌ها و روابط به گراف
        graph_builder.add_entities(entities)
        graph_builder.add_relations(relations)
        
        # دریافت داده‌های گراف
        node_data = graph_builder.get_node_data()
        edge_data = graph_builder.get_edge_data()

        # چاپ داده‌های گراف برای اشکال‌زدایی
        print("Graph Nodes:", node_data)
        print("Graph Edges:", edge_data)

        # آماده‌سازی گره‌ها و یال‌ها برای نمایش
        nodes, edges = prepare_agraph_nodes_edges(node_data, edge_data)
    else:
        nodes = []
        edges = []
    
    # بخش نمایش گراف
    st.header("Knowledge Graph Visualization")
    
    tab1, tab2 = st.tabs(["Interactive Graph", "Tabular View"])
    
    with tab1:
        if nodes and edges:
            config = Config(width=700,
                            height=500,
                            directed=True,
                            physics=True,
                            hierarchical=False)
            agraph(nodes=nodes, edges=edges, config=config)  # نمایش گراف
        else:
            st.info("No data to visualize. Please upload or input data.")
        
    with tab2:
        if nodes or edges:
            # ایجاد DataFrame برای موجودیت‌ها
            entity_df = pd.DataFrame(node_data)
            
            # ایجاد DataFrame برای روابط
            edge_df = pd.DataFrame(edge_data)
            
            st.subheader("Entities")
            st.dataframe(entity_df)
            
            st.subheader("Relationships")
            st.dataframe(edge_df)
        else:
            st.info("No data to display. Please upload or input data.")
    
    # بخش تحلیل‌های گراف
    st.header("Graph Analytics")
    
    if nodes or edges:
        metric1, metric2, metric3 = st.columns(3)
        
        with metric1:
            st.metric("Total Entities", len(nodes))
        
        with metric2:
            st.metric("Total Relationships", len(edges))
        
        with metric3:
            st.metric("Graph Density", round(nx.density(nx.DiGraph()), 4))
    else:
        st.info("No analytics available. Please upload or input data.")

if __name__ == "__main__":
    main()