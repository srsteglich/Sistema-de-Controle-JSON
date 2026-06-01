import streamlit as st
import json
from components.base_renderer import BaseRenderer
 
def render_keyrefs_input(container, keyrefs_data, index, subitem_name, tlist):
    container.markdown("**Keyrefs:**")    
    renderer = BaseRenderer(container, keyrefs_data, index, subitem_name, tlist, "keyrefs")
    renderer.initialize_state()   
     
    # Normaliza para lista de dicts
    if st.session_state[renderer.state_key] and isinstance(st.session_state[renderer.state_key][0], str):
        st.session_state[renderer.state_key] = [{'key': k} for k in st.session_state[renderer.state_key]]

    # Chave para contar quantos itens devem existir
    count_key = f"{renderer.state_key}_count"
    if count_key not in st.session_state:
        st.session_state[count_key] = len(st.session_state[renderer.state_key]) 

    # Botão de adicionar aumenta a contagem
    if container.button(f"Adicionar Keyref +", key=f"{renderer.state_key}_add"):
        st.session_state[count_key] += 1
        st.rerun()  

    # Garante que a lista tenha o mesmo tamanho da contagem
    current_list = st.session_state[renderer.state_key]
    while len(current_list) < st.session_state[count_key]:
        current_list.append({'key': ''})    

    # Renderiza Apenas o ultimo campo (mais recente) logo após o botão
    if st.session_state[count_key] > 0: 
        last_index = st.session_state[count_key] - 1
        if last_index < len(current_list):
            current_list[last_index]['key'] = container.text_input(
                f"Keyref {last_index+1}", 
                value=current_list[last_index].get('key', ''), 
                key=f"{renderer.state_key}_{last_index}", 
                label_visibility="collapsed"
            )
        else:
            new_val = container.text_input(
                f"Keyref {last_index+1}", 
                value="", 
                key=f"{renderer.state_key}_{last_index}", 
                label_visibility="collapsed"
            )
            current_list.append({'key': new_val})

    # Renderiza os campos ANTERIORES (do mais antigo para o mais novo, exceto o último)
    for j in range(st.session_state[count_key] - 1):
        if j < len(current_list):
            current_list[j]['key'] = container.text_input(
                f"Keyref {j+1}", 
                value=current_list[j].get('key', ''), 
                key=f"{renderer.state_key}_{j}", 
                label_visibility="collapsed"
            )
        else:
            new_val = container.text_input(
                f"Keyref {j+1}", 
                value="", 
                key=f"{renderer.state_key}_{j}", 
                label_visibility="collapsed"
            )
            if j == len(current_list):
                current_list.append({'key': new_val})
            else:
                current_list[j] = {'key': new_val}

    # Atualiza o estado
    st.session_state[renderer.state_key] = current_list 
    renderer.update_tlist()
    