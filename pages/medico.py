# pages/medico.py
# ===== PERFIL MÉDICO - AVALIAÇÃO CLÍNICA =====

import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import json
import uuid
import base64
import time
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from app import t, SUPABASE_AVAILABLE
from supabase_config import salvar_encaminhamento_supabase, carregar_encaminhamentos_supabase

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

def carregar_pacientes_supabase():
    if not SUPABASE_AVAILABLE:
        return False, []
    try:
        resultado = supabase.table('criancas').select('*').order('created_at', desc=True).execute()
        return True, resultado.data
    except Exception as e:
        return False, str(e)

def atualizar_dados_clinicos_supabase(paciente_id, dados):
    """Atualiza os dados clínicos no Supabase"""
    try:
        if not SUPABASE_AVAILABLE:
            return False, "Supabase não disponível"
        if not paciente_id:
            return False, "ID do paciente não fornecido"
        resultado = supabase.table('criancas').update(dados).eq('id', paciente_id).execute()
        if resultado.data:
            return True, resultado.data
        else:
            return False, "Nenhum dado foi atualizado"
    except Exception as e:
        return False, str(e)

def salvar_decisao_clinica_supabase(decisao):
    try:
        if not SUPABASE_AVAILABLE:
            return False, "Supabase não disponível"
        dados = {
            'paciente': decisao['paciente'],
            'data': decisao['data'],
            'diagnostico': decisao.get('diagnostico', ''),
            'prescricao': decisao.get('prescricao', ''),
            'seguimento': decisao.get('seguimento', ''),
            'observacoes': decisao.get('observacoes', ''),
            'hemoglobina': decisao.get('hemoglobina', None),
            'tipo_anemia': decisao.get('tipo_anemia', None),
            'densidade_parasitaria': decisao.get('densidade_parasitaria', None),
            'diarreia': decisao.get('diarreia', None),
            'doenca_cronica': decisao.get('doenca_cronica', None),
            'created_at': datetime.now().isoformat()
        }
        resultado = supabase.table('decisoes_clinicas').insert(dados).execute()
        return True, resultado.data
    except Exception as e:
        return False, str(e)

def carregar_decisoes_clinicas_supabase():
    try:
        if not SUPABASE_AVAILABLE:
            return False, []
        resultado = supabase.table('decisoes_clinicas').select('*').order('created_at', desc=True).execute()
        return True, resultado.data
    except Exception as e:
        return False, str(e)

def recarregar_pacientes():
    if SUPABASE_AVAILABLE:
        sucesso, dados = carregar_pacientes_supabase()
        if sucesso and dados:
            pacientes = []
            for item in dados:
                paciente = {
                    'id': item.get('id'),
                    'nome': item.get('nome_completo', 'N/A'),
                    'idade_meses': item.get('idade_meses', 0),
                    'peso_kg': item.get('peso', 0),
                    'altura_cm': item.get('altura', 0),
                    'muac_mm': item.get('muac', 0),
                    'hemoglobina': item.get('hemoglobina', None),
                    'tipo_anemia': item.get('tipo_anemia', None),
                    'densidade_parasitaria': item.get('densidade_parasitaria', None),
                    'diarreia': item.get('diarreia', None),
                    'doenca_cronica': item.get('doenca_cronica', None),
                    'doenca_cronica_especificar': item.get('doenca_cronica_especificar', None),
                    'anemia_risco': item.get('risco_anemia_nivel', 'N/A'),
                    'anemia_prob': item.get('risco_anemia_score', 0),
                    'diversidade_alimentar': item.get('dds_calculado', 0),
                    'data_registo': item.get('data_registo', 'N/A'),
                    'provincia': item.get('provincia', 'N/A'),
                    'distrito': item.get('distrito', 'N/A'),
                    'residencia': item.get('residencia', 'N/A'),
                    'hospital': item.get('hospital', 'N/A'),
                    'sexo': item.get('sexo', 'N/A'),
                    'producao_familiar': item.get('producao_familiar', 'N/A'),
                    'acesso_terra': item.get('acesso_terra', 'N/A'),
                    'culturas_produzidas': item.get('culturas_produzidas', 'N/A'),
                    'fonte_agua': item.get('fonte_agua', 'N/A'),
                    'dificuldades_producao': item.get('dificuldades_producao', 'N/A'),
                    'refeicoes_dia': item.get('refeicoes_dia', 'N/A'),
                    'alimentos_consumidos': item.get('alimentos_consumidos', []),
                    'alimentos_ferro': item.get('alimentos_ferro', []),
                    'frequencia_ferro': item.get('frequencia_ferro', 'N/A'),
                    'amamentacao': item.get('amamentacao', 'N/A'),
                    'meses_amamentacao': item.get('meses_amamentacao', 0),
                    'suplementacao_ferro': item.get('suplementacao_ferro', 'N/A'),
                    'suplementacao_vit_a': item.get('suplementacao_vit_a', 'N/A'),
                    'desparasitacao': item.get('desparasitacao', 'N/A')
                }
                pacientes.append(paciente)
            st.session_state.patients = pacientes
            return True
    return False

