# pages/nutricionista.py
# ===== PERFIL NUTRICIONISTA =====

import streamlit as st
from utils.helpers import t

def renderizar_nutricionista():
    st.title(t('avaliacoes'))
    st.markdown("Avaliação Nutricional")
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📋 Avaliações")
        st.write("**João Silva** - DDS: 5/9")
        st.write("**Maria Santos** - DDS: 3/9")
        st.write("**Pedro Costa** - DDS: 7/9")
    
    with col2:
        st.subheader("🍽️ Planos Alimentares")
        plano = st.selectbox("Paciente", ["João Silva", "Maria Santos", "Pedro Costa"])
        st.text_area("Plano Alimentar", "Diversificar com 5 grupos\nRico em ferro", height=100)
        if st.button("💾 Salvar Plano", type="primary"):
            st.success("✅ Plano salvo com sucesso!")