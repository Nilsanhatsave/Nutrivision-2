import streamlit as st
from supabase import create_client, Client

# Configuração do Supabase
try:
    SUPABASE_URL = st.secrets["SUPABASE_URL"]
    SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    SUPABASE_AVAILABLE = True
    print("✅ Supabase conectado!")
except Exception as e:
    SUPABASE_AVAILABLE = False
    print(f"❌ Erro ao conectar Supabase: {e}")