# ========== FUNÇÃO GERAR RELATÓRIO PDF ==========
def gerar_relatorio_pdf_com_qr(patient_data, record, medico_nome, assinatura):
    try:
        from fpdf import FPDF
        import qrcode
        from io import BytesIO
        import tempfile
        import os
        
        paciente = patient_data.get('nome', 'N/A') or 'N/A'
        prescricao_texto = record.get('prescricao', 'N/A') or 'N/A'
        diagnostico_texto = record.get('diagnostico', 'N/A') or 'N/A'
        seguimento_texto = record.get('seguimento', '30 dias') or '30 dias'
        data_emissao = datetime.now().strftime('%Y-%m-%d %H:%M')
        validade = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
        
        codigo_prescricao = datetime.now().strftime('%Y%m%d%H%M%S') + str(uuid.uuid4())[:8]
        
        dados_qr = {
            'codigo': codigo_prescricao,
            'paciente': paciente,
            'data': data_emissao,
            'medico': medico_nome,
            'prescricao': prescricao_texto,
            'diagnostico': diagnostico_texto,
            'seguimento': seguimento_texto,
            'validade': validade
        }
        
        qr = qrcode.QRCode(version=2, error_correction=qrcode.constants.ERROR_CORRECT_M, box_size=5, border=2)
        qr.add_data(json.dumps(dados_qr))
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        buffered = BytesIO()
        img.save(buffered, format="PNG")
        qr_data = buffered.getvalue()
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp_file:
            tmp_file.write(qr_data)
            qr_path = tmp_file.name
        
        pdf = FPDF()
        pdf.add_page()
        
        pdf.set_font("Arial", "B", 24)
        pdf.set_text_color(46, 125, 50)
        pdf.cell(0, 15, "NutriVision", ln=True, align='C')
        
        pdf.set_text_color(0, 0, 0)
        pdf.set_font("Arial", "B", 16)
        pdf.cell(0, 10, "RELATORIO CLINICO", ln=True, align='C')
        pdf.set_font("Arial", "I", 10)
        pdf.cell(0, 8, f"Data de emissao: {data_emissao}", ln=True, align='C')
        pdf.line(10, 55, 200, 55)
        pdf.ln(5)
        
        # DADOS DO PACIENTE
        pdf.set_font("Arial", "B", 12)
        pdf.set_fill_color(230, 240, 230)
        pdf.cell(0, 10, "DADOS DO PACIENTE", ln=True, fill=True)
        pdf.set_fill_color(255, 255, 255)
        pdf.set_font("Arial", "", 11)
        
        pdf.cell(60, 7, "Nome:", ln=0)
        pdf.cell(0, 7, f"{paciente}", ln=True)
        idade = patient_data.get('idade_meses', 0) or 0
        pdf.cell(60, 7, "Idade:", ln=0)
        pdf.cell(0, 7, f"{idade} meses", ln=True)
        sexo = patient_data.get('sexo', 'N/A') or 'N/A'
        pdf.cell(60, 7, "Sexo:", ln=0)
        pdf.cell(0, 7, f"{sexo}", ln=True)
        provincia = patient_data.get('provincia', 'N/A') or 'N/A'
        pdf.cell(60, 7, "Provincia:", ln=0)
        pdf.cell(0, 7, f"{provincia}", ln=True)
        hospital = patient_data.get('hospital', 'N/A') or 'N/A'
        pdf.cell(60, 7, "Hospital:", ln=0)
        pdf.cell(0, 7, f"{hospital}", ln=True)
        pdf.ln(3)
        
        pdf.set_font("Arial", "B", 12)
        pdf.set_fill_color(230, 240, 230)
        pdf.cell(0, 10, "DADOS CLINICOS", ln=True, fill=True)
        pdf.set_fill_color(255, 255, 255)
        pdf.set_font("Arial", "", 11)
        
        peso = patient_data.get('peso_kg', 0) or 0
        pdf.cell(60, 7, "Peso:", ln=0)
        pdf.cell(0, 7, f"{peso} kg", ln=True)
        altura = patient_data.get('altura_cm', 0) or 0
        pdf.cell(60, 7, "Altura:", ln=0)
        pdf.cell(0, 7, f"{altura} cm", ln=True)
        muac = patient_data.get('muac_mm', 0) or 0
        pdf.cell(60, 7, "MUAC:", ln=0)
        pdf.cell(0, 7, f"{muac} mm", ln=True)
        hemoglobina = patient_data.get('hemoglobina', 'N/A')
        if hemoglobina is None or hemoglobina == '':
            hemoglobina = 'N/A'
        pdf.cell(60, 7, "Hemoglobina:", ln=0)
        pdf.cell(0, 7, f"{hemoglobina} g/dL", ln=True)
        tipo_anemia = patient_data.get('tipo_anemia', 'N/A') or 'N/A'
        pdf.cell(60, 7, "Tipo de Anemia:", ln=0)
        pdf.cell(0, 7, f"{tipo_anemia}", ln=True)
        risco = patient_data.get('anemia_risco', 'N/A') or 'N/A'
        prob = patient_data.get('anemia_prob', 0)
        if prob is None:
            prob = 0
        pdf.cell(60, 7, "Risco de Anemia:", ln=0)
        pdf.cell(0, 7, f"{risco} ({prob:.1f}%)", ln=True)
        dds = patient_data.get('diversidade_alimentar', 0) or 0
        pdf.cell(60, 7, "DDS (Diversidade Alimentar):", ln=0)
        pdf.cell(0, 7, f"{dds}/9", ln=True)
        pdf.ln(3)
        
        pdf.set_font("Arial", "B", 12)
        pdf.set_fill_color(230, 240, 230)
        pdf.cell(0, 10, "DECISAO CLINICA", ln=True, fill=True)
        pdf.set_fill_color(255, 255, 255)
        pdf.set_font("Arial", "", 11)
        
        pdf.cell(60, 7, "Data da Decisao:", ln=0)
        pdf.cell(0, 7, f"{data_emissao}", ln=True)
        pdf.cell(60, 7, "Diagnostico:", ln=0)
        pdf.cell(0, 7, "", ln=True)
        pdf.set_x(60)
        pdf.multi_cell(0, 7, f"{diagnostico_texto}")
        pdf.ln(2)
        pdf.set_font("Arial", "B", 11)
        pdf.set_text_color(0, 100, 0)
        pdf.cell(60, 7, "PRESCRICAO MEDICA:", ln=0)
        pdf.set_text_color(0, 0, 0)
        pdf.set_font("Arial", "", 11)
        pdf.cell(0, 7, "", ln=True)
        pdf.set_x(60)
        pdf.multi_cell(0, 7, f"{prescricao_texto}")
        pdf.ln(2)
        pdf.set_text_color(0, 0, 0)
        pdf.cell(60, 7, "Plano de Seguimento:", ln=0)
        pdf.cell(0, 7, f"{seguimento_texto}", ln=True)
        pdf.ln(5)
        
        pdf.set_font("Arial", "B", 12)
        pdf.set_fill_color(230, 240, 230)
        pdf.cell(0, 10, "VALIDACAO DO RELATORIO", ln=True, fill=True)
        pdf.set_fill_color(255, 255, 255)
        
        try:
            if os.path.exists(qr_path):
                pdf.image(qr_path, x=10, y=pdf.get_y() + 5, w=50, h=50)
            else:
                pdf.cell(0, 7, "QR Code nao disponivel", ln=True)
        except Exception as e:
            pdf.cell(0, 7, f"QR Code: {str(e)[:30]}", ln=True)
        
        pdf.set_y(pdf.get_y() + 5)
        pdf.set_x(70)
        pdf.set_font("Arial", "B", 11)
        pdf.cell(0, 7, "ESCANEIE O QR CODE", ln=True)
        pdf.set_x(70)
        pdf.set_font("Arial", "", 9)
        pdf.cell(0, 5, "Para validar a autenticidade do relatorio", ln=True)
        pdf.set_x(70)
        pdf.cell(0, 5, f"Codigo: {codigo_prescricao}", ln=True)
        pdf.set_x(70)
        pdf.cell(0, 5, f"Validade: {validade}", ln=True)
        pdf.ln(15)
        
        pdf.set_font("Arial", "B", 12)
        pdf.set_fill_color(230, 240, 230)
        pdf.cell(0, 10, "ASSINATURA DO MEDICO", ln=True, fill=True)
        pdf.set_fill_color(255, 255, 255)
        pdf.set_font("Arial", "", 11)
        
        pdf.ln(10)
        pdf.cell(80, 10, "_________________________", ln=0)
        pdf.cell(30, 10, "", ln=0)
        pdf.set_font("Arial", "B", 14)
        pdf.set_text_color(0, 100, 0)
        pdf.cell(20, 10, "[SELO]", ln=0, align='C')
        pdf.set_text_color(0, 0, 0)
        pdf.set_font("Arial", "", 11)
        pdf.cell(30, 10, "", ln=0)
        pdf.cell(80, 10, "_________________________", ln=True)
        
        medico_nome = medico_nome or '_________________________'
        pdf.cell(80, 7, medico_nome, ln=0)
        pdf.cell(30, 7, "", ln=0)
        pdf.set_font("Arial", "I", 8)
        pdf.set_text_color(0, 100, 0)
        pdf.cell(20, 7, "DIGITAL", ln=0, align='C')
        pdf.set_text_color(0, 0, 0)
        pdf.set_font("Arial", "", 11)
        pdf.cell(30, 7, "", ln=0)
        pdf.cell(80, 7, "Assinatura Eletronica", ln=True)
        pdf.cell(0, 7, f"Assinado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}", ln=True)
        
        pdf.set_y(270)
        pdf.set_font("Arial", "I", 8)
        pdf.cell(0, 7, "NutriVision - Plataforma de Detecao Precoce", ln=True, align='C')
        pdf.cell(0, 7, f"Relatorio Clinico - {datetime.now().strftime('%Y-%m-%d')}", ln=True, align='C')
        
        pdf_output = pdf.output(dest='S').encode('latin1')
        
        try:
            if os.path.exists(qr_path):
                os.remove(qr_path)
        except:
            pass
        
        return pdf_output
    
    except ImportError as e:
        st.error(f"❌ Biblioteca nao instalada: {e}. Execute: pip install qrcode[pil] fpdf")
        return None
    except Exception as e:
        st.error(f"❌ Erro ao gerar PDF: {e}")
        return None

