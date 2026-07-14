# pages/medico.py
# ===== PERFIL MÉDICO - FICHA DIRETO NA PÁGINA =====

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import random

# ===== IMPORTAR SUPABASE =====
try:
    from supabase_client import (
        SUPABASE_AVAILABLE,
        salvar_crianca_supabase,
        carregar_criancas_supabase,
        atualizar_crianca_supabase
    )
except ImportError:
    SUPABASE_AVAILABLE = False
    def salvar_crianca_supabase(dados):
        return False, "Supabase nao disponivel"
    def carregar_criancas_supabase():
        return False, []
    def atualizar_crianca_supabase(id, dados):
        return False, "Supabase nao disponivel"

# ========== CSS PERSONALIZADO ==========
def aplicar_css():
    st.markdown("""
    <style>
    /* Estilo geral */
    .main {
        padding: 0 10px;
    }
    
    /* Botões principais */
    .stButton > button {
        background: linear-gradient(135deg, #1565C0, #42A5F5);
        color: white;
        font-weight: bold;
        border: none;
        border-radius: 12px;
        padding: 12px 24px;
        font-size: 16px;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(21, 101, 192, 0.3);
        width: 100%;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 25px rgba(21, 101, 192, 0.5);
        background: linear-gradient(135deg, #0D47A1, #1E88E5);
    }
    
    /* Botão secundário */
    .stButton > button.secondary {
        background: linear-gradient(135deg, #2E7D32, #4CAF50);
        box-shadow: 0 4px 15px rgba(46, 125, 50, 0.3);
    }
    .stButton > button.secondary:hover {
        background: linear-gradient(135deg, #1B5E20, #388E3C);
        box-shadow: 0 6px 25px rgba(46, 125, 50, 0.5);
    }
    
    /* Botão perigo */
    .stButton > button.danger {
        background: linear-gradient(135deg, #C62828, #EF5350);
        box-shadow: 0 4px 15px rgba(198, 40, 40, 0.3);
    }
    .stButton > button.danger:hover {
        background: linear-gradient(135deg, #B71C1C, #D32F2F);
        box-shadow: 0 6px 25px rgba(198, 40, 40, 0.5);
    }
    
    /* Título das seções */
    .section-title {
        font-size: 1.3rem;
        font-weight: 700;
        color: #0D47A1;
        margin: 20px 0 15px 0;
        padding: 10px 15px;
        background: linear-gradient(135deg, #e3f2fd, #bbdefb);
        border-radius: 10px;
        border-left: 5px solid #1565C0;
    }
    
    /* Cards de paciente */
    .paciente-card {
        background: white;
        padding: 15px 20px;
        border-radius: 12px;
        margin: 10px 0;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        border-left: 5px solid #1565C0;
        transition: all 0.3s ease;
    }
    .paciente-card:hover {
        transform: translateX(5px);
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    .paciente-card.pendente {
        border-left-color: #EF6C00;
        background: #fff8e1;
    }
    .paciente-card.avaliado {
        border-left-color: #2E7D32;
        background: #e8f5e9;
    }
    .paciente-card.alto-risco {
        border-left-color: #C62828;
        background: #ffebee;
    }
    
    /* Cards de risco */
    .risk-high {
        background: linear-gradient(135deg, #ffebee, #ffcdd2);
        border-left: 8px solid #c62828;
        padding: 20px;
        border-radius: 12px;
        margin: 10px 0;
        box-shadow: 0 4px 15px rgba(198, 40, 40, 0.1);
    }
    .risk-medium {
        background: linear-gradient(135deg, #fff3e0, #ffe0b2);
        border-left: 8px solid #ef6c00;
        padding: 20px;
        border-radius: 12px;
        margin: 10px 0;
        box-shadow: 0 4px 15px rgba(239, 108, 0, 0.1);
    }
    .risk-low {
        background: linear-gradient(135deg, #e8f5e9, #c8e6c9);
        border-left: 8px solid #2e7d32;
        padding: 20px;
        border-radius: 12px;
        margin: 10px 0;
        box-shadow: 0 4px 15px rgba(46, 125, 50, 0.1);
    }
    
    /* Badges */
    .badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        margin: 3px;
    }
    .badge-success {
        background: #c8e6c9;
        color: #2e7d32;
    }
    .badge-warning {
        background: #ffe0b2;
        color: #e65100;
    }
    .badge-danger {
        background: #ffcdd2;
        color: #c62828;
    }
    .badge-info {
        background: #bbdefb;
        color: #0D47A1;
    }
    .badge-pendente {
        background: #fff3e0;
        color: #e65100;
        border: 1px solid #ffb74d;
    }
    .badge-avaliado {
        background: #e8f5e9;
        color: #2e7d32;
        border: 1px solid #81c784;
    }
    
    /* Medicamento item */
    .medicamento-item {
        background: white;
        padding: 10px 15px;
        border-radius: 8px;
        margin: 5px 0;
        border: 1px solid #e0e0e0;
        border-left: 4px solid #1565C0;
    }
    
    /* Info box */
    .info-box {
        background: #e3f2fd;
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
        border-left: 4px solid #1565C0;
    }
    
    /* Stats */
    .stat-box {
        background: white;
        padding: 15px;
        border-radius: 10px;
        text-align: center;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        border: 1px solid #e0e0e0;
    }
    .stat-box .number {
        font-size: 2rem;
        font-weight: 700;
        color: #0D47A1;
    }
    .stat-box .label {
        font-size: 0.9rem;
        color: #666;
    }
    </style>
    """, unsafe_allow_html=True)

