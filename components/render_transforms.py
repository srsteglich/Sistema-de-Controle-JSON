import streamlit as st
import json
from components.base_renderer import BaseRenderer

def _edit_string_list(container, title, values, key_prefix):
    st.markdown(f"**{title}**")
    count_key = f"{key_prefix}_count"
    if count_key not in st.session_state:
        st.session_state[count_key] = len(values) 
        
    # Botão de Adicionar
    if container.button(f"Adicionar {title} +", key=f"{key_prefix}_add"):
        st.session_state[count_key] += 1

    # Garante que a lista tenha o mesmo tamanho da contagem    
    while len(values) < st.session_state[count_key]:
        values.insert(0, "")

    # Renderiza todos os campos (novo sempre no topo)
    for i in range(st.session_state[count_key]):
        values[i] = container.text_input(
            f"{title}_{i+1}",
            value=values[i],
            key=f"{key_prefix}_item_{i}",
            label_visibility="collapsed",
        )
    return values

def _edit_dict(container, title, values, key_prefix):
    st.markdown(f"**{title}**")
    # Garante que values é um dicionário
    if not isinstance(values, dict):
        values = {} 

    # Chave para contar quantos itens devem existir
    count_key = f"{key_prefix}_count"
    if count_key not in st.session_state:
        st.session_state[count_key] = len(values)

    # Botão de adicionar aumenta a contagem
    if container.button(f"Adicionar {title} +", key=f"{key_prefix}_add"):
        st.session_state[count_key] += 1

    # Converte o dicionário em lista de pares key-value para edição
    keys = list(values.keys())
    values_list = list(values.values()) 
    # Garante que a lista tenha o mesmo tamanho da contagem
    while len(values_list) < st.session_state[count_key]:
        values_list.append("")
        keys.append(f"new_key_{len(values_list)}")

    # Cria listas temporárias para armazenar as edições
    new_keys = []
    new_values = []
    
    for i in range(st.session_state[count_key]):
        col1, col2 = container.columns(2)
        with col1:
            new_key = col1.text_input(
                f"Chave {i+1}",
                value=keys[i] if i < len(keys) else "",
                key=f"{key_prefix}_key_{i}",
                label_visibility="collapsed",
            )
        with col2:
            new_value = col2.text_input(
                f"Valor {i+1}",
                value=values_list[i] if i < len(values_list) else "",
                key=f"{key_prefix}_value_{i}",
                label_visibility="collapsed",
            )
        new_keys.append(new_key)
        new_values.append(new_value)

    # Reconstrói o dicionário com as novas chaves e valores
    result_dict = {}
    for k, v in zip(new_keys, new_values):
        if k:  # Ignora chaves vazias
            result_dict[k] = v 
    return result_dict

def show_transform_modal(transform, state_key="transforms", j=0):
    module_name = transform.get("module", f"Transform {j+1}")

    @st.dialog(f"Transform: {module_name}")
    def modal_content():
        # module & class
        col1, col2 = st.columns(2)
        transform["module"] = col1.text_input(
            "Module",
            value=transform.get("module", ""),
            key=f"{state_key}_module_{j}"
        )
        transform["class"] = col2.text_input(
            "Class",
            value=transform.get("class", ""),
            key=f"{state_key}_class_{j}"
        )

        # columns 
        transform["columns"] = _edit_string_list(
            st, "Columns", transform.get("columns", []), f"{state_key}_columns_{j}"
        )

        # args 
        transform["args"] = _edit_dict(
            st, "Args", transform.get("args", {}), f"{state_key}_args_{j}"
        )

        # Botão de salvar
        if st.button("💾 Salvar Alterações", key=f"save_{state_key}_{j}"):
            if state_key in st.session_state and j < len(st.session_state[state_key]):
                st.session_state[state_key][j] = transform.copy()
            st.success("Alterações salvas!")
            st.rerun()

    modal_content()

