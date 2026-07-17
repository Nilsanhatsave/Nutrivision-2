# pages/nutricionista.py
# ===== PERFIL NUTRICIONISTA - AVALIAÇÃO NUTRICIONAL =====

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
    salvar_avaliacao_nutricional_supabase,
    salvar_plano_intervencao_nutri_supabase,
    atualizar_status_encaminhamento_supabase
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

def obter_dados_encaminhamento(encaminhamento):
    """Extrai os dados do encaminhamento de forma segura"""
    dados = encaminhamento.get('dados_clinicos', {})
    if isinstance(dados, str):
        try:
            dados = json.loads(dados)
        except:
            dados = {}
    return dados

def render_nutricionista():
    # ===== CARREGAR DADOS =====
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
    
    # ===== ENCAMINHAMENTOS =====
    if 'encaminhamentos' not in st.session_state:
        if SUPABASE_AVAILABLE:
            sucesso, dados = carregar_encaminhamentos_supabase()
            if sucesso and dados:
                st.session_state.encaminhamentos = dados
            else:
                st.session_state.encaminhamentos = []
        else:
            st.session_state.encaminhamentos = []
    
    # ===== PLANOS DE INTERVENÇÃO =====
    if 'planos_intervencao_nutri' not in st.session_state:
        st.session_state.planos_intervencao_nutri = []
    
    st.title("🍎 Nutricionista - Avaliação Nutricional")
    st.markdown("""
    <p style='color: #555; margin-bottom: 2rem;'>
    Avaliação nutricional detalhada, plano de intervenção e recomendações dietéticas.
    </p>
    """, unsafe_allow_html=True)
    
    # ===== FILTRAR ENCAMINHAMENTOS PARA NUTRICIONISTA =====
    enc_nutri = [e for e in st.session_state.encaminhamentos if 'Nutricionista' in e.get('especialidade', '')]
    
    # ===== LISTA DE PACIENTES PENDENTES E ATENDIDOS =====
    pacientes_pendentes = []
    pacientes_atendidos = []
    
    for enc in enc_nutri:
        paciente_nome = enc.get('paciente', '')
        if enc.get('status') != 'Concluído':
            if paciente_nome not in pacientes_pendentes:
                pacientes_pendentes.append(paciente_nome)
        else:
            if paciente_nome not in pacientes_atendidos:
                pacientes_atendidos.append(paciente_nome)
    
    # ===== ESTATÍSTICAS =====
    total = len(st.session_state.criancas)
    pendentes = len([e for e in enc_nutri if e.get('status') != 'Concluído'])
    atendidos = len([e for e in enc_nutri if e.get('status') == 'Concluído'])
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("👶 Total Pacientes", total)
    with col2:
        st.metric("📨 Encaminhamentos", len(enc_nutri))
    with col3:
        st.metric("⏳ Pendentes", pendentes)
    with col4:
        st.metric("✅ Atendidos", atendidos)
    
    st.markdown("---")
    
    # ============================================================
    # ===== ABAS =====
    # ============================================================
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📋 Avaliação Nutricional",
        "📝 Plano de Intervenção",
        "📊 Dashboard",
        "📨 Encaminhamentos",
        "💡 Recomendações"
    ])
    
    # ============================================================
    # ===== TAB 1: AVALIAÇÃO NUTRICIONAL =====
    # ============================================================
    with tab1:
        st.subheader("👤 Selecionar Paciente")
        
        if not st.session_state.criancas:
            st.info("📋 Nenhum paciente registado no sistema.")
            return
        
        df = pd.DataFrame(st.session_state.criancas)
        
        # ===== FILTRAR APENAS PACIENTES ENCAMINHADOS =====
        pacientes_encaminhados = []
        for enc in enc_nutri:
            paciente_nome = enc.get('paciente', '')
            if paciente_nome and paciente_nome not in pacientes_encaminhados:
                pacientes_encaminhados.append(paciente_nome)
        
        if not pacientes_encaminhados:
            st.info("📋 Nenhum paciente encaminhado para nutricionista.")
            return
        
        df_encaminhados = df[df['nome_completo'].isin(pacientes_encaminhados)]
        
        # ===== CRIAR LISTA COM STATUS PARA O SELECTBOX =====
        lista_pacientes = []
        for nome in df_encaminhados['nome_completo'].unique().tolist():
            if nome in pacientes_pendentes:
                lista_pacientes.append(f"⏳ {nome} (Pendente)")
            elif nome in pacientes_atendidos:
                lista_pacientes.append(f"✅ {nome} (Atendido)")
            else:
                lista_pacientes.append(f"📋 {nome}")
        
        selected = st.selectbox(
            "Selecione o paciente encaminhado:",
            lista_pacientes,
            key="select_paciente_nutri"
        )
        
        # ===== EXTRAIR O NOME CORRETAMENTE =====
        nome_selected = selected
        if selected.startswith("⏳ ") or selected.startswith("✅ ") or selected.startswith("📋 "):
            nome_selected = selected[2:]
        if " (" in nome_selected:
            nome_selected = nome_selected.split(" (")[0]
        
        # ===== VERIFICAR SE O NOME EXISTE =====
        if nome_selected not in df['nome_completo'].values:
            st.error(f"❌ Paciente '{nome_selected}' não encontrado.")
            return
        
        patient_data = df[df['nome_completo'] == nome_selected].iloc[0]
        
        # ===== BUSCAR OS DADOS DO ENCAMINHAMENTO =====
        encaminhamento_data = None
        for enc in enc_nutri:
            if enc.get('paciente') == nome_selected:
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
            st.markdown("### 📋 Dados do Encaminhamento Médico")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**🩸 Dados Clínicos**")
                st.markdown(f"- Hemoglobina: {dados_clinicos.get('hemoglobina', 'N/A')} g/dL")
                st.markdown(f"- Tipo Anemia: {dados_clinicos.get('tipo_anemia', 'N/A')}")
                st.markdown(f"- Densidade Parasitária: {dados_clinicos.get('densidade_parasitaria', 'N/A')}")
                st.markdown(f"- Diarreia: {dados_clinicos.get('diarreia', 'N/A')}")
                st.markdown(f"- Doença Crónica: {dados_clinicos.get('doenca_cronica', 'N/A')}")
            
            with col2:
                st.markdown("**🍽️ Dados Alimentares**")
                st.markdown(f"- DDS: {dados_clinicos.get('dds', 0)}/9")
                st.markdown(f"- MUAC: {dados_clinicos.get('muac', 0)} mm")
                st.markdown(f"- Refeições/dia: {dados_clinicos.get('refeicoes_dia', 'N/A')}")
                st.markdown(f"- Amamentação: {dados_clinicos.get('amamentacao', 'N/A')}")
                st.markdown(f"- Frequência Ferro: {dados_clinicos.get('frequencia_ferro', 'N/A')}")
            
            # Alimentos consumidos
            alimentos_ferro = dados_clinicos.get('alimentos_ferro', [])
            if alimentos_ferro:
                st.markdown("**🥩 Alimentos Ricos em Ferro:**")
                for alimento in alimentos_ferro:
                    st.markdown(f"- {alimento}")
            
            st.markdown("---")
            st.markdown("**👨‍⚕️ Dados do Médico**")
            st.markdown(f"- Diagnóstico: {dados_clinicos.get('diagnostico_medico', 'N/A')}")
            st.markdown(f"- Prescrição: {dados_clinicos.get('prescricao_medica', 'N/A')}")
            st.markdown(f"- Seguimento: {dados_clinicos.get('seguimento', 'N/A')}")
            st.markdown(f"- Data Encaminhamento: {dados_clinicos.get('data_encaminhamento', 'N/A')}")
        else:
            st.warning("⚠️ Dados clínicos não disponíveis para este encaminhamento.")
        
        st.divider()
        
        # ============================================================
        # ===== FORMULÁRIO DE AVALIAÇÃO NUTRICIONAL =====
        # ============================================================
        st.markdown("### 🥗 Avaliação Nutricional Detalhada")
        st.markdown("Preencha o formulário para avaliar detalhadamente o estado nutricional da criança.")
        
        with st.form("avaliacao_nutricional_form"):
            
            # ===== 1. INTRODUÇÃO ALIMENTAR =====
            st.markdown("#### 🍼 1. Introdução Alimentar")
            
            col1, col2 = st.columns(2)
            with col1:
                idade_inicio_outros = st.selectbox(
                    "Com que idade iniciou outros alimentos além do leite materno?",
                    ["Nunca iniciou", "Menos de 4 meses", "4-6 meses", "7-9 meses", "10-12 meses", "Mais de 12 meses"],
                    key=f"idade_inicio_{selected}"
                )
            
            with col2:
                recusa_alimentos = st.selectbox(
                    "A criança costuma recusar alimentos?",
                    ["Sim", "Não"],
                    key=f"recusa_{selected}"
                )
            
            if recusa_alimentos == "Sim":
                quais_recusa = st.text_input(
                    "Se sim, quais alimentos recusa?",
                    placeholder="Ex: Verduras, carnes...",
                    key=f"quais_recusa_{selected}"
                )
            else:
                quais_recusa = ""
            
            col1, col2 = st.columns(2)
            with col1:
                lanches_entre_refeicoes = st.selectbox(
                    "A criança faz lanches entre as refeições?",
                    ["Sim", "Não"],
                    key=f"lanches_{selected}"
                )
            
            with col2:
                quem_alimenta = st.selectbox(
                    "Quem alimenta a criança?",
                    ["Mãe", "Pai", "Avó", "Outro"],
                    key=f"quem_alimenta_{selected}"
                )
                if quem_alimenta == "Outro":
                    quem_alimenta_outro = st.text_input(
                        "Especifique:",
                        key=f"quem_alimenta_outro_{selected}"
                    )
            
            come_sozinho = st.selectbox(
                "A criança come sozinha ou é alimentada por um adulto?",
                ["Sozinha", "Com ajuda", "Totalmente alimentada"],
                key=f"come_sozinho_{selected}"
            )
            
            st.divider()
            
            # ===== 2. APETITE E ALIMENTAÇÃO =====
            st.markdown("#### 🍽️ 2. Apetite e Alimentação")
            
            col1, col2 = st.columns(2)
            with col1:
                apetite = st.selectbox(
                    "Como considera o apetite da criança?",
                    ["Bom", "Regular", "Fraco"],
                    key=f"apetite_{selected}"
                )
            
            with col2:
                dificuldade_mastigar = st.selectbox(
                    "A criança apresenta dificuldade para mastigar ou engolir alimentos?",
                    ["Sim", "Não"],
                    key=f"dificuldade_mastigar_{selected}"
                )
            
            alergia = st.selectbox(
                "Existe algum alimento que a criança não pode consumir por alergia ou intolerância?",
                ["Sim", "Não"],
                key=f"alergia_{selected}"
            )
            
            if alergia == "Sim":
                qual_alergia = st.text_input(
                    "Se sim, qual alimento?",
                    placeholder="Ex: Leite, Ovos, Amendoim...",
                    key=f"qual_alergia_{selected}"
                )
            else:
                qual_alergia = ""
            
            st.divider()
            
            # ===== 3. CAPACIDADE DA FAMÍLIA =====
            st.markdown("#### 👨‍👩‍👧‍👦 3. Capacidade da Família para Seguir Recomendações")
            
            col1, col2 = st.columns(2)
            with col1:
                obter_alimentos = st.selectbox(
                    "A família consegue obter os alimentos recomendados?",
                    ["Sempre", "Às vezes", "Raramente"],
                    key=f"obter_alimentos_{selected}"
                )
            
            with col2:
                dificuldades_alimentacao = st.multiselect(
                    "Quais são as principais dificuldades para alimentar a criança?",
                    ["Falta de dinheiro", "Falta de alimentos", "A criança recusa alimentos", "Falta de tempo", "Falta de conhecimentos sobre alimentação", "Outra"],
                    key=f"dificuldades_{selected}"
                )
                if "Outra" in dificuldades_alimentacao:
                    outra_dificuldade = st.text_input(
                        "Especifique outra dificuldade:",
                        key=f"outra_dificuldade_{selected}"
                    )
            
            st.divider()
            
            # ===== 4. PRODUÇÃO DE ALIMENTOS =====
            st.markdown("#### 🌾 4. Produção de Alimentos")
            
            condicoes_produzir = st.selectbox(
                "Se os alimentos recomendados para a criança não estão disponíveis em casa, a família teria condições de os produzir?",
                ["Sim", "Não", "Não sabe"],
                key=f"condicoes_produzir_{selected}"
            )
            
            st.divider()
            
            # ============================================================
            # ===== BOTÃO SALVAR AVALIAÇÃO =====
            # ============================================================
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.form_submit_button("💾 Salvar Avaliação Nutricional", use_container_width=True):
                    dados_avaliacao = {
                        'paciente': nome_selected,
                        'data': datetime.now().strftime('%Y-%m-%d %H:%M'),
                        'idade_inicio_outros': idade_inicio_outros,
                        'recusa_alimentos': recusa_alimentos,
                        'quais_recusa': quais_recusa,
                        'lanches_entre_refeicoes': lanches_entre_refeicoes,
                        'quem_alimenta': quem_alimenta,
                        'quem_alimenta_outro': quem_alimenta_outro if quem_alimenta == "Outro" else "",
                        'come_sozinho': come_sozinho,
                        'apetite': apetite,
                        'dificuldade_mastigar': dificuldade_mastigar,
                        'alergia': alergia,
                        'qual_alergia': qual_alergia,
                        'obter_alimentos': obter_alimentos,
                        'dificuldades_alimentacao': dificuldades_alimentacao,
                        'condicoes_produzir': condicoes_produzir
                    }
                    
                    if SUPABASE_AVAILABLE:
                        sucesso, resultado = salvar_avaliacao_nutricional_supabase(dados_avaliacao)
                        if sucesso:
                            st.success(f"✅ Avaliação nutricional salva para {nome_selected} no Supabase!")
                        else:
                            st.warning(f"⚠️ Erro ao salvar no Supabase: {resultado}")
                    else:
                        st.warning("⚠️ Supabase não disponível. Avaliação salva localmente.")
                    
                    if 'avaliacoes_nutricionais' not in st.session_state:
                        st.session_state.avaliacoes_nutricionais = []
                    
                    st.session_state.avaliacoes_nutricionais.append(dados_avaliacao)
    
    # ============================================================
    # ===== TAB 2: PLANO DE INTERVENÇÃO =====
    # ============================================================
    with tab2:
        st.subheader("📝 Plano de Intervenção Nutricional")
        
        if not st.session_state.criancas:
            st.info("📋 Nenhum paciente registado no sistema.")
            return
        
        df = pd.DataFrame(st.session_state.criancas)
        selected_plano = st.selectbox(
            "Selecione o paciente:",
            df['nome_completo'].unique().tolist(),
            key="select_plano_nutri"
        )
        
        patient_data_plano = df[df['nome_completo'] == selected_plano].iloc[0]
        
        st.markdown(f"#### 👶 {patient_data_plano['nome_completo']}")
        st.markdown(f"**Idade:** {patient_data_plano['idade_meses']} meses")
        st.markdown(f"**📊 DDS:** {patient_data_plano.get('dds_calculado', 0)}/9")
        
        st.divider()
        
        with st.form("plano_intervencao_nutri_form"):
            st.markdown("### 🎯 Objetivos da Intervenção")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**📋 Objetivo Principal**")
                objetivo_principal = st.text_area(
                    "Objetivo principal da intervenção:",
                    placeholder="Ex: Melhorar o estado nutricional da criança...",
                    height=80,
                    key=f"obj_principal_nutri_{selected_plano}"
                )
                
                st.markdown("**📊 Metas Específicas**")
                metas = st.text_area(
                    "Metas específicas:",
                    placeholder="Ex: Aumentar a hemoglobina para >11 g/dL...",
                    height=80,
                    key=f"metas_nutri_{selected_plano}"
                )
            
            with col2:
                st.markdown("**⏱️ Prazo de Execução**")
                prazo = st.selectbox(
                    "Prazo de execução:",
                    ["1 semana", "2 semanas", "1 mês", "2 meses", "3 meses"],
                    key=f"prazo_nutri_{selected_plano}"
                )
                
                st.markdown("**📅 Data de Início**")
                data_inicio = st.date_input(
                    "Data de início:",
                    value=datetime.now().date(),
                    key=f"data_inicio_nutri_{selected_plano}"
                )
            
            st.markdown("### 🍽️ Intervenções Nutricionais")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**🥗 Recomendações Dietéticas**")
                recomendacoes = st.text_area(
                    "Recomendações dietéticas:",
                    placeholder="Ex: Aumentar consumo de carnes e feijão...",
                    height=100,
                    key=f"recomendacoes_nutri_{selected_plano}"
                )
                
                st.markdown("**💊 Suplementação Recomendada**")
                suplementacao = st.text_area(
                    "Suplementação recomendada:",
                    placeholder="Ex: Sulfato Ferroso 3mg/kg/dia...",
                    height=60,
                    key=f"suplementacao_nutri_{selected_plano}"
                )
            
            with col2:
                st.markdown("**📋 Atividades Educativas**")
                atividades = st.text_area(
                    "Atividades educativas:",
                    placeholder="Ex: Sessões de educação nutricional...",
                    height=100,
                    key=f"atividades_nutri_{selected_plano}"
                )
                
                st.markdown("**👨‍👩‍👧‍👦 Envolvimento Familiar**")
                envolvimento = st.text_area(
                    "Envolvimento familiar:",
                    placeholder="Ex: Orientar a família sobre alimentação...",
                    height=60,
                    key=f"envolvimento_nutri_{selected_plano}"
                )
            
            st.markdown("### 📊 Monitoramento e Avaliação")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**📅 Frequência de Monitoramento**")
                frequencia_monitoramento = st.selectbox(
                    "Frequência de monitoramento:",
                    ["Semanal", "Quinzenal", "Mensal", "Trimestral"],
                    key=f"freq_monitor_nutri_{selected_plano}"
                )
            
            with col2:
                st.markdown("**📋 Indicadores de Avaliação**")
                indicadores = st.text_area(
                    "Indicadores de avaliação:",
                    placeholder="Ex: Peso, altura, hemoglobina...",
                    height=60,
                    key=f"indicadores_nutri_{selected_plano}"
                )
            
            st.markdown("### 📝 Observações Finais")
            observacoes_plano = st.text_area(
                "Observações finais:",
                placeholder="Informações adicionais sobre o plano...",
                height=80,
                key=f"obs_plano_nutri_{selected_plano}"
            )
            
            # ===== ANEXAR DOCUMENTOS =====
            st.markdown("### 📎 Anexar Documentos")
            
            uploaded_file = st.file_uploader(
                "Selecionar arquivo (PDF, DOCX, DOC, TXT):",
                type=['pdf', 'docx', 'doc', 'txt'],
                key=f"upload_nutri_{selected_plano}"
            )
            
            if uploaded_file is not None:
                st.success(f"✅ Arquivo anexado: {uploaded_file.name}")
                st.info(f"📊 Tamanho: {uploaded_file.size} bytes")
                st.info(f"📁 Tipo: {uploaded_file.type}")
            
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.form_submit_button("💾 Registar Plano de Intervenção", use_container_width=True):
                    if objetivo_principal or recomendacoes:
                        novo_plano = {
                            'paciente': selected_plano,
                            'data': datetime.now().strftime('%Y-%m-%d %H:%M'),
                            'objetivo_principal': objetivo_principal,
                            'metas': metas,
                            'prazo': prazo,
                            'data_inicio': data_inicio.strftime('%Y-%m-%d'),
                            'recomendacoes_dieteticas': recomendacoes,
                            'suplementacao': suplementacao,
                            'atividades_educativas': atividades,
                            'envolvimento_familiar': envolvimento,
                            'frequencia_monitoramento': frequencia_monitoramento,
                            'indicadores_avaliacao': indicadores,
                            'observacoes': observacoes_plano,
                            'status': 'Ativo'
                        }
                        
                        if uploaded_file is not None:
                            novo_plano['arquivo_anexado'] = uploaded_file.name
                            novo_plano['arquivo_tipo'] = uploaded_file.type
                            novo_plano['arquivo_tamanho'] = uploaded_file.size
                            novo_plano['arquivo_conteudo'] = uploaded_file.getvalue()
                        
                        if SUPABASE_AVAILABLE:
                            sucesso, resultado = salvar_plano_intervencao_nutri_supabase(novo_plano)
                            if sucesso:
                                st.success(f"✅ Plano de intervenção registado para {selected_plano} no Supabase!")
                            else:
                                st.warning(f"⚠️ Erro ao salvar no Supabase: {resultado}")
                        
                        st.session_state.planos_intervencao_nutri.append(novo_plano)
                        st.success(f"✅ Plano de intervenção registado para {selected_plano}!")
                    else:
                        st.warning("⚠️ Preencha pelo menos o objetivo principal ou as recomendações dietéticas.")
        
        # ===== LISTA DE PLANOS REGISTADOS =====
        st.divider()
        st.subheader("📋 Planos Registados")
        
        planos_paciente = [p for p in st.session_state.planos_intervencao_nutri if p['paciente'] == selected_plano]
        
        if planos_paciente:
            for i, plano in enumerate(planos_paciente):
                with st.expander(f"📋 Plano {i+1} - {plano['data']} - {plano.get('status', 'Ativo')}", expanded=False):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown(f"**🎯 Objetivo Principal:** {plano.get('objetivo_principal', 'N/A')}")
                        st.markdown(f"**📊 Metas:** {plano.get('metas', 'N/A')}")
                        st.markdown(f"**⏱️ Prazo:** {plano.get('prazo', 'N/A')}")
                        st.markdown(f"**📅 Data Início:** {plano.get('data_inicio', 'N/A')}")
                    
                    with col2:
                        st.markdown(f"**🥗 Recomendações:** {plano.get('recomendacoes_dieteticas', 'N/A')}")
                        st.markdown(f"**💊 Suplementação:** {plano.get('suplementacao', 'N/A')}")
                        st.markdown(f"**📋 Atividades:** {plano.get('atividades_educativas', 'N/A')}")
                        st.markdown(f"**📅 Monitoramento:** {plano.get('frequencia_monitoramento', 'N/A')}")
                    
                    st.markdown(f"**📝 Observações:** {plano.get('observacoes', 'N/A')}")
                    
                    if plano.get('arquivo_anexado'):
                        st.markdown(f"**📎 Arquivo:** {plano['arquivo_anexado']}")
                    
                    st.divider()
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if plano.get('status') == 'Ativo':
                            if st.button(f"✅ Marcar como Concluído", key=f"concluir_nutri_{i}_{selected_plano}"):
                                st.session_state.planos_intervencao_nutri[i]['status'] = 'Concluído'
                                st.rerun()
                    with col2:
                        if st.button(f"🗑️ Remover", key=f"remover_nutri_{i}_{selected_plano}"):
                            st.session_state.planos_intervencao_nutri.pop(i)
                            st.rerun()
        else:
            st.info(f"📋 Nenhum plano registado para {selected_plano}.")
    
    # ============================================================
    # ===== TAB 3: DASHBOARD =====
    # ============================================================
    with tab3:
        st.subheader("📊 Dashboard Nutricional")
        
        if not st.session_state.criancas:
            st.info("📋 Nenhum dado disponível")
            return
        
        df = pd.DataFrame(st.session_state.criancas)
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            total = len(df)
            st.metric("👶 Total", total)
        with col2:
            alto_anemia = len(df[df['risco_anemia_nivel'] == 'ALTO'])
            st.metric("🩸 Anemia ALTA", alto_anemia)
        with col3:
            alto_fome = len(df[df['risco_fome_nivel'] == 'ALTO'])
            st.metric("🍽️ Fome Oculta ALTA", alto_fome)
        with col4:
            alto_inseg = len(df[df['risco_inseguranca_nivel'] == 'ALTO'])
            st.metric("🏠 Insegurança ALTA", alto_inseg)
        
        st.divider()
        
        col1, col2 = st.columns(2)
        
        with col1:
            if 'risco_anemia_nivel' in df.columns:
                fig1 = px.pie(df, names='risco_anemia_nivel', 
                             title='Distribuição - Risco de Anemia',
                             color='risco_anemia_nivel',
                             color_discrete_map={'ALTO': '#c62828', 'MÉDIO': '#ef6c00', 'BAIXO': '#2e7d32'})
                fig1.update_layout(showlegend=True)
                st.plotly_chart(fig1, use_container_width=True)
        
        with col2:
            if 'dds_calculado' in df.columns:
                fig2 = px.histogram(df, x='dds_calculado', 
                                   title='Distribuição - Diversidade Alimentar (DDS)',
                                   nbins=10,
                                   color='risco_anemia_nivel',
                                   color_discrete_map={'ALTO': '#c62828', 'MÉDIO': '#ef6c00', 'BAIXO': '#2e7d32'})
                st.plotly_chart(fig2, use_container_width=True)
        
        # ===== RECOMENDAÇÕES =====
        st.divider()
        st.subheader("💡 Recomendações Gerais")
        
        total_alto = len(df[df['risco_anemia_nivel'] == 'ALTO'])
        total_medio = len(df[df['risco_anemia_nivel'] == 'MÉDIO'])
        total_fome_alto = len(df[df['risco_fome_nivel'] == 'ALTO'])
        total_inseg_alto = len(df[df['risco_inseguranca_nivel'] == 'ALTO'])
        
        if total_alto > 0:
            st.warning(f"🔴 **{total_alto} pacientes com Anemia ALTA** - Recomendar suplementação de ferro e alimentação rica em ferro.")
        
        if total_medio > 0:
            st.info(f"🟠 **{total_medio} pacientes com Anemia MÉDIA** - Reforçar consumo de alimentos ricos em ferro.")
        
        if total_fome_alto > 0:
            st.warning(f"🔴 **{total_fome_alto} pacientes com Fome Oculta ALTA** - Diversificar alimentação com micronutrientes.")
        
        if total_inseg_alto > 0:
            st.warning(f"🔴 **{total_inseg_alto} pacientes com Insegurança Alimentar ALTA** - Avaliar programas de complementação alimentar.")
        
        if total_alto == 0 and total_medio == 0 and total_fome_alto == 0 and total_inseg_alto == 0:
            st.success("✅ Todos os pacientes estão com baixo risco nutricional.")
    
    # ============================================================
    # ===== TAB 4: ENCAMINHAMENTOS =====
    # ============================================================
    with tab4:
        st.subheader("📨 Encaminhamentos Recebidos")
        
        if not enc_nutri:
            st.info("📋 Nenhum encaminhamento para nutricionista recebido ainda.")
        else:
            pendentes = [e for e in enc_nutri if e.get('status') != 'Concluído']
            atendidos = [e for e in enc_nutri if e.get('status') == 'Concluído']
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("📨 Total", len(enc_nutri))
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
                            st.markdown("**📊 Dados Clínicos**")
                            if 'dados_clinicos' in enc and enc['dados_clinicos']:
                                dados = enc['dados_clinicos']
                                if isinstance(dados, dict):
                                    st.markdown(f"- Hemoglobina: {dados.get('hemoglobina', 'N/A')} g/dL")
                                    st.markdown(f"- Tipo Anemia: {dados.get('tipo_anemia', 'N/A')}")
                                    st.markdown(f"- DDS: {dados.get('dds', 0)}/9")
                                    st.markdown(f"- MUAC: {dados.get('muac', 0)} mm")
                                else:
                                    st.markdown(f"- Dados: {dados}")
                        
                        st.divider()
                        
                        if st.button(f"✅ Marcar como Atendido - {enc.get('paciente', '')}", key=f"atender_nutri_{enc.get('paciente')}_{enc.get('data')}"):
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
                            st.markdown("**📊 Dados Clínicos**")
                            if 'dados_clinicos' in enc and enc['dados_clinicos']:
                                dados = enc['dados_clinicos']
                                if isinstance(dados, dict):
                                    st.markdown(f"- Hemoglobina: {dados.get('hemoglobina', 'N/A')} g/dL")
                                    st.markdown(f"- Tipo Anemia: {dados.get('tipo_anemia', 'N/A')}")
                                    st.markdown(f"- DDS: {dados.get('dds', 0)}/9")
                                    st.markdown(f"- MUAC: {dados.get('muac', 0)} mm")
                                else:
                                    st.markdown(f"- Dados: {dados}")
    
    # ============================================================
    # ===== TAB 5: RECOMENDAÇÕES =====
    # ============================================================
    with tab5:
        st.subheader("💡 Recomendações Gerais")
        
        st.markdown("""
        <div style="background-color: #e8f5e9; padding: 20px; border-radius: 12px; border-left: 8px solid #2e7d32;">
            <h4>📋 Orientações para a Família</h4>
            <ul>
                <li>✅ Alimentação variada com 5 grupos alimentares por dia</li>
                <li>✅ Incluir alimentos ricos em ferro (carnes, feijão, espinafre)</li>
                <li>✅ Consumir frutas e verduras coloridas diariamente</li>
                <li>✅ Evitar consumo excessivo de açúcares e gorduras</li>
                <li>✅ Beber água potável e manter boas práticas de higiene</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        st.divider()
        
        st.markdown("""
        <div style="background-color: #fff3e0; padding: 20px; border-radius: 12px; border-left: 8px solid #ef6c00;">
            <h4>🥗 Alimentos Ricos em Ferro</h4>
            <ul>
                <li>🥩 Carnes vermelhas, fígado, frango</li>
                <li>🐟 Peixe, mariscos</li>
                <li>🥚 Ovos</li>
                <li>🫘 Feijão, amendoim, ervilhas</li>
                <li>🥬 Espinafre, couve, hortaliças verdes</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        st.divider()
        
        st.markdown("""
        <div style="background-color: #e3f2fd; padding: 20px; border-radius: 12px; border-left: 8px solid #1565c0;">
            <h4>🍊 Alimentos Ricos em Vitamina C (para absorção de ferro)</h4>
            <ul>
                <li>🍊 Laranja, limão, toranja</li>
                <li>🥝 Kiwi</li>
                <li>🍓 Morango</li>
                <li>🍅 Tomate</li>
                <li>🥬 Pimentão, brócolos</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    render_nutricionista()