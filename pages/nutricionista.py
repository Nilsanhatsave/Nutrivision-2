import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# ========== IMPORT SUPABASE ==========
try:
    from supabase import create_client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False
    print("⚠️ Supabase não instalado. Execute: pip install supabase")

# ========== FUNÇÕES SUPABASE ==========
def get_supabase_client():
    """Inicializa o cliente Supabase"""
    if not SUPABASE_AVAILABLE:
        return None
    try:
        url = st.secrets["SUPABASE_URL"]
        key = st.secrets["SUPABASE_KEY"]
        return create_client(url, key)
    except:
        return None

def carregar_criancas_supabase():
    """Carrega todas as crianças do Supabase"""
    try:
        supabase = get_supabase_client()
        if supabase is None:
            return False, []
        
        resultado = supabase.table('criancas').select('*').order('created_at', desc=True).execute()
        return True, resultado.data
    except Exception as e:
        return False, str(e)

def render_nutricionista():
    st.title("👨🏾⚕️ Nutricionista - Recomendações Dietéticas")
    st.markdown("""
    <p style='color: #555; margin-bottom: 2rem;'>
    Análise nutricional e recomendações dietéticas baseadas nos dados da triagem
    </p>
    """, unsafe_allow_html=True)
    
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
    
    # ===== ENCAMINHAMENTOS =====
    if 'encaminhamentos' not in st.session_state:
        st.session_state.encaminhamentos = []
    
    # ===== FILTRAR ENCAMINHAMENTOS PARA NUTRICIONISTA =====
    encaminhamentos_nutri = [
        e for e in st.session_state.encaminhamentos 
        if 'Nutricionista' in e.get('especialidade', '')
    ]
    
    # Abas
    tab1, tab2, tab3, tab4 = st.tabs([
        "📋 Pacientes", 
        "📨 Encaminhamentos",
        "📊 Análise Nutricional", 
        "💡 Recomendações"
    ])
    
    with tab1:
        st.subheader("👤 Selecionar Paciente")
        
        if not st.session_state.criancas:
            st.info("📋 Nenhum paciente registado no sistema.")
            return
        
        df = pd.DataFrame(st.session_state.criancas)
        selected = st.selectbox(
            "Selecione um paciente:",
            df['nome_completo'].unique().tolist()
        )
        
        patient_data = df[df['nome_completo'] == selected].iloc[0]
        
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
        
        # ===== RECOMENDAÇÕES =====
        st.divider()
        st.markdown("### 💡 Recomendações Nutricionais")
        
        recomendacoes = []
        
        if patient_data.get('risco_anemia_nivel') == 'ALTO':
            recomendacoes.append("🔴 **Anemia - Ação Imediata:**")
            recomendacoes.append("• Aumentar consumo de alimentos ricos em ferro (carnes, feijão, espinafre)")
            recomendacoes.append("• Combinar ferro com vitamina C (laranja, limão, goiaba)")
            recomendacoes.append("• Considerar suplementação de ferro (consultar médico)")
        
        if patient_data.get('dds_calculado', 0) <= 3:
            recomendacoes.append("🟠 **Baixa Diversidade Alimentar:**")
            recomendacoes.append("• Diversificar alimentação com 5 grupos alimentares por dia")
            recomendacoes.append("• Incluir frutas, verduras e proteínas em todas as refeições")
        
        if patient_data.get('ferro_consumidos', 0) <= 2:
            recomendacoes.append("🟠 **Baixo Consumo de Ferro:**")
            recomendacoes.append("• Incluir feijão, amendoim e carnes na alimentação")
            recomendacoes.append("• Consumir verduras escuras (espinafre, couve)")
        
        if not recomendacoes:
            recomendacoes.append("✅ Criança com bom estado nutricional. Manter acompanhamento.")
        
        for rec in recomendacoes:
            st.info(rec)
        
        # ===== PLANO ALIMENTAR =====
        st.markdown("### 📝 Elaborar Plano Alimentar")
        
        with st.form("plano_alimentar"):
            col1, col2 = st.columns(2)
            
            with col1:
                frequencia = st.selectbox(
                    "Frequência de refeições recomendada:",
                    ["3 refeições/dia", "4 refeições/dia", "5 refeições/dia"]
                )
                proteinas = st.multiselect(
                    "Fontes de proteína recomendadas:",
                    ["Carnes", "Ovos", "Feijão", "Amendoim", "Peixe"]
                )
            
            with col2:
                frutas_verduras = st.multiselect(
                    "Frutas e verduras recomendadas:",
                    ["Banana", "Manga", "Laranja", "Cenoura", "Abóbora", "Espinafre", "Couve"]
                )
                observacoes_plano = st.text_area("Observações:", height=80)
            
            if st.form_submit_button("💾 Registar Plano Alimentar"):
                st.success("✅ Plano alimentar registado com sucesso!")
    
    with tab2:
        st.subheader("📨 Encaminhamentos Recebidos")
        
        if encaminhamentos_nutri:
            for enc in encaminhamentos_nutri:
                with st.expander(f"👶 {enc['paciente']} - {enc['data']}", expanded=False):
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
                            st.markdown(f"- Hemoglobina: {dados.get('hemoglobina', 'N/A')} g/dL")
                            st.markdown(f"- Tipo Anemia: {dados.get('tipo_anemia', 'N/A')}")
                            st.markdown(f"- Densidade Parasitária: {dados.get('densidade_parasitaria', 'N/A')}")
                            st.markdown(f"- DDS: {dados.get('dds', 0)}/9")
                            st.markdown(f"- MUAC: {dados.get('muac', 0)} mm")
                    
                    # Marcar como visto
                    if enc.get('status') == 'Pendente':
                        if st.button(f"✅ Marcar como Visto - {enc['paciente']}"):
                            for e in st.session_state.encaminhamentos:
                                if e['paciente'] == enc['paciente'] and e['data'] == enc['data']:
                                    e['status'] = 'Em análise'
                                    st.rerun()
        else:
            st.info("📋 Nenhum encaminhamento recebido ainda.")
    
    with tab3:
        st.subheader("📊 Análise Nutricional")
        
        if st.session_state.criancas:
            df = pd.DataFrame(st.session_state.criancas)
            
            col1, col2 = st.columns(2)
            
            with col1:
                fig1 = px.pie(df, names='risco_anemia_nivel', 
                             title='Distribuição - Risco de Anemia',
                             color='risco_anemia_nivel',
                             color_discrete_map={'ALTO': '#c62828', 'MÉDIO': '#ef6c00', 'BAIXO': '#2e7d32'})
                st.plotly_chart(fig1, use_container_width=True)
            
            with col2:
                fig2 = px.histogram(df, x='dds_calculado', 
                                  title='Distribuição - Diversidade Alimentar (DDS)',
                                  nbins=9)
                st.plotly_chart(fig2, use_container_width=True)
        else:
            st.info("📋 Nenhum dado disponível")
    
    with tab4:
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

if __name__ == "__main__":
    render_nutricionista()


