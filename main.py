import streamlit as st
import json
from streamlit import set_page_config
#from utils import load_json, save_json
from dashboard import display_dashboard
from editor import edit_json

# Observe que os módulos 'dashboard' e 'editor' devem ser implementados
def main():
    set_page_config(layout="wide")
    # Carregar o arquivo JSON
    uploaded_file = st.sidebar.file_uploader("Escolha um arquivo JSON", type="json")
    # Exibe a imagem do logoazul.jpg na barra lateral somente se nenhum arquivo foi carregado
    if uploaded_file is None:
        st.image("images/*********.png", width=1000)
        # Limpar o estado da sessão
        st.session_state.clear()  
        
    # Verificar se o arquivo foi carregado
    if uploaded_file is not None:   
        try:
            # Carrega para verificação
            source_data = json.load(uploaded_file)
            # Posiciona no inicio da leitura
            uploaded_file.seek(0)
            # Define as chaves do JSON deve conter
            valid_keys = {"TRANSFORMS", "SOURCES", "DESTINIES"}
            # Verifica menos uma das chaves validas está presentes no JSON
            # Any: Avalia a veracidade das chaves 
            if not any(key in source_data for key in valid_keys):
                st.warning("Arquivo JSON inválidos no Sistema.  \nRecarregue novamente o arquivo, pois usam as chaves: TRANSFORMS, SOURCES ou DESTINIES.", icon="⚠️")
                #msg = st.toast("Arquivo JSON inválidos no Sistema.", icon="⚠️")
                #time.sleep(3)
                #msg.toast("Recarregue o JSON novamente.", icon="⚠️")
            else:
                # Arquivo válido 
                st.sidebar.header("Editar JSON")
                # Carregar os dados do JSON
                if "source_data" not in st.session_state or st.session_state["uploaded_file_name"] != uploaded_file.name:
                    # Carregar os dados do JSON no estado da sessão
                    st.session_state["source_data"] = source_data
                    # Armazenar o nome do arquivo carregado
                    st.session_state["uploaded_file_name"] = uploaded_file.name
                # Exibir o nome do arquivo carregado
                page = st.sidebar.selectbox("Escolha uma seção:", ["Edit JSON", "Dashboard"])
                # Exibir o nome do arquivo carregado
                if page == "Dashboard":
                    display_dashboard(st.session_state["source_data"], uploaded_file)
                elif page == "Edit JSON":
                    edit_json(st.session_state["source_data"], st.session_state["uploaded_file_name"])
        except json.JSONDecodeError:
            st.error("Erro ao decodificar o arquivo. Verifique se é um JSON")
        except Exception as e:
            st.error(f"Ocorreu um erro inesperado: {e}")    

if __name__ == "__main__":
    main()