# pages/agronomo.py
# ===== PERFIL AGRÔNOMO - INTERVENÇÃO AGROALIMENTAR =====

import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import json
import base64
import time
import sys
import os

# Adicionar o diretório pai ao path para importar funções
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from app import t, SUPABASE_AVAILABLE
from supabase_client import (
    carregar_criancas_supabase,
    carregar_encaminhamentos_supabase,
    atualizar_status_encaminhamento_supabase,
    salvar_plano_intervencao_agro_supabase,
    salvar_avaliacao_agro_supabase
)

# ========== CONEXÃO SUPABASE ==========
try:
    from supabase import create_client
    SUPABASE_URL = "https://llfcnigfidoiyhaitala.supabase.co"
    SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImxsZmNuaWdmaWRvaXloYWl0YWxhIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODM2NTY2OTYsImV4cCI6MjA5OTIzMjY5Nn0.-WtmiDwYPS9eQDRsQ-bmXGKzvy4p9x7i9bzYGCgX3VM"
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    SUPABASE_AVAILABLE = True
    print("✅ Supabase conectado!")
except Exception as e:
    SUPABASE_AVAILABLE = False
    print(f"❌ Erro: {e}")

def carregar_encaminhamentos_agronomo():
    """Carrega todos os encaminhamentos do Supabase"""
    if not SUPABASE_AVAILABLE:
        return False, []
    try:
        resultado = supabase.table('encaminhamentos').select('*').order('created_at', desc=True).execute()
        return True, resultado.data
    except Exception as e:
        return False, str(e)

def obter_dados_encaminhamento(encaminhamento):
    """Extrai os dados do encaminhamento de forma segura"""
    dados = encaminhamento.get('dados_clinicos', {})
    if isinstance(dados, str):
        try:
            dados = json.loads(dados)
        except:
            dados = {}
    return dados

# ========== FUNÇÕES PARA CALCULAR ÍNDICES ==========
def calcular_indices(respostas):
    """Calcula todos os índices baseado nas respostas do formulário"""
    
    indices = {}
    
    # 1. Índice de Resiliência Climática Agrícola
    resiliencia = 0
    
    if respostas.get('disponibilidade_agua') in ['Suficiente todo o ano', 'Apenas na época chuvosa']:
        resiliencia += 25
    elif respostas.get('disponibilidade_agua') == 'Insuficiente':
        resiliencia += 10
    else:
        resiliencia += 5
    
    if respostas.get('exposicao_climatica') == 'Nenhum':
        resiliencia += 25
    elif respostas.get('exposicao_climatica') in ['Seca', 'Cheias', 'Ciclones']:
        resiliencia += 10
    else:
        resiliencia += 5
    
    if respostas.get('estado_solo') in ['Solo fértil com conservação', 'Solo moderado com alguma conservação']:
        resiliencia += 25
    elif respostas.get('estado_solo') == 'Solo degradado':
        resiliencia += 10
    else:
        resiliencia += 5
    
    if respostas.get('sistema_producao') == 'Produção diversificada com variedades resilientes':
        resiliencia += 25
    elif respostas.get('sistema_producao') == 'Diversificada sem variedades resilientes':
        resiliencia += 15
    elif respostas.get('sistema_producao') == 'Monocultura':
        resiliencia += 10
    else:
        resiliencia += 5
    
    indices['Resiliência Climática'] = min(100, resiliencia)
    
    # 2. Índice de Vulnerabilidade à Seca
    vulnerabilidade_seca = 0
    
    if respostas.get('disponibilidade_agua') in ['Insuficiente', 'Sem fonte permanente de água']:
        vulnerabilidade_seca += 30
    elif respostas.get('disponibilidade_agua') == 'Apenas na época chuvosa':
        vulnerabilidade_seca += 20
    
    if respostas.get('exposicao_climatica') in ['Seca', 'Múltiplos eventos']:
        vulnerabilidade_seca += 30
    
    if respostas.get('estado_solo') in ['Solo degradado', 'Erosão severa sem conservação']:
        vulnerabilidade_seca += 20
    
    if respostas.get('sistema_producao') in ['Monocultura', 'Produção muito reduzida']:
        vulnerabilidade_seca += 20
    
    indices['Vulnerabilidade à Seca'] = min(100, vulnerabilidade_seca)
    
    # 3. Índice de Vulnerabilidade a Cheias
    vulnerabilidade_cheias = 0
    
    if respostas.get('exposicao_climatica') in ['Cheias', 'Múltiplos eventos']:
        vulnerabilidade_cheias += 35
    
    if respostas.get('estado_solo') in ['Solo degradado', 'Erosão severa sem conservação']:
        vulnerabilidade_cheias += 30
    
    if respostas.get('disponibilidade_agua') in ['Insuficiente', 'Sem fonte permanente de água']:
        vulnerabilidade_cheias += 20
    
    if respostas.get('sistema_producao') in ['Monocultura', 'Produção muito reduzida']:
        vulnerabilidade_cheias += 15
    
    indices['Vulnerabilidade a Cheias'] = min(100, vulnerabilidade_cheias)
    
    # 4. Índice de Degradação do Solo
    degradacao_solo = 0
    
    if respostas.get('estado_solo') == 'Erosão severa sem conservação':
        degradacao_solo += 40
    elif respostas.get('estado_solo') == 'Solo degradado':
        degradacao_solo += 30
    elif respostas.get('estado_solo') == 'Solo moderado com alguma conservação':
        degradacao_solo += 15
    
    if respostas.get('sistema_producao') in ['Monocultura', 'Produção muito reduzida']:
        degradacao_solo += 25
    
    if respostas.get('capacidade_adaptativa') == 'Nenhum recurso de adaptação':
        degradacao_solo += 20
    
    if respostas.get('impacto_producao') in ['Perdas >50% ou produção insuficiente', 'Perdas 25–50%']:
        degradacao_solo += 15
    
    indices['Degradação do Solo'] = min(100, degradacao_solo)
    
    # 5. Índice de Segurança Hídrica
    seguranca_hidrica = 0
    
    if respostas.get('disponibilidade_agua') == 'Suficiente todo o ano':
        seguranca_hidrica += 40
    elif respostas.get('disponibilidade_agua') == 'Apenas na época chuvosa':
        seguranca_hidrica += 25
    elif respostas.get('disponibilidade_agua') == 'Insuficiente':
        seguranca_hidrica += 15
    else:
        seguranca_hidrica += 5
    
    if respostas.get('capacidade_adaptativa') in ['Irrigação + assistência técnica + informação climática', 'Apenas um ou dois destes recursos']:
        seguranca_hidrica += 30
    
    if respostas.get('impacto_producao') in ['Produção suficiente sem perdas', 'Perdas <25%']:
        seguranca_hidrica += 30
    elif respostas.get('impacto_producao') == 'Perdas 25–50%':
        seguranca_hidrica += 15
    else:
        seguranca_hidrica += 5
    
    indices['Segurança Hídrica'] = min(100, seguranca_hidrica)
    
    # 6. Índice de Diversificação da Produção
    diversificacao = 0
    
    if respostas.get('sistema_producao') == 'Produção diversificada com variedades resilientes':
        diversificacao += 50
    elif respostas.get('sistema_producao') == 'Diversificada sem variedades resilientes':
        diversificacao += 35
    elif respostas.get('sistema_producao') == 'Monocultura':
        diversificacao += 15
    else:
        diversificacao += 5
    
    if respostas.get('estado_solo') in ['Solo fértil com conservação', 'Solo moderado com alguma conservação']:
        diversificacao += 25
    
    if respostas.get('capacidade_adaptativa') in ['Irrigação + assistência técnica + informação climática', 'Apenas um ou dois destes recursos']:
        diversificacao += 25
    
    indices['Diversificação da Produção'] = min(100, diversificacao)
    
    # 7. Índice de Adoção de Agricultura Inteligente (CSA)
    csa = 0
    
    if respostas.get('estado_solo') in ['Solo fértil com conservação', 'Solo moderado com alguma conservação']:
        csa += 30
    
    if respostas.get('sistema_producao') == 'Produção diversificada com variedades resilientes':
        csa += 30
    elif respostas.get('sistema_producao') == 'Diversificada sem variedades resilientes':
        csa += 15
    
    if respostas.get('capacidade_adaptativa') == 'Irrigação + assistência técnica + informação climática':
        csa += 25
    elif respostas.get('capacidade_adaptativa') == 'Apenas um ou dois destes recursos':
        csa += 15
    
    if respostas.get('impacto_producao') in ['Produção suficiente sem perdas', 'Perdas <25%']:
        csa += 15
    
    indices['Agricultura Inteligente (CSA)'] = min(100, csa)
    
    # 8. Índice de Capacidade Adaptativa da Família
    capacidade_adaptativa = 0
    
    if respostas.get('capacidade_adaptativa') == 'Irrigação + assistência técnica + informação climática':
        capacidade_adaptativa += 50
    elif respostas.get('capacidade_adaptativa') == 'Apenas um ou dois destes recursos':
        capacidade_adaptativa += 30
    else:
        capacidade_adaptativa += 10
    
    if respostas.get('sistema_producao') == 'Produção diversificada com variedades resilientes':
        capacidade_adaptativa += 25
    
    if respostas.get('estado_solo') in ['Solo fértil com conservação', 'Solo moderado com alguma conservação']:
        capacidade_adaptativa += 25
    
    indices['Capacidade Adaptativa'] = min(100, capacidade_adaptativa)
    
    # 9. Índice de Risco Agroalimentar
    risco_agro = 0
    
    if respostas.get('impacto_producao') == 'Perdas >50% ou produção insuficiente':
        risco_agro += 40
    elif respostas.get('impacto_producao') == 'Perdas 25–50%':
        risco_agro += 30
    elif respostas.get('impacto_producao') == 'Perdas <25%':
        risco_agro += 15
    
    if respostas.get('exposicao_climatica') in ['Seca', 'Cheias', 'Ciclones', 'Múltiplos eventos']:
        risco_agro += 25
    
    if respostas.get('disponibilidade_agua') in ['Insuficiente', 'Sem fonte permanente de água']:
        risco_agro += 20
    
    if respostas.get('sistema_producao') in ['Monocultura', 'Produção muito reduzida']:
        risco_agro += 15
    
    indices['Risco Agroalimentar'] = min(100, risco_agro)
    
    # 10. Índice Integrado One Health/Nexus
    one_health = 0
    
    if indices['Resiliência Climática'] >= 50:
        one_health += 15
    if indices['Segurança Hídrica'] >= 50:
        one_health += 15
    if indices['Diversificação da Produção'] >= 50:
        one_health += 15
    if indices['Capacidade Adaptativa'] >= 50:
        one_health += 15
    if indices['Agricultura Inteligente (CSA)'] >= 50:
        one_health += 15
    
    if respostas.get('capacidade_adaptativa') in ['Irrigação + assistência técnica + informação climática', 'Apenas um ou dois destes recursos']:
        one_health += 15
    
    if respostas.get('estado_solo') in ['Solo fértil com conservação', 'Solo moderado com alguma conservação']:
        one_health += 10
    
    indices['Índice Integrado One Health/Nexus'] = min(100, one_health)
    
    return indices

