import streamlit as st
import json
from components.base_renderer import BaseRenderer 

# Esta função renderiza o componente de entrada para listas genéricas 
def render_list_input(container, label_singular, list_data_raw, item_key_prefix, index, subitem_name, column_name, tlist):
    renderer = BaseRenderer(container, list_data_raw, index, subitem_name, tlist, item_key_prefix)
    renderer.initialize_state()
    # Título da seção
    container.markdown(f"**{column_name}:**")

    # Chave para contar quantos itens devem existir
    count_key = f"{renderer.state_key}_count"
    if count_key not in st.session_state:
        st.session_state[count_key] = len(st.session_state[renderer.state_key])

    # Botão de adicionar aumenta a contagem
    if container.button(f"Adicionar {label_singular} +", key=f"{renderer.state_key}_add"):
        st.session_state[count_key] += 1
        st.rerun()  # Adiciona rerun para atualizar imediatamente

    # Garante que a lista tenha o mesmo tamanho da contagem
    current_list = st.session_state[renderer.state_key]
    while len(current_list) < st.session_state[count_key]:
        current_list.insert(0, "")  # Insere no início para manter o mais recente no topo

    # Processar APENAS o primeiro campo (mais recente) logo após o botão
    if st.session_state[count_key] > 0:
        first_index = 0  # Sempre o primeiro item é o mais recente
        if first_index < len(current_list):
            current_list[first_index] = container.text_input(
                f"{label_singular} {first_index+1}", 
                value=current_list[first_index], 
                key=f"{renderer.state_key}_{first_index}", 
                label_visibility="collapsed"
            )
        else:
            new_val = container.text_input(
                f"{label_singular} {first_index+1}", 
                value="", 
                key=f"{renderer.state_key}_{first_index}", 
                label_visibility="collapsed"
            )
            current_list.insert(0, new_val)

    # Processar os campos ANTERIORES (do segundo em diante)
    for j in range(1, st.session_state[count_key]):  # Começa do 1, não do 0
        if j < len(current_list):
            current_list[j] = container.text_input(
                f"{label_singular} {j+1}", 
                value=current_list[j], 
                key=f"{renderer.state_key}_{j}", 
                label_visibility="collapsed"
            )
        else:
            new_val = container.text_input(
                f"{label_singular} {j+1}", 
                value="", 
                key=f"{renderer.state_key}_{j}", 
                label_visibility="collapsed"
            )
            current_list.append(new_val)

    # Atualiza o estado 
    st.session_state[renderer.state_key] = current_list
    renderer.update_tlist()