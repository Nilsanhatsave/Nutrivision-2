# supabase_client.py
# ===== CONEXÃO SUPABASE =====

from supabase import create_client
import json
from datetime import datetime

# ===== CHAVES DIRETAS (SEM SECRETS) =====
SUPABASE_URL = "https://llfcnigfidoiyhaitala.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImxsZmNuaWdmaWRvaXloYWl0YWxhIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODM2NTY2OTYsImV4cCI6MjA5OTIzMjY5Nn0.-WtmiDwYPS9eQDRsQ-bmXGKzvy4p9x7i9bzYGCgX3VM"

try:
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    SUPABASE_AVAILABLE = True
    print("✅ Supabase conectado com sucesso!")
except Exception as e:
    SUPABASE_AVAILABLE = False
    print(f"❌ Erro ao conectar Supabase: {e}")

# ============================================================
# ===== FUNÇÕES PARA CRIANÇAS =====
# ============================================================
def salvar_crianca_supabase(dados):
    if not SUPABASE_AVAILABLE:
        return False, "Supabase nao disponivel"
    try:
        response = supabase.table("criancas").insert(dados).execute()
        return True, response.data
    except Exception as e:
        return False, str(e)

def carregar_criancas_supabase():
    if not SUPABASE_AVAILABLE:
        return False, []
    try:
        response = supabase.table("criancas").select("*").execute()
        return True, response.data
    except Exception as e:
        return False, str(e)

def atualizar_crianca_supabase(id, dados):
    if not SUPABASE_AVAILABLE:
        return False, "Supabase nao disponivel"
    try:
        response = supabase.table("criancas").update(dados).eq("id", id).execute()
        return True, response.data
    except Exception as e:
        return False, str(e)

# ============================================================
# ===== FUNÇÕES PARA ENCAMINHAMENTOS =====
# ============================================================
def salvar_encaminhamento_supabase(encaminhamento):
    """Salva um encaminhamento no Supabase"""
    if not SUPABASE_AVAILABLE:
        return False, "Supabase não disponível"
    try:
        dados_clinicos = encaminhamento.get('dados_clinicos', {})
        if isinstance(dados_clinicos, str):
            try:
                dados_clinicos = json.loads(dados_clinicos)
            except:
                dados_clinicos = {}
        
        dados = {
            'paciente': encaminhamento.get('paciente', ''),
            'especialidade': encaminhamento.get('especialidade', ''),
            'urgencia': encaminhamento.get('urgencia', 'Normal'),
            'motivo': encaminhamento.get('motivo', ''),
            'data': encaminhamento.get('data', datetime.now().strftime('%Y-%m-%d %H:%M')),
            'status': encaminhamento.get('status', 'Pendente'),
            'medico_responsavel': encaminhamento.get('medico_responsavel', ''),
            'dados_clinicos': json.dumps(dados_clinicos)
        }
        resultado = supabase.table('encaminhamentos').insert(dados).execute()
        return True, resultado.data
    except Exception as e:
        return False, str(e)

def carregar_encaminhamentos_supabase(especialidade=None):
    """Carrega encaminhamentos do Supabase"""
    if not SUPABASE_AVAILABLE:
        return False, []
    try:
        query = supabase.table('encaminhamentos').select('*').order('created_at', desc=True)
        if especialidade:
            query = query.eq('especialidade', especialidade)
        resultado = query.execute()
        
        for item in resultado.data:
            if 'dados_clinicos' in item and item['dados_clinicos']:
                if isinstance(item['dados_clinicos'], str):
                    try:
                        item['dados_clinicos'] = json.loads(item['dados_clinicos'])
                    except:
                        item['dados_clinicos'] = {}
        return True, resultado.data
    except Exception as e:
        return False, str(e)

def atualizar_status_encaminhamento_supabase(paciente, data, novo_status):
    """Atualiza o status de um encaminhamento no Supabase"""
    if not SUPABASE_AVAILABLE:
        return False, "Supabase nao disponivel"
    try:
        resultado = supabase.table('encaminhamentos')\
            .update({'status': novo_status})\
            .eq('paciente', paciente)\
            .eq('data', data)\
            .execute()
        return True, resultado.data
    except Exception as e:
        return False, str(e)

def atualizar_encaminhamento_supabase(id, dados):
    """Atualiza um encaminhamento específico no Supabase"""
    if not SUPABASE_AVAILABLE:
        return False, "Supabase nao disponivel"
    try:
        resultado = supabase.table('encaminhamentos')\
            .update(dados)\
            .eq('id', id)\
            .execute()
        return True, resultado.data
    except Exception as e:
        return False, str(e)

