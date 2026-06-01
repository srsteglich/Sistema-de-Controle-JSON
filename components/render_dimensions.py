import streamlit as st
import json
from components.base_renderer import BaseRenderer
 
def _edit_string_list(container, title, values, key_prefix):
    # Editor simples de listas de strings.
    st.markdown(f"**{title}**")
    # Chave para contar quantos itens devem existir
    count_key = f"{key_prefix}_count"
    if count_key not in st.session_state:
        st.session_state[count_key] = len(values)

    # Botão de adicionar aumenta a contagem
    if container.button(f"Adicionar {title} +", key=f"{key_prefix}_add"):
        st.session_state[count_key] += 1

    # Garante que a lista tenha o mesmo tamanho da contagem
    while len(values) < st.session_state[count_key]:
        values.append("")   
     
    for i in range(st.session_state[count_key]):
        v = values[i] if i < len(values) else ""
        values[i] = container.text_input(
            f"{title}_{i+1}",
            value=v,
            key=f"{key_prefix}_item_{i}",
            label_visibility="collapsed",
        )  
    return values

def _generate_default_lambda(table_name, key):
    #Gera a estrutura padrão do lambda_setup_args baseado em table_name e key
    if not table_name or not key:
        return None
     
    full_table_name = table_name.replace('"', '')
    parts = full_table_name.split(".")

    schema_name = parts[0] if len(parts) > 1 else ""
    table_name_only = parts[1] if len(parts) > 1 else parts[0]

    return {
        "lambda_setup_args": {
            "finder_type": 0,
            "finder_module": "g2metl.facts_and_dimensions",
            "finder_class": "Stadin",
            "finder_schema": schema_name,
            "finder_table": table_name_only,
            "finder_column": key
        }
    }

# Função para criar o modal com os dados da tabela
def show_table_modal(table_data, state_key="dimensions", j=0):    
    # Exibe os dados da tabela em um modal
    table_name = table_data.get('table_name', 'N/A')

    # Limpa o valor do campo lambda no session_state antes de abrir o modal
    lambda_key = f"{state_key}_idf_lambda_{j}"
    if lambda_key in st.session_state:
        del st.session_state[lambda_key]

    @st.dialog(f"Tabela: {table_name}")
    def modal_content():
        # Variável para detectar mudanças
        table_changed = False
        key_changed = False
        
        # Expander 1: Table Data
        with st.expander("📊 Table", expanded=False):
            col1, col2 = st.columns(2)
            with col1:
                old_table_name = table_data.get("table_name", "")
                new_table_name = st.text_input(
                    "Table Name",
                    value=old_table_name,
                    key=f"{state_key}_table_{j}"
                )
                if new_table_name != old_table_name:
                    table_data["table_name"] = new_table_name
                    table_changed = True
                
                table_data["cached"] = st.checkbox(
                    "Cached",
                    value=table_data.get("cached", False),
                    key=f"{state_key}_cached_{j}",
                    help="Marque se for verdadeiro, desmarque se for falso"
                )                
            with col2:
                old_key = table_data.get("key", "")
                new_key = st.text_input(
                    "Key",
                    value=old_key,
                    key=f"{state_key}_key_{j}"
                )
                if new_key != old_key:
                    table_data["key"] = new_key
                    key_changed = True
        
        # Expander 2: IdFinder Data 
        with st.expander("🔍 IdFinder", expanded=False):
            idfinder = table_data.get("idfinder", {})            
            # Campo Class
            idfinder["class"] = st.text_input(
                "Class",
                value=idfinder.get("class", "") or "LambdaIdFinder",
                key=f"{state_key}_idf_class_{j}"
            )

            # Verifica se o lambda está vazio ou precisa ser atualizado
            is_lambda_empty = not idfinder.get("lambda") and not idfinder.get("lambda_setup_args")
            
            # Se Table Name e Key foram preenchidos E (lambda está vazio OU houve mudança nos campos)
            if table_data.get("table_name") and table_data.get("key") and (is_lambda_empty or table_changed or key_changed):
                default_lambda = _generate_default_lambda(table_data["table_name"], table_data["key"])
                # Verifica se o lambda padrão foi gerado
                if default_lambda:
                    # Atualiza o dicionário idfinder com a nova estrutura
                    idfinder.update(default_lambda)
                    # Remove a chave lambda antiga se existir
                    idfinder.pop("lambda", None)

            # Garante que a chave lambda vazia seja removida se existir
            if "lambda" in idfinder and not idfinder["lambda"]:
                del idfinder["lambda"]

            # Captura tanto "lambda" quanto "lambda_setup_args"
            if "lambda_setup_args" in idfinder:
                lambda_data = {"lambda_setup_args": idfinder["lambda_setup_args"]}
            else:
                lambda_data = idfinder.get("lambda", {})
            
            # Mostra no text_area             
            lambda_val = json.dumps(lambda_data, indent=2, ensure_ascii=False)
            lambda_txt = st.text_area(
                "Lambda",
                value=lambda_val,
                height=300, 
                key=f"{state_key}_idf_lambda_{j}",
                help="Edite o JSON manualmente ou deixe o sistema preencher automaticamente baseado em Table Name e Key"
            )            
            try:
                if lambda_txt.strip():
                    parsed_lambda = json.loads(lambda_txt)
                    # Se for no formato "lambda_setup_args", mantém no lugar certo
                    if "lambda_setup_args" in parsed_lambda:
                        idfinder["lambda_setup_args"] = parsed_lambda["lambda_setup_args"]
                        if "lambda" in idfinder:
                            del idfinder["lambda"]                                        
                    else:
                        idfinder["lambda"] = parsed_lambda
                        if "lambda_setup_args" in idfinder:
                            del idfinder["lambda_setup_args"]
                else:
                    idfinder.pop("lambda", None)
                    idfinder.pop("lambda_setup_args", None)
            except Exception as e:
                st.warning(f"JSON inválido em 'lambda': {e}")            
            table_data["idfinder"] = idfinder

        # Expander 3: Lookup & Columns Data
        with st.expander("📋 Lookup & Columns", expanded=False):
            table_data["lookupatts"] = _edit_string_list(
                st, "LookupAtts", table_data.get("lookupatts", []), f"{state_key}_lookup_{j}"
            )
            table_data["columns_name"] = _edit_string_list(
                st, "Columns", table_data.get("columns_name", []), f"{state_key}_columns_{j}"
            )

        # Botão para salvar as alterações
        if st.button("💾 Salvar Alterações", key=f"save_{state_key}_{j}"):
            if state_key in st.session_state and j < len(st.session_state[state_key]):
                st.session_state[state_key][j] = table_data.copy()
            st.success("Alterações salvas!")
            st.rerun()

    # Abre o modal
    modal_content()

