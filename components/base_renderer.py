import streamlit as st

#  Esta classe fornece uma estrutura para renderizar diferentes tipos de componentes 
class BaseRenderer:
    # Inicializa o renderizador com os parâmetros necessários
    def __init__(self, container, data, index, subitem_name, tlist, component_type):
        self.container = container
        self.data = data if isinstance(data, list) else []
        self.index = index
        self.subitem_name = subitem_name
        self.tlist = tlist
        self.component_type = component_type
        self.state_key = f"{component_type}_{subitem_name}_{index}"

    # Inicializa o estado do componente, se necessário    
    def initialize_state(self):
        if self.state_key not in st.session_state:
            st.session_state[self.state_key] = self.data[:]

        # Inicializa também o contador para esta lista
        count_key = f"{self.state_key}_count"  
        if count_key not in st.session_state:
            st.session_state[count_key] = len(self.data)

    # Renderiza o componente com base no tipo
    def render_header(self, headers):
        cols = st.columns([1]*len(headers))
        for col, header in zip(cols, headers):
            with col:
                st.markdown(f"**{header}**")
        return cols

    # Renderiza o componente de entrada
    def update_tlist(self):
        self.tlist[self.index][self.component_type] = st.session_state[self.state_key]

    # Adiciona um novo item ao componenteword
    def add_new_item(self, default_item):
        count_key = f"{self.state_key}_count"

        if self.container.button(f"Adicionar {self.component_type}", key=f"add_{self.state_key}"):
            st.session_state[count_key] += 1
            # Adiciona o novo item à lista
            if self.state_key not in st.session_state:
                st.session_state[self.state_key] = []
            # Garante que a lista tenha o tamanho do contador
            while len(st.session_state[self.state_key]) < st.session_state[count_key]:
                st.session_state[self.state_key].append(default_item)
            # Atualiza o tlist
            self.update_tlist()
            st.rerun()