def deletar_encaminhamento_supabase(id):
    """Deleta um encaminhamento do Supabase"""
    if not SUPABASE_AVAILABLE:
        return False, "Supabase nao disponivel"
    try:
        resultado = supabase.table('encaminhamentos')\
            .delete()\
            .eq('id', id)\
            .execute()
        return True, resultado.data
    except Exception as e:
        return False, str(e)

# ============================================================
# ===== FUNÇÕES PARA DECISÕES CLÍNICAS =====
# ============================================================
def salvar_decisao_clinica_supabase(decisao):
    """Salva a decisão clínica no Supabase"""
    try:
        if not SUPABASE_AVAILABLE:
            return False, "Supabase não disponível"
        
        dados = {
            'paciente': decisao.get('paciente', ''),
            'data': decisao.get('data', datetime.now().strftime('%Y-%m-%d %H:%M')),
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
    """Carrega as decisões clínicas do Supabase"""
    try:
        if not SUPABASE_AVAILABLE:
            return False, []
        
        resultado = supabase.table('decisoes_clinicas')\
            .select('*')\
            .order('created_at', desc=True)\
            .execute()
        return True, resultado.data
    except Exception as e:
        return False, str(e)

# ============================================================
# ===== FUNÇÕES PARA AVALIAÇÕES NUTRICIONAIS =====
# ============================================================
def salvar_avaliacao_nutricional_supabase(dados):
    """Salva a avaliação nutricional no Supabase"""
    if not SUPABASE_AVAILABLE:
        return False, "Supabase nao disponivel"
    try:
        resultado = supabase.table('avaliacoes_nutricionais').insert(dados).execute()
        return True, resultado.data
    except Exception as e:
        return False, str(e)

def carregar_avaliacoes_nutricionais_supabase():
    """Carrega as avaliações nutricionais do Supabase"""
    if not SUPABASE_AVAILABLE:
        return False, []
    try:
        resultado = supabase.table('avaliacoes_nutricionais')\
            .select('*')\
            .order('created_at', desc=True)\
            .execute()
        return True, resultado.data
    except Exception as e:
        return False, str(e)

# ============================================================
# ===== FUNÇÕES PARA PLANOS DE INTERVENÇÃO NUTRICIONAL =====
# ============================================================
def salvar_plano_intervencao_nutri_supabase(dados):
    """Salva o plano de intervenção nutricional no Supabase"""
    if not SUPABASE_AVAILABLE:
        return False, "Supabase nao disponivel"
    try:
        resultado = supabase.table('planos_intervencao_nutri').insert(dados).execute()
        return True, resultado.data
    except Exception as e:
        return False, str(e)

def carregar_planos_intervencao_nutri_supabase():
    """Carrega os planos de intervenção nutricional do Supabase"""
    if not SUPABASE_AVAILABLE:
        return False, []
    try:
        resultado = supabase.table('planos_intervencao_nutri')\
            .select('*')\
            .order('created_at', desc=True)\
            .execute()
        return True, resultado.data
    except Exception as e:
        return False, str(e)

# ============================================================
# ===== FUNÇÕES PARA AVALIAÇÕES AGRONÓMICAS =====
# ============================================================
def salvar_avaliacao_agro_supabase(dados):
    """Salva a avaliação agroalimentar no Supabase"""
    if not SUPABASE_AVAILABLE:
        return False, "Supabase nao disponivel"
    try:
        resultado = supabase.table('avaliacoes_agro').insert(dados).execute()
        return True, resultado.data
    except Exception as e:
        return False, str(e)

def carregar_avaliacoes_agro_supabase():
    """Carrega as avaliações agroalimentares do Supabase"""
    if not SUPABASE_AVAILABLE:
        return False, []
    try:
        resultado = supabase.table('avaliacoes_agro').select('*').order('created_at', desc=True).execute()
        return True, resultado.data
    except Exception as e:
        return False, str(e)

# ============================================================
# ===== FUNÇÕES PARA PLANOS DE INTERVENÇÃO AGRONÓMICA =====
# ============================================================
def salvar_plano_intervencao_agro_supabase(dados):
    """Salva o plano de intervenção agronómica no Supabase"""
    if not SUPABASE_AVAILABLE:
        return False, "Supabase nao disponivel"
    try:
        resultado = supabase.table('planos_intervencao_agro').insert(dados).execute()
        return True, resultado.data
    except Exception as e:
        return False, str(e)

def carregar_planos_intervencao_agro_supabase():
    """Carrega os planos de intervenção agronómica do Supabase"""
    if not SUPABASE_AVAILABLE:
        return False, []
    try:
        resultado = supabase.table('planos_intervencao_agro')\
            .select('*')\
            .order('created_at', desc=True)\
            .execute()
        return True, resultado.data
    except Exception as e:
        return False, str(e)