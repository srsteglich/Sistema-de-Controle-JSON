import streamlit as st

def display_dashboard(source_data, uploaded_file):
    # Exibe o dashboard com informações sobre o JSON carregado.
    st.markdown("### 📊 Dashboard de Configuração JSON")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total de Transforms", len(source_data.get("TRANSFORMS", [])), border=True)
    with col2:
        st.metric("Total de Sources", len(source_data.get("SOURCES", [])), border=True)
    with col3:
        st.metric("Total de DESTINIES", len(source_data.get("DESTINIES", [])), border=True)
    with col4:
        st.metric("ETL Configurações", len([k for k in source_data if k.startswith("ETL_")]), border=True)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Bancos Configurados", len([k for k in source_data if k.startswith(("DB_", "DW_"))]), border=True)
    with col2:       
        st.metric("Total de Chaves", len(source_data.keys()), border=True)
    with col3:
        file_size_kb = len(uploaded_file.getvalue()) / 1024 
        st.metric("Tamanho do arquivo", f"{file_size_kb:.1f} KB", border=True)
    with col4:
        num_linhas = uploaded_file.getvalue().decode('utf-8').count(chr(10)) + 1
        # colocar em milhares em Brasileiro
        st.metric("Número de linhas", f"{num_linhas:,}".replace(",", "."), border=True) 
        #st.metric("Número de linhas", str(num_linhas), border=True) 
       
    st.markdown("### 🔍 Análise de Tipos de Dados") 
    type_analysis = analyze_types(source_data)
    col1, col2, col3, col4 = st.columns(4)
    with col1:    
                # colocar em milhares em Brasileiro
        st.metric("Dicionários", f"{type_analysis['dict']:,}".replace(",", "."), border=True)        
        #st.metric("Dicionários", type_analysis["dict"], border=True)  
        st.metric("Strings", f"{type_analysis['str']:,}".replace(",", "."), border=True)      
        #st.metric("Strings", type_analysis["str"], border=True)

    with col2:
        st.metric("Listas", f"{type_analysis['list']:,}".replace(",", "."), border=True)
        st.metric("Inteiros", f"{type_analysis['int']:,}".replace(",", "."), border=True)
    with col3:
        st.metric("Booleanos(False)", f"{type_analysis['bool_false']:,}".replace(",", "."), border=True)
        st.metric("Booleanos(True)", f"{type_analysis['bool_true']:,}".replace(",", "."), border=True)
    with col4:
        st.metric("Nulos", f"{type_analysis['null']:,}".replace(",", "."), border=True)
        total_elements = sum(v for k, v in type_analysis.items() if k not in ("bool_true", "bool_false"))
        st.metric("Total Elementos", f"{total_elements:,}".replace(",", "."), border=True)

def analyze_types(obj, results=None):
    if results is None:
        results = {"dict": 0, "list": 0, "str": 0, "int": 0, "float": 0, "bool": 1, "null": 0, "bool_true": 0, "bool_false": 0}
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
    elif isinstance(obj, bool):
            results["bool"] += 1
            if obj is True:
                results["bool_true"] += 1
            else:
                results["bool_false"] += 1        
    elif isinstance(obj, int):
        results["int"] += 1
    elif isinstance(obj, float):
        results["float"] += 1
 
    return results