# ========== FUNÇÃO PARA CARREGAR ENCAMINHAMENTOS ==========
def carregar_encaminhamentos_medico():
    if SUPABASE_AVAILABLE:
        sucesso, dados = carregar_encaminhamentos_supabase()
        if sucesso and dados:
            st.session_state.encaminhamentos = dados
            return True
    return False

# ========== FUNÇÃO PRINCIPAL ==========
def render_medico():
    # ===== CARREGAR DADOS =====
    if 'patients' not in st.session_state or not st.session_state.patients:
        if SUPABASE_AVAILABLE:
            recarregar_pacientes()
            if st.session_state.patients:
                st.success(f"✅ {len(st.session_state.patients)} {t('pacientes')} {t('carregados')}!")
        else:
            st.session_state.patients = []
            st.warning(t('supabase_indisponivel'))
    
    st.title(f"👨🏾⚕️ {t('medico_titulo')}")
    st.markdown(f"""
    <p style='color: #555; margin-bottom: 2rem;'>
    {t('descricao_medico')}
    </p>
    """, unsafe_allow_html=True)
    
    # ===== INICIALIZAR SESSION STATE =====
    if 'medical_records' not in st.session_state:
        st.session_state.medical_records = []
    if 'encaminhamentos' not in st.session_state:
        st.session_state.encaminhamentos = []
    if 'modo_edicao' not in st.session_state:
        st.session_state.modo_edicao = False
    if 'paciente_em_edicao' not in st.session_state:
        st.session_state.paciente_em_edicao = None
    if 'paciente_selecionado' not in st.session_state:
        st.session_state.paciente_selecionado = None
    if 'limpar_campos' not in st.session_state:
        st.session_state.limpar_campos = False
    
    # ===== CARREGAR DECISÕES =====
    if SUPABASE_AVAILABLE and not st.session_state.medical_records:
        sucesso, dados = carregar_decisoes_clinicas_supabase()
        if sucesso and dados:
            st.session_state.medical_records = dados
    
    # ===== CARREGAR ENCAMINHAMENTOS =====
    if SUPABASE_AVAILABLE and not st.session_state.encaminhamentos:
        carregar_encaminhamentos_medico()
    
    # ===== VERIFICAR SE HÁ PACIENTES =====
    if not st.session_state.patients:
        st.warning(t('nenhum_paciente'))
        st.info("""
        📋 **Fluxo de Trabalho:**
        1. 👩🏾⚕️ Enfermeiro realiza a triagem e regista o paciente
        2. 📨 Pacientes com alto risco são encaminhados para o médico
        3. 👨🏾⚕️ Médico avalia, regista dados e faz o seguimento
        """)
        if st.button(t('recarregar'), use_container_width=True):
            recarregar_pacientes()
            st.rerun()
        return
    
    patients = st.session_state.patients
    
    # ===== ABAS =====
    tab1, tab2, tab3, tab4 = st.tabs([
        t('avaliacao'), 
        t('dashboard'), 
        t('historico'), 
        t('encaminhamentos')
    ])
    
    # ============================================================
    # ===== TAB 1: AVALIAÇÃO =====
    # ============================================================
    with tab1:
        st.subheader(t('gestao_pacientes'))
        
        pacientes_pendentes = [p for p in patients if p.get('hemoglobina') is None or p.get('hemoglobina') == 0]
        pacientes_analisados = [p for p in patients if p.get('hemoglobina') is not None and p.get('hemoglobina') > 0]
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("👶 Total", len(patients))
        with col2:
            st.metric("⏳ Pendentes", len(pacientes_pendentes))
        with col3:
            st.metric("✅ Analisados", len(pacientes_analisados))
        with col4:
            alto_risco = len([p for p in pacientes_pendentes if p.get('anemia_risco') == 'ALTO'])
            st.metric("🔴 Alto Risco", alto_risco)
        
        st.divider()
        
        if pacientes_pendentes:
            st.warning(f"⚠️ **{len(pacientes_pendentes)} {t('casos_aguardam_avaliacao')}**")
            df_pendentes = pd.DataFrame(pacientes_pendentes)
            st.dataframe(df_pendentes[['nome', 'idade_meses', 'anemia_risco', 'anemia_prob', 'data_registo']], use_container_width=True)
            if st.button("📋 Avaliar Próximo Caso", use_container_width=True):
                primeiro = pacientes_pendentes[0]['nome']
                st.session_state.paciente_selecionado = primeiro
                st.session_state.paciente_em_edicao = primeiro
                st.session_state.modo_edicao = True
                st.rerun()
        else:
            st.success("✅ Todos os pacientes foram avaliados!")
        
        st.divider()
        
        st.subheader(t('selecionar_paciente'))
        lista_pacientes = [p['nome'] for p in patients]
        selected = st.selectbox(t('pacientes'), lista_pacientes)
        st.session_state.paciente_selecionado = selected
        
        patient_data = next((p for p in patients if p['nome'] == selected), None)
        
        if patient_data:
            st.divider()
            
            # ===== STATUS DE AVALIAÇÃO =====
            is_avaliado = patient_data.get('hemoglobina') is not None and patient_data.get('hemoglobina') > 0
            
            if is_avaliado:
                ultima_data = "N/A"
                for r in reversed(st.session_state.medical_records):
                    if r.get('paciente') == selected:
                        ultima_data = r.get('data', 'N/A')
                        break
                st.success(f"✅ **Paciente avaliado em:** {ultima_data}")
            else:
                st.warning("⏳ **Paciente aguarda avaliação médica**")
            
            st.divider()
            
            # ===== DADOS DO PACIENTE =====
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f"### 👶 {patient_data['nome']}")
                st.markdown(f"**📏 {t('idade')}:** {patient_data['idade_meses']} {t('meses')}")
                st.markdown(f"**⚖️ {t('peso')}:** {patient_data['peso_kg']} kg")
                st.markdown(f"**📐 {t('altura')}:** {patient_data['altura_cm']} cm")
                st.markdown(f"**📏 {t('muac')}:** {patient_data['muac_mm']} mm")
                st.markdown(f"**📍 {t('provincia')}:** {patient_data.get('provincia', 'N/A')}")
                st.markdown(f"**🏥 {t('hospital')}:** {patient_data.get('hospital', 'N/A')}")
            
            with col2:
                st.markdown("#### 🩺 Risco")
                risco = patient_data.get('anemia_risco', 'N/A')
                cor = "🔴" if risco == "ALTO" else "🟡" if risco == "MÉDIO" else "🟢"
                st.metric(t('risco_anemia'), f"{cor} {risco}")
                st.metric("Probabilidade", f"{patient_data.get('anemia_prob', 0)}%")
                st.metric(t('dds'), f"{patient_data.get('diversidade_alimentar', 0)}/9")
            
            st.divider()
            
            # ============================================================
            # ===== ATUALIZAR DADOS CLÍNICOS =====
            # ============================================================
            st.markdown(f"### 🩺 {t('atualizar_dados_clinicos')}")
            st.caption(t('atualizar_dados_caption'))
            
            # Inicializar campos
            if f'hb_{selected}' not in st.session_state or st.session_state[f'hb_{selected}'] is None:
                valor_inicial = patient_data.get('hemoglobina', 12.0)
                if valor_inicial is None or valor_inicial == '':
                    valor_inicial = 12.0
                st.session_state[f'hb_{selected}'] = float(valor_inicial)
            
            if f'tipo_anemia_{selected}' not in st.session_state or st.session_state[f'tipo_anemia_{selected}'] is None:
                valor_inicial = patient_data.get('tipo_anemia', 'Selecionar...')
                if valor_inicial is None or valor_inicial == '':
                    valor_inicial = 'Selecionar...'
                st.session_state[f'tipo_anemia_{selected}'] = valor_inicial
            
            if f'densidade_{selected}' not in st.session_state or st.session_state[f'densidade_{selected}'] is None:
                valor_inicial = patient_data.get('densidade_parasitaria', 'Selecionar...')
                if valor_inicial is None or valor_inicial == '':
                    valor_inicial = 'Selecionar...'
                st.session_state[f'densidade_{selected}'] = valor_inicial
            
            if f'diarreia_{selected}' not in st.session_state or st.session_state[f'diarreia_{selected}'] is None:
                valor_inicial = patient_data.get('diarreia', 'Selecionar...')
                if valor_inicial is None or valor_inicial == '':
                    valor_inicial = 'Selecionar...'
                st.session_state[f'diarreia_{selected}'] = valor_inicial
            
            if f'doenca_{selected}' not in st.session_state or st.session_state[f'doenca_{selected}'] is None:
                valor_inicial = patient_data.get('doenca_cronica', 'Selecionar...')
                if valor_inicial is None or valor_inicial == '':
                    valor_inicial = 'Selecionar...'
                st.session_state[f'doenca_{selected}'] = valor_inicial
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f"**🩸 {t('hemoglobina')}**")
                novo_valor_hb = st.number_input(
                    f"{t('hemoglobina')} (g/dL):",
                    min_value=0.0,
                    max_value=20.0,
                    value=float(st.session_state[f'hb_{selected}']),
                    step=0.1,
                    key=f"hb_input_{selected}"
                )
                st.session_state[f'hb_{selected}'] = novo_valor_hb
            
            with col2:
                st.markdown(f"**📋 {t('tipo_anemia')}**")
                tipo_options = [
                    "Selecionar...",
                    "Anemia Ferropriva",
                    "Anemia da Doença Crónica",
                    "Anemia Hemolítica",
                    "Anemia Megaloblástica",
                    "Anemia Falciforme",
                    "Talassemia",
                    "Anemia Mista",
                    "Não Anemia",
                    "Em investigação"
                ]
                tipo_anemia_select = st.selectbox(
                    t('selecione_tipo'),
                    tipo_options,
                    index=tipo_options.index(st.session_state[f'tipo_anemia_{selected}']) if st.session_state[f'tipo_anemia_{selected}'] in tipo_options else 0,
                    key=f"tipo_anemia_select_{selected}"
                )
                st.session_state[f'tipo_anemia_{selected}'] = tipo_anemia_select
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f"**🦟 {t('densidade_parasitaria')}**")
                densidade_options = [
                    "Selecionar...",
                    "Negativa",
                    "Positiva - Baixa (< 1000)",
                    "Positiva - Média (1000-5000)",
                    "Positiva - Alta (> 5000)",
                    "Em análise"
                ]
                densidade_select = st.selectbox(
                    t('selecione_resultado'),
                    densidade_options,
                    index=densidade_options.index(st.session_state[f'densidade_{selected}']) if st.session_state[f'densidade_{selected}'] in densidade_options else 0,
                    key=f"densidade_select_{selected}"
                )
                st.session_state[f'densidade_{selected}'] = densidade_select
            
            with col2:
                st.markdown(f"**💧 {t('diarreia')}**")
                diarreia_options = [
                    "Selecionar...",
                    "Não",
                    "Sim, 1-3 dias",
                    "Sim, 4-7 dias",
                    "Sim, mais de 7 dias",
                    "Em observação"
                ]
                diarreia_select = st.selectbox(
                    f"{t('diarreia')} ({t('ultimas_2_semanas')}):",
                    diarreia_options,
                    index=diarreia_options.index(st.session_state[f'diarreia_{selected}']) if st.session_state[f'diarreia_{selected}'] in diarreia_options else 0,
                    key=f"diarreia_select_{selected}"
                )
                st.session_state[f'diarreia_{selected}'] = diarreia_select
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f"**🏥 {t('doenca_cronica')}**")
                doenca_options = [
                    "Selecionar...",
                    "Não",
                    "Sim - HIV/SIDA",
                    "Sim - Tuberculose",
                    "Sim - Doença Cardíaca",
                    "Sim - Doença Renal",
                    "Sim - Diabetes",
                    "Sim - Asma",
                    "Sim - Desnutrição Crónica",
                    "Sim - Outra"
                ]
                doenca_cronica_select = st.selectbox(
                    t('doenca_cronica_conhecida'),
                    doenca_options,
                    index=doenca_options.index(st.session_state[f'doenca_{selected}']) if st.session_state[f'doenca_{selected}'] in doenca_options else 0,
                    key=f"doenca_cronica_select_{selected}"
                )
                st.session_state[f'doenca_{selected}'] = doenca_cronica_select
            
            with col2:
                st.markdown(f"**📋 {t('especificar_doenca')}**")
                doenca_especificar = st.text_input(
                    t('especificar_doenca_texto'),
                    value=patient_data.get('doenca_cronica_especificar', ''),
                    placeholder="Ex: HIV em TARV, Cardiopatia congénita...",
                    key=f"doenca_especificar_input_{selected}"
                )
            
            st.divider()
            
            # ============================================================
            # ===== SALVAR DADOS CLÍNICOS =====
            # ============================================================
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button(t('btn_atualizar_dados'), use_container_width=True):
                    if patient_data:
                        dados_atualizar = {}
                        alteracoes = False
                        
                        if novo_valor_hb != patient_data.get('hemoglobina', 0):
                            dados_atualizar['hemoglobina'] = novo_valor_hb
                            alteracoes = True
                        
                        if tipo_anemia_select != "Selecionar..." and tipo_anemia_select != patient_data.get('tipo_anemia'):
                            dados_atualizar['tipo_anemia'] = tipo_anemia_select
                            alteracoes = True
                        
                        if densidade_select != "Selecionar..." and densidade_select != patient_data.get('densidade_parasitaria'):
                            dados_atualizar['densidade_parasitaria'] = densidade_select
                            alteracoes = True
                        
                        if diarreia_select != "Selecionar..." and diarreia_select != patient_data.get('diarreia'):
                            dados_atualizar['diarreia'] = diarreia_select
                            alteracoes = True
                        
                        if doenca_cronica_select != "Selecionar..." and doenca_cronica_select != patient_data.get('doenca_cronica'):
                            dados_atualizar['doenca_cronica'] = doenca_cronica_select
                            alteracoes = True
                            if doenca_especificar:
                                dados_atualizar['doenca_cronica_especificar'] = doenca_especificar
                        
                        if alteracoes and dados_atualizar:
                            if SUPABASE_AVAILABLE and patient_data.get('id'):
                                with st.spinner("🔄 A atualizar no Supabase..."):
                                    sucesso, resultado = atualizar_dados_clinicos_supabase(
                                        patient_data['id'], 
                                        dados_atualizar
                                    )
                                    if sucesso:
                                        st.success(f"✅ Dados de {selected} atualizados no Supabase!")
                                        recarregar_pacientes()
                                        st.rerun()
                                    else:
                                        st.error(f"❌ Erro: {resultado}")
                            else:
                                st.warning(f"⚠️ Supabase não disponível. Dados salvos localmente.")
                                st.rerun()
                        elif not alteracoes:
                            st.warning(f"⚠️ Nenhum dado foi alterado")
                    else:
                        st.error(f"❌ Selecione um paciente válido")
            
            st.divider()
            
            # ============================================================
            # ===== DECISÃO CLÍNICA =====
            # ============================================================
            st.markdown(f"### 📝 {t('decisao_clinica')}")

            # Verificar se o paciente já foi avaliado
            is_avaliado = patient_data.get('hemoglobina') is not None and patient_data.get('hemoglobina') > 0

            # Se já foi avaliado, carregar a última decisão
            ultima_decisao = None
            if is_avaliado:
                for r in reversed(st.session_state.medical_records):
                    if r.get('paciente') == selected:
                        ultima_decisao = r
                        break

            # Inicializar ou carregar valores
            if f'prescricao_{selected}' not in st.session_state:
                if ultima_decisao:
                    st.session_state[f'prescricao_{selected}'] = ultima_decisao.get('prescricao', '')
                    st.session_state[f'diagnostico_{selected}'] = ultima_decisao.get('diagnostico', '')
                    st.session_state[f'observacoes_{selected}'] = ultima_decisao.get('observacoes', '')
                    st.session_state[f'seguimento_{selected}'] = ultima_decisao.get('seguimento', '30 dias')
                else:
                    st.session_state[f'prescricao_{selected}'] = ""
                    st.session_state[f'diagnostico_{selected}'] = ""
                    st.session_state[f'observacoes_{selected}'] = ""
                    st.session_state[f'seguimento_{selected}'] = "30 dias"

            # Estado de edição
            if f'editando_{selected}' not in st.session_state:
                st.session_state[f'editando_{selected}'] = False

            # ===== MOSTRAR MODO VISUALIZAÇÃO OU EDIÇÃO =====
            if is_avaliado and not st.session_state[f'editando_{selected}']:
                # ===== MODO VISUALIZAÇÃO =====
                st.info("📋 **Modo de visualização** - Clique em 'Editar' para modificar")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown(f"**💊 {t('prescricao')}**")
                    st.markdown(f"<div style='background-color: #f5f5f5; padding: 10px; border-radius: 5px; min-height: 80px;'>{st.session_state[f'prescricao_{selected}'] or 'N/A'}</div>", unsafe_allow_html=True)
                
                with col2:
                    st.markdown(f"**📋 {t('diagnostico')}**")
                    st.markdown(f"<div style='background-color: #f5f5f5; padding: 10px; border-radius: 5px; min-height: 80px;'>{st.session_state[f'diagnostico_{selected}'] or 'N/A'}</div>", unsafe_allow_html=True)
                
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"**📅 {t('seguimento')}**")
                    st.markdown(f"<div style='background-color: #f5f5f5; padding: 10px; border-radius: 5px;'>{st.session_state[f'seguimento_{selected}']}</div>", unsafe_allow_html=True)
                
                with col2:
                    st.markdown(f"**📋 {t('observacoes')}**")
                    st.markdown(f"<div style='background-color: #f5f5f5; padding: 10px; border-radius: 5px; min-height: 60px;'>{st.session_state[f'observacoes_{selected}'] or 'N/A'}</div>", unsafe_allow_html=True)
                
                st.divider()
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("✏️ Editar Decisão", use_container_width=True):
                        st.session_state[f'editando_{selected}'] = True
                        st.rerun()
                
                with col2:
                    # ===== GERAR RELATÓRIO =====
                    with st.expander("📄 Gerar Relatório PDF", expanded=False):
                        st.markdown(f"#### 📄 {t('relatorio_clinico')}")
                        
                        medico_nome = st.text_input(
                            t('medico_responsavel'),
                            placeholder="Dr. Nome Completo",
                            key=f"medico_nome_relatorio_view_{selected}"
                        )
                        
                        st.markdown(f"**✍️ {t('assinatura_eletronica')}**")
                        assinatura = st.text_input(
                            t('digitar_assinatura'),
                            placeholder=t('digitar_nome_assinar'),
                            key=f"assinatura_eletronica_view_{selected}"
                        )
                        
                        if st.button(t('btn_pdf'), use_container_width=True, key=f"pdf_view_{selected}"):
                            if not medico_nome:
                                st.warning(f"⚠️ {t('inserir_medico_responsavel')}")
                            elif not assinatura:
                                st.warning(f"⚠️ {t('inserir_assinatura')}")
                            else:
                                record_temp = {
                                    'data': datetime.now().strftime('%Y-%m-%d %H:%M'),
                                    'diagnostico': st.session_state.get(f'diagnostico_{selected}', ''),
                                    'prescricao': st.session_state.get(f'prescricao_{selected}', ''),
                                    'seguimento': st.session_state.get(f'seguimento_{selected}', '30 dias'),
                                    'observacoes': st.session_state.get(f'observacoes_{selected}', '')
                                }
                                
                                with st.spinner(t('gerando_pdf')):
                                    pdf_data = gerar_relatorio_pdf_com_qr(
                                        patient_data, 
                                        record_temp, 
                                        medico_nome, 
                                        assinatura
                                    )
                                    if pdf_data:
                                        b64 = base64.b64encode(pdf_data).decode()
                                        href = f'''
                                        <a href="data:application/pdf;base64,{b64}" 
                                        download="relatorio_{patient_data.get('nome', 'paciente')}_{datetime.now().strftime('%Y%m%d')}.pdf"
                                        style="display: inline-block; 
                                                background: linear-gradient(135deg, #2E7D32, #4CAF50);
                                                color: white;
                                                padding: 12px 24px;
                                                border-radius: 12px;
                                                text-decoration: none;
                                                font-weight: bold;
                                                text-align: center;
                                                width: 100%;
                                                box-shadow: 0 4px 15px rgba(46, 125, 50, 0.3);
                                                transition: all 0.3s ease;">
                                            📥 {t('btn_pdf')}
                                        </a>
                                        '''
                                        st.markdown(href, unsafe_allow_html=True)
                                        st.success(f"✅ {t('pdf_gerado')}")
                                        st.info(f"📱 {t('qr_code_validar')}")
                                    else:
                                        st.error(f"❌ {t('erro_gerar_pdf')}")
            else:
                # ===== MODO EDIÇÃO =====
                if is_avaliado:
                    st.info("✏️ **Modo de edição** - Modifique os campos e clique em 'Salvar Decisão'")
                    if st.button("🔒 Cancelar Edição", use_container_width=True):
                        if ultima_decisao:
                            st.session_state[f'prescricao_{selected}'] = ultima_decisao.get('prescricao', '')
                            st.session_state[f'diagnostico_{selected}'] = ultima_decisao.get('diagnostico', '')
                            st.session_state[f'observacoes_{selected}'] = ultima_decisao.get('observacoes', '')
                            st.session_state[f'seguimento_{selected}'] = ultima_decisao.get('seguimento', '30 dias')
                        st.session_state[f'editando_{selected}'] = False
                        st.rerun()
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown(f"#### 💊 {t('prescricao')}")
                    prescricao = st.text_area(
                        f"{t('prescricao')}:",
                        placeholder="Ex: Sulfato Ferroso 3mg/kg/dia, Ácido Fólico 0.4mg/dia...",
                        height=120,
                        key=f"prescricao_edit_{selected}",
                        value=st.session_state[f'prescricao_{selected}']
                    )
                    st.session_state[f'prescricao_{selected}'] = prescricao
                
                with col2:
                    st.markdown(f"#### 📋 {t('diagnostico')}")
                    diagnostico = st.text_area(
                        f"{t('diagnostico')}:",
                        placeholder="Ex: Anemia ferropriva moderada...",
                        height=120,
                        key=f"diagnostico_edit_{selected}",
                        value=st.session_state[f'diagnostico_{selected}']
                    )
                    st.session_state[f'diagnostico_{selected}'] = diagnostico
                
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"#### 📅 {t('seguimento')}")
                    seguimento = st.selectbox(
                        t('seguimento'),
                        ["7 dias", "15 dias", "30 dias", "60 dias", "90 dias"],
                        key=f"seguimento_edit_{selected}",
                        index=["7 dias", "15 dias", "30 dias", "60 dias", "90 dias"].index(st.session_state[f'seguimento_{selected}']) if st.session_state[f'seguimento_{selected}'] in ["7 dias", "15 dias", "30 dias", "60 dias", "90 dias"] else 2
                    )
                    st.session_state[f'seguimento_{selected}'] = seguimento
                with col2:
                    st.markdown(f"#### 📋 {t('observacoes')}")
                    observacoes = st.text_area(
                        f"{t('observacoes')}:",
                        placeholder=t('notas_caso'),
                        height=80,
                        key=f"observacoes_edit_{selected}",
                        value=st.session_state[f'observacoes_{selected}']
                    )
                    st.session_state[f'observacoes_{selected}'] = observacoes
                
                st.divider()
                
                # ===== BOTÃO SALVAR DECISÃO =====
                col1, col2, col3 = st.columns([1, 2, 1])
                with col2:
                    if st.button(t('btn_salvar'), use_container_width=True):
                        prescricao_val = st.session_state.get(f'prescricao_{selected}', '')
                        diagnostico_val = st.session_state.get(f'diagnostico_{selected}', '')
                        
                        if prescricao_val or diagnostico_val:
                            nova_decisao = {
                                'paciente': selected,
                                'data': datetime.now().strftime('%Y-%m-%d %H:%M'),
                                'diagnostico': diagnostico_val,
                                'prescricao': prescricao_val,
                                'seguimento': st.session_state.get(f'seguimento_{selected}', '30 dias'),
                                'observacoes': st.session_state.get(f'observacoes_{selected}', ''),
                                'hemoglobina': patient_data.get('hemoglobina', None),
                                'tipo_anemia': patient_data.get('tipo_anemia', None),
                                'densidade_parasitaria': patient_data.get('densidade_parasitaria', None),
                                'diarreia': patient_data.get('diarreia', None),
                                'doenca_cronica': patient_data.get('doenca_cronica', None)
                            }
                            
                            st.session_state.medical_records.append(nova_decisao)
                            
                            if SUPABASE_AVAILABLE:
                                sucesso, resultado = salvar_decisao_clinica_supabase(nova_decisao)
                                if sucesso:
                                    st.success(f"✅ {t('decisao_registada')} {selected} {t('no_supabase')}")
                                else:
                                    st.warning(f"⚠️ {t('decisao_local_erro')}: {resultado}")
                            else:
                                st.success(f"✅ {t('decisao_registada')} {selected} {t('localmente')}")
                            
                            st.session_state[f'editando_{selected}'] = False
                            st.rerun()
                        else:
                            st.warning(f"⚠️ {t('preencher_diagnostico_prescricao')}")
                            
            # ============================================================
            # ===== BOTÃO ENCAMINHAR =====
            # ============================================================
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                st.markdown(f"### 📨 {t('encaminhamento_integrado')}")
                st.markdown(f"""
                <div style="background-color: #e8f5e9; padding: 10px; border-radius: 10px; border-left: 5px solid #2e7d32; margin-bottom: 10px; font-size: 0.85rem;">
                    <p style="font-weight: bold; color: #1b5e20;">🌿 {t('encaminhamento_integrado')}</p>
                    <p>{t('encaminhamento_texto')}</p>
                    <p style="font-size: 0.8rem; color: #555;">💡 {t('encaminhamento_info')}</p>
                    <p style="font-size: 0.8rem; color: #555;">📤 Os encaminhamentos são guardados no Supabase</p>
                </div>
                """, unsafe_allow_html=True)
                
                urgencia_enc = st.selectbox(
                    t('urgencia'),
                    [t('urgencia_normal'), t('urgencia_urgente'), t('urgencia_muito_urgente')],
                    key=f"urgencia_enc_{selected}"
                )
                
                # ===== VERIFICAR SE JÁ EXISTE ENCAMINHAMENTO =====
                enc_existente = False
                for e in st.session_state.encaminhamentos:
                    if e.get('paciente') == selected and e.get('especialidade') in ['Nutricionista', 'Agrônomo'] and e.get('status') == 'Pendente':
                        enc_existente = True
                        break
                
                if enc_existente:
                    st.warning(f"⚠️ {selected} {t('encaminhamento_existente')}")
                else:
                    if st.button(t('btn_encaminhar'), use_container_width=True):
                        if selected and patient_data:
                            
                            # ============================================================
                            # ===== DADOS PARA NUTRICIONISTA (COMPLETOS) =====
                            # ============================================================
                            dados_nutricionista = {
                                # Dados clínicos
                                'hemoglobina': patient_data.get('hemoglobina', None),
                                'tipo_anemia': patient_data.get('tipo_anemia', None),
                                'densidade_parasitaria': patient_data.get('densidade_parasitaria', None),
                                'diarreia': patient_data.get('diarreia', None),
                                'doenca_cronica': patient_data.get('doenca_cronica', None),
                                'doenca_cronica_especificar': patient_data.get('doenca_cronica_especificar', None),
                                
                                # Risco e antropometria
                                'anemia_risco': patient_data.get('anemia_risco', 'N/A'),
                                'anemia_prob': patient_data.get('anemia_prob', 0),
                                'dds': patient_data.get('diversidade_alimentar', 0),
                                'muac': patient_data.get('muac_mm', 0),
                                'idade_meses': patient_data.get('idade_meses', 0),
                                'peso': patient_data.get('peso_kg', 0),
                                'altura': patient_data.get('altura_cm', 0),
                                
                                # Dados alimentares
                                'alimentos_consumidos': patient_data.get('alimentos_consumidos', []),
                                'alimentos_ferro': patient_data.get('alimentos_ferro', []),
                                'frequencia_ferro': patient_data.get('frequencia_ferro', 'N/A'),
                                'refeicoes_dia': patient_data.get('refeicoes_dia', 'N/A'),
                                'amamentacao': patient_data.get('amamentacao', 'N/A'),
                                'meses_amamentacao': patient_data.get('meses_amamentacao', 0),
                                'suplementacao_ferro': patient_data.get('suplementacao_ferro', 'N/A'),
                                'suplementacao_vit_a': patient_data.get('suplementacao_vit_a', 'N/A'),
                                'desparasitacao': patient_data.get('desparasitacao', 'N/A'),
                                
                                # Localização
                                'provincia': patient_data.get('provincia', 'N/A'),
                                'distrito': patient_data.get('distrito', 'N/A'),
                                'residencia': patient_data.get('residencia', 'N/A'),
                                'hospital': patient_data.get('hospital', 'N/A'),
                                
                                # Dados do médico
                                'diagnostico_medico': st.session_state.get(f'diagnostico_{selected}', 'N/A'),
                                'prescricao_medica': st.session_state.get(f'prescricao_{selected}', 'N/A'),
                                'seguimento': st.session_state.get(f'seguimento_{selected}', '30 dias'),
                                'observacoes_medicas': st.session_state.get(f'observacoes_{selected}', ''),
                                'data_encaminhamento': datetime.now().strftime('%Y-%m-%d %H:%M')
                            }
                            
                            # ============================================================
                            # ===== DADOS PARA AGRÔNOMO (COMPLETOS) =====
                            # ============================================================
                            dados_agronomo = {
                                # Dados nutricionais
                                'dds': patient_data.get('diversidade_alimentar', 0),
                                'muac': patient_data.get('muac_mm', 0),
                                'anemia_risco': patient_data.get('anemia_risco', 'N/A'),
                                'anemia_prob': patient_data.get('anemia_prob', 0),
                                'peso': patient_data.get('peso_kg', 0),
                                'altura': patient_data.get('altura_cm', 0),
                                'idade_meses': patient_data.get('idade_meses', 0),
                                
                                # Produção agrícola (do Enfermeiro)
                                'producao_familiar': patient_data.get('producao_familiar', 'N/A'),
                                'acesso_terra': patient_data.get('acesso_terra', 'N/A'),
                                'culturas_produzidas': patient_data.get('culturas_produzidas', 'N/A'),
                                'fonte_agua': patient_data.get('fonte_agua', 'N/A'),
                                'dificuldades_producao': patient_data.get('dificuldades_producao', 'N/A'),
                                
                                # Localização completa
                                'provincia': patient_data.get('provincia', 'N/A'),
                                'distrito': patient_data.get('distrito', 'N/A'),
                                'residencia': patient_data.get('residencia', 'N/A'),
                                'hospital': patient_data.get('hospital', 'N/A'),
                                
                                # Dados do médico
                                'diagnostico_medico': st.session_state.get(f'diagnostico_{selected}', 'N/A'),
                                'prescricao_medica': st.session_state.get(f'prescricao_{selected}', 'N/A'),
                                'seguimento': st.session_state.get(f'seguimento_{selected}', '30 dias'),
                                'observacoes_medicas': st.session_state.get(f'observacoes_{selected}', ''),
                                'data_encaminhamento': datetime.now().strftime('%Y-%m-%d %H:%M')
                            }
                            
                            # ============================================================
                            # ===== CRIAR ENCAMINHAMENTOS =====
                            # ============================================================
                            encaminhamento_nutri = {
                                'paciente': selected,
                                'especialidade': 'Nutricionista',
                                'urgencia': urgencia_enc,
                                'motivo': f"Encaminhamento integrado - Avaliação nutricional necessária. Diagnóstico: {st.session_state.get(f'diagnostico_{selected}', 'N/A')}",
                                'data': datetime.now().strftime('%Y-%m-%d %H:%M'),
                                'status': 'Pendente',
                                'medico_responsavel': st.session_state.get('usuario', 'Médico'),
                                'dados_clinicos': dados_nutricionista
                            }
                            
                            encaminhamento_agro = {
                                'paciente': selected,
                                'especialidade': 'Agrônomo',
                                'urgencia': urgencia_enc,
                                'motivo': f"Encaminhamento integrado - Intervenção agroalimentar necessária. Risco: {patient_data.get('anemia_risco', 'N/A')}",
                                'data': datetime.now().strftime('%Y-%m-%d %H:%M'),
                                'status': 'Pendente',
                                'medico_responsavel': st.session_state.get('usuario', 'Médico'),
                                'dados_clinicos': dados_agronomo
                            }
                            
                            # ===== SALVAR LOCALMENTE =====
                            st.session_state.encaminhamentos.append(encaminhamento_nutri)
                            st.session_state.encaminhamentos.append(encaminhamento_agro)
                            
                            # ===== SALVAR NO SUPABASE =====
                            sucesso_nutri, msg_nutri = salvar_encaminhamento_supabase(encaminhamento_nutri)
                            sucesso_agro, msg_agro = salvar_encaminhamento_supabase(encaminhamento_agro)
                            
                            if sucesso_nutri and sucesso_agro:
                                st.success(f"✅ {selected} {t('encaminhado_sucesso')} (guardado no Supabase!)")
                                
                                # Mostrar detalhes
                                with st.expander("📋 Detalhes dos dados enviados", expanded=False):
                                    st.markdown("#### 🍎 Dados enviados para Nutricionista:")
                                    st.json(dados_nutricionista)
                                    
                                    st.markdown("#### 🌾 Dados enviados para Agrônomo:")
                                    st.json(dados_agronomo)
                                    
                                    st.info(f"📊 Total: Nutricionista: {len(dados_nutricionista)} campos | Agrônomo: {len(dados_agronomo)} campos")
                            else:
                                st.warning(f"⚠️ {selected} encaminhado localmente. Erro no Supabase.")
                                st.info(f"Erro Nutricionista: {msg_nutri}")
                                st.info(f"Erro Agrônomo: {msg_agro}")
                            
                            # ===== ALERTAS DE URGÊNCIA =====
                            if urgencia_enc == t('urgencia_muito_urgente'):
                                st.error("🔴 🔴 **ENCAMINHAMENTO DE ALTA URGÊNCIA!** 🔴 🔴")
                                st.info("📞 Contactar imediatamente os profissionais responsáveis.")
                            elif urgencia_enc == t('urgencia_urgente'):
                                st.warning("🟠 **Encaminhamento URGENTE!**")
                                st.info("📞 Contactar os profissionais o mais breve possível.")
                            
                            st.session_state.modo_edicao = False
                            st.session_state.paciente_em_edicao = None
                            
                            time.sleep(1.5)
                            st.rerun()
                        else:
                            st.warning(f"⚠️ {t('selecionar_paciente_valido')}")
            
            st.divider()
            
            # ===== BOTÃO FECHAR CASO =====
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button(t('btn_fechar'), use_container_width=True):
                    st.session_state.modo_edicao = False
                    st.session_state.paciente_em_edicao = None
                    st.info(f"ℹ️ {t('caso_fechado')} {selected}")
                    time.sleep(1)
                    st.rerun()
    
    # ============================================================
    # ===== TAB 2: DASHBOARD =====
    # ============================================================
    with tab2:
        st.subheader(t('dashboard'))
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("👶 Total", len(patients))
        with col2:
            hb_baixa = sum(1 for p in patients if p.get('hemoglobina') is not None and p.get('hemoglobina', 12) < 11)
            st.metric("🩸 Hb < 11", hb_baixa)
        with col3:
            alto_risco = sum(1 for p in patients if p.get('anemia_risco') == 'ALTO')
            st.metric("🔴 Alto Risco", alto_risco)
        with col4:
            st.metric("📋 Decisões", len(st.session_state.medical_records))
        
        st.divider()
        
        col1, col2 = st.columns(2)
        with col1:
            if patients:
                df = pd.DataFrame(patients)
                fig = px.pie(df, names='anemia_risco', title=t('distribuicao_risco'),
                            color='anemia_risco',
                            color_discrete_map={'ALTO': '#c62828', 'MÉDIO': '#ef6c00', 'BAIXO': '#2e7d32'})
                fig.update_traces(textposition='inside', textinfo='percent+label')
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            if patients:
                df = pd.DataFrame(patients)
                fig = px.histogram(df, x='idade_meses', title='Distribuição por Idade', nbins=20)
                st.plotly_chart(fig, use_container_width=True)
        
        st.subheader(t('lista_pacientes'))
        df_patients = pd.DataFrame(patients)
        colunas = ['nome', 'idade_meses', 'hemoglobina', 'tipo_anemia', 'anemia_risco']
        colunas_exist = [c for c in colunas if c in df_patients.columns]
        st.dataframe(df_patients[colunas_exist], use_container_width=True)
    
    # ============================================================
    # ===== TAB 3: HISTÓRICO =====
    # ============================================================
    with tab3:
        st.subheader(t('historico'))
        
        if st.session_state.medical_records:
            df_records = pd.DataFrame(st.session_state.medical_records)
            st.dataframe(df_records[['paciente', 'data', 'diagnostico', 'prescricao', 'seguimento']], 
                        use_container_width=True)
            
            st.subheader("🔍 Detalhes por Paciente")
            selected_hist = st.selectbox(
                t('pacientes'),
                df_records['paciente'].unique().tolist()
            )
            if selected_hist:
                df_paciente = df_records[df_records['paciente'] == selected_hist]
                for _, row in df_paciente.iterrows():
                    with st.expander(f"📋 {row['data']}"):
                        st.markdown(f"**{t('diagnostico')}:** {row['diagnostico']}")
                        st.markdown(f"**{t('prescricao')}:** {row['prescricao']}")
                        st.markdown(f"**{t('seguimento')}:** {row['seguimento']}")
                        st.markdown(f"**{t('observacoes')}:** {row.get('observacoes', 'N/A')}")
                        st.markdown(f"**{t('hemoglobina')}:** {row.get('hemoglobina', 'N/A')} g/dL")
                        st.markdown(f"**{t('tipo_anemia')}:** {row.get('tipo_anemia', 'N/A')}")
        else:
            st.info(t('nenhum_registo'))
    
    # ============================================================
    # ===== TAB 4: ENCAMINHAMENTOS =====
    # ============================================================
    with tab4:
        st.subheader(t('encaminhamentos'))
        
        col1, col2 = st.columns([3, 1])
        with col2:
            if st.button("🔄 Recarregar", use_container_width=True):
                sucesso, dados = carregar_encaminhamentos_supabase()
                if sucesso and dados:
                    st.session_state.encaminhamentos = dados
                    st.success(f"✅ {len(dados)} encaminhamentos recarregados!")
                    st.rerun()
                else:
                    st.error(f"❌ Erro ao recarregar: {dados if not sucesso else 'vazio'}")
        
        if SUPABASE_AVAILABLE and not st.session_state.encaminhamentos:
            carregar_encaminhamentos_medico()
        
        if st.session_state.encaminhamentos:
            df_enc = pd.DataFrame(st.session_state.encaminhamentos)
            st.dataframe(df_enc, use_container_width=True)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                total = len(df_enc)
                st.metric("📋 Total", total)
            with col2:
                pendentes = len(df_enc[df_enc['status'] == 'Pendente'])
                st.metric("⏳ Pendentes", pendentes)
            with col3:
                concluidos = len(df_enc[df_enc['status'] == 'Concluído'])
                st.metric("✅ Concluídos", concluidos)
        else:
            st.info(t('nenhum_encaminhamento'))

if __name__ == "__main__":
    render_medico()