def render_dimensions_input(container, dimensions_data, index, subitem_name, tlist):
    renderer = BaseRenderer(container, dimensions_data, index, subitem_name, tlist, "dimensions")
    renderer.initialize_state()

    # Modelo para novo item
    new_dim = {
        "table_name": "",
        "cached": False,
        "key": "",
        "idfinder": {"class": "LambdaIdFinder", "lambda": {}},
        "lookupatts": [],
        "columns_name": [],
    }

    # Botão para adicionar uma nova dimension - AGORA NO TOPO
    if container.button(f"Nova Dimension +", key=f"add_dim_{subitem_name}_{index}"):
        # Adiciona novo item no estado da sessão
        if renderer.state_key not in st.session_state:        
            st.session_state[renderer.state_key] = []
        st.session_state[renderer.state_key].append(new_dim.copy())

        # Sincroniza no tlist também
        renderer.update_tlist()
        # Índice do novo item
        new_index = len(st.session_state[renderer.state_key]) - 1
        # Abre modal do novo item automaticamente
        show_table_modal(st.session_state[renderer.state_key][new_index], renderer.state_key, new_index)

    # Repete sobre os elementos armazenados - DEPOIS DO BOTÃO
    for j, dim in enumerate(st.session_state[renderer.state_key]):
        # Verifica se o item não é dicionario
        if not isinstance(dim, dict):
            # Sobrescreve novo dicionário vazio
            dim = {}
       
        # Botão para abrir modal com os dados da tabela
        table_name = dim.get("table_name", "Nova Tabela")        
        if st.button(f"{table_name}", key=f"view_table_{subitem_name}_{index}_{j}"):
            show_table_modal(dim, renderer.state_key, j)

        st.session_state[renderer.state_key][j] = dim

    # Campos columns_type e columns_rename
    container.markdown("---")
    container.markdown("**Configurações Adicionais de Colunas**")

    # Acessar o item específico da tlist em vez de tratar como dict
    current_item = tlist[index] if isinstance(tlist, list) and index < len(tlist) else {}
        
    # Verifica se tlist tem as chaves columns_type e columns_rename
    # Se não tiver, inicializa com None e string vazia respectivamente
    if "columns_type" not in current_item:
        current_item["columns_type"] = None
    if "columns_rename" not in current_item:
        current_item["columns_rename"] = ""

    # columns_type
    columns_type_key = f"{renderer.state_key}_columns_type_{index}"
    current_columns_type = current_item.get("columns_type", "") or ""
    
    columns_type = container.text_input(
        "Columns Type",
        value=current_columns_type,
        key=columns_type_key
    )

    # Atualiza o valor no item atual da tlist
    if isinstance(tlist, list) and index < len(tlist):
        tlist[index]["columns_type"] = columns_type if columns_type else None

    # columns_rename
    columns_rename_key = f"{renderer.state_key}_columns_rename_{index}"    
    current_columns_rename = current_item.get("columns_rename", "")
     
    columns_rename = container.text_input(
        "Columns Rename",        
        value=current_columns_rename,
        key=columns_rename_key
    )
    
    # Atualiza o valor no item atual da tlist
    if isinstance(tlist, list) and index < len(tlist):
        tlist[index]["columns_rename"] = columns_rename

    # Atualiza o tlist sempre no final
    renderer.update_tlist()