# ========== FUNÇÃO PARA CALCULAR IDADE ==========
def calcular_idade(data_nascimento):
    hoje = datetime.now().date()
    if data_nascimento <= hoje:
        meses = (hoje.year - data_nascimento.year) * 12 + (hoje.month - data_nascimento.month)
        if hoje.day < data_nascimento.day:
            meses -= 1
        return max(0, meses)
    return 0

# ========== FUNÇÃO PRINCIPAL ==========
def render_medico():
    # Aplicar CSS
    aplicar_css()
    
    # ===== TÍTULO =====
    st.title("👨‍⚕️ Médico - Consulta Nutricional")
    st.markdown("""
    <p style='color: #555; margin-bottom: 2rem;'>
    Avaliação médica, diagnóstico, prescrição e encaminhamento
    </p>
    """, unsafe_allow_html=True)
    
    # ===== INICIALIZAR SESSION STATE =====
    if 'criancas' not in st.session_state:
        if SUPABASE_AVAILABLE:
            sucesso, dados = carregar_criancas_supabase()
            if sucesso and dados:
                st.session_state.criancas = dados
                st.success(f"✅ {len(dados)} registos carregados do Supabase!")
            else:
                st.session_state.criancas = []
        else:
            st.session_state.criancas = []
    
    if 'exames_laboratorio' not in st.session_state:
        st.session_state.exames_laboratorio = {}
    
    if 'diagnosticos' not in st.session_state:
        st.session_state.diagnosticos = {}
    
    if 'prescricoes' not in st.session_state:
        st.session_state.prescricoes = {}
    
    if 'encaminhamentos' not in st.session_state:
        st.session_state.encaminhamentos = []
    
    if 'pacientes_avaliados' not in st.session_state:
        st.session_state.pacientes_avaliados = []
    
    if 'paciente_selecionado' not in st.session_state:
        st.session_state.paciente_selecionado = None
    
    if 'aba_ativa' not in st.session_state:
        st.session_state.aba_ativa = "Dashboard"
    
    # ===== ESTATÍSTICAS RÁPIDAS =====
    total = len(st.session_state.criancas)
    pendentes = len([c for c in st.session_state.criancas if c.get('nome_completo') not in st.session_state.pacientes_avaliados])
    avaliados = len(st.session_state.pacientes_avaliados)
    
    alto = len([c for c in st.session_state.criancas if c.get('risco_anemia_nivel') == 'ALTO'])
    medio = len([c for c in st.session_state.criancas if c.get('risco_anemia_nivel') == 'MEDIO'])
    baixo = len([c for c in st.session_state.criancas if c.get('risco_anemia_nivel') == 'BAIXO'])
    
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.markdown(f"""
        <div class="stat-box">
            <div class="number">{total}</div>
            <div class="label">👶 Total</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="stat-box" style="border-color: #EF6C00;">
            <div class="number" style="color: #EF6C00;">{pendentes}</div>
            <div class="label">⏳ Pendentes</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div class="stat-box" style="border-color: #2E7D32;">
            <div class="number" style="color: #2E7D32;">{avaliados}</div>
            <div class="label">✅ Avaliados</div>
        </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown(f"""
        <div class="stat-box" style="border-color: #C62828;">
            <div class="number" style="color: #C62828;">{alto}</div>
            <div class="label">🔴 Alto Risco</div>
        </div>
        """, unsafe_allow_html=True)
    with col5:
        st.markdown(f"""
        <div class="stat-box" style="border-color: #2E7D32;">
            <div class="number" style="color: #2E7D32;">{baixo}</div>
            <div class="label">🟢 Baixo Risco</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # ===== MENU DE NAVEGAÇÃO =====
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("📋 Todos", use_container_width=True):
            st.session_state.aba_ativa = "Todos"
            st.rerun()
    
    with col2:
        if st.button(f"⏳ Pendentes ({pendentes})", use_container_width=True):
            st.session_state.aba_ativa = "Pendentes"
            st.rerun()
    
    with col3:
        if st.button(f"✅ Avaliados ({avaliados})", use_container_width=True):
            st.session_state.aba_ativa = "Avaliados"
            st.rerun()
    
    with col4:
        if st.button("🩺 Consulta", use_container_width=True):
            st.session_state.aba_ativa = "Consulta"
            st.rerun()
    
    st.markdown("---")
    
    # ===== CONTEÚDO =====
    if st.session_state.aba_ativa == "Todos":
        mostrar_todos()
    elif st.session_state.aba_ativa == "Pendentes":
        mostrar_pendentes()
    elif st.session_state.aba_ativa == "Avaliados":
        mostrar_avaliados()
    elif st.session_state.aba_ativa == "Consulta":
        mostrar_consulta()
    else:
        mostrar_dashboard()

# ========== DASHBOARD ==========
def mostrar_dashboard():
    st.markdown('<div class="section-title">📊 Últimos Pacientes</div>', unsafe_allow_html=True)
    
    if not st.session_state.criancas:
        st.info("📋 Nenhum paciente registado ainda.")
        return
    
    ultimos = st.session_state.criancas[-5:] if len(st.session_state.criancas) > 5 else st.session_state.criancas
    
    for crianca in reversed(ultimos):
        nome = crianca.get('nome_completo', 'Sem nome')
        idade = crianca.get('idade_meses', 0)
        risco = crianca.get('risco_anemia_nivel', 'N/A')
        avaliado = nome in st.session_state.pacientes_avaliados
        
        classe = "paciente-card"
        if avaliado:
            classe += " avaliado"
        elif risco == "ALTO":
            classe += " alto-risco"
        else:
            classe += " pendente"
        
        st.markdown(f"""
        <div class="{classe}">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <strong>👶 {nome}</strong>
                    <span style="color: #666; margin-left: 10px;">{idade} meses</span>
                    <span class="badge {'badge-avaliado' if avaliado else 'badge-pendente'}">
                        {'✅ Avaliado' if avaliado else '⏳ Pendente'}
                    </span>
                    <span class="badge {'badge-danger' if risco == 'ALTO' else 'badge-warning' if risco == 'MEDIO' else 'badge-success'}">
                        {risco}
                    </span>
                </div>
                <div>
                    <span style="color: #999; font-size: 0.85rem;">
                        📍 {crianca.get('provincia', 'N/A')}
                    </span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

# ========== TODOS OS PACIENTES ==========
def mostrar_todos():
    st.markdown('<div class="section-title">📋 Todos os Pacientes</div>', unsafe_allow_html=True)
    
    if not st.session_state.criancas:
        st.info("📋 Nenhum paciente registado.")
        return
    
    # Filtros
    col1, col2, col3 = st.columns(3)
    with col1:
        filtro_status = st.selectbox("Status", ["Todos", "Pendente", "Avaliado"])
    with col2:
        filtro_risco = st.selectbox("Risco", ["Todos", "ALTO", "MEDIO", "BAIXO"])
    with col3:
        busca = st.text_input("🔍 Buscar", placeholder="Nome...")
    
    # Filtrar
    dados = st.session_state.criancas
    
    if filtro_status == "Pendente":
        dados = [c for c in dados if c.get('nome_completo') not in st.session_state.pacientes_avaliados]
    elif filtro_status == "Avaliado":
        dados = [c for c in dados if c.get('nome_completo') in st.session_state.pacientes_avaliados]
    
    if filtro_risco != "Todos":
        dados = [c for c in dados if c.get('risco_anemia_nivel') == filtro_risco]
    
    if busca:
        dados = [c for c in dados if busca.lower() in c.get('nome_completo', '').lower()]
    
    st.write(f"**{len(dados)}** pacientes encontrados")
    
    for idx, crianca in enumerate(dados):
        nome = crianca.get('nome_completo', 'Sem nome')
        idade = crianca.get('idade_meses', 0)
        risco = crianca.get('risco_anemia_nivel', 'N/A')
        avaliado = nome in st.session_state.pacientes_avaliados
        
        classe = "paciente-card"
        if avaliado:
            classe += " avaliado"
        elif risco == "ALTO":
            classe += " alto-risco"
        else:
            classe += " pendente"
        
        with st.expander(f"👶 {nome} - {idade} meses - {risco}"):
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(f"""
                <div class="{classe}" style="margin: 0;">
                    <div style="display: flex; gap: 10px; flex-wrap: wrap; margin-bottom: 10px;">
                        <span class="badge {'badge-avaliado' if avaliado else 'badge-pendente'}">
                            {'✅ Avaliado' if avaliado else '⏳ Pendente'}
                        </span>
                        <span class="badge {'badge-danger' if risco == 'ALTO' else 'badge-warning' if risco == 'MEDIO' else 'badge-success'}">
                            {risco}
                        </span>
                    </div>
                    <p><strong>📍 Província:</strong> {crianca.get('provincia', 'N/A')}</p>
                    <p><strong>📏 MUAC:</strong> {crianca.get('muac', 'N/A')} mm</p>
                    <p><strong>⚖️ Peso:</strong> {crianca.get('peso', 'N/A')} kg | 
                    <strong>📐 Altura:</strong> {crianca.get('altura', 'N/A')} cm</p>
                    <p><strong>📅 Registo:</strong> {crianca.get('data_registo', 'N/A')}</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                if not avaliado:
                    if st.button("🩺 Atender", key=f"atender_{idx}", use_container_width=True):
                        st.session_state.paciente_selecionado = crianca
                        st.session_state.aba_ativa = "Consulta"
                        st.rerun()
                else:
                    if st.button("📋 Detalhes", key=f"detalhes_{idx}", use_container_width=True):
                        st.session_state.paciente_selecionado = crianca
                        st.session_state.aba_ativa = "Consulta"
                        st.rerun()

# ========== PACIENTES PENDENTES ==========
def mostrar_pendentes():
    st.markdown('<div class="section-title">⏳ Pacientes Pendentes</div>', unsafe_allow_html=True)
    
    pendentes = [c for c in st.session_state.criancas if c.get('nome_completo') not in st.session_state.pacientes_avaliados]
    
    if not pendentes:
        st.success("✅ Todos os pacientes foram avaliados! 🎉")
        return
    
    # Contagem por risco
    alto = len([c for c in pendentes if c.get('risco_anemia_nivel') == 'ALTO'])
    medio = len([c for c in pendentes if c.get('risco_anemia_nivel') == 'MEDIO'])
    baixo = len([c for c in pendentes if c.get('risco_anemia_nivel') == 'BAIXO'])
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("🔴 Alto Risco", alto)
    with col2:
        st.metric("🟠 Médio Risco", medio)
    with col3:
        st.metric("🟢 Baixo Risco", baixo)
    
    # Busca
    busca = st.text_input("🔍 Buscar paciente", placeholder="Digite o nome...")
    
    if busca:
        pendentes = [c for c in pendentes if busca.lower() in c.get('nome_completo', '').lower()]
    
    st.write(f"**{len(pendentes)}** pacientes pendentes")
    
    for idx, crianca in enumerate(pendentes):
        nome = crianca.get('nome_completo', 'Sem nome')
        idade = crianca.get('idade_meses', 0)
        risco = crianca.get('risco_anemia_nivel', 'N/A')
        
        classe = "paciente-card pendente"
        if risco == "ALTO":
            classe += " alto-risco"
        
        with st.expander(f"⏳ {nome} - {idade} meses - Risco: {risco}", expanded=risco=="ALTO"):
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(f"""
                <div class="{classe}" style="margin: 0;">
                    <p><strong>📍 Província:</strong> {crianca.get('provincia', 'N/A')}</p>
                    <p><strong>📏 MUAC:</strong> {crianca.get('muac', 'N/A')} mm</p>
                    <p><strong>⚖️ Peso:</strong> {crianca.get('peso', 'N/A')} kg</p>
                    <p><strong>📅 Registo:</strong> {crianca.get('data_registo', 'N/A')}</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                if st.button("🩺 Atender", key=f"atender_pendente_{idx}", use_container_width=True):
                    st.session_state.paciente_selecionado = crianca
                    st.session_state.aba_ativa = "Consulta"
                    st.rerun()

# ========== PACIENTES AVALIADOS ==========
def mostrar_avaliados():
    st.markdown('<div class="section-title">✅ Pacientes Avaliados</div>', unsafe_allow_html=True)
    
    avaliados = [c for c in st.session_state.criancas if c.get('nome_completo') in st.session_state.pacientes_avaliados]
    
    if not avaliados:
        st.info("📋 Nenhum paciente avaliado ainda.")
        return
    
    # Busca
    busca = st.text_input("🔍 Buscar paciente", placeholder="Digite o nome...")
    
    if busca:
        avaliados = [c for c in avaliados if busca.lower() in c.get('nome_completo', '').lower()]
    
    st.write(f"**{len(avaliados)}** pacientes avaliados")
    
    for idx, crianca in enumerate(avaliados):
        nome = crianca.get('nome_completo', 'Sem nome')
        idade = crianca.get('idade_meses', 0)
        risco = crianca.get('risco_anemia_nivel', 'N/A')
        
        diag = st.session_state.diagnosticos.get(nome, {})
        presc = st.session_state.prescricoes.get(nome, {})
        
        with st.expander(f"✅ {nome} - {idade} meses"):
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(f"""
                <div class="paciente-card avaliado" style="margin: 0;">
                    <div style="display: flex; gap: 10px; flex-wrap: wrap; margin-bottom: 10px;">
                        <span class="badge badge-avaliado">✅ Avaliado</span>
                        <span class="badge {'badge-danger' if risco == 'ALTO' else 'badge-warning' if risco == 'MEDIO' else 'badge-success'}">
                            {risco}
                        </span>
                        {f'<span class="badge badge-info">💊 {len(presc.get("medicamentos", []))} medicamentos</span>' if presc else ''}
                    </div>
                    <p><strong>📋 Diagnóstico:</strong> {diag.get('diagnostico', 'N/A')}</p>
                    <p><strong>📅 Data:</strong> {diag.get('data', 'N/A')}</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                if st.button("📋 Ver", key=f"ver_avaliado_{idx}", use_container_width=True):
                    st.session_state.paciente_selecionado = crianca
                    st.session_state.aba_ativa = "Consulta"
                    st.rerun()

# ========== CONSULTA MÉDICA ==========
def mostrar_consulta():
    st.markdown('<div class="section-title">🩺 Consulta Médica</div>', unsafe_allow_html=True)
    
    # Selecionar paciente
    if st.session_state.paciente_selecionado:
        dados = st.session_state.paciente_selecionado
    else:
        nomes = [c.get('nome_completo', 'Sem nome') for c in st.session_state.criancas]
        if nomes:
            nome = st.selectbox("Selecione o paciente:", nomes)
            for c in st.session_state.criancas:
                if c.get('nome_completo') == nome:
                    dados = c
                    break
        else:
            st.warning("⚠️ Nenhum paciente registado.")
            return
    
    if not dados:
        st.warning("⚠️ Paciente não encontrado.")
        return
    
    nome = dados.get('nome_completo')
    avaliado = nome in st.session_state.pacientes_avaliados
    
    # ===== DADOS DO PACIENTE =====
    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown(f"""
        <div style="background: { '#e8f5e9' if avaliado else '#fff3e0' }; 
                    padding: 20px; 
                    border-radius: 15px; 
                    margin-bottom: 20px;
                    border-left: 5px solid { '#2E7D32' if avaliado else '#EF6C00' };">
            <h3 style="color: { '#2E7D32' if avaliado else '#EF6C00' }; margin: 0;">
                { '✅' if avaliado else '⏳' } {dados.get('nome_completo')}
            </h3>
            <p><strong>Idade:</strong> {dados.get('idade_meses')} meses | 
            <strong>Sexo:</strong> {dados.get('sexo')} | 
            <strong>Província:</strong> {dados.get('provincia')}</p>
            <p><strong>Peso:</strong> {dados.get('peso')} kg | 
            <strong>Altura:</strong> {dados.get('altura')} cm | 
            <strong>MUAC:</strong> {dados.get('muac')} mm</p>
            <p style="font-weight: bold; color: { '#2E7D32' if avaliado else '#EF6C00' };">
                Status: { '✅ Avaliado' if avaliado else '⏳ Pendente' }
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        risco = dados.get('risco_anemia_nivel', 'N/A')
        if risco == 'ALTO':
            st.error("🔴 Alto Risco")
        elif risco == 'MEDIO':
            st.warning("🟠 Médio Risco")
        else:
            st.success("🟢 Baixo Risco")
        
        if not avaliado:
            if st.button("✅ Marcar Avaliado", use_container_width=True):
                if nome not in st.session_state.pacientes_avaliados:
                    st.session_state.pacientes_avaliados.append(nome)
                    st.success(f"✅ {nome} marcado como avaliado!")
                    st.rerun()
    
    # ===== EXAMES =====
    st.markdown('<div class="section-title">🧪 Exames Laboratoriais</div>', unsafe_allow_html=True)
    
    with st.form("form_exames"):
        col1, col2, col3 = st.columns(3)
        with col1:
            hemoglobina = st.number_input("Hemoglobina (g/dL)", 0.0, 20.0, 10.0, 0.1)
            ferritina = st.number_input("Ferritina (ng/mL)", 0.0, 500.0, 30.0, 1.0)
        with col2:
            hematocrito = st.number_input("Hematócrito (%)", 0.0, 60.0, 35.0, 0.5)
            ferro = st.number_input("Ferro Sérico (µg/dL)", 0, 300, 60, 5)
        with col3:
            albumina = st.number_input("Albumina (g/dL)", 0.0, 6.0, 3.5, 0.1)
            proteinas = st.number_input("Proteínas Totais (g/dL)", 0.0, 10.0, 6.0, 0.1)
        
        hemoglobina_enfermeiro = st.text_area(
            "🩸 Hemoglobina - Informação do Enfermeiro",
            placeholder="Resultado da hemoglobina conforme informação recebida...",
            height=60
        )
        
        if st.form_submit_button("💾 Salvar Exames", use_container_width=True):
            st.session_state.exames_laboratorio[nome] = {
                'hemoglobina': hemoglobina,
                'ferritina': ferritina,
                'hematocrito': hematocrito,
                'ferro': ferro,
                'albumina': albumina,
                'proteinas': proteinas,
                'hemoglobina_enfermeiro': hemoglobina_enfermeiro,
                'data': datetime.now().strftime('%Y-%m-%d %H:%M')
            }
            st.success("✅ Exames salvos!")
    
    # ===== DIAGNÓSTICO =====
    st.markdown('<div class="section-title">📋 Diagnóstico</div>', unsafe_allow_html=True)
    
    with st.form("form_diagnostico"):
        col1, col2 = st.columns(2)
        with col1:
            diagnostico = st.text_area("Diagnóstico", placeholder="Diagnóstico principal...", height=80)
            cid = st.text_input("CID-10", placeholder="Ex: D50.9")
        with col2:
            gravidade = st.selectbox("Gravidade", ["Leve", "Moderada", "Grave", "Crítica"])
            conduta = st.text_area("Conduta", placeholder="Conduta médica...", height=80)
        
        if st.form_submit_button("💾 Salvar Diagnóstico", use_container_width=True):
            if diagnostico and conduta:
                st.session_state.diagnosticos[nome] = {
                    'diagnostico': diagnostico,
                    'cid': cid,
                    'gravidade': gravidade,
                    'conduta': conduta,
                    'data': datetime.now().strftime('%Y-%m-%d %H:%M')
                }
                st.success("✅ Diagnóstico salvo!")
                if nome not in st.session_state.pacientes_avaliados:
                    st.session_state.pacientes_avaliados.append(nome)
                    st.success(f"✅ {nome} marcado como avaliado!")
                    st.rerun()
            else:
                st.warning("⚠️ Preencha diagnóstico e conduta.")
    
    # ===== PRESCRIÇÃO =====
    st.markdown('<div class="section-title">💊 Prescrição</div>', unsafe_allow_html=True)
    
    with st.form("form_prescricao"):
        num = st.number_input("Número de medicamentos", 0, 10, 1, step=1)
        
        medicamentos = []
        for i in range(num):
            st.markdown(f"**Medicamento {i+1}**")
            col1, col2, col3 = st.columns(3)
            with col1:
                nome_med = st.text_input("Nome", placeholder="Sulfato Ferroso", key=f"med_{i}")
            with col2:
                dosagem = st.text_input("Dosagem", placeholder="200mg", key=f"dos_{i}")
            with col3:
                frequencia = st.text_input("Frequência", placeholder="1x/dia", key=f"freq_{i}")
            
            col1, col2 = st.columns(2)
            with col1:
                duracao = st.text_input("Duração", placeholder="30 dias", key=f"dur_{i}")
            with col2:
                via = st.selectbox("Via", ["Oral", "IV", "IM", "SC", "Tópica"], key=f"via_{i}")
            
            if nome_med and dosagem:
                medicamentos.append({
                    'nome': nome_med,
                    'dosagem': dosagem,
                    'frequencia': frequencia,
                    'duracao': duracao,
                    'via': via
                })
            st.divider()
        
        obs = st.text_area("Observações", placeholder="Instruções adicionais...", height=60)
        
        if st.form_submit_button("💾 Salvar Prescrição", use_container_width=True):
            if medicamentos:
                st.session_state.prescricoes[nome] = {
                    'medicamentos': medicamentos,
                    'observacoes': obs,
                    'data': datetime.now().strftime('%Y-%m-%d %H:%M')
                }
                st.success("✅ Prescrição salva!")
            else:
                st.warning("⚠️ Adicione pelo menos um medicamento.")
    
    # ===== ENCAMINHAMENTOS =====
    st.markdown('<div class="section-title">🔄 Encaminhamentos</div>', unsafe_allow_html=True)
    
    with st.form("form_encaminhamento"):
        col1, col2, col3 = st.columns(3)
        with col1:
            enc_agro = st.checkbox("👨‍🌾 Agrônomo")
        with col2:
            enc_nutri = st.checkbox("👩‍⚕️ Nutricionista")
        with col3:
            enc_psico = st.checkbox("🧠 Psicólogo")
        
        motivo = st.text_area("Motivo", placeholder="Descreva o motivo...", height=60)
        
        if st.form_submit_button("🔄 Encaminhar", use_container_width=True):
            if enc_agro or enc_nutri or enc_psico:
                if enc_agro:
                    st.session_state.encaminhamentos.append({
                        'paciente': nome,
                        'profissional': 'Agrônomo',
                        'motivo': motivo or 'Avaliação da produção agrícola',
                        'data': datetime.now().strftime('%Y-%m-%d %H:%M'),
                        'status': 'Pendente'
                    })
                if enc_nutri:
                    st.session_state.encaminhamentos.append({
                        'paciente': nome,
                        'profissional': 'Nutricionista',
                        'motivo': motivo or 'Avaliação nutricional',
                        'data': datetime.now().strftime('%Y-%m-%d %H:%M'),
                        'status': 'Pendente'
                    })
                if enc_psico:
                    st.session_state.encaminhamentos.append({
                        'paciente': nome,
                        'profissional': 'Psicólogo',
                        'motivo': motivo or 'Apoio psicológico',
                        'data': datetime.now().strftime('%Y-%m-%d %H:%M'),
                        'status': 'Pendente'
                    })
                st.success(f"✅ {nome} encaminhado com sucesso!")
                st.balloons()
            else:
                st.warning("⚠️ Selecione pelo menos um profissional.")
    
    # ===== VOLTAR =====
    st.markdown("---")
    if st.button("🏠 Voltar", use_container_width=True):
        st.session_state.aba_ativa = "Dashboard"
        st.session_state.paciente_selecionado = None
        st.rerun()

# ===== PONTO DE ENTRADA =====
if __name__ == "__main__":
    render_medico()