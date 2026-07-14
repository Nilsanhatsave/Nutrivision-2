# pages/agronomo.py
# ===== PERFIL AGRÔNOMO =====

import streamlit as st
from utils.helpers import t

def renderizar_agronomo():
    """Renderiza a página do Agrônomo"""
    
    st.title(t('producao'))
    st.markdown("Produção Agrícola")
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Produção")
        st.metric("Área plantada", "2.5 ha", "+10%")
        st.metric("Produção total", "900 kg", "+15%")
        st.write("**Culturas:**")
        st.write("- Milho: 500 kg")
        st.write("- Feijão: 100 kg")
    
    with col2:
        st.subheader("Análise do Solo")
        st.write("**pH:** 6.5 - Bom")
        st.write("**Fósforo:** Baixo")
        st.write("**Potássio:** Médio")
        st.info("Recomendação: Adubação fosfatada")