# ========== FUNÇÃO PRINCIPAL ==========
def render_agronomo():
    # ===== CARREGAR DADOS DO SUPABASE =====
    if 'criancas' not in st.session_state or not st.session_state.criancas:
        if SUPABASE_AVAILABLE:
            sucesso, dados = carregar_criancas_supabase()
            if sucesso and dados:
                st.session_state.criancas = dados
                st.success(f"✅ {len(dados)} pacientes carregados do Supabase!")
            else:
                st.session_state.criancas = []
                if dados:
                    st.info(f"ℹ️ {dados}")
        else:
            st.session_state.criancas = []
            st.warning("⚠️ Supabase não disponível")
    
    # ===== CARREGAR ENCAMINHAMENTOS DO SUPABASE =====
    if 'encaminhamentos' not in st.session_state or not st.session_state.encaminhamentos:
        if SUPABASE_AVAILABLE:
            sucesso, dados = carregar_encaminhamentos_agronomo()
            if sucesso and dados:
                st.session_state.encaminhamentos = dados
                st.success(f"✅ {len(dados)} encaminhamentos carregados do Supabase!")
            else:
                st.session_state.encaminhamentos = []
                if dados:
                    st.info(f"ℹ️ {dados}")
        else:
            st.session_state.encaminhamentos = []
            st.warning("⚠️ Supabase não disponível")
    
    # ===== PLANOS DE INTERVENÇÃO AGRONÔMICA =====
    if 'planos_intervencao_agro' not in st.session_state:
        st.session_state.planos_intervencao_agro = []
    
    # ===== AVALIAÇÕES AGRO =====
    if 'avaliacoes_agro' not in st.session_state:
        st.session_state.avaliacoes_agro = []
    
    st.title("👨🏾🌾 Agrônomo - Intervenção Agroalimentar")
    st.markdown("""
    <p style='color: #555; margin-bottom: 2rem;'>
    Avaliação agroalimentar, resiliência climática e planos de intervenção para famílias encaminhadas pelo médico.
    </p>
    """, unsafe_allow_html=True)
    
    # ===== FILTRAR APENAS ENCAMINHAMENTOS PARA AGRÔNOMO =====
    enc_agro = [e for e in st.session_state.encaminhamentos if 'Agrônomo' in e.get('especialidade', '')]
    
    # ===== OBTER LISTA DE PACIENTES ENCAMINHADOS =====
    pacientes_encaminhados = []
    for enc in enc_agro:
        paciente_nome = enc.get('paciente', '')
        if paciente_nome:
            for p in st.session_state.criancas:
                if p.get('nome_completo') == paciente_nome:
                    paciente_data = p.copy()
                    paciente_data['encaminhamento_data'] = enc.get('data', 'N/A')
                    paciente_data['encaminhamento_urgencia'] = enc.get('urgencia', 'Normal')
                    paciente_data['encaminhamento_status'] = enc.get('status', 'Pendente')
                    paciente_data['encaminhamento_motivo'] = enc.get('motivo', 'N/A')
                    pacientes_encaminhados.append(paciente_data)
                    break
    
    # ===== ESTATÍSTICAS =====
    total = len(pacientes_encaminhados)
    pendentes = len([e for e in enc_agro if e.get('status') != 'Concluído'])
    atendidos = len([e for e in enc_agro if e.get('status') == 'Concluído'])
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("📨 Encaminhamentos", total)
    with col2:
        st.metric("⏳ Pendentes", pendentes)
    with col3:
        st.metric("✅ Atendidos", atendidos)
    with col4:
        st.metric("📋 Planos de Intervenção", len(st.session_state.planos_intervencao_agro))
    
    st.markdown("---")
    
    # ============================================================
    # ===== ABAS =====
    # ============================================================
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📋 Avaliação",
        "📝 Plano de Intervenção",
        "📊 Índices",
        "📊 Dashboard",
        "📨 Encaminhamentos"
    ])
    
    # ============================================================
    # ===== TAB 1: AVALIAÇÃO =====
    # ============================================================
    with tab1:
        st.subheader("👤 Selecionar Paciente")
        
        if not pacientes_encaminhados:
            st.info("📋 Nenhum encaminhamento para agrônomo recebido ainda.")
            return
        
        df = pd.DataFrame(pacientes_encaminhados)
        selected = st.selectbox(
            "Selecione o paciente:",
            df['nome_completo'].unique().tolist()
        )
        
        patient_data = df[df['nome_completo'] == selected].iloc[0]
        
        # ===== BUSCAR OS DADOS DO ENCAMINHAMENTO =====
        encaminhamento_data = None
        for enc in enc_agro:
            if enc.get('paciente') == selected:
                encaminhamento_data = enc
                break
        
        # ===== OBTER DADOS CLÍNICOS =====
        dados_clinicos = {}
        if encaminhamento_data:
            dados_clinicos = obter_dados_encaminhamento(encaminhamento_data)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 📊 Dados do Paciente")
            st.markdown(f"**👶 Nome:** {patient_data['nome_completo']}")
            st.markdown(f"**📏 Idade:** {patient_data['idade_meses']} meses")
            st.markdown(f"**⚖️ Peso:** {patient_data['peso']} kg")
            st.markdown(f"**📐 Altura:** {patient_data['altura']} cm")
            st.markdown(f"**📏 MUAC:** {patient_data['muac']} mm")
            st.markdown(f"**📊 DDS:** {patient_data.get('dds_calculado', 0)}/9")
            st.markdown(f"**📍 Província:** {patient_data.get('provincia', 'N/A')}")
            st.markdown(f"**📍 Distrito:** {patient_data.get('distrito', 'N/A')}")
        
        with col2:
            st.markdown("#### 🩺 Risco")
            risco = patient_data.get('risco_anemia_nivel', 'N/A')
            cor = "🔴" if risco == "ALTO" else "🟡" if risco == "MÉDIO" else "🟢"
            st.metric("Risco de Anemia", f"{cor} {risco}")
            st.metric("Fome Oculta", patient_data.get('risco_fome_nivel', 'N/A'))
            st.metric("Insegurança Alimentar", patient_data.get('risco_inseguranca_nivel', 'N/A'))
        
        # ===== MOSTRAR DADOS DO ENCAMINHAMENTO =====
        if dados_clinicos and isinstance(dados_clinicos, dict):
            st.divider()
            st.markdown("### 🌾 Dados do Encaminhamento Médico")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**🌾 Produção Agrícola**")
                st.markdown(f"- Produção Familiar: {dados_clinicos.get('producao_familiar', 'N/A')}")
                st.markdown(f"- Acesso à Terra: {dados_clinicos.get('acesso_terra', 'N/A')}")
                st.markdown(f"- Culturas Produzidas: {dados_clinicos.get('culturas_produzidas', 'N/A')}")
                st.markdown(f"- Fonte de Água: {dados_clinicos.get('fonte_agua', 'N/A')}")
                st.markdown(f"- Dificuldades: {dados_clinicos.get('dificuldades_producao', 'N/A')}")
            
            with col2:
                st.markdown("**📍 Localização**")
                st.markdown(f"- Província: {dados_clinicos.get('provincia', 'N/A')}")
                st.markdown(f"- Distrito: {dados_clinicos.get('distrito', 'N/A')}")
                st.markdown(f"- Residência: {dados_clinicos.get('residencia', 'N/A')}")
                st.markdown(f"- Hospital: {dados_clinicos.get('hospital', 'N/A')}")
                
                st.markdown("**👨‍⚕️ Dados do Médico**")
                st.markdown(f"- Diagnóstico: {dados_clinicos.get('diagnostico_medico', 'N/A')}")
                st.markdown(f"- Seguimento: {dados_clinicos.get('seguimento', 'N/A')}")
        
        st.divider()
        
        # ============================================================
        # ===== FORMULÁRIO DE AVALIAÇÃO AGROALIMENTAR =====
        # ============================================================
        st.markdown("### 🌾 Avaliação de Resiliência Agroalimentar")
        st.markdown("""
        <div style="background-color: #e8f5e9; padding: 10px; border-radius: 8px; margin-bottom: 10px; border-left: 4px solid #2e7d32;">
            <p style="font-size: 0.9rem; color: #555;">
                💡 <strong>Nota:</strong> As perguntas sobre produção familiar, acesso à terra, culturas produzidas, fonte de água e dificuldades já foram respondidas no Enfermeiro.
                Esta secção avalia a <strong>resiliência climática</strong> e <strong>capacidade adaptativa</strong> da família.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        if 'respostas_agro' not in st.session_state:
            st.session_state.respostas_agro = {}
        
        with st.form("form_avaliacao_agro"):
            
            # ===== 1. DISPONIBILIDADE DE ÁGUA =====
            st.markdown("#### 💧 1. Qual é a disponibilidade de água para a produção agrícola?")
            disponibilidade_agua = st.selectbox(
                "Selecione a opção:",
                ["Suficiente todo o ano", "Apenas na época chuvosa", "Insuficiente", "Sem fonte permanente de água"],
                key="disponibilidade_agua"
            )
            
            # ===== 2. EXPOSIÇÃO A EVENTOS CLIMÁTICOS =====
            st.markdown("#### 🌪️ 2. Como classifica a exposição da exploração agrícola a eventos climáticos nos últimos 5 anos?")
            exposicao_climatica = st.selectbox(
                "Selecione a opção:",
                ["Nenhum", "Seca", "Cheias", "Ciclones", "Múltiplos eventos"],
                key="exposicao_climatica"
            )
            
            # ===== 3. ESTADO DO SOLO =====
            st.markdown("#### 🌱 3. Qual é o estado atual do solo e as práticas de conservação?")
            estado_solo = st.selectbox(
                "Selecione a opção:",
                ["Solo fértil com conservação", "Solo moderado com alguma conservação", "Solo degradado", "Erosão severa sem conservação"],
                key="estado_solo"
            )
            
            # ===== 4. SISTEMA DE PRODUÇÃO =====
            st.markdown("#### 🌾 4. Como caracteriza o sistema de produção agrícola?")
            sistema_producao = st.selectbox(
                "Selecione a opção:",
                ["Produção diversificada com variedades resilientes", "Diversificada sem variedades resilientes", "Monocultura", "Produção muito reduzida"],
                key="sistema_producao"
            )
            
            # ===== 5. CAPACIDADE ADAPTATIVA =====
            st.markdown("#### 🧠 5. Qual é o nível de capacidade adaptativa da família agrícola?")
            capacidade_adaptativa = st.selectbox(
                "Selecione a opção:",
                ["Irrigação + assistência técnica + informação climática", "Apenas um ou dois destes recursos", "Nenhum recurso de adaptação"],
                key="capacidade_adaptativa"
            )
            
            # ===== 6. IMPACTO NA SEGURANÇA ALIMENTAR =====
            st.markdown("#### 🍽️ 6. Qual foi o impacto da produção agrícola na segurança alimentar da família nos últimos 12 meses?")
            impacto_producao = st.selectbox(
                "Selecione a opção:",
                ["Produção suficiente sem perdas", "Perdas <25%", "Perdas 25–50%", "Perdas >50% ou produção insuficiente"],
                key="impacto_producao"
            )
            
            st.markdown("---")
            st.caption("📊 Após preencher todas as perguntas, clique em 'Calcular Índices' para obter os resultados.")
            
            if st.form_submit_button("📊 Calcular Índices", use_container_width=True):
                respostas = {
                    'paciente': selected,
                    'disponibilidade_agua': disponibilidade_agua,
                    'exposicao_climatica': exposicao_climatica,
                    'estado_solo': estado_solo,
                    'sistema_producao': sistema_producao,
                    'capacidade_adaptativa': capacidade_adaptativa,
                    'impacto_producao': impacto_producao,
                    'fonte_agua': patient_data.get('fonte_agua', 'N/A'),
                    'producao_familiar': patient_data.get('producao_familiar', 'N/A'),
                    'acesso_terra': patient_data.get('acesso_terra', 'N/A'),
                    'culturas_produzidas': patient_data.get('culturas_produzidas', 'N/A'),
                    'dificuldades_producao': patient_data.get('dificuldades_producao', 'N/A'),
                    'data_avaliacao': datetime.now().strftime('%Y-%m-%d %H:%M')
                }
                
                st.session_state.respostas_agro = respostas
                indices = calcular_indices(respostas)
                st.session_state.indices_agro = indices
                
                # Salvar no Supabase
                if SUPABASE_AVAILABLE:
                    sucesso, resultado = salvar_avaliacao_agro_supabase(respostas)
                    if sucesso:
                        st.success("✅ Índices calculados e avaliação salva no Supabase!")
                    else:
                        st.warning(f"⚠️ Índices calculados, mas erro ao salvar: {resultado}")
                else:
                    st.success("✅ Índices calculados! (Supabase não disponível)")
                
                st.rerun()
    
    # ============================================================
    # ===== TAB 2: PLANO DE INTERVENÇÃO AGRONÔMICA =====
    # ============================================================
    with tab2:
        st.subheader("📝 Plano de Intervenção Agronómica")
        
        if not pacientes_encaminhados:
            st.info("📋 Nenhum encaminhamento para agrônomo recebido ainda.")
            return
        
        df = pd.DataFrame(pacientes_encaminhados)
        selected_plano = st.selectbox(
            "Selecione o paciente:",
            df['nome_completo'].unique().tolist(),
            key="select_plano_agro"
        )
        
        patient_data_plano = df[df['nome_completo'] == selected_plano].iloc[0]
        
        st.markdown(f"#### 👶 {patient_data_plano['nome_completo']}")
        st.markdown(f"**Idade:** {patient_data_plano['idade_meses']} meses")
        st.markdown(f"**📍 Província:** {patient_data_plano.get('provincia', 'N/A')}")
        
        st.divider()
        
        # ===== SELECIONAR TIPO DE PLANO =====
        st.markdown("### 📋 Tipo de Plano de Intervenção")
        
        col1, col2, col3 = st.columns([2, 1, 2])
        
        with col1:
            tipo_plano_temp = st.selectbox(
                "Selecione o tipo de plano:",
                ["Individual", "Familiar", "Comunitário"],
                key=f"tipo_plano_temp_{selected_plano}"
            )
        
        with col2:
            st.write("")
            st.write("")
            if st.button("✅ Aplicar Tipo", key=f"aplicar_tipo_{selected_plano}", use_container_width=True):
                st.session_state[f'tipo_plano_{selected_plano}'] = tipo_plano_temp
                st.rerun()
        
        if f'tipo_plano_{selected_plano}' not in st.session_state:
            st.session_state[f'tipo_plano_{selected_plano}'] = "Individual"
        
        tipo_plano = st.session_state[f'tipo_plano_{selected_plano}']
        
        if tipo_plano == "Individual":
            st.info("👤 **Plano Individual** - Focado numa única criança.")
        elif tipo_plano == "Familiar":
            st.info("👨‍👩‍👧‍👦 **Plano Familiar** - Várias crianças da mesma família.")
        else:
            st.info("🏘️ **Plano Comunitário** - Crianças de diferentes famílias no mesmo bairro.")
        
        st.divider()
        
        with st.form("plano_intervencao_agro_form"):
            # Dados específicos do plano
            if tipo_plano == "Individual":
                st.markdown("### 👤 Plano Individual")
                col1, col2 = st.columns(2)
                with col1:
                    nome_beneficiario = st.text_input("👶 Nome da Criança:", placeholder="Ex: João Silva", key=f"nome_individual_{selected_plano}")
                with col2:
                    idade_beneficiario = st.number_input("📋 Idade (meses):", min_value=0, max_value=60, value=24, step=1, key=f"idade_individual_{selected_plano}")
                n_beneficiarios = 1
            elif tipo_plano == "Familiar":
                st.markdown("### 👨‍👩‍👧‍👦 Plano Familiar")
                col1, col2 = st.columns(2)
                with col1:
                    nome_beneficiario = st.text_input("👨‍👩‍👧‍👦 Nome do Chefe de Família:", placeholder="Ex: Manuel Silva", key=f"nome_familiar_{selected_plano}")
                with col2:
                    n_beneficiarios = st.number_input("👶 Número de crianças na família:", min_value=2, max_value=10, value=2, step=1, key=f"n_beneficiarios_{selected_plano}")
                idade_beneficiario = None
            else:
                st.markdown("### 🏘️ Plano Comunitário")
                col1, col2 = st.columns(2)
                with col1:
                    nome_beneficiario = st.text_input("🏘️ Nome do Bairro/Comunidade:", placeholder="Ex: Bairro Esperança", key=f"nome_comunitario_{selected_plano}")
                with col2:
                    n_beneficiarios = st.number_input("👶 Número de crianças no bairro:", min_value=5, max_value=100, value=5, step=1, key=f"n_beneficiarios_comunitario_{selected_plano}")
                idade_beneficiario = None
            
            st.divider()
            
            # ===== OBJETIVOS =====
            st.markdown("### 🎯 Objetivos da Intervenção Agronómica")
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**📋 Objetivo Principal**")
                objetivo_principal = st.text_area("Objetivo principal da intervenção:", placeholder="Ex: Diversificar a produção agrícola familiar...", height=80, key=f"obj_principal_{selected_plano}")
                st.markdown("**📊 Metas Específicas**")
                metas = st.text_area("Metas específicas:", placeholder="Ex: Aumentar em 30% a diversidade de culturas...", height=80, key=f"metas_{selected_plano}")
            with col2:
                st.markdown("**⏱️ Prazo de Execução**")
                prazo = st.selectbox("Prazo de execução:", ["1 mês", "2 meses", "3 meses", "6 meses", "1 ano"], key=f"prazo_{selected_plano}")
                st.markdown("**📅 Data de Início**")
                data_inicio = st.date_input("Data de início:", value=datetime.now().date(), key=f"data_inicio_{selected_plano}")
            
            st.divider()
            
            # ===== INTERVENÇÕES =====
            st.markdown("### 🌾 Intervenções Agronómicas")
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**🌱 Práticas Agrícolas Recomendadas**")
                praticas_agricolas = st.text_area("Práticas agrícolas recomendadas:", placeholder="Ex: Rotação de culturas, adubação orgânica...", height=100, key=f"praticas_{selected_plano}")
                st.markdown("**🌿 Culturas Recomendadas**")
                culturas = st.text_area("Culturas recomendadas:", placeholder="Ex: Feijão, amendoim, hortícolas...", height=60, key=f"culturas_{selected_plano}")
            with col2:
                st.markdown("**💧 Recomendações de Água**")
                recomendacoes_agua = st.text_area("Recomendações para gestão de água:", placeholder="Ex: Sistemas de irrigação, captação de água da chuva...", height=100, key=f"recomendacoes_agua_{selected_plano}")
                st.markdown("**🧑‍🌾 Formação Técnica**")
                formacao = st.text_area("Formação técnica recomendada:", placeholder="Ex: Formação em técnicas de conservação do solo...", height=60, key=f"formacao_{selected_plano}")
            
            st.divider()
            
            # ===== MONITORAMENTO =====
            st.markdown("### 📊 Monitoramento e Avaliação")
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**📅 Frequência de Monitoramento**")
                frequencia_monitoramento = st.selectbox("Frequência de monitoramento:", ["Semanal", "Quinzenal", "Mensal", "Trimestral"], key=f"freq_monitor_{selected_plano}")
            with col2:
                st.markdown("**📋 Indicadores de Avaliação**")
                indicadores = st.text_area("Indicadores de avaliação:", placeholder="Ex: Número de culturas, produção por hectare...", height=60, key=f"indicadores_{selected_plano}")
            
            st.divider()
            
            # ===== OBSERVAÇÕES =====
            st.markdown("### 📝 Observações Finais")
            observacoes_plano = st.text_area("Observações finais:", placeholder="Informações adicionais sobre a intervenção...", height=80, key=f"obs_plano_{selected_plano}")
            
            # ===== ANEXAR DOCUMENTOS =====
            st.markdown("### 📎 Anexar Documentos")
            uploaded_file = st.file_uploader("Selecionar arquivo (PDF, DOCX, DOC, TXT):", type=['pdf', 'docx', 'doc', 'txt'], key=f"upload_{selected_plano}")
            if uploaded_file is not None:
                st.success(f"✅ Arquivo anexado: {uploaded_file.name}")
                st.info(f"📊 Tamanho: {uploaded_file.size} bytes")
                st.info(f"📁 Tipo: {uploaded_file.type}")
            
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.form_submit_button("💾 Registar Plano de Intervenção", use_container_width=True):
                    if objetivo_principal or praticas_agricolas:
                        novo_plano = {
                            'paciente': selected_plano,
                            'tipo_plano': tipo_plano,
                            'nome_beneficiario': nome_beneficiario,
                            'n_beneficiarios': n_beneficiarios,
                            'idade_beneficiario': idade_beneficiario,
                            'data': datetime.now().strftime('%Y-%m-%d %H:%M'),
                            'objetivo_principal': objetivo_principal,
                            'metas': metas,
                            'prazo': prazo,
                            'data_inicio': data_inicio.strftime('%Y-%m-%d'),
                            'praticas_agricolas': praticas_agricolas,
                            'culturas': culturas,
                            'recomendacoes_agua': recomendacoes_agua,
                            'formacao': formacao,
                            'frequencia_monitoramento': frequencia_monitoramento,
                            'indicadores': indicadores,
                            'observacoes': observacoes_plano,
                            'status': 'Ativo'
                        }
                        if uploaded_file is not None:
                            novo_plano['arquivo_anexado'] = uploaded_file.name
                            novo_plano['arquivo_tipo'] = uploaded_file.type
                            novo_plano['arquivo_tamanho'] = uploaded_file.size
                            novo_plano['arquivo_conteudo'] = uploaded_file.getvalue()
                        
                        # Salvar no Supabase
                        if SUPABASE_AVAILABLE:
                            sucesso, resultado = salvar_plano_intervencao_agro_supabase(novo_plano)
                            if sucesso:
                                st.success(f"✅ Plano de intervenção {tipo_plano} registado para {selected_plano} no Supabase!")
                            else:
                                st.warning(f"⚠️ Erro ao salvar no Supabase: {resultado}")
                        
                        # Salvar localmente
                        st.session_state.planos_intervencao_agro.append(novo_plano)
                        st.success(f"✅ Plano de intervenção {tipo_plano} registado para {selected_plano}!")
                    else:
                        st.warning("⚠️ Preencha pelo menos o objetivo principal ou as práticas agrícolas.")
        
        # ===== LISTA DE PLANOS REGISTADOS =====
        st.divider()
        st.subheader("📋 Planos Registados")
        
        planos_paciente = [p for p in st.session_state.planos_intervencao_agro if p['paciente'] == selected_plano]
        
        if planos_paciente:
            for i, plano in enumerate(planos_paciente):
                icone = "🏘️" if plano.get('tipo_plano') == 'Comunitário' else "👨‍👩‍👧‍👦" if plano.get('tipo_plano') == 'Familiar' else "👤"
                with st.expander(f"{icone} {plano.get('tipo_plano', 'Individual')} - {plano['data']} ({plano.get('status', 'Ativo')})", expanded=False):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown(f"**📋 Tipo:** {plano.get('tipo_plano', 'Individual')}")
                        st.markdown(f"**👶 Nº Beneficiários:** {plano.get('n_beneficiarios', 1)}")
                        if plano.get('tipo_plano') == 'Individual':
                            st.markdown(f"**👶 Nome:** {plano.get('nome_beneficiario', 'N/A')}")
                            st.markdown(f"**📏 Idade:** {plano.get('idade_beneficiario', 'N/A')} meses")
                        elif plano.get('tipo_plano') == 'Familiar':
                            st.markdown(f"**👨‍👩‍👧‍👦 Chefe Família:** {plano.get('nome_beneficiario', 'N/A')}")
                        else:
                            st.markdown(f"**🏘️ Bairro:** {plano.get('nome_beneficiario', 'N/A')}")
                        st.markdown(f"**🎯 Objetivo Principal:** {plano.get('objetivo_principal', 'N/A')}")
                    with col2:
                        st.markdown(f"**🌱 Práticas Agrícolas:** {plano.get('praticas_agricolas', 'N/A')}")
                        st.markdown(f"**🌿 Culturas:** {plano.get('culturas', 'N/A')}")
                        st.markdown(f"**💧 Recomendações Água:** {plano.get('recomendacoes_agua', 'N/A')}")
                        st.markdown(f"**📅 Monitoramento:** {plano.get('frequencia_monitoramento', 'N/A')}")
                    st.markdown(f"**📝 Observações:** {plano.get('observacoes', 'N/A')}")
                    if plano.get('arquivo_anexado'):
                        st.markdown(f"**📎 Arquivo:** {plano['arquivo_anexado']}")
                    st.divider()
                    col1, col2 = st.columns(2)
                    with col1:
                        if plano.get('status') == 'Ativo':
                            if st.button(f"✅ Marcar como Concluído", key=f"concluir_{i}_{selected_plano}"):
                                st.session_state.planos_intervencao_agro[i]['status'] = 'Concluído'
                                st.rerun()
                    with col2:
                        if st.button(f"🗑️ Remover", key=f"remover_{i}_{selected_plano}"):
                            st.session_state.planos_intervencao_agro.pop(i)
                            st.rerun()
        else:
            st.info(f"📋 Nenhum plano registado para {selected_plano}.")
    
    # ============================================================
    # ===== TAB 3: ÍNDICES =====
    # ============================================================
    with tab3:
        if 'indices_agro' in st.session_state and st.session_state.indices_agro:
            st.subheader("📊 Resultados dos Índices")
            
            indices = st.session_state.indices_agro
            
            col1, col2, col3 = st.columns(3)
            
            def card_style(valor, titulo, descricao, icone):
                if valor >= 60:
                    bg = "#c8e6c9"
                    border = "#2e7d32"
                    texto = "✅ Bom"
                elif valor >= 40:
                    bg = "#ffe0b2"
                    border = "#ef6c00"
                    texto = "⚠️ Médio"
                else:
                    bg = "#ffcdd2"
                    border = "#c62828"
                    texto = "🔴 Baixo"
                
                return f"""
                <div style="background: {bg}; padding: 15px; border-radius: 10px; margin: 8px 0; border-left: 5px solid {border};">
                    <h4>{icone} {titulo}</h4>
                    <h2 style="text-align: center;">{valor}%</h2>
                    <p style="font-size: 0.8rem; color: #555;">{descricao}</p>
                    <p style="font-size: 0.8rem; font-weight: bold; color: {border};">{texto}</p>
                </div>
                """
            
            with col1:
                st.markdown(card_style(indices['Resiliência Climática'], "Resiliência Climática", "Capacidade de recuperação", "🔄"), unsafe_allow_html=True)
                st.markdown(card_style(indices['Segurança Hídrica'], "Segurança Hídrica", "Disponibilidade de água", "💧"), unsafe_allow_html=True)
                st.markdown(card_style(indices['Agricultura Inteligente (CSA)'], "Agricultura Inteligente", "Práticas sustentáveis", "🌱"), unsafe_allow_html=True)
            
            with col2:
                st.markdown(card_style(indices['Diversificação da Produção'], "Diversificação", "Número de culturas", "🌾"), unsafe_allow_html=True)
                st.markdown(card_style(indices['Capacidade Adaptativa'], "Capacidade Adaptativa", "Adaptação às mudanças", "🧠"), unsafe_allow_html=True)
                st.markdown(card_style(indices['Índice Integrado One Health/Nexus'], "One Health/Nexus", "Integração saúde-agricultura", "🔄"), unsafe_allow_html=True)
            
            with col3:
                vul_seca = indices['Vulnerabilidade à Seca']
                bg = "#c8e6c9" if vul_seca <= 40 else "#ffe0b2" if vul_seca <= 60 else "#ffcdd2"
                border = "#2e7d32" if vul_seca <= 40 else "#ef6c00" if vul_seca <= 60 else "#c62828"
                st.markdown(f"""
                <div style="background: {bg}; padding: 15px; border-radius: 10px; margin: 8px 0; border-left: 5px solid {border};">
                    <h4>☀️ Vulnerabilidade à Seca</h4>
                    <h2 style="text-align: center;">{vul_seca}%</h2>
                    <p style="font-size: 0.8rem; color: #555;">Quanto menor, melhor</p>
                </div>
                """, unsafe_allow_html=True)
                
                vul_cheias = indices['Vulnerabilidade a Cheias']
                bg = "#c8e6c9" if vul_cheias <= 40 else "#ffe0b2" if vul_cheias <= 60 else "#ffcdd2"
                border = "#2e7d32" if vul_cheias <= 40 else "#ef6c00" if vul_cheias <= 60 else "#c62828"
                st.markdown(f"""
                <div style="background: {bg}; padding: 15px; border-radius: 10px; margin: 8px 0; border-left: 5px solid {border};">
                    <h4>🌊 Vulnerabilidade a Cheias</h4>
                    <h2 style="text-align: center;">{vul_cheias}%</h2>
                    <p style="font-size: 0.8rem; color: #555;">Quanto menor, melhor</p>
                </div>
                """, unsafe_allow_html=True)
                
                degradacao = indices['Degradação do Solo']
                bg = "#c8e6c9" if degradacao <= 40 else "#ffe0b2" if degradacao <= 60 else "#ffcdd2"
                border = "#2e7d32" if degradacao <= 40 else "#ef6c00" if degradacao <= 60 else "#c62828"
                st.markdown(f"""
                <div style="background: {bg}; padding: 15px; border-radius: 10px; margin: 8px 0; border-left: 5px solid {border};">
                    <h4>🏜️ Degradação do Solo</h4>
                    <h2 style="text-align: center;">{degradacao}%</h2>
                    <p style="font-size: 0.8rem; color: #555;">Quanto menor, melhor</p>
                </div>
                """, unsafe_allow_html=True)
                
                risco = indices['Risco Agroalimentar']
                bg = "#c8e6c9" if risco <= 40 else "#ffe0b2" if risco <= 60 else "#ffcdd2"
                border = "#2e7d32" if risco <= 40 else "#ef6c00" if risco <= 60 else "#c62828"
                st.markdown(f"""
                <div style="background: {bg}; padding: 15px; border-radius: 10px; margin: 8px 0; border-left: 5px solid {border};">
                    <h4>⚠️ Risco Agroalimentar</h4>
                    <h2 style="text-align: center;">{risco}%</h2>
                    <p style="font-size: 0.8rem; color: #555;">Quanto menor, melhor</p>
                </div>
                """, unsafe_allow_html=True)
            
            # ===== RECOMENDAÇÕES =====
            st.divider()
            st.markdown("### 💡 Recomendações Personalizadas")
            
            recomendacoes = []
            
            if indices['Resiliência Climática'] < 50:
                recomendacoes.append("🔴 **Baixa Resiliência Climática:** Implementar sistemas de irrigação e diversificar culturas para reduzir riscos.")
            
            if indices['Segurança Hídrica'] < 50:
                recomendacoes.append("🟠 **Insegurança Hídrica:** Investir em captação de água da chuva e sistemas de irrigação eficientes.")
            
            if indices['Diversificação da Produção'] < 50:
                recomendacoes.append("🟠 **Baixa Diversificação:** Aumentar o número de culturas para melhorar a segurança alimentar.")
            
            if indices['Vulnerabilidade à Seca'] > 60:
                recomendacoes.append("🔴 **Alta Vulnerabilidade à Seca:** Plantar variedades resistentes à seca e implementar sistemas de armazenamento de água.")
            
            if indices['Vulnerabilidade a Cheias'] > 60:
                recomendacoes.append("🔴 **Alta Vulnerabilidade a Cheias:** Melhorar a drenagem e plantar em áreas menos sujeitas a inundações.")
            
            if indices['Degradação do Solo'] > 60:
                recomendacoes.append("🔴 **Degradação do Solo:** Implementar práticas de conservação como rotação de culturas e adubação orgânica.")
            
            if indices['Agricultura Inteligente (CSA)'] < 50:
                recomendacoes.append("🟠 **Baixa Adoção de CSA:** Adotar práticas de agricultura sustentável e usar previsões meteorológicas.")
            
            if indices['Capacidade Adaptativa'] < 50:
                recomendacoes.append("🟠 **Baixa Capacidade Adaptativa:** Buscar assistência técnica e formar-se em práticas agrícolas resilientes.")
            
            if indices['Risco Agroalimentar'] > 60:
                recomendacoes.append("🔴 **Alto Risco Agroalimentar:** Diversificar fontes de renda e melhorar o armazenamento pós-colheita.")
            
            if indices['Índice Integrado One Health/Nexus'] < 50:
                recomendacoes.append("🟠 **Baixa Integração One Health:** Promover sinergias entre saúde, agricultura e ambiente.")
            
            if not recomendacoes:
                recomendacoes.append("✅ **Boa resiliência agroalimentar!** A família apresenta boas práticas de adaptação climática.")
            
            for rec in recomendacoes:
                st.info(rec)
        else:
            st.info("📋 Nenhum índice calculado. Preencha a avaliação agroalimentar na aba 'Avaliação'.")
    
    # ============================================================
    # ===== TAB 4: DASHBOARD =====
    # ============================================================
    with tab4:
        st.subheader("📊 Dashboard Agroalimentar")
        
        if not pacientes_encaminhados:
            st.info("📋 Nenhum encaminhamento para agrônomo recebido ainda.")
            return
        
        df = pd.DataFrame(pacientes_encaminhados)
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("📨 Total", len(df))
        with col2:
            producao = len(df[df['producao_familiar'] != 'Não produz'])
            st.metric("🌾 Produção Familiar", producao)
        with col3:
            terra = len(df[df['acesso_terra'] != 'Não tem terra'])
            st.metric("🏠 Acesso à Terra", terra)
        with col4:
            agua = len(df[df['fonte_agua'] != 'Nenhuma'])
            st.metric("💧 Fonte de Água", agua)
        
        st.divider()
        
        col1, col2 = st.columns(2)
        
        with col1:
            if 'producao_familiar' in df.columns:
                fig1 = px.pie(df, names='producao_familiar', title='Produção Familiar')
                fig1.update_layout(showlegend=True)
                st.plotly_chart(fig1, use_container_width=True)
        
        with col2:
            if 'acesso_terra' in df.columns:
                fig2 = px.pie(df, names='acesso_terra', title='Acesso à Terra')
                fig2.update_layout(showlegend=True)
                st.plotly_chart(fig2, use_container_width=True)
        
        col3, col4 = st.columns(2)
        
        with col3:
            if 'fonte_agua' in df.columns:
                fig3 = px.pie(df, names='fonte_agua', title='Fonte de Água')
                fig3.update_layout(showlegend=True)
                st.plotly_chart(fig3, use_container_width=True)
        
        with col4:
            if 'culturas_produzidas' in df.columns:
                culturas_counts = df['culturas_produzidas'].value_counts().head(5)
                if not culturas_counts.empty:
                    fig4 = px.bar(x=culturas_counts.values, y=culturas_counts.index,
                                orientation='h', title='Culturas Produzidas')
                    st.plotly_chart(fig4, use_container_width=True)
        
        st.divider()
        
        # ===== RECOMENDAÇÕES AGROALIMENTARES =====
        st.subheader("💡 Recomendações Agroalimentares")
        
        total_producao = len(df[df['producao_familiar'] != 'Não produz'])
        total_terra = len(df[df['acesso_terra'] != 'Não tem terra'])
        total_agua = len(df[df['fonte_agua'] != 'Nenhuma'])
        
        if total_producao < len(df) * 0.5:
            st.warning(f"🔴 **{len(df) - total_producao} famílias não produzem alimentos** - Incentivar produção familiar para segurança alimentar.")
        
        if total_terra < len(df) * 0.5:
            st.warning(f"🔴 **{len(df) - total_terra} famílias não têm acesso à terra** - Avaliar programas de acesso à terra.")
        
        if total_agua < len(df) * 0.5:
            st.warning(f"🔴 **{len(df) - total_agua} famílias não têm fonte de água** - Implementar sistemas de captação de água.")
        
        if 'dificuldades_producao' in df.columns:
            dificuldades_counts = df['dificuldades_producao'].value_counts()
            if not dificuldades_counts.empty:
                top_dificuldade = dificuldades_counts.index[0]
                st.info(f"🟠 **Principal dificuldade:** {top_dificuldade} - {dificuldades_counts.iloc[0]} famílias")
        
        if total_producao >= len(df) * 0.7 and total_terra >= len(df) * 0.7 and total_agua >= len(df) * 0.7:
            st.success("✅ Boa resiliência agroalimentar! As famílias têm boas condições de production.")
    
    # ============================================================
    # ===== TAB 5: ENCAMINHAMENTOS =====
    # ============================================================
    with tab5:
        st.subheader("📨 Encaminhamentos Recebidos")
        
        if not enc_agro:
            st.info("📋 Nenhum encaminhamento para agrônomo recebido ainda.")
        else:
            pendentes = [e for e in enc_agro if e.get('status') != 'Concluído']
            atendidos = [e for e in enc_agro if e.get('status') == 'Concluído']
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("📨 Total", len(enc_agro))
            with col2:
                st.metric("⏳ Pendentes", len(pendentes))
            with col3:
                st.metric("✅ Atendidos", len(atendidos))
            
            st.divider()
            
            if pendentes:
                st.markdown(f"### ⏳ Lista de Pendentes ({len(pendentes)})")
                for enc in pendentes:
                    urgencia = enc.get('urgencia', 'Normal')
                    cor = "🔴" if urgencia == "Muito Urgente" else "🟠" if urgencia == "Urgente" else "🟢"
                    with st.expander(f"{cor} 👶 {enc.get('paciente', 'N/A')} - {enc.get('data', 'N/A')}", expanded=False):
                        col1, col2 = st.columns(2)
                        with col1:
                            st.markdown("**📋 Dados do Encaminhamento**")
                            st.markdown(f"**Especialidade:** {enc.get('especialidade', 'N/A')}")
                            st.markdown(f"**Urgência:** {enc.get('urgencia', 'Normal')}")
                            st.markdown(f"**Motivo:** {enc.get('motivo', 'N/A')}")
                            st.markdown(f"**Status:** {enc.get('status', 'Pendente')}")
                            st.markdown(f"**Médico:** {enc.get('medico_responsavel', 'N/A')}")
                        with col2:
                            st.markdown("**📊 Dados Agroalimentares**")
                            if 'dados_clinicos' in enc and enc['dados_clinicos']:
                                dados = enc['dados_clinicos']
                                if isinstance(dados, dict):
                                    st.markdown(f"- DDS: {dados.get('dds', 0)}/9")
                                    st.markdown(f"- MUAC: {dados.get('muac', 0)} mm")
                                    st.markdown(f"- Produção: {dados.get('producao_familiar', 'N/A')}")
                                    st.markdown(f"- Terra: {dados.get('acesso_terra', 'N/A')}")
                                    st.markdown(f"- Dificuldades: {dados.get('dificuldades_producao', 'N/A')}")
                                else:
                                    st.markdown(f"- Dados: {dados}")
                        
                        st.divider()
                        
                        # ===== BOTÃO MARCAR COMO ATENDIDO (COM SUPABASE) =====
                        if st.button(f"✅ Marcar como Atendido - {enc.get('paciente', '')}", key=f"atender_agro_{enc.get('paciente')}_{enc.get('data')}"):
                            if SUPABASE_AVAILABLE:
                                sucesso, resultado = atualizar_status_encaminhamento_supabase(
                                    enc.get('paciente'),
                                    enc.get('data'),
                                    'Concluído'
                                )
                                if sucesso:
                                    for e in st.session_state.encaminhamentos:
                                        if e.get('paciente') == enc.get('paciente') and e.get('data') == enc.get('data'):
                                            e['status'] = 'Concluído'
                                    st.success(f"✅ {enc.get('paciente')} marcado como atendido no Supabase!")
                                    st.rerun()
                                else:
                                    st.error(f"❌ Erro ao atualizar: {resultado}")
                            else:
                                st.warning("⚠️ Supabase não disponível. Atualizado apenas localmente.")
                                for e in st.session_state.encaminhamentos:
                                    if e.get('paciente') == enc.get('paciente') and e.get('data') == enc.get('data'):
                                        e['status'] = 'Concluído'
                                st.rerun()
            else:
                st.success("✅ Todos os encaminhamentos foram atendidos!")
            
            if atendidos:
                st.divider()
                st.markdown(f"### ✅ Lista de Atendidos ({len(atendidos)})")
                for enc in atendidos:
                    with st.expander(f"✅ 👶 {enc.get('paciente', 'N/A')} - {enc.get('data', 'N/A')}", expanded=False):
                        col1, col2 = st.columns(2)
                        with col1:
                            st.markdown("**📋 Dados do Encaminhamento**")
                            st.markdown(f"**Especialidade:** {enc.get('especialidade', 'N/A')}")
                            st.markdown(f"**Urgência:** {enc.get('urgencia', 'Normal')}")
                            st.markdown(f"**Motivo:** {enc.get('motivo', 'N/A')}")
                            st.markdown(f"**Status:** {enc.get('status', 'Concluído')}")
                            st.markdown(f"**Médico:** {enc.get('medico_responsavel', 'N/A')}")
                        with col2:
                            st.markdown("**📊 Dados Agroalimentares**")
                            if 'dados_clinicos' in enc and enc['dados_clinicos']:
                                dados = enc['dados_clinicos']
                                if isinstance(dados, dict):
                                    st.markdown(f"- DDS: {dados.get('dds', 0)}/9")
                                    st.markdown(f"- MUAC: {dados.get('muac', 0)} mm")
                                    st.markdown(f"- Produção: {dados.get('producao_familiar', 'N/A')}")
                                    st.markdown(f"- Terra: {dados.get('acesso_terra', 'N/A')}")
                                else:
                                    st.markdown(f"- Dados: {dados}")

if __name__ == "__main__":
    render_agronomo()