def render_transforms_input(container, transforms_data, index, subitem_name, tlist):
    #container.markdown("**Transforms:**")
    renderer = BaseRenderer(container, transforms_data, index, subitem_name, tlist, "transforms")
    renderer.initialize_state()

    # Novo transform
    new_transform = {"module": "", "class": "", "columns": [], "args": {}}
    if container.button(f"Novo Transform +", key=f"add_transform_{subitem_name}_{index}"):
        if renderer.state_key not in st.session_state:
            st.session_state[renderer.state_key] = []
        st.session_state[renderer.state_key].append(new_transform)
        renderer.update_tlist()
        new_index = len(st.session_state[renderer.state_key]) - 1
        show_transform_modal(st.session_state[renderer.state_key][new_index], renderer.state_key, new_index)

    for j, transform in enumerate(st.session_state[renderer.state_key]):
        if not isinstance(transform, dict):
            transform = {}

        module_name = transform.get("module", f"Transform {j+1}")
        if st.button(module_name or f"Transform {j+1}", key=f"view_transform_{subitem_name}_{index}_{j}"):
            show_transform_modal(transform, renderer.state_key, j)

        st.session_state[renderer.state_key][j] = transform



    # Campos fixes e from (fora do modal, após o botão Novo Transform)
    container.markdown("---")
    container.markdown("**Configurações Adicionais de Transforms**")
    
    # Acessar o item específico da tlist em vez de tratar como dict
    current_item = tlist[index] if isinstance(tlist, list) and index < len(tlist) else {}
    
    # Verifica se o item atual tem as chaves fixes e from
    # Se não tiver, inicializa
    if "fixes" not in current_item:
        current_item["fixes"] = []
    if "from" not in current_item:
        current_item["from"] = {"year": "", "month": ""}

    # Campo fixes (lista de strings)
    container.markdown("**Fixes:**")
    fixes_key = f"{renderer.state_key}_fixes_{index}"
    
    # Inicializa no session_state se não existir
    if f"{fixes_key}_count" not in st.session_state:
        st.session_state[f"{fixes_key}_count"] = len(current_item.get("fixes", []))
    
    # Botão para adicionar fix
    if container.button("Adicionar Fix +", key=f"{fixes_key}_add"):
        st.session_state[f"{fixes_key}_count"] += 1
    
    # Garante que a lista de fixes tenha o tamanho correto
    fixes_list = current_item.get("fixes", [])
    while len(fixes_list) < st.session_state[f"{fixes_key}_count"]:
        fixes_list.append("")
    
    # Renderiza os campos de fixes
    for i in range(st.session_state[f"{fixes_key}_count"]):
        fix_value = fixes_list[i] if i < len(fixes_list) else ""
        fixes_list[i] = container.text_input(
            f"Fix {i+1}",
            value=fix_value,
            key=f"{fixes_key}_item_{i}",
            label_visibility="collapsed"
        )
    
    # Atualiza a lista de fixes no item atual
    if isinstance(tlist, list) and index < len(tlist):
        tlist[index]["fixes"] = fixes_list

    # Campo from (year e month)
    container.markdown("**From:**")
    from_data = current_item.get("from", {"year": "", "month": ""})
    
    col1, col2 = container.columns(2)
    
    # year
    year_key = f"{renderer.state_key}_from_year_{index}"
    # Pega o valor atual diretamente, sem definir no session_state antes
    current_year = str(from_data.get("year", ""))
    
    year_value = col1.text_input(
        "Year",
        value = current_year,        
        key=year_key
    )
    
    # month
    month_key = f"{renderer.state_key}_from_month_{index}"
    # Pega o valor atual diretamente, sem definir no session_state antes
    current_month = str(from_data.get("month", ""))
    
    month_value = col2.text_input(
        "Month",        
        value=current_month,
        key=month_key
    )
    
    # Atualiza os valores no item atual da tlist
    if isinstance(tlist, list) and index < len(tlist):
        # Converte year e month para int se forem números, senão mantém como string
        try:
            year_int = int(year_value) if year_value else ""
        except ValueError:
            year_int = year_value
            
        try:
            month_int = int(month_value) if month_value else ""
        except ValueError:
            month_int = month_value
            
        tlist[index]["from"] = {
            "year": year_int,
            "month": month_int
        }

    renderer.update_tlist()
