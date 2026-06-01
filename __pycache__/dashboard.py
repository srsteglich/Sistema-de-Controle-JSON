import streamlit as st

def display_dashboard(source_data, uploaded_file):
    # Exibe o dashboard com informações sobre o JSON carregado.
    st.markdown("### 📊 Dashboard de Configuração JSON")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total de Chaves", len(source_data.keys()))
    with col2:
        file_size_kb = len(uploaded_file.getvalue()) / 1024 
        st.metric("Tamanho do arquivo", f"{file_size_kb:.1f} KB")
    with col3:
        num_linhas = uploaded_file.getvalue().decode('utf-8').count(chr(10)) + 1
        st.metric("Número de linhas", str(num_linhas))

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total de Transforms", len(source_data.get("TRANSFORMS", [])))
    with col2:
        st.metric("Total de Sources", len(source_data.get("SOURCES", [])))
    with col3:
        st.metric("Bancos Configurados", len([k for k in source_data if k.startswith(("DB_", "DW_"))]))
    with col4:
        st.metric("ETL Configurações", len([k for k in source_data if k.startswith("ETL_")]))

    st.markdown("### 🔍 Análise de Tipos de Dados") 
    type_analysis = analyze_types(source_data)
    col1, col2, col3, col4 = st.columns(4)
    with col1:      
        st.metric("Dicionários", type_analysis["dict"])
        st.metric("Strings", type_analysis["str"])
    with col2:
        st.metric("Listas", type_analysis["list"])
        st.metric("Inteiros", type_analysis["int"]) 
    with col3:
        st.metric("Floats", type_analysis["float"])
        st.metric("Booleanos", type_analysis["bool"])
    with col4:
        st.metric("Nulos", type_analysis["null"])
        total_elements = sum(type_analysis.values())
        st.metric("Total Elementos", total_elements)

def analyze_types(obj, results=None):
    if results is None:
        results = {"dict": 0, "list": 0, "str": 0, "int": 0, "float": 0, "bool": 0, "null": 0}
    if obj is None:
        results["null"] += 1
    elif isinstance(obj, dict):
        results["dict"] += 1
        for v in obj.values():
            analyze_types(v, results)
    elif isinstance(obj, list):
        results["list"] += 1
        for item in obj:
            analyze_types(item, results)
    elif isinstance(obj, str):
        results["str"] += 1
    elif isinstance(obj, int):
        results["int"] += 1
    elif isinstance(obj, float):
        results["float"] += 1
    elif isinstance(obj, bool):
        results["bool"] += 1
    return results