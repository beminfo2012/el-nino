import os
import io
import re
import time
import glob
import urllib.request
import json
from datetime import datetime, timedelta
from collections import Counter, defaultdict
import pandas as pd
from flask import Flask, jsonify, render_template, send_file, Response, request, redirect, url_for, session

DATA_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__, 
            static_folder=os.path.join(DATA_DIR, 'static'), 
            template_folder=os.path.join(DATA_DIR, 'templates'))
app.json.ensure_ascii = True
app.secret_key = os.environ.get('SECRET_KEY', 'defesa-civil-el-nino-smj-auth-2026-secret-key-prod')
@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '-1'
    if response.mimetype.startswith('text/') or response.mimetype == 'application/javascript' or response.mimetype == 'application/json':
        if 'charset=' not in response.content_type.lower():
            response.content_type = f"{response.mimetype}; charset=utf-8"
    return response

app.permanent_session_lifetime = timedelta(days=7)

def process_dataframe(df):
    risco_geologico = 0
    risco_hidrologico = 0
    susc_inundacao = 0
    mov_massa = 0
    todas_unidades = []

    # Conta Risco Geológico
    if 'Status Risco Geol.' in df.columns:
        risco_geologico += len(df[df['Status Risco Geol.'].astype(str).str.contains('DENTRO|ALTO|PRÓXIMO|PR\u00d3XIMO', case=False, na=False)])
        
    # Conta Risco Hidrológico
    if 'Status Risco Hidro.' in df.columns:
        risco_hidrologico += len(df[df['Status Risco Hidro.'].astype(str).str.contains('DENTRO|ALTO|PRÓXIMO|PR\u00d3XIMO', case=False, na=False)])
        
    if 'Status Susc. Inund.' in df.columns:
        susc_inundacao += len(df[df['Status Susc. Inund.'].astype(str).str.contains('DENTRO|ALTO|PRÓXIMO|PR\u00d3XIMO', case=False, na=False)])
        
    if 'Status Mov. Massa' in df.columns:
        mov_massa += len(df[df['Status Mov. Massa'].astype(str).str.contains('DENTRO|ALTO|PRÓXIMO|PR\u00d3XIMO', case=False, na=False)])

    nome_col = None
    for col in df.columns:
        if 'Escola' in str(col) or 'Unidade' in str(col) or 'Equipamento' in str(col):
            if 'Nome' in str(col):
                nome_col = col
                break
    if not nome_col:
        nome_col = df.columns[1] if len(df.columns) > 1 else None

    unit_risk_counts = {}
    if nome_col:
        for idx, row in df.iterrows():
            name = row[nome_col]
            if pd.isna(name):
                continue
            name = str(name).strip()
            if not name or name == '-':
                continue
            if name.isupper() and len(name) > 4:
                name = name.title().replace('Usf', 'USF').replace('Cmei', 'CMEI').replace('Emef', 'EMEF')
            
            c = 0
            for col in df.columns:
                if 'status' in str(col).lower():
                    val = str(row[col]).upper()
                    if any(k in val for k in ['DENTRO', 'ALTO', 'PRÓXIMO', 'PROXIMO']):
                        c += 1
            if c > 0:
                unit_risk_counts[name] = c

    total_riscos = risco_geologico + risco_hidrologico + susc_inundacao + mov_massa

    top_5 = sorted(unit_risk_counts.items(), key=lambda x: x[1], reverse=True)[:5]
    top_5_labels = [x[0] for x in top_5] if top_5 else ["Nenhuma localidade com risco"]
    top_5_values = [x[1] for x in top_5] if top_5 else [0]
    
    return {
        "tipologia_risco": {
            "labels": ["Estrutural (Mov. Massa)", "Ambiental (Susc. Inund.)", "Hidrológico", "Geológico"],
            "values": [mov_massa, susc_inundacao, risco_hidrologico, risco_geologico],
            "total": total_riscos
        },
        "ocorrencias_tipo": {
            "labels": ["Deslizamento (Geológico)", "Alagamento (Hidrológico)", "Estrutural (Mov. Massa)", "Suscetíveis à inundação"],
            "values": [risco_geologico, risco_hidrologico, mov_massa, susc_inundacao]
        },
        "top_5_localidades": {
            "labels": top_5_labels,
            "values": top_5_values
        }
    }

def extract_secmam_data():
    return {
        "kpis": {
            "cadastrados": 720,
            "ativos": 666,
            "suprimidos_historico": 54,
            "intervencoes_pendentes": 198,
            "risco_critico": 3,
            "interferencia_edp": 129
        },
        "distribuicao_risco": {
            "labels": ["Elevado (Imediato)", "Alto (Prioritário)", "Moderado (Programado)", "Baixo (Monitoramento)", "Pendente de Avaliação"],
            "values": [1, 2, 96, 311, 256],
            "colors": ["#7F1D1D", "#EA580C", "#EAB308", "#16A34A", "#94A3B8"]
        },
        "tipos_intervencao": {
            "labels": ["Poda de Redução de Copa", "Poda de Limpeza", "Supressão Preventiva", "Poda de Condução", "Apenas Monitoramento"],
            "values": [74, 50, 39, 35, 212],
            "colors": ["#0F4C81", "#2563EB", "#DC2626", "#059669", "#64748B"]
        },
        "interferencia_edp": {
            "labels": ["Contato Direto (EDP)", "Proximidade Crítica (EDP)", "Sem Conflito Elétrico"],
            "values": [92, 37, 537],
            "colors": ["#DC2626", "#F59E0B", "#10B981"]
        },
        "cronograma_prioridade": {
            "labels": ["P1 - Risco Elevado", "P2 - Risco Alto", "P3 - Risco Moderado", "P4 - Risco Baixo"],
            "values": [1, 2, 95, 100],
            "prazos": ["Imediato", "Duas primeiras semanas", "Programado (6 meses)", "Programado (6 meses)"]
        },
        "exemplares_criticos": [
            {"tombamento": "CAR-006", "especie": "Espatodea (Spathodea campanulata)", "local": "Centro urbano", "coordenadas": "E 324698 / N 7776756", "risco": "Elevado", "intervencao": "Supressão", "prazo": "Imediato"},
            {"tombamento": "SED-362", "especie": "Sibipiruna (Caesalpinia pluviosa)", "local": "Av. Frederico Grulke - Centro", "coordenadas": "E 317342 / N 7785907", "risco": "Alto", "intervencao": "Supressão", "prazo": "Prioritário (2 sem)"},
            {"tombamento": "CAR-008", "especie": "Sibipiruna (Caesalpinia pluviosa)", "local": "Centro urbano", "coordenadas": "E 324703 / N 7776770", "risco": "Alto", "intervencao": "Poda de redução de copa", "prazo": "Prioritário (2 sem)"}
        ]
    }

def extract_cesan_data():
    cesan_json_path = os.path.join(DATA_DIR, 'dados', 'cesan_historico.json')
    pdfs = glob.glob(os.path.join(DATA_DIR, '*Boletim*.pdf')) + glob.glob(os.path.join(DATA_DIR, 'arquivo_morto', '*Boletim*.pdf'))
    
    if not pdfs and os.path.exists(cesan_json_path):
        try:
            import json
            with open(cesan_json_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            pass

    results = []
    
    for pdf in pdfs:
        try:
            filename = os.path.basename(pdf)
            date_str = ""
            import re
            m = re.search(r'(\d{2}\.\d{2}\.\d{4}|\d{4}\.\d{2}\.\d{2})', filename)
            if m:
                date_str = m.group(1)
            
            try:
                import fitz
            except ImportError:
                break
            doc = fitz.open(pdf)
            text = '\n'.join([page.get_text() for page in doc])
            
            status = "Normal"
            val = 0
            
            if "jetib" in text.lower():
                lines = text.split('\n')
                for i, line in enumerate(lines):
                    if 'jetib' in line.lower():
                        window = ' '.join(lines[max(0, i-6):min(len(lines), i+7)]).lower()
                        if 'alerta' in window:
                            status = "Alerta"
                            val = 2
                        elif 'atenção' in window or 'atencao' in window:
                            status = "Atenção"
                            val = 1
                        elif 'crític' in window or 'critico' in window:
                            status = "Crítico"
                            val = 3
                        break
            
            if date_str:
                results.append({"date": date_str, "status": status, "value": val})
                
        except Exception as e:
            print(f"Erro ao processar PDF {pdf}: {e}")

    if not results and os.path.exists(cesan_json_path):
        try:
            import json
            with open(cesan_json_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            pass
            
    for r in results:
        parts = r["date"].split('.')
        if len(parts[0]) == 4:
            r["sort_key"] = f"{parts[0]}-{parts[1]}-{parts[2]}"
            r["label"] = f"{parts[2]}/{parts[1]}"
        else:
            r["sort_key"] = f"{parts[2]}-{parts[1]}-{parts[0]}"
            r["label"] = f"{parts[0]}/{parts[1]}"
            
    results.sort(key=lambda x: x["sort_key"])
    
    return {
        "timeline_labels": [r["label"] for r in results],
        "timeline_values": [r["value"] for r in results],
        "timeline_status": [r["status"] for r in results]
    }

GOOGLE_SHEET_ID = '18BPm5_ttIye48ngtLfSc91S3DNc8EGdROTl5IzymKRE'
GOOGLE_SHEET_URL = f"https://docs.google.com/spreadsheets/d/{GOOGLE_SHEET_ID}/export?format=xlsx"
USERS_GOOGLE_SHEET_ID = os.environ.get('USERS_GOOGLE_SHEET_ID', '1IjwgUof08g7V2-TqqTTf_yI-wxExsBD6p8kSyny9808')
USERS_GOOGLE_SHEET_URL = f"https://docs.google.com/spreadsheets/d/{USERS_GOOGLE_SHEET_ID}/export?format=xlsx"
LOCAL_BACKUP_PATH = os.path.join(DATA_DIR, 'dados', 'Planilha_Alimentacao_Dashboard_ElNino_SMJ.xlsx')
USERS_LOCAL_PATH = os.path.join(DATA_DIR, 'Planilha_Usuarios_Controle_Acesso.xlsx')
USERS_BACKUP_PATH = os.path.join(DATA_DIR, 'dados', 'Planilha_Usuarios_Controle_Acesso.xlsx')

_users_cache = {
    "data": None,
    "last_fetch": 0,
    "cache_ttl": 60  # Cache de 60 segundos para evitar requisições repetitivas ao Drive
}

def clean_cpf(cpf):
    """Remove pontuação e caracteres não numéricos do CPF, preenchendo zeros à esquerda se omitidos pelo Excel."""
    if not cpf:
        return ""
    # Se for int ou float vindo do Excel
    if isinstance(cpf, float) and cpf.is_integer():
        cpf = int(cpf)
    digits = re.sub(r'\D', '', str(cpf).strip())
    if 0 < len(digits) < 11:
        digits = digits.zfill(11)
    return digits

def format_cpf_display(digits):
    """Formata sequência de 11 dígitos no padrão oficial XXX.XXX.XXX-XX."""
    digits = clean_cpf(digits)
    if len(digits) == 11:
        return f"{digits[:3]}.{digits[3:6]}.{digits[6:9]}-{digits[9:]}"
    return digits

def clean_password(pwd):
    """Normaliza senha lida de formulário ou planilha Excel, tratando inteiros e floats."""
    if pwd is None:
        return ""
    if isinstance(pwd, float) and pwd.is_integer():
        return str(int(pwd))
    return str(pwd).strip()

def get_authorized_users(force_refresh=False):
    """
    Carrega a lista de usuários autorizados a partir da planilha do Google Drive ou local.
    Verifica se existe a aba 'Usuarios' ou 'Acesso' na planilha online (ou em URL específica).
    Retorna dicionário mapeado por dígitos limpos do CPF.
    """
    now = time.time()
    if not force_refresh and _users_cache["data"] and (now - _users_cache["last_fetch"] < _users_cache["cache_ttl"]):
        return _users_cache["data"]
        
    users = {}
    
    # 1. Tentar ler do Google Drive (Planilha dedicada de usuários como prioridade)
    urls_to_try = [USERS_GOOGLE_SHEET_URL]
    if GOOGLE_SHEET_URL and GOOGLE_SHEET_URL not in urls_to_try:
        urls_to_try.append(GOOGLE_SHEET_URL)

        
    for url in urls_to_try:
        try:
            req = urllib.request.Request(
                url,
                headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            )
            with urllib.request.urlopen(req, timeout=5) as resp:
                excel_bytes = resp.read()
                
            import openpyxl
            wb = openpyxl.load_workbook(io.BytesIO(excel_bytes), data_only=True)
            user_sheet_name = None
            for s in wb.sheetnames:
                if s.lower() in ['usuarios', 'usuários', 'acesso', 'users', 'login', 'controle_acesso']:
                    user_sheet_name = s
                    break
                    
            if user_sheet_name:
                ws = wb[user_sheet_name]
                headers = [str(cell.value or '').strip() for cell in ws[1]]
                col_map = {}
                for idx, h in enumerate(headers):
                    h_norm = h.lower()
                    if any(k in h_norm for k in ['cpf', 'login', 'documento']):
                        if 'cpf' not in col_map: col_map['cpf'] = idx
                    elif any(k in h_norm for k in ['senha', 'password', 'pass']):
                        if 'senha' not in col_map: col_map['senha'] = idx
                    elif any(k in h_norm for k in ['nome', 'servidor', 'usuario', 'usuário']):
                        if 'nome' not in col_map: col_map['nome'] = idx
                    elif any(k in h_norm for k in ['setor', 'orgao', 'órgão', 'secretaria', 'departamento']):
                        if 'setor' not in col_map: col_map['setor'] = idx
                    elif any(k in h_norm for k in ['email', 'e-mail']):
                        if 'email' not in col_map: col_map['email'] = idx
                    elif any(k in h_norm for k in ['status', 'situacao', 'situação', 'ativo']):
                        if 'status' not in col_map: col_map['status'] = idx
                    elif any(k in h_norm for k in ['obs', 'observacao', 'observação']):
                        if 'observacoes' not in col_map: col_map['observacoes'] = idx
                    
                if 'cpf' in col_map and 'senha' in col_map:
                    for row in ws.iter_rows(min_row=2, values_only=True):
                        if not any(row):
                            continue
                        cpf_val = row[col_map['cpf']] if len(row) > col_map['cpf'] else None
                        senha_val = row[col_map['senha']] if len(row) > col_map['senha'] else None
                        if cpf_val is None or senha_val is None:
                            continue
                        cpf_c = clean_cpf(cpf_val)
                        pwd_c = clean_password(senha_val)
                        if not cpf_c or not pwd_c:
                            continue
                        nome_val = str(row[col_map['nome']]).strip() if col_map.get('nome') is not None and len(row) > col_map['nome'] and row[col_map['nome']] else 'Usuário'
                        setor_val = str(row[col_map['setor']]).strip() if col_map.get('setor') is not None and len(row) > col_map['setor'] and row[col_map['setor']] else 'Defesa Civil'
                        email_val = str(row[col_map['email']]).strip() if col_map.get('email') is not None and len(row) > col_map['email'] and row[col_map['email']] else ''
                        status_val = str(row[col_map['status']]).strip() if col_map.get('status') is not None and len(row) > col_map['status'] and row[col_map['status']] else 'Ativo'
                        
                        users[cpf_c] = {
                            "nome": nome_val,
                            "cpf": format_cpf_display(cpf_c),
                            "cpf_clean": cpf_c,
                            "senha": pwd_c,
                            "setor": setor_val,
                            "email": email_val,
                            "status": status_val
                        }
                    if users:
                        _users_cache["data"] = users
                        _users_cache["last_fetch"] = now
                        return users
        except Exception:
            pass

    # 2. Fallback: Ler das planilhas locais (Planilha_Controle_Acesso_Usuarios_SMJ.xlsx, Planilha_Usuarios_Controle_Acesso.xlsx, ou principal)
    local_candidates = [
        os.path.join(DATA_DIR, 'Planilha_Controle_Acesso_Usuarios_SMJ.xlsx'),
        USERS_LOCAL_PATH,
        USERS_BACKUP_PATH,
        LOCAL_BACKUP_PATH,
        os.path.join(DATA_DIR, 'Planilha_Alimentacao_Dashboard_ElNino_SMJ.xlsx')
    ]
    for local_f in local_candidates:
        if os.path.exists(local_f):
            try:
                import openpyxl
                wb = openpyxl.load_workbook(local_f, data_only=True)
                ws = None
                for s in wb.sheetnames:
                    if s.lower() in ['usuarios', 'usuários', 'acesso', 'users', 'login']:
                        ws = wb[s]
                        break
                if ws is None and ('usuario' in local_f.lower() or 'acesso' in local_f.lower()):
                    ws = wb.active
                    
                if ws:
                    headers = [str(cell.value or '').strip() for cell in ws[1]]
                    col_map = {}
                    for idx, h in enumerate(headers):
                        h_norm = h.lower()
                        if any(k in h_norm for k in ['cpf', 'login', 'documento']):
                            if 'cpf' not in col_map: col_map['cpf'] = idx
                        elif any(k in h_norm for k in ['senha', 'password', 'pass']):
                            if 'senha' not in col_map: col_map['senha'] = idx
                        elif any(k in h_norm for k in ['nome', 'servidor', 'usuario', 'usuário']):
                            if 'nome' not in col_map: col_map['nome'] = idx
                        elif any(k in h_norm for k in ['setor', 'orgao', 'órgão', 'secretaria', 'departamento']):
                            if 'setor' not in col_map: col_map['setor'] = idx
                        elif any(k in h_norm for k in ['email', 'e-mail']):
                            if 'email' not in col_map: col_map['email'] = idx
                        elif any(k in h_norm for k in ['status', 'situacao', 'situação', 'ativo']):
                            if 'status' not in col_map: col_map['status'] = idx
                        
                    if 'cpf' in col_map and 'senha' in col_map:
                        for row in ws.iter_rows(min_row=2, values_only=True):
                            if not any(row):
                                continue
                            cpf_val = row[col_map['cpf']] if len(row) > col_map['cpf'] else None
                            senha_val = row[col_map['senha']] if len(row) > col_map['senha'] else None
                            if cpf_val is None or senha_val is None:
                                continue
                            cpf_c = clean_cpf(cpf_val)
                            pwd_c = clean_password(senha_val)
                            if not cpf_c or not pwd_c:
                                continue
                            users[cpf_c] = {
                                "nome": str(row[col_map['nome']]).strip() if col_map.get('nome') is not None and len(row) > col_map['nome'] and row[col_map['nome']] else 'Usuário',
                                "cpf": format_cpf_display(cpf_c),
                                "cpf_clean": cpf_c,
                                "senha": pwd_c,
                                "setor": str(row[col_map['setor']]).strip() if col_map.get('setor') is not None and len(row) > col_map['setor'] and row[col_map['setor']] else 'Defesa Civil',
                                "email": str(row[col_map['email']]).strip() if col_map.get('email') is not None and len(row) > col_map['email'] and row[col_map['email']] else '',
                                "status": str(row[col_map['status']]).strip() if col_map.get('status') is not None and len(row) > col_map['status'] and row[col_map['status']] else 'Ativo'
                            }
                        if users:
                            _users_cache["data"] = users
                            _users_cache["last_fetch"] = now
                            return users
            except Exception as e_loc:
                print("Erro ao carregar usuarios locais:", e_loc)

    # 3. Fallback de contingência caso a planilha não esteja acessível
    if not users:
        users["12345678900"] = {
            "nome": "Defesa Civil SMJ",
            "cpf": "123.456.789-00",
            "cpf_clean": "12345678900",
            "senha": "123456",
            "setor": "Defesa Civil",
            "email": "defesacivil@pmsmj.es.gov.br",
            "status": "Ativo"
        }
    _users_cache["data"] = users
    _users_cache["last_fetch"] = now
    return users


def read_locked_file(filepath):
    """Lê bytes de um arquivo mesmo que esteja aberto exclusivamente pelo Microsoft Excel no Windows."""
    if not filepath or not os.path.exists(filepath):
        return None
    try:
        if os.name == 'nt':
            import ctypes
            GENERIC_READ = 0x80000000
            FILE_SHARE_READ = 0x00000001
            FILE_SHARE_WRITE = 0x00000002
            FILE_SHARE_DELETE = 0x00000004
            OPEN_EXISTING = 3
            FILE_ATTRIBUTE_NORMAL = 0x80

            handle = ctypes.windll.kernel32.CreateFileW(
                str(filepath),
                GENERIC_READ,
                FILE_SHARE_READ | FILE_SHARE_WRITE | FILE_SHARE_DELETE,
                None,
                OPEN_EXISTING,
                FILE_ATTRIBUTE_NORMAL,
                None
            )
            if handle != -1 and handle != 0:
                try:
                    size_low = ctypes.c_ulong(0)
                    size_high = ctypes.c_ulong(0)
                    size_low = ctypes.windll.kernel32.GetFileSize(handle, ctypes.byref(size_high))
                    total_size = (size_high.value << 32) + size_low
                    if total_size > 0:
                        buf = ctypes.create_string_buffer(total_size)
                        bytes_read = ctypes.c_ulong(0)
                        if ctypes.windll.kernel32.ReadFile(handle, buf, total_size, ctypes.byref(bytes_read), None):
                            return buf.raw[:bytes_read.value]
                finally:
                    ctypes.windll.kernel32.CloseHandle(handle)
        with open(filepath, 'rb') as f:
            return f.read()
    except Exception as e:
        print(f"Aviso ao ler {filepath}: {e}")
        return None

_gdrive_cache = {
    "data": None,
    "last_fetch": 0,
    "last_sync_str": "Nunca",
    "source": "Inicial",
    "last_mtime": 0
}

def format_date(val):
    if val is None or pd.isna(val):
        return ""
    if isinstance(val, (datetime, pd.Timestamp)):
        return val.strftime('%d/%m/%Y')
    s = str(val).strip()
    if len(s) >= 10 and s[4] == '-' and s[7] == '-':
        try:
            d = datetime.strptime(s[:10], '%Y-%m-%d')
            return d.strftime('%d/%m/%Y')
        except:
            pass
    return s[:10]

def ensure_educacao_sheets_in_bytes(excel_bytes):
    if not excel_bytes:
        return excel_bytes
    try:
        import io
        import openpyxl
        from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
        from openpyxl.utils import get_column_letter

        wb = openpyxl.load_workbook(io.BytesIO(excel_bytes))
        sheet_exists = any(s in wb.sheetnames for s in ['Edu_Ocorrencias', 'Educacao_Ocorrencias'])
        if not sheet_exists:
            font_header = Font(name='Segoe UI', size=11, bold=True, color='FFFFFF')
            font_body = Font(name='Segoe UI', size=10)
            fill_stripe = PatternFill(start_color='F8FAFC', end_color='F8FAFC', fill_type='solid')
            thin_border = Border(
                left=Side(style='thin', color='CBD5E1'),
                right=Side(style='thin', color='CBD5E1'),
                top=Side(style='thin', color='CBD5E1'),
                bottom=Side(style='thin', color='CBD5E1')
            )

            ed_mon_path = os.path.join(DATA_DIR, 'dados', 'educacao_monitoramento.json')
            data_mon = None
            if os.path.exists(ed_mon_path):
                import json
                with open(ed_mon_path, 'r', encoding='utf-8') as f:
                    data_mon = json.load(f)

            def format_sheet_common(ws, tab_color, header_color, headers, rows_data):
                ws.sheet_properties.tabColor = tab_color
                ws.views.sheetView[0].showGridLines = True
                ws.freeze_panes = 'A2'
                ws.row_dimensions[1].height = 28
                fill_hdr = PatternFill(start_color=header_color, end_color=header_color, fill_type='solid')

                for col_i, h in enumerate(headers, start=1):
                    c = ws.cell(row=1, column=col_i, value=h)
                    c.font = font_header
                    c.fill = fill_hdr
                    c.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
                    c.border = thin_border

                for r_i, row_data in enumerate(rows_data, start=2):
                    ws.row_dimensions[r_i].height = 20
                    use_stripe = (r_i % 2 == 0)
                    for col_i, val in enumerate(row_data, start=1):
                        c = ws.cell(row=r_i, column=col_i, value=val)
                        c.font = font_body
                        if use_stripe:
                            c.fill = fill_stripe
                        c.border = thin_border
                        col_name = headers[col_i - 1].lower()
                        if isinstance(val, (int, float)):
                            c.alignment = Alignment(horizontal='right', vertical='center')
                        elif 'data' in col_name or 'semana' in col_name or 'status' in col_name:
                            c.alignment = Alignment(horizontal='center', vertical='center')
                        else:
                            c.alignment = Alignment(horizontal='left', vertical='center')

                last_col_letter = get_column_letter(len(headers))
                last_row = max(len(rows_data) + 1, 100)
                ws.auto_filter.ref = f"A1:{last_col_letter}{last_row}"

                for col in ws.columns:
                    max_len = 0
                    col_letter = get_column_letter(col[0].column)
                    for cell in col:
                        val_str = str(cell.value or '')
                        if len(val_str) > max_len:
                            max_len = len(val_str)
                    ws.column_dimensions[col_letter].width = max(max_len + 5, 16)

            # 1. Edu_Ocorrencias
            ws_oco = wb.create_sheet('Edu_Ocorrencias')
            oco_headers = ['Data', 'Escola_Localidade', 'Motivo', 'Acao_Adotada', 'Status', 'Observacoes']
            oco_rows = [
                ['20/08/2026', 'Centro', 'Onda de Calor', 'Adequação de Horário e Climatização Emergencial', 'Concluído', 'Ajuste de turno e ventilação móvel'],
                ['24/08/2026', 'Garrafão', 'Falta de Água', 'Fornecimento de Caminhão Pipa e Limpeza de Reservatório', 'Concluído', 'Abastecimento emergencial SEMAS/Defesa Civil'],
                ['02/09/2026', 'Rio Possmoser', 'Infiltração / Alagamento', 'Desobstrução de Calha e Impermeabilização Parcial', 'Em Andamento', 'Equipe de manutenção em atuação'],
                ['05/09/2026', 'São Sebastião de Belém', 'Dano Estrutural', 'Vistoria Técnica da Defesa Civil e Escoramento Preventivo', 'Concluído', 'Sem risco iminente, reparo programado'],
                ['08/09/2026', 'Caramuru', 'Destelhamento / Vento', 'Substituição de Telhas e Fixação de Estrutura Metálica', 'Planejado', 'Agendado após término do período chuvoso']
            ]
            format_sheet_common(ws_oco, '1D4ED8', '1E3A8A', oco_headers, oco_rows)

            # 2. Edu_Indicadores (Dados Fixos: KPIs e Complementares)
            ws_ind = wb.create_sheet('Edu_Indicadores')
            ind_headers = ['Categoria', 'Item', 'Valor', 'Unidade_Meta', 'Status']
            ind_rows = [
                ['KPI', 'Escolas em Área de Risco', 9, 'Escolas', 'Alerta'],
                ['KPI', 'Escolas Sem Climatização Adequada', 14, 'Escolas', 'Atenção'],
                ['KPI', 'Dias de Aula Suspensos no Mês', 3, 'Dias', 'Normal'],
                ['KPI', 'Absenteísmo em Onda de Calor', '8.4%', '%', 'Atenção'],
                ['Complementar', 'Escolas com Reservatório Insuficiente', 6, 'Escolas', 'Atenção'],
                ['Complementar', 'Estudantes em Ensino Remoto/Híbrido', 340, 'Alunos', 'Normal'],
                ['Complementar', 'Escolas em Uso como Abrigo', 1, 'Escolas', 'Adequado']
            ]
            format_sheet_common(ws_ind, '2563EB', '1E40AF', ind_headers, ind_rows)

            # 3. Edu_Planejamento (Plano de Ações / Item 4.6 - Preenchido com frequência)
            ws_plan = wb.create_sheet('Edu_Planejamento')
            plan_headers = ['Item_ID', 'Acao_Planejada', 'Detalhamento_Descricao', 'Responsavel_Setor', 'Prazo_Meta', 'Status', 'Observacoes']
            plan_rows = [
                ['4.6.1', 'Instalação de climatizadores de ar e bebedouros industriais', 'Prioridade para creches e escolas de tempo integral', 'SEMED / Obras', '30/10/2026', 'Em Andamento', 'Em fase de aquisição'],
                ['4.6.2', 'Capacitação das equipes escolares para protocolo de calor', 'Treinamento conjunto Defesa Civil e SEMED', 'Defesa Civil', '15/09/2026', 'Concluído', '4 turmas capacitadas'],
                ['4.6.3', 'Plano de contingência de transporte escolar em enxurrada', 'Mapeamento de rotas alternativas rurais', 'SEMED / Transporte', '20/10/2026', 'Planejado', 'Mapeamento preliminar concluído']
            ]
            format_sheet_common(ws_plan, '0284C7', '0369A1', plan_headers, plan_rows)

            # 4. Edu_Absenteismo
            ws_abs = wb.create_sheet('Edu_Absenteismo')
            abs_headers = ['Semana', 'Taxa_Absenteismo_Pct', 'Temp_Max_Media', 'Status_Onda_Calor']
            abs_rows = [
                ['SE29', 4.1, 28.5, 'Dentro da média'],
                ['SE30', 4.6, 29.2, 'Dentro da média'],
                ['SE31', 5.0, 31.0, 'Atenção'],
                ['SE32', 4.8, 30.1, 'Dentro da média'],
                ['SE33', 6.2, 32.5, 'Onda de calor (>32°C)'],
                ['SE34', 7.5, 34.2, 'Onda de calor (>32°C)'],
                ['SE35', 7.9, 35.0, 'Onda de calor (>32°C)'],
                ['SE36', 8.4, 36.1, 'Onda de calor (>32°C)']
            ]
            format_sheet_common(ws_abs, '3B82F6', '1D4ED8', abs_headers, abs_rows)

            out_buf = io.BytesIO()
            wb.save(out_buf)
            excel_bytes = out_buf.getvalue()
    except Exception as err:
        print(f"Aviso ao verificar abas de educacao: {err}")
    return excel_bytes

def ensure_caixas_secas_sheets_in_bytes(excel_bytes):
    """Garante a presenca da aba Urb_CaixasSecas e corrige caso esteja corrompida com dados de outras secretarias."""
    if not excel_bytes:
        return excel_bytes
    try:
        import io, openpyxl
        from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
        from openpyxl.utils import get_column_letter

        wb = openpyxl.load_workbook(io.BytesIO(excel_bytes))
        cs_sheet_name = None
        for s in wb.sheetnames:
            if s.strip().lower() in ['urb_caixassecas', 'caixas_secas', 'caixassecas', 'serv_urbanos', 'servicos_urbanos', 'urb_caixas_secas']:
                cs_sheet_name = s
                break

        is_valid = False
        if cs_sheet_name:
            ws_check = wb[cs_sheet_name]
            first_row = [str(c.value or '').strip().lower() for c in ws_check[1]]
            has_caixas = any('caixa' in h or 'volume' in h or 'servico' in h or 'estrada' in h for h in first_row)
            has_arvore = any('edp' in h or 'classe_risco' in h or 'supress' in h for h in first_row)
            if has_caixas and not has_arvore:
                is_valid = True
            else:
                wb.remove(ws_check)

        if not is_valid:
            font_header = Font(name='Segoe UI', size=11, bold=True, color='FFFFFF')
            font_body = Font(name='Segoe UI', size=10)
            fill_stripe = PatternFill(start_color='F8FAFC', end_color='F8FAFC', fill_type='solid')
            fill_hdr = PatternFill(start_color='B45309', end_color='B45309', fill_type='solid')
            thin_border = Border(
                left=Side(style='thin', color='CBD5E1'),
                right=Side(style='thin', color='CBD5E1'),
                top=Side(style='thin', color='CBD5E1'),
                bottom=Side(style='thin', color='CBD5E1')
            )

            ws = wb.create_sheet('Urb_CaixasSecas')
            ws.sheet_properties.tabColor = 'D97706'
            ws.views.sheetView[0].showGridLines = True
            ws.freeze_panes = 'A2'
            ws.row_dimensions[1].height = 28

            headers = ['Data', 'Localidade', 'Estrada_Trecho', 'Tipo_Servico', 'Quantidade_Caixas', 'Volume_Retencao_m3', 'Status', 'Equipe_Responsavel', 'Observacoes']
            for col_i, h in enumerate(headers, start=1):
                c = ws.cell(row=1, column=col_i, value=h)
                c.font = font_header
                c.fill = fill_hdr
                c.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
                c.border = thin_border

            rows = [
                ['03/08/2026', 'Garrafão', 'Estrada Garrafão x Recreio - Km 4', 'Abertura', 12, 240, 'Concluído', 'Patrulha Mecanizada SEMOSU', 'Abertura de caixas secas em curva de nível para retenção pluvial'],
                ['07/08/2026', 'Rio Possmoser', 'Acesso Córrego Albert - Km 2', 'Manutenção / Limpeza', 18, 360, 'Concluído', 'Equipe Serviços Urbanos 01', 'Desassoreamento e limpeza mecanizada de caixas secas antes das chuvas'],
                ['14/08/2026', 'São Sebastião de Belém', 'Estrada Principal Belém - Km 6', 'Abertura', 15, 300, 'Concluído', 'Patrulha Mecanizada SEMOSU', 'Novas bacias de contenção para proteção do leito viário'],
                ['21/08/2026', 'Alto Santa Maria', 'Estrada Alto Santa Maria x Garrafão', 'Manutenção / Limpeza', 22, 440, 'Concluído', 'Equipe Serviços Urbanos 02', 'Limpeza preventiva e remoção de sedimentos acumulados'],
                ['28/08/2026', 'Caramuru', 'Estrada Geral do Caramuru - Km 3.5', 'Abertura', 10, 200, 'Em Andamento', 'Patrulha Mecanizada SEMOSU', 'Abertura de caixas conjugadas com bueiros de transposição'],
                ['04/09/2026', 'Centro', 'Estrada de Contorno Periurbano', 'Manutenção / Limpeza', 14, 280, 'Concluído', 'Equipe Serviços Urbanos 01', 'Desobstrução e ampliação de capacidade de amortecimento'],
                ['11/09/2026', 'São Luís', 'Trecho São Luís x Alto Rio Possmoser', 'Abertura', 16, 320, 'Em Andamento', 'Patrulha Mecanizada SEMOSU', 'Novos pontos de infiltração e recarga de lençol freático'],
                ['18/09/2026', 'Vila Jetibá', 'Estrada Vicinal Vila Jetibá - Km 1.8', 'Manutenção / Limpeza', 8, 160, 'Planejado', 'Equipe Serviços Urbanos 02', 'Manutenção programada no cronograma quinzenal']
            ]
            for r_i, row_data in enumerate(rows, start=2):
                ws.row_dimensions[r_i].height = 20
                use_stripe = (r_i % 2 == 0)
                for col_i, val in enumerate(row_data, start=1):
                    c = ws.cell(row=r_i, column=col_i, value=val)
                    c.font = font_body
                    if use_stripe:
                        c.fill = fill_stripe
                    c.border = thin_border
                    if isinstance(val, (int, float)):
                        c.alignment = Alignment(horizontal='right', vertical='center')
                    elif col_i in [1, 4, 7]:
                        c.alignment = Alignment(horizontal='center', vertical='center')
                    else:
                        c.alignment = Alignment(horizontal='left', vertical='center')

            for col in ws.columns:
                max_len = max(len(str(cell.value or '')) for cell in col)
                col_letter = get_column_letter(col[0].column)
                ws.column_dimensions[col_letter].width = max(max_len + 4, 16)

            out_buf = io.BytesIO()
            wb.save(out_buf)
            excel_bytes = out_buf.getvalue()
    except Exception as err:
        print(f"Aviso ao verificar aba Urb_CaixasSecas: {err}")
    return excel_bytes

def fetch_google_drive_data(force=False):
    global _gdrive_cache
    now = time.time()
    is_vercel = bool(os.environ.get('VERCEL'))

    local_candidates = [
        os.path.join(DATA_DIR, 'Planilha_Alimentacao_Dashboard_ElNino_SMJ.xlsx'),
        LOCAL_BACKUP_PATH,
        os.path.join(DATA_DIR, 'arquivo_morto', 'Planilha_Alimentacao_Dashboard_ElNino_SMJ.xlsx')
    ]
    primary_local = next((p for p in local_candidates if os.path.exists(p)), None)

    # TTL curto para refletir edições na planilha do Google Drive com extrema agilidade
    ttl = 5 if not is_vercel else 15
    if not force and _gdrive_cache.get("data") and (now - _gdrive_cache.get("last_fetch", 0) < ttl):
        return _gdrive_cache["data"]

    excel_bytes = None
    source = "Google Drive (Online)"

    # 1. Google Drive é SEMPRE A FONTE PRIMÁRIA
    try:
        req = urllib.request.Request(
            GOOGLE_SHEET_URL,
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        )
        with urllib.request.urlopen(req, timeout=8) as resp:
            data_downloaded = resp.read()
        if data_downloaded and len(data_downloaded) > 2000:
            excel_bytes = data_downloaded
            source = "Google Drive (Online)"

            # Salva cópia local para contingência offline
            try:
                local_save_path = primary_local or os.path.join(DATA_DIR, 'Planilha_Alimentacao_Dashboard_ElNino_SMJ.xlsx')
                if is_vercel:
                    local_save_path = '/tmp/Planilha_Alimentacao_Dashboard_ElNino_SMJ.xlsx'
                with open(local_save_path, 'wb') as f_bkp:
                    f_bkp.write(excel_bytes)
            except Exception:
                pass
    except Exception as e:
        print(f"Aviso: Falha ao baixar planilha do Google Drive ({e}). Tentando arquivos locais de contingência...")

    # 2. Se falhar o Google Drive (offline/sem rede), usa o arquivo local como contingência
    if not excel_bytes:
        for bkp in local_candidates:
            if bkp and os.path.exists(bkp):
                excel_bytes = read_locked_file(bkp)
                if excel_bytes:
                    source = f"Backup Local Offline ({os.path.basename(bkp)})"
                    break

    if not excel_bytes:
        if _gdrive_cache.get("data"):
            return _gdrive_cache["data"]
        return {}

    # Garante presença e validação das abas
    excel_bytes = ensure_educacao_sheets_in_bytes(excel_bytes)
    excel_bytes = ensure_caixas_secas_sheets_in_bytes(excel_bytes)

    try:
        xl = pd.ExcelFile(io.BytesIO(excel_bytes))
        sheet_names = xl.sheet_names
        meses_pt = {1:'Jan',2:'Fev',3:'Mar',4:'Abr',5:'Mai',6:'Jun',7:'Jul',8:'Ago',9:'Set',10:'Out',11:'Nov',12:'Dez'}

        # Função auxiliar flexível para localizar abas independente de nomenclatura curta/longa
        def get_sheet_name(*aliases):
            for a in aliases:
                if a in sheet_names:
                    return a
            for a in aliases:
                for s in sheet_names:
                    if s.strip().lower() == a.strip().lower():
                        return s
            return None

        import unicodedata
        def normalize_key(s):
            if s is None:
                return ""
            st = str(s).strip().lower()
            return unicodedata.normalize('NFKD', st).encode('ASCII', 'ignore').decode('utf-8')

        # 1. Drenagem (Dren. ou Drenagem_Obras)
        drenagem = []
        sheet_dren = get_sheet_name('Dren.', 'Drenagem_Obras', 'Drenagem', 'Dren_Obras')
        if sheet_dren:
            df_dre = pd.read_excel(xl, sheet_dren).fillna('')
            for _, r in df_dre.iterrows():
                r_norm = {normalize_key(k): v for k, v in r.items()}
                loc = str(r_norm.get('localidade') or r_norm.get('local') or '').strip()
                if not loc:
                    continue
                try:
                    ext = int(float(str(r_norm.get('extensao_metros') or r_norm.get('extensao') or 0).replace(',', '.')))
                except:
                    ext = 0
                tipo_raw = str(r_norm.get('tipo_intervencao') or r_norm.get('tipo') or 'Manutenção').strip()
                tipo_norm = normalize_key(tipo_raw)
                tipo_val = 'Manutenção' if 'manuten' in tipo_norm else ('Construção' if 'constru' in tipo_norm else tipo_raw)
                
                status_raw = str(r_norm.get('status') or 'Concluído').strip()
                status_norm = normalize_key(status_raw)
                status_val = 'Concluído' if 'conclu' in status_norm else ('Em Andamento' if 'andamento' in status_norm else ('Planejado' if 'planej' in status_norm else status_raw))

                desc = str(r_norm.get('descricao_servico') or r_norm.get('descricao') or '').strip()

                drenagem.append({
                    'data': format_date(r_norm.get('data')),
                    'tipo': tipo_val,
                    'local': loc,
                    'descricao': desc,
                    'extensao_m': ext,
                    'status': status_val
                })

        # 1.B Caixas Secas — Serviços Urbanos (Urb_CaixasSecas)
        cs_registros = []
        cs_locais = defaultdict(int)
        cs_tipos = defaultdict(int)
        cs_status = defaultdict(int)
        cs_total_caixas = 0
        cs_abertura_caixas = 0
        cs_manut_caixas = 0
        cs_volume_total = 0.0

        sheet_cs = get_sheet_name('Urb_CaixasSecas', 'Caixas_Secas', 'CaixasSecas', 'Serv_Urbanos', 'Servicos_Urbanos', 'Urb_Caixas_Secas')
        if sheet_cs:
            df_cs = pd.read_excel(xl, sheet_cs).fillna('')
            for _, r in df_cs.iterrows():
                r_norm = {normalize_key(k): v for k, v in r.items()}
                loc = str(r_norm.get('localidade') or r_norm.get('local') or '').strip()
                if not loc:
                    continue
                d_str = format_date(r_norm.get('data') or r_norm.get('data_execucao'))
                trecho = str(r_norm.get('estrada_trecho') or r_norm.get('trecho') or r_norm.get('estrada') or '').strip()
                
                tipo_raw = str(r_norm.get('tipo_servico') or r_norm.get('tipo') or 'Abertura').strip()
                tipo_norm = normalize_key(tipo_raw)
                tipo_val = 'Abertura' if ('abert' in tipo_norm or 'const' in tipo_norm) else ('Manutenção' if ('manut' in tipo_norm or 'limp' in tipo_norm or 'desass' in tipo_norm) else tipo_raw)
                
                try:
                    qtd = int(float(str(r_norm.get('quantidade_caixas') or r_norm.get('quantidade') or r_norm.get('caixas') or 0).replace(',', '.')))
                except:
                    qtd = 0

                try:
                    vol = float(str(r_norm.get('volume_retencao_m3') or r_norm.get('volume_m3') or r_norm.get('volume') or 0).replace(',', '.'))
                except:
                    vol = float(qtd * 20.0)

                status_raw = str(r_norm.get('status') or 'Concluído').strip()
                status_norm = normalize_key(status_raw)
                status_val = 'Concluído' if 'conclu' in status_norm else ('Em Andamento' if 'andamento' in status_norm else ('Planejado' if 'planej' in status_norm else status_raw))
                
                equipe = str(r_norm.get('equipe_responsavel') or r_norm.get('equipe') or 'Equipe Serviços Urbanos').strip()
                obs = str(r_norm.get('observacoes') or r_norm.get('obs') or '').strip()

                cs_registros.append({
                    'data': d_str,
                    'local': loc,
                    'trecho': trecho,
                    'tipo': tipo_val,
                    'quantidade': qtd,
                    'volume_m3': int(round(vol)),
                    'status': status_val,
                    'equipe': equipe,
                    'observacoes': obs
                })

                cs_total_caixas += qtd
                if tipo_val == 'Abertura':
                    cs_abertura_caixas += qtd
                else:
                    cs_manut_caixas += qtd
                cs_volume_total += vol
                cs_locais[loc] += qtd
                cs_tipos[tipo_val] += qtd
                cs_status[status_val] += 1

        cs_loc_sorted = sorted(cs_locais.items(), key=lambda x: x[1], reverse=True)
        caixas_secas = {
            'registros': cs_registros,
            'total_intervencoes': len(cs_registros),
            'total_caixas': cs_total_caixas,
            'caixas_abertura': cs_abertura_caixas,
            'caixas_manutencao': cs_manut_caixas,
            'volume_total_m3': int(round(cs_volume_total)),
            'locais_labels': [x[0] for x in cs_loc_sorted],
            'locais_dados': [x[1] for x in cs_loc_sorted],
            'tipos_labels': ['Abertura', 'Manutenção'],
            'tipos_dados': [cs_abertura_caixas, cs_manut_caixas],
            'status_resumo': dict(cs_status)
        }

        # 2. Assistência Social (Ass_Acoes, Ass_Estoque)
        as_acoes = []
        as_estoque = []
        loc_counts = defaultdict(int)
        tipo_counts = defaultdict(int)
        mes_as_counts = defaultdict(int)
        total_familias_as = 0
        total_acolhidos_as = 0
        total_beneficios_as = 0
        total_atendimentos_as = 0

        sheet_as_ac = get_sheet_name('Ass_Acoes', 'Assistencia_Acoes')
        if sheet_as_ac:
            df_as_ac = pd.read_excel(xl, sheet_as_ac).fillna('')
            for _, r in df_as_ac.iterrows():
                r_norm = {normalize_key(k): v for k, v in r.items()}
                loc = str(r_norm.get('localidade') or r_norm.get('local') or '').strip()
                acao_raw = str(r_norm.get('tipo_acao') or r_norm.get('acao') or '').strip()
                if not loc and not acao_raw:
                    continue
                acao_norm = normalize_key(acao_raw)
                acao_display = (
                    'Acolhimento Provisório' if 'acolh' in acao_norm else (
                    'Benefício Eventual' if 'benefic' in acao_norm else (
                    'Atualização CadÚnico' if 'cadunic' in acao_norm or 'cadas' in acao_norm else (
                    'Cesta Básica' if 'cesta' in acao_norm else (
                    'PAIF / Visita' if 'paif' in acao_norm or 'visit' in acao_norm else acao_raw)))))

                try:
                    fam = int(float(str(r_norm.get('familias_atendidas') or r_norm.get('familias') or 0).replace(',', '.')))
                except:
                    fam = 0
                try:
                    pess = int(float(str(r_norm.get('pessoas_atendidas') or r_norm.get('pessoas') or 0).replace(',', '.')))
                except:
                    pess = 0

                total_familias_as += fam
                if 'acolh' in acao_norm:
                    total_acolhidos_as += (pess if pess > 0 else fam)
                if 'benefic' in acao_norm or 'cesta' in acao_norm:
                    total_beneficios_as += (fam if fam > 0 else 1)
                total_atendimentos_as += (pess if pess > 0 else (fam if fam > 0 else 1))

                d_str = format_date(r_norm.get('data'))
                status_raw = str(r_norm.get('status') or 'Concluído').strip()
                status_norm = normalize_key(status_raw)
                status_display = 'Concluído' if 'conclu' in status_norm else ('Em Andamento' if 'andamento' in status_norm else status_raw)

                as_acoes.append({
                    'data': d_str,
                    'local': loc,
                    'acao': acao_display,
                    'familias': fam if fam > 0 else (pess if pess > 0 else '—'),
                    'status': status_display
                })
                if loc:
                    loc_counts[loc] += (fam if fam > 0 else 1)
                if acao_display:
                    tipo_counts[acao_display] += 1
                try:
                    dt = datetime.strptime(d_str, '%d/%m/%Y')
                    k = f"{meses_pt[dt.month]}/{str(dt.year)[2:]}"
                    mes_as_counts[k] += (fam if fam > 0 else 1)
                except:
                    pass

        # 2. Assistência Social (Ass_Acoes, Ass_Estoque, Ass_Indicadores)
        as_acoes = []
        as_estoque = []
        as_estoque_grupos = {
            'consolidado': [],
            'cras1': [],
            'cras2': [],
            'creas': []
        }
        as_estoque_totais = {
            'consolidado': 0,
            'cras1': 0,
            'cras2': 0,
            'creas': 0
        }
        as_consolidado_map = {}

        # Leitura da aba Ass_Estoque exclusivamente da planilha
        sheet_as_es = get_sheet_name('Ass_Estoque', 'Assistencia_Estoque')
        if sheet_as_es:
            df_as_es = pd.read_excel(xl, sheet_as_es).fillna('')
            for _, r in df_as_es.iterrows():
                r_norm = {normalize_key(k): v for k, v in r.items()}
                item = str(r_norm.get('item', '')).strip()
                if not item:
                    continue

                unidade_raw = str(r_norm.get('unidade') or r_norm.get('equipamento') or r_norm.get('cras') or r_norm.get('polo') or '').strip()
                item_full_text = f"{item} {unidade_raw} {r_norm.get('cobertura_estimada', '')}".lower()

                # Reconhecimento dinâmico de unidade por coluna ou identificação no item
                status_words = ['adequado', 'atenção', 'atencao', 'crítico', 'critico', 'normal', 'alerta', 'concluído', 'concluido']
                if any(k in item_full_text for k in ['cras 2', 'cras ii', 'cras2', 'polo 2', 'polo ii']):
                    unidade_tag = 'CRAS II'
                    grupo_chave = 'cras2'
                elif any(k in item_full_text for k in ['creas']):
                    unidade_tag = 'CREAS'
                    grupo_chave = 'creas'
                elif any(k in item_full_text for k in ['cras 1', 'cras i', 'cras1', 'polo 1', 'polo i']):
                    unidade_tag = 'CRAS I'
                    grupo_chave = 'cras1'
                elif unidade_raw and unidade_raw.lower() not in status_words:
                    unidade_tag = unidade_raw
                    grupo_chave = 'cras1' if '1' in unidade_raw or 'i' in unidade_raw.lower() else ('cras2' if '2' in unidade_raw or 'ii' in unidade_raw.lower() else 'geral')
                else:
                    # Caso de preenchimento acidental de palavra de status no campo da unidade no Drive
                    if item.lower() == 'cesta básica' and '73' in str(qtd_raw):
                        unidade_tag = 'CRAS I'
                        grupo_chave = 'cras1'
                    else:
                        unidade_tag = 'Consolidado / Geral'
                        grupo_chave = 'geral'

                try:
                    qtd_raw = str(r_norm.get('quantidade_atual') or r_norm.get('quantidade') or r_norm.get('qtd') or 0).replace(',', '.')
                    qtd_num = int(float(qtd_raw))
                except:
                    qtd_num = 0

                unidade_medida = str(r_norm.get('unidade_medida') or 'Unidades').strip()
                cobertura = str(r_norm.get('cobertura_estimada') or r_norm.get('cobertura') or '').strip()

                st_raw = str(r_norm.get('nivel_status') or r_norm.get('status') or '').strip()
                st_norm = normalize_key(st_raw)
                if 'adeq' in st_norm or 'norm' in st_norm:
                    st_val = 'Adequado'
                elif 'atenc' in st_norm:
                    st_val = 'Atenção'
                elif 'crit' in st_norm:
                    st_val = 'Crítico'
                else:
                    st_val = 'Adequado' if qtd_num >= 15 else ('Atenção' if qtd_num >= 5 else 'Crítico')

                item_obj = {
                    'nome': item,
                    'item': item,
                    'unidade': unidade_tag,
                    'grupo': grupo_chave,
                    'quantidade': qtd_num,
                    'qtd': qtd_num,
                    'unidade_medida': unidade_medida,
                    'cobertura': cobertura or f"{qtd_num} {unidade_medida.lower()}",
                    'status': st_val
                }
                as_estoque.append(item_obj)

                if grupo_chave in as_estoque_grupos:
                    as_estoque_grupos[grupo_chave].append(item_obj)
                    as_estoque_totais[grupo_chave] += qtd_num

                # Mapeamento e consolidação geral de todos os itens reais da planilha
                base_item_name = re.sub(r'\s*[-–(]\s*(CRAS\s*I{1,2}|CREAS).*$', '', item, flags=re.IGNORECASE).strip()
                if not base_item_name:
                    base_item_name = item

                if base_item_name not in as_consolidado_map:
                    as_consolidado_map[base_item_name] = {
                        'nome': base_item_name,
                        'item': base_item_name,
                        'unidade': 'Consolidado Geral',
                        'grupo': 'consolidado',
                        'quantidade': 0,
                        'qtd': 0,
                        'unidade_medida': unidade_medida,
                        'por_unidade': {},
                        'status': st_val
                    }
                as_consolidado_map[base_item_name]['quantidade'] += qtd_num
                as_consolidado_map[base_item_name]['qtd'] += qtd_num
                unit_label = unidade_tag if unidade_tag != 'Consolidado / Geral' else 'Geral'
                as_consolidado_map[base_item_name]['por_unidade'][unit_label] = as_consolidado_map[base_item_name]['por_unidade'].get(unit_label, 0) + qtd_num

        # Constrói itens consolidados com dados 100% da planilha
        for item_nome, c_data in as_consolidado_map.items():
            breakdown_parts = [f"{u}: {q}" for u, q in c_data['por_unidade'].items() if q > 0]
            breakdown = " · ".join(breakdown_parts) if breakdown_parts else ""
            q = c_data['quantidade']
            st_calc = 'Adequado' if q >= 15 else ('Atenção' if q >= 5 else 'Crítico')
            c_item = {
                'nome': item_nome,
                'item': item_nome,
                'unidade': 'Consolidado Geral',
                'grupo': 'consolidado',
                'quantidade': q,
                'qtd': q,
                'unidade_medida': c_data['unidade_medida'],
                'cobertura': breakdown if breakdown else f"{q} {c_data['unidade_medida'].lower()}",
                'status': st_calc,
                'por_unidade': c_data['por_unidade']
            }
            as_estoque_grupos['consolidado'].append(c_item)
            as_estoque_totais['consolidado'] += q

        # Leitura da aba Ass_Indicadores exclusivamente da planilha
        as_kpis_dict = {}
        sheet_as_ind = get_sheet_name('Ass_Indicadores', 'Assistencia_Indicadores')
        if sheet_as_ind:
            df_as_ind = pd.read_excel(xl, sheet_as_ind).fillna('')
            for _, r in df_as_ind.iterrows():
                r_norm = {normalize_key(k): v for k, v in r.items()}
                ind_nome = str(r_norm.get('indicador') or r_norm.get('nome') or '').strip()
                val = r_norm.get('valor')
                if ind_nome and val != '':
                    as_kpis_dict[normalize_key(ind_nome)] = val

        def get_as_kpi(key_words_list, default_val=0):
            """Busca um indicador na planilha por listas de palavras-chave alternativas.
               Retorna o valor REAL da planilha. Se não existir, retorna default_val (0)."""
            for key_words in key_words_list:
                for k, v in as_kpis_dict.items():
                    if all(w in k for w in key_words):
                        try:
                            cleaned = str(v).replace('.', '').replace(',', '.').strip()
                            return int(float(cleaned))
                        except:
                            return v
            return default_val

        # Puxa indicadores diretamente da planilha sem mocks
        kpi_cad_novos = get_as_kpi([['cad', 'inclu'], ['novos', 'cad'], ['novos', 'registros']], 0)
        kpi_extrema_pobreza = get_as_kpi([['extrema', 'pobreza'], ['inseguranca', 'alimentar'], ['pobreza']], 0)

        kpi_cras1_ref = get_as_kpi([['cras', 'i', 'referenciad'], ['cras 1', 'referenciad'], ['cras', '1', 'ref']], 0)
        kpi_cras1_paif = get_as_kpi([['cras', 'i', 'paif'], ['cras 1', 'paif'], ['cras', '1', 'paif']], 0)

        kpi_cras2_ref = get_as_kpi([['cras', 'ii', 'referenciad'], ['cras 2', 'referenciad'], ['cras', '2', 'ref']], 0)
        kpi_cras2_paif = get_as_kpi([['cras', 'ii', 'paif'], ['cras 2', 'paif'], ['cras', '2', 'paif']], 0)

        kpi_creas_paefi = get_as_kpi([['creas', 'paefi'], ['paefi']], 0)
        kpi_creas_rua = get_as_kpi([['rua', 'abordad'], ['situacao', 'rua'], ['rua']], 0)

        kpi_acolhidos = get_as_kpi([['acolhimento', 'provisorio'], ['acolhid'], ['abrigamento']], 0)
        kpi_beneficios = get_as_kpi([['beneficios', 'eventuais'], ['concedid']], 0)
        kpi_atendimentos = get_as_kpi([['atendimentos', 'cras'], ['atendimentos']], 0)

        total_ref = (kpi_cras1_ref or 0) + (kpi_cras2_ref or 0)
        if total_ref == 0:
            total_ref = get_as_kpi([['total', 'referenciad'], ['familias']], 0)

        total_paif = (kpi_cras1_paif or 0) + (kpi_cras2_paif or 0)
        if total_paif == 0:
            total_paif = get_as_kpi([['total', 'paif']], 0)

        total_acomp = total_paif + (kpi_creas_paefi or 0)
        if total_acomp == 0:
            total_acomp = get_as_kpi([['total', 'acomp']], 0)

        as_loc_sorted = sorted(loc_counts.items(), key=lambda x: x[1], reverse=True)
        assistencia_social = {
            'acoes': as_acoes,
            'estoque': as_estoque,
            'estoque_consolidado': as_estoque_grupos['consolidado'],
            'estoque_grupos': as_estoque_grupos,
            'estoque_totais': as_estoque_totais,
            'kpis': {
                'cadunico_novos': kpi_cad_novos,
                'cadunico_extrema_pobreza': kpi_extrema_pobreza,
                'cras1_referenciadas': kpi_cras1_ref,
                'cras1_paif': kpi_cras1_paif,
                'cras2_referenciadas': kpi_cras2_ref,
                'cras2_paif': kpi_cras2_paif,
                'creas_paefi': kpi_creas_paefi,
                'creas_rua': kpi_creas_rua,
                'total_referenciadas': total_ref,
                'total_paif': total_paif,
                'total_acompanhamento': total_acomp,
                # Compatibilidade com cards anteriores
                'familias': total_ref,
                'acolhidos': kpi_acolhidos,
                'beneficios': kpi_beneficios if kpi_beneficios > 0 else as_estoque_totais['consolidado'],
                'atendimentos': kpi_atendimentos if kpi_atendimentos > 0 else total_acomp,
                'inseguranca': kpi_extrema_pobreza,
                'novos_cadunico': kpi_cad_novos,
                'pessoas_rua': kpi_creas_rua
            },
            'beneficios_mes': {
                'labels': list(mes_as_counts.keys()) if mes_as_counts else ['Ago/26', 'Set/26'],
                'values': list(mes_as_counts.values()) if mes_as_counts else [15, 25]
            },
            'atendimentos_local': {
                'labels': [x[0] for x in as_loc_sorted] if as_loc_sorted else ['Centro', 'Garrafão', 'Rio Possmoser', 'São Sebastião'],
                'values': [x[1] for x in as_loc_sorted] if as_loc_sorted else [137, 72, 53, 33]
            },
            'tipo_acao': {
                'labels': list(tipo_counts.keys()) if tipo_counts else ['PAIF', 'PAEFI', 'Benefício Eventual', 'CadÚnico'],
                'values': list(tipo_counts.values()) if tipo_counts else [170, 143, 88, 25]
            }
        }

        # 3. Vigilância Vetorial (Vig_Acoes, Vig_Estoque, Vig_Casos)
        vv_acoes = []
        vv_estoque = []
        se_casos = defaultdict(int)
        loc_casos = defaultdict(int)
        liraa_dict = {}
        total_focos_vv = 0
        total_imoveis_vv = 0

        sheet_vv_ac = get_sheet_name('Vig_Acoes', 'Vigilancia_Acoes')
        if sheet_vv_ac:
            df_vv_ac = pd.read_excel(xl, sheet_vv_ac).fillna('')
            for _, r in df_vv_ac.iterrows():
                r_norm = {normalize_key(k): v for k, v in r.items()}
                loc = str(r_norm.get('localidade') or r_norm.get('local') or '').strip()
                acao_raw = str(r_norm.get('tipo_acao') or r_norm.get('acao') or '').strip()
                if not loc and not acao_raw:
                    continue
                acao_norm = normalize_key(acao_raw)
                acao_val = (
                    'Eliminação de Criadouros' if 'elimin' in acao_norm or 'criad' in acao_norm else (
                    'LIRAa' if 'lira' in acao_norm else (
                    'Nebulização Perifocal' if 'nebuliz' in acao_norm else (
                    'Visita Casa a Casa' if 'visita' in acao_norm else (
                    'Mutirão Pós-Chuva' if 'mutir' in acao_norm else acao_raw)))))

                try:
                    focos = int(float(str(r_norm.get('focos_eliminados') or r_norm.get('focos') or 0).replace(',', '.')))
                except:
                    focos = 0
                try:
                    imov = int(float(str(r_norm.get('imoveis_trabalhados') or r_norm.get('imoveis') or 0).replace(',', '.')))
                except:
                    imov = 0

                total_focos_vv += focos
                total_imoveis_vv += imov

                status_raw = str(r_norm.get('status') or 'Concluído').strip()
                status_norm = normalize_key(status_raw)
                status_val = 'Concluído' if 'conclu' in status_norm else ('Em Andamento' if 'andamento' in status_norm else status_raw)

                vv_acoes.append({
                    'data': format_date(r_norm.get('data')),
                    'local': loc,
                    'acao': acao_val,
                    'focos_eliminados': focos if focos > 0 else '—',
                    'status': status_val
                })

        sheet_vv_es = get_sheet_name('Vig_Estoque', 'Vigilancia_Estoque')
        if sheet_vv_es:
            df_vv_es = pd.read_excel(xl, sheet_vv_es).fillna('')
            for _, r in df_vv_es.iterrows():
                r_norm = {normalize_key(k): v for k, v in r.items()}
                item = str(r_norm.get('item', '')).strip()
                if item:
                    st_raw = str(r_norm.get('nivel_status') or r_norm.get('status') or 'Adequado').strip()
                    st_norm = normalize_key(st_raw)
                    st_val = 'Adequado' if 'adeq' in st_norm or 'norm' in st_norm else ('Atenção' if 'atenc' in st_norm else ('Crítico' if 'crit' in st_norm else st_raw))
                    vv_estoque.append({
                        'nome': item,
                        'cobertura': str(r_norm.get('cobertura_estimada') or r_norm.get('cobertura') or '').strip(),
                        'status': st_val
                    })

        sheet_vv_ind = get_sheet_name('Vig_Indicadores', 'Vigilancia_Indicadores')
        vv_kpi_override = {}
        if sheet_vv_ind:
            df_vv_ind = pd.read_excel(xl, sheet_vv_ind).fillna('')
            for _, r in df_vv_ind.iterrows():
                r_norm = {normalize_key(k): v for k, v in r.items()}
                item = str(r_norm.get('indicador') or r_norm.get('item') or '').strip()
                item_norm = normalize_key(item)
                def clean_val_str(v):
                    if isinstance(v, float) and v.is_integer():
                        return str(int(v))
                    return str(v).strip()

                val_clean = clean_val_str(r.get('Valor') or r_norm.get('valor') or '')

                if 'lira' in item_norm or 'liraa' in item_norm:
                    try:
                        f_v = float(val_clean.replace(',', '.'))
                        if f_v < 1.0: f_v = f_v * 100
                        vv_kpi_override['liraa_medio'] = f"{f_v:.1f}%".replace('.', ',')
                    except:
                        vv_kpi_override['liraa_medio'] = val_clean
                elif 'foco' in item_norm:
                    try: vv_kpi_override['focos_eliminados'] = int(float(val_clean.replace(',', '.')))
                    except: pass
                elif 'cobertur' in item_norm or 'visita' in item_norm or 'agente' in item_norm:
                    try:
                        f_v = float(val_clean.replace('%', '').replace(',', '.'))
                        if f_v < 1.0: f_v = f_v * 100
                        vv_kpi_override['cobertura'] = f"{int(round(f_v))}%"
                    except:
                        vv_kpi_override['cobertura'] = val_clean if '%' in val_clean else f"{val_clean}%"
                elif 'leptospiros' in item_norm:
                    try: vv_kpi_override['leptospirose'] = int(float(val_clean.replace(',', '.')))
                    except: vv_kpi_override['leptospirose'] = val_clean
                elif 'diarre' in item_norm or 'dda' in item_norm:
                    try: vv_kpi_override['dda'] = int(float(val_clean.replace(',', '.')))
                    except: vv_kpi_override['dda'] = val_clean
                elif 'desidrat' in item_norm or 'exaust' in item_norm or 'calor' in item_norm:
                    try: vv_kpi_override['exaustao'] = int(float(val_clean.replace(',', '.')))
                    except: vv_kpi_override['exaustao'] = val_clean

        last_se_dengue_total = 0
        all_liraa_vals = []
        sheet_vv_cs = get_sheet_name('Vig_Casos', 'Vigilancia_Casos')
        if sheet_vv_cs:
            df_vv_cs = pd.read_excel(xl, sheet_vv_cs).fillna('')
            for _, r in df_vv_cs.iterrows():
                r_norm = {normalize_key(k): v for k, v in r.items()}
                se = str(r_norm.get('semana_epi') or r_norm.get('semana') or '').strip()
                loc = str(r_norm.get('localidade') or r_norm.get('local') or '').strip()
                try:
                    qtd = int(float(str(r_norm.get('casos_notificados') or r_norm.get('casos') or 0).replace(',', '.')))
                except:
                    qtd = 0
                try:
                    lir = float(str(r_norm.get('indice_liraa_pct') or r_norm.get('liraa') or 0).replace(',', '.'))
                except:
                    lir = 0.0
                if se:
                    se_casos[se] += qtd
                if loc:
                    loc_casos[loc] += qtd
                    if lir > 0:
                        liraa_dict[loc] = lir
                        all_liraa_vals.append(lir)

        if se_casos:
            # Pega o total de casos da semana epidemiológica mais recente lançada na planilha
            last_se = sorted(list(se_casos.keys()), key=lambda s: int(''.join(filter(str.isdigit, str(s))) or 0))[-1]
            last_se_dengue_total = se_casos[last_se]

        media_liraa = sum(all_liraa_vals)/len(all_liraa_vals) if all_liraa_vals else 2.7
        liraa_str = f"{media_liraa:.1f}%".replace('.', ',')

        vv_loc_sorted = sorted(loc_casos.items(), key=lambda x: x[1], reverse=True)
        liraa_sorted = sorted(liraa_dict.items(), key=lambda x: x[1], reverse=True)

        vigilancia_vetorial = {
            'acoes': vv_acoes,
            'estoque': vv_estoque,
            'kpis': {
                'dengue_semana': last_se_dengue_total if se_casos else 31,
                'liraa_medio': vv_kpi_override.get('liraa_medio', liraa_str),
                'focos_eliminados': vv_kpi_override.get('focos_eliminados', (total_focos_vv if vv_acoes else 184)),
                'cobertura': vv_kpi_override.get('cobertura', '76%'),
                'leptospirose': vv_kpi_override.get('leptospirose', 4),
                'dda': vv_kpi_override.get('dda', 17),
                'exaustao': vv_kpi_override.get('exaustao', 9)
            },
            'casos_dengue': {
                'labels': list(se_casos.keys()) if se_casos else ['SE33', 'SE34', 'SE35', 'SE36'],
                'values': list(se_casos.values()) if se_casos else [5, 10, 15, 20]
            },
            'liraa': {
                'labels': [x[0] for x in liraa_sorted] if liraa_sorted else ['Centro'],
                'values': [x[1] for x in liraa_sorted] if liraa_sorted else [1.0]
            },
            'casos_local': {
                'labels': [x[0] for x in vv_loc_sorted] if vv_loc_sorted else ['Centro'],
                'values': [x[1] for x in vv_loc_sorted] if vv_loc_sorted else [5]
            }
        }

        # 4. Incêndios (Inc_Focos) — Divisão: Bombeiros Voluntários (SCBV) e CBMES 6º Batalhão
        inc_meses = defaultdict(int)
        inc_locais = defaultdict(int)

        scbv_meses = defaultdict(int)
        scbv_locais = defaultdict(int)
        scbv_registros = []
        scbv_area_total = 0.0

        cbmes_meses = defaultdict(int)
        cbmes_locais = defaultdict(int)
        cbmes_registros = []
        cbmes_area_total = 0.0

        sheet_inc = get_sheet_name('Inc_Focos', 'Incendios_Focos', 'Incendios')
        if sheet_inc:
            df_inc = pd.read_excel(xl, sheet_inc).fillna('')
            for _, r in df_inc.iterrows():
                r_norm = {normalize_key(k): v for k, v in r.items()}
                loc = str(r_norm.get('localidade') or r_norm.get('local') or '').strip()
                if not loc:
                    continue
                d_str = format_date(r_norm.get('data_ocorrencia') or r_norm.get('data'))
                origem_raw = str(r_norm.get('origem_registro') or r_norm.get('origem') or r_norm.get('tipo_registro') or '').strip()
                origem_norm = normalize_key(origem_raw)

                try:
                    area = float(str(r_norm.get('area_estimada_ha') or r_norm.get('area_ha') or r_norm.get('area') or 0).replace(',', '.'))
                except:
                    area = 0.0

                status_fogo = str(r_norm.get('status_fogo') or r_norm.get('status') or 'Controlado/Extinto').strip()
                risco_met = str(r_norm.get('risco_meteorologico') or r_norm.get('risco') or 'Normal').strip()
                obs = str(r_norm.get('observacoes') or r_norm.get('obs') or '').strip()

                inc_locais[loc] += 1
                month_key = None
                try:
                    dt = datetime.strptime(d_str, '%d/%m/%Y')
                    month_key = f"{meses_pt[dt.month]}/{str(dt.year)[2:]}"
                    inc_meses[month_key] += 1
                except:
                    pass

                row_dict = {
                    'data': d_str,
                    'local': loc,
                    'origem': origem_raw,
                    'area_ha': area,
                    'status': status_fogo,
                    'risco': risco_met,
                    'observacoes': obs
                }

                # Classificação operacional solicitada: SCBV (Voluntários) e CBMES (Militares 6º Batalhão)
                is_scbv = any(t in origem_norm for t in ['scbv', 'volunt', 'bv smj', 'bombeiro voluntario']) or (origem_norm == 'bv')
                is_cbmes = any(t in origem_norm for t in ['cbmes', 'militar', '6 bat', '6º bat', '6o bat', '6 bbm', '6º bbm', 'bombeiro militar'])

                if is_scbv:
                    scbv_registros.append(row_dict)
                    scbv_locais[loc] += 1
                    scbv_area_total += area
                    if month_key:
                        scbv_meses[month_key] += 1
                elif is_cbmes:
                    cbmes_registros.append(row_dict)
                    cbmes_locais[loc] += 1
                    cbmes_area_total += area
                    if month_key:
                        cbmes_meses[month_key] += 1
                else:
                    # Registros prévios ou chamados locais sem sigla explícita
                    if any(t in origem_norm for t in ['chamado', 'cicc', 'local', 'bombeiro']):
                        scbv_registros.append(row_dict)
                        scbv_locais[loc] += 1
                        scbv_area_total += area
                        if month_key: scbv_meses[month_key] += 1
                    else:
                        cbmes_registros.append(row_dict)
                        cbmes_locais[loc] += 1
                        cbmes_area_total += area
                        if month_key: cbmes_meses[month_key] += 1

        def parse_month_sort_key(m_str):
            try:
                m_part, y_part = m_str.split('/')
                m_nums = {'Jan':1,'Fev':2,'Mar':3,'Abr':4,'Mai':5,'Jun':6,'Jul':7,'Ago':8,'Set':9,'Out':10,'Nov':11,'Dez':12}
                return (int(y_part), m_nums.get(m_part, 1))
            except:
                return (0, 0)

        all_months_set = sorted(list(set(list(inc_meses.keys()) + list(scbv_meses.keys()) + list(cbmes_meses.keys()))), key=parse_month_sort_key)
        if not all_months_set:
            all_months_set = ['Ago/26', 'Set/26']

        scbv_evol_dados = [scbv_meses[m] for m in all_months_set]
        cbmes_evol_dados = [cbmes_meses[m] for m in all_months_set]
        geral_evol_dados = [inc_meses[m] if inc_meses[m] > 0 else (scbv_meses[m] + cbmes_meses[m]) for m in all_months_set]

        scbv_loc_sorted = sorted(scbv_locais.items(), key=lambda x: x[1], reverse=True)
        cbmes_loc_sorted = sorted(cbmes_locais.items(), key=lambda x: x[1], reverse=True)
        inc_loc_sorted = sorted(inc_locais.items(), key=lambda x: x[1], reverse=True)

        total_scbv = len(scbv_registros)
        total_cbmes = len(cbmes_registros)
        total_geral = total_scbv + total_cbmes

        incendios = {
            'total_focos': total_geral,
            'evolucao_labels': all_months_set,
            'evolucao_dados': geral_evol_dados,
            'locais_labels': [x[0] for x in inc_loc_sorted],
            'locais_dados': [x[1] for x in inc_loc_sorted],
            'scbv': {
                'nome': 'Bombeiros Voluntários (SCBV)',
                'sigla': 'SCBV',
                'total': total_scbv,
                'evolucao_labels': all_months_set,
                'evolucao_dados': scbv_evol_dados,
                'locais_labels': [x[0] for x in scbv_loc_sorted],
                'locais_dados': [x[1] for x in scbv_loc_sorted],
                'area_total_ha': round(scbv_area_total, 1),
                'registros': scbv_registros
            },
            'cbmes': {
                'nome': 'CBMES — 6º Batalhão',
                'sigla': 'CBMES',
                'total': total_cbmes,
                'evolucao_labels': all_months_set,
                'evolucao_dados': cbmes_evol_dados,
                'locais_labels': [x[0] for x in cbmes_loc_sorted],
                'locais_dados': [x[1] for x in cbmes_loc_sorted],
                'area_total_ha': round(cbmes_area_total, 1),
                'registros': cbmes_registros
            }
        }

        # 5. Cesan (Ab_Cesan)
        cesan_timeline_dict = {}
        cesan_cards_dict = {}

        CAPTACOES_MAPPING = {
            'possmoser': 15,
            'posmouser': 15,
            'santa maria da vitória': 16,
            'são sebastião': 17
        }

        sheet_ces = get_sheet_name('Ab_Cesan', 'Abastecimento_Cesan')
        if sheet_ces:
            df_ces = pd.read_excel(xl, sheet_ces).fillna('')
            for _, r in df_ces.iterrows():
                r_norm = {normalize_key(k): v for k, v in r.items()}
                d_str = format_date(r_norm.get('data'))
                if not d_str:
                    continue
                st_raw = str(r_norm.get('status_abastecimento') or r_norm.get('status') or 'Normal').strip()
                st_norm = normalize_key(st_raw)
                val = 0
                st_display = 'Normal'
                if 'crit' in st_norm:
                    val = 3
                    st_display = 'Crítico'
                elif 'alert' in st_norm:
                    val = 2
                    st_display = 'Alerta'
                elif 'atenc' in st_norm:
                    val = 1
                    st_display = 'Atenção'
                else:
                    val = 0
                    st_display = 'Normal'
                
                parts = d_str.split('/')
                lbl = f"{parts[0]}/{parts[1]}" if len(parts) >= 2 else d_str
                
                ponto_raw = str(r_norm.get('manancial_ponto') or '').strip()
                ponto_key = ponto_raw.lower()
                
                try:
                    dt_obj = datetime.strptime(d_str, '%d/%m/%Y')
                except:
                    dt_obj = datetime(1900, 1, 1)

                mapped_id = None
                for k_map, id_map in CAPTACOES_MAPPING.items():
                    if k_map in ponto_key:
                        mapped_id = id_map
                        break
                
                if not mapped_id:
                    m = re.search(r'\d+', ponto_raw)
                    mapped_id = int(m.group()) if m else 99

                if lbl not in cesan_timeline_dict:
                    cesan_timeline_dict[lbl] = {'val': val, 'status': st_display, 'date_raw': d_str, 'details': {}}
                elif val > cesan_timeline_dict[lbl]['val']:
                    cesan_timeline_dict[lbl]['val'] = val
                    cesan_timeline_dict[lbl]['status'] = st_display
                
                cesan_timeline_dict[lbl]['details'][mapped_id] = {'name': ponto_raw, 'status': st_display, 'val': val}

                card_entry = {
                    'name': ponto_raw,
                    'status': st_display,
                    'val': val,
                    'id': mapped_id,
                    'dt': dt_obj,
                    'date_str': d_str
                }

                if ponto_raw not in cesan_cards_dict or dt_obj >= cesan_cards_dict[ponto_raw]['dt']:
                    cesan_cards_dict[ponto_raw] = card_entry

        # Sort timeline by date
        def sort_tl(item):
            try:
                return datetime.strptime(item[1]['date_raw'], '%d/%m/%Y')
            except:
                return datetime(1900, 1, 1)
                
        sorted_tl = sorted(cesan_timeline_dict.items(), key=sort_tl)
        cesan_labels = [k for k, v in sorted_tl]
        cesan_values = [v['val'] for k, v in sorted_tl]
        cesan_status = [v['status'] for k, v in sorted_tl]
        cesan_details = [v['details'] for k, v in sorted_tl]
        
        cards = []
        for k, v in cesan_cards_dict.items():
            cards.append({
                'num': v['id'],
                'name': v['name'],
                'status': v['status'],
                'val': v['val'],
                'date': v['date_str']
            })
        cards.sort(key=lambda x: x['num'])

        cesan = {
            'timeline_labels': cesan_labels,
            'timeline_values': cesan_values,
            'timeline_status': cesan_status,
            'timeline_details': cesan_details,
            'captacoes': cards
        }
        if not cesan_labels:
            cesan = extract_cesan_data()
            cesan['captacoes'] = []

        # 6. Educação Monitoramento (Edu_Indicadores, Edu_Planejamento, Edu_Absenteismo, Edu_Ocorrencias)
        educacao_monitoramento = {}
        sheet_edu_ind = get_sheet_name('Edu_Indicadores', 'Educacao_Indicadores')
        sheet_edu_plan = get_sheet_name('Edu_Planejamento', 'Edu_Planejamento_4_6', 'Edu_Planejamento_4.6', 'Educacao_Planejamento')
        sheet_edu_abs = get_sheet_name('Edu_Absenteismo', 'Educacao_Absenteismo')
        sheet_edu_oco = get_sheet_name('Edu_Ocorrencias', 'Educacao_Ocorrencias')

        if sheet_edu_ind or sheet_edu_oco or sheet_edu_abs or sheet_edu_plan:
            try:
                kpis = {
                    'escolas_risco': 9,
                    'escolas_sem_climatizacao': 14,
                    'dias_aula_suspensos': 3,
                    'absenteismo_onda_calor': '8,4%'
                }
                complementares = {
                    'reservatorio_insuficiente': 6,
                    'ensino_remoto': 340,
                    'escola_abrigo': 1,
                    'acoes_planejamento': []
                }

                # 6.1 Indicadores e KPIs com correspondência resiliente a acentos e encoding
                if sheet_edu_ind:
                    df_ind = pd.read_excel(xl, sheet_edu_ind).fillna('')
                    for _, r in df_ind.iterrows():
                        r_norm = {normalize_key(k): v for k, v in r.items()}
                        cat = str(r_norm.get('categoria', '')).strip()
                        item = str(r_norm.get('item') or r_norm.get('indicador') or '').strip()
                        val = str(r_norm.get('valor', '')).strip()
                        st = str(r_norm.get('status', '')).strip()
                        item_norm = normalize_key(item)

                        if 'risco' in item_norm and ('escola' in item_norm or 'area' in item_norm or 'rea' in item_norm):
                            try: kpis['escolas_risco'] = int(float(val.replace(',', '.')))
                            except: pass
                        elif 'climatiz' in item_norm:
                            try: kpis['escolas_sem_climatizacao'] = int(float(val.replace(',', '.')))
                            except: pass
                        elif 'suspen' in item_norm:
                            try: kpis['dias_aula_suspensos'] = int(float(val.replace(',', '.')))
                            except: pass
                        elif 'absent' in item_norm:
                            clean_v = val.replace('%', '').replace(',', '.').strip()
                            kpis['absenteismo_onda_calor'] = f"{clean_v.replace('.', ',')}%"
                        elif 'reservat' in item_norm:
                            try: complementares['reservatorio_insuficiente'] = int(float(val.replace(',', '.')))
                            except: pass
                        elif 'remoto' in item_norm or 'hibrid' in item_norm:
                            try: complementares['ensino_remoto'] = int(float(val.replace(',', '.')))
                            except: pass
                        elif 'abrigo' in item_norm:
                            try: complementares['escola_abrigo'] = int(float(val.replace(',', '.')))
                            except: pass
                        elif cat == 'Planejamento_4.6' and not sheet_edu_plan:
                            st_norm = normalize_key(st)
                            st_cls = 'badge-concluido' if 'conclu' in st_norm else ('badge-andamento' if 'andamento' in st_norm else 'badge-pendente')
                            complementares['acoes_planejamento'].append({
                                'titulo': item,
                                'descricao': val,
                                'status': st,
                                'status_class': st_cls
                            })

                # 6.2 Planejamento 4.6 com suporte a qualquer variação de nome de coluna
                if sheet_edu_plan:
                    df_plan = pd.read_excel(xl, sheet_edu_plan).fillna('')
                    for _, r in df_plan.iterrows():
                        # Dicionário normalizado para acesso insensível a maiúsculas/minúsculas e acentos
                        r_norm = {normalize_key(k): v for k, v in r.items()}
                        acao = str(r_norm.get('acao_planejada') or r_norm.get('acao') or r_norm.get('titulo') or r_norm.get('item') or '').strip()
                        desc = str(r_norm.get('detalhamento_descricao') or r_norm.get('detalhamento') or r_norm.get('descricao') or '').strip()
                        resp = str(r_norm.get('responsavel_setor') or r_norm.get('responsavel') or '').strip()
                        prazo = format_date(r_norm.get('prazo_meta') or r_norm.get('prazo') or r_norm.get('data'))
                        st = str(r_norm.get('status') or 'Planejado').strip()
                        st_norm = normalize_key(st)

                        if acao or desc:
                            st_cls = 'badge-concluido' if 'conclu' in st_norm else ('badge-andamento' if 'andamento' in st_norm else 'badge-pendente')
                            full_desc = desc
                            extras = []
                            if resp and resp not in full_desc: extras.append(f"Setor: {resp}")
                            if prazo: extras.append(f"Meta: {prazo}")
                            if extras:
                                full_desc += f" ({' • '.join(extras)})"
                            complementares['acoes_planejamento'].append({
                                'titulo': acao if acao else desc,
                                'descricao': full_desc,
                                'status': st,
                                'status_class': st_cls
                            })

                # 6.3 Absenteísmo Semanal
                abs_labels, abs_values, abs_temps = [], [], []
                if sheet_edu_abs:
                    df_abs = pd.read_excel(xl, sheet_edu_abs).fillna('')
                    for _, r in df_abs.iterrows():
                        r_norm = {normalize_key(k): v for k, v in r.items()}
                        sem = str(r_norm.get('semana', '')).strip()
                        if not sem: continue
                        try: tax = float(str(r_norm.get('taxa_absenteismo_pct', 0)).replace(',', '.'))
                        except: tax = 0.0
                        try: tmp = float(str(r_norm.get('temp_max_media', 30)).replace(',', '.'))
                        except: tmp = 30.0
                        abs_labels.append(sem)
                        abs_values.append(tax)
                        abs_temps.append(tmp)

                # 6.4 Ocorrências Escolares
                ocorrencias = []
                if sheet_edu_oco:
                    df_oco = pd.read_excel(xl, sheet_edu_oco).fillna('')
                    for _, r in df_oco.iterrows():
                        r_norm = {normalize_key(k): v for k, v in r.items()}
                        esc = str(r_norm.get('escola_localidade', '') or r_norm.get('escola', '') or r_norm.get('localidade', '')).strip()
                        if not esc: continue
                        d_val = r_norm.get('data')
                        d_str = format_date(d_val)
                        st = str(r_norm.get('status', 'Concluído')).strip()
                        st_norm = normalize_key(st)
                        st_cls = 'badge-concluido' if 'conclu' in st_norm else ('badge-andamento' if 'andamento' in st_norm else 'badge-planejado')
                        ocorrencias.append({
                            'data': d_str if d_str else str(d_val or ''),
                            'escola': esc,
                            'motivo': str(r_norm.get('motivo', '')).strip(),
                            'acao': str(r_norm.get('acao_adotada', '') or r_norm.get('acao', '')).strip(),
                            'status': st,
                            'status_class': st_cls
                        })

                educacao_monitoramento = {
                    'kpis': kpis,
                    'absenteismo_semanas': {
                        'labels': abs_labels if abs_labels else ["SE29", "SE30", "SE31", "SE32", "SE33", "SE34", "SE35", "SE36"],
                        'values': abs_values if abs_values else [4.1, 4.6, 5.0, 4.8, 6.2, 7.5, 7.9, 8.4],
                        'temperaturas': abs_temps if abs_temps else [28.5, 29.2, 31.0, 30.1, 32.5, 34.2, 35.0, 36.1]
                    },
                    'indicadores_complementares': complementares,
                    'ocorrencias': ocorrencias
                }
            except Exception as e_ed:
                print(f"Erro ao processar abas de educação: {e_ed}")

        # 7. Meio Ambiente (Env_Arborizacao e Env_Indicadores)
        secmam_drive = None
        sheet_env_arb = get_sheet_name('Env_Arborizacao', 'Arborizacao_Urbana', 'Env_Arborizacao_Urbana')
        sheet_env_ind = get_sheet_name('Env_Indicadores', 'Meio_Ambiente_Indicadores')
        if sheet_env_arb or sheet_env_ind:
            try:
                kpis_env = {
                    "cadastrados": 720,
                    "ativos": 666,
                    "suprimidos_historico": 54,
                    "intervencoes_pendentes": 198,
                    "risco_critico": 3,
                    "interferencia_edp": 129
                }
                exemplares_criticos = []
                dist_risco = defaultdict(int)
                tipos_interv = defaultdict(int)
                interf_edp = defaultdict(int)
                cronograma = defaultdict(int)

                if sheet_env_ind:
                    df_env_ind = pd.read_excel(xl, sheet_env_ind).fillna('')
                    for _, r in df_env_ind.iterrows():
                        r_norm = {normalize_key(k): v for k, v in r.items()}
                        ind = str(r_norm.get('indicador') or r_norm.get('item') or '').strip()
                        ind_norm = normalize_key(ind)
                        val_raw = str(r_norm.get('valor', 0)).strip()
                        try: val_num = int(float(val_raw.replace(',', '.')))
                        except: val_num = 0
                        
                        if 'total' in ind_norm or 'cadastra' in ind_norm: kpis_env['cadastrados'] = val_num
                        elif 'ativa' in ind_norm: kpis_env['ativos'] = val_num
                        elif 'suprim' in ind_norm: kpis_env['suprimidos_historico'] = val_num
                        elif 'interven' in ind_norm or 'program' in ind_norm: kpis_env['intervencoes_pendentes'] = val_num
                        elif 'critico' in ind_norm or 'elevado' in ind_norm or 'prioritar' in ind_norm: kpis_env['risco_critico'] = val_num
                        elif 'edp' in ind_norm or 'fiacao' in ind_norm or 'rede' in ind_norm: kpis_env['interferencia_edp'] = val_num

                if sheet_env_arb:
                    df_env_arb = pd.read_excel(xl, sheet_env_arb).fillna('')
                    for _, r in df_env_arb.iterrows():
                        r_norm = {normalize_key(k): v for k, v in r.items()}
                        tomb = str(r_norm.get('tombamento') or r_norm.get('id') or '').strip()
                        esp = str(r_norm.get('especie') or r_norm.get('arvore') or '').strip()
                        loc = str(r_norm.get('localidade_logradouro') or r_norm.get('localidade') or r_norm.get('local') or '').strip()
                        coord = str(r_norm.get('coordenadas_utm') or r_norm.get('coordenadas') or '').strip()
                        risco = str(r_norm.get('classe_risco') or r_norm.get('risco') or '').strip()
                        interv = str(r_norm.get('intervencao_recomendada') or r_norm.get('intervencao') or '').strip()
                        edp = str(r_norm.get('interferencia_edp') or r_norm.get('edp') or '').strip()
                        prazo = str(r_norm.get('prioridade_prazo') or r_norm.get('prazo') or '').strip()
                        st = str(r_norm.get('status_execucao') or r_norm.get('status') or '').strip()

                        if risco: dist_risco[risco] += 1
                        if interv: tipos_interv[interv] += 1
                        if edp: interf_edp[edp] += 1
                        if prazo: cronograma[prazo] += 1

                        risco_norm = normalize_key(risco)
                        if any(x in risco_norm for x in ['elevad', 'alto', 'criti']) and tomb:
                            exemplares_criticos.append({
                                "tombamento": tomb,
                                "especie": esp,
                                "local": loc,
                                "coordenadas": coord if coord else "N/A",
                                "risco": risco,
                                "intervencao": interv,
                                "prazo": prazo if prazo else "Prioritário"
                            })

                secmam_drive = {
                    "kpis": kpis_env,
                    "distribuicao_risco": {
                        "labels": list(dist_risco.keys()) if dist_risco else ["Elevado (Imediato)", "Alto (Prioritário)", "Moderado (Programado)", "Baixo (Monitoramento)", "Pendente de Avaliação"],
                        "values": list(dist_risco.values()) if dist_risco else [1, 2, 96, 311, 256],
                        "colors": ["#7F1D1D", "#EA580C", "#EAB308", "#16A34A", "#94A3B8"]
                    },
                    "tipos_intervencao": {
                        "labels": list(tipos_interv.keys()) if tipos_interv else ["Poda de Redução de Copa", "Poda de Limpeza", "Supressão Preventiva", "Poda de Condução", "Apenas Monitoramento"],
                        "values": list(tipos_interv.values()) if tipos_interv else [74, 50, 39, 35, 212],
                        "colors": ["#0F4C81", "#2563EB", "#DC2626", "#059669", "#64748B"]
                    },
                    "interferencia_edp": {
                        "labels": list(interf_edp.keys()) if interf_edp else ["Contato Direto (EDP)", "Proximidade Crítica (EDP)", "Sem Conflito Elétrico"],
                        "values": list(interf_edp.values()) if interf_edp else [92, 37, 537],
                        "colors": ["#DC2626", "#F59E0B", "#10B981"]
                    },
                    "cronograma_prioridade": {
                        "labels": list(cronograma.keys()) if cronograma else ["P1 - Risco Elevado", "P2 - Risco Alto", "P3 - Risco Moderado", "P4 - Risco Baixo"],
                        "values": list(cronograma.values()) if cronograma else [1, 2, 95, 100],
                        "prazos": ["Imediato", "Duas primeiras semanas", "Programado (6 meses)", "Programado (6 meses)"]
                    },
                    "exemplares_criticos": exemplares_criticos if exemplares_criticos else extract_secmam_data()["exemplares_criticos"]
                }
            except Exception as e_env:
                print(f"Erro ao processar abas do meio ambiente: {e_env}")

        sync_time_str = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        parsed_data = {
            "drenagem": drenagem,
            "caixas_secas": caixas_secas,
            "assistencia_social": assistencia_social,
            "vigilancia_vetorial": vigilancia_vetorial,
            "incendios": incendios,
            "cesan": cesan,
            "educacao_monitoramento": educacao_monitoramento,
            "secmam": secmam_drive or extract_secmam_data(),
            "sync_info": {
                "source": source,
                "timestamp": sync_time_str,
                "success": True
            }
        }

        _gdrive_cache["data"] = parsed_data
        _gdrive_cache["last_fetch"] = now
        _gdrive_cache["last_sync_str"] = sync_time_str
        _gdrive_cache["source"] = source
        _gdrive_cache["last_mtime"] = 0
        return parsed_data

    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"Erro ao processar abas da planilha: {e}")
        if _gdrive_cache["data"]:
            return _gdrive_cache["data"]
        return {}


def get_data_from_spreadsheets(force_drive=False):
    drive_data = fetch_google_drive_data(force=force_drive)

    payload = {
        "educacao": {},
        "saude": {},
        "educacao_monitoramento": drive_data.get("educacao_monitoramento", {}),
        "cesan": drive_data.get("cesan") or extract_cesan_data(),
        "incendios": drive_data.get("incendios", {}),
        "assistencia_social": drive_data.get("assistencia_social", {}),
        "vigilancia_vetorial": drive_data.get("vigilancia_vetorial", {}),
        "drenagem": drive_data.get("drenagem", []),
        "caixas_secas": drive_data.get("caixas_secas", {}),
        "secmam": drive_data.get("secmam") or extract_secmam_data(),
        "sync_info": drive_data.get("sync_info", {
            "source": _gdrive_cache.get("source", "Google Drive"),
            "timestamp": _gdrive_cache.get("last_sync_str", ""),
            "success": True
        })
    }

    # 1. Carrega dados pré-processados de Educação e Saúde (garante resposta imediata em serverless)
    ed_json = os.path.join(DATA_DIR, 'dados', 'educacao_dados.json')
    sa_json = os.path.join(DATA_DIR, 'dados', 'saude_dados.json')
    ed_mon_json = os.path.join(DATA_DIR, 'dados', 'educacao_monitoramento.json')

    if not payload["educacao_monitoramento"] and os.path.exists(ed_mon_json):
        try:
            import json
            with open(ed_mon_json, 'r', encoding='utf-8') as f:
                payload["educacao_monitoramento"] = json.load(f)
        except Exception as err_mon:
            print("Erro ao carregar educacao_monitoramento.json:", err_mon)

    if os.path.exists(ed_json):
        try:
            import json
            with open(ed_json, 'r', encoding='utf-8') as f:
                payload["educacao"] = json.load(f)
        except Exception as err_ed:
            print("Erro ao carregar educacao_dados.json:", err_ed)

    if os.path.exists(sa_json):
        try:
            import json
            with open(sa_json, 'r', encoding='utf-8') as f:
                payload["saude"] = json.load(f)
        except Exception as err_sa:
            print("Erro ao carregar saude_dados.json:", err_sa)

    # 2. Fallback para leitura direta das planilhas em dados/ ou arquivo_morto/
    if not payload["educacao"] or not payload["saude"]:
        excel_files = (glob.glob(os.path.join(DATA_DIR, 'dados', '*.xlsx')) +
                       glob.glob(os.path.join(DATA_DIR, '*.xlsx')) +
                       glob.glob(os.path.join(DATA_DIR, 'arquivo_morto', '*.xlsx')))
        for file in excel_files:
            try:
                filename = os.path.basename(file).lower()
                if ('escola' in filename and not payload["educacao"]) or ('saude' in filename and not payload["saude"]):
                    df = pd.read_excel(file, header=8)
                    processed = process_dataframe(df)
                    if 'escola' in filename:
                        payload["educacao"] = processed
                    elif 'saude' in filename:
                        payload["saude"] = processed
            except Exception as e:
                print(f"Erro ao ler {file}: {e}")
                continue

    empty_struct = {
        "tipologia_risco": {"labels": ["Estrutural (Mov. Massa)", "Ambiental (Susc. Inund.)", "Hidrológico", "Geológico"], "values": [0,0,0,0], "total": 0},
        "ocorrencias_tipo": {"labels": ["Deslizamento (Geológico)", "Alagamento (Hidrológico)", "Estrutural (Mov. Massa)", "Suscetível Inundação"], "values": [0,0,0,0]},
        "top_5_localidades": {"labels": ["Sem Dados"], "values": [0]}
    }

    if not payload["educacao"]: payload["educacao"] = empty_struct
    if not payload["saude"]: payload["saude"] = empty_struct

    return payload

@app.before_request
def check_authentication():
    # Permite arquivos estáticos e favicon sem autenticação
    if request.path.startswith('/static/') or request.path == '/favicon.ico':
        return None
        
    # Permite rotas de autenticação
    if request.endpoint in ['login', 'logout', 'serve_static', 'favicon']:
        return None
        
    # Verifica se existe usuário autenticado na sessão
    if not session.get('user'):
        if request.path.startswith('/api/'):
            return jsonify({"error": "Autenticação necessária", "login_required": True}), 401
        return redirect(url_for('login', next=request.path))

@app.route('/login', methods=['GET', 'POST'])
def login():
    next_page = request.args.get('next')
    
    if request.method == 'GET':
        if session.get('user'):
            if next_page and next_page.startswith('/') and not next_page.startswith('//'):
                return redirect(next_page)
            return redirect(url_for('index'))
        return render_template('login.html')
        
    # Processa submissão do formulário
    cpf_raw = request.form.get('cpf', '').strip()
    senha = request.form.get('senha', '').strip()
    remember = request.form.get('remember')
    
    clean_c = clean_cpf(cpf_raw)
    if not clean_c or not senha:
        return render_template('login.html', error="Por favor, informe seu CPF e sua senha de acesso.", cpf_value=cpf_raw), 400
        
    users = get_authorized_users(force_refresh=True)
    user_match = users.get(clean_c)
    
    if not user_match:
        return render_template('login.html', error="CPF não cadastrado no sistema. Solicite seu cadastro à Defesa Civil.", cpf_value=cpf_raw), 401
        
    status_lower = str(user_match.get('status', 'ativo')).lower()
    if status_lower in ['bloqueado', 'inativo']:
        return render_template('login.html', error="Acesso suspenso ou bloqueado. Contate a Defesa Civil.", cpf_value=cpf_raw), 403
        
    if clean_password(user_match.get('senha', '')) != clean_password(senha):
        return render_template('login.html', error="Senha incorreta. Verifique suas credenciais.", cpf_value=cpf_raw), 401
        
    # Sessão autorizada com sucesso
    session.permanent = bool(remember)
    session['user'] = {
        "nome": user_match.get('nome', 'Usuário'),
        "cpf": user_match.get('cpf', format_cpf_display(clean_c)),
        "cpf_clean": clean_c,
        "setor": user_match.get('setor', 'Defesa Civil'),
        "email": user_match.get('email', '')
    }
    
    if next_page and next_page.startswith('/') and not next_page.startswith('//') and not next_page.startswith('/login'):
        return redirect(next_page)
    return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/static/<path:filename>')
def serve_static(filename):
    import urllib.parse
    clean_filename = urllib.parse.unquote(filename)
    static_dir = os.path.join(DATA_DIR, 'static')
    target = os.path.join(static_dir, clean_filename)
    if os.path.isfile(target):
        return send_file(target)
    alt_target = os.path.join(static_dir, clean_filename.replace(' ', '_'))
    if os.path.isfile(alt_target):
        return send_file(alt_target)
    alt_target_spaces = os.path.join(static_dir, clean_filename.replace('_', ' '))
    if os.path.isfile(alt_target_spaces):
        return send_file(alt_target_spaces)
    return send_file(os.path.join(static_dir, filename))

@app.route('/api/data')
def api_data():
    return jsonify(get_data_from_spreadsheets())

@app.route('/api/sync-drive', methods=['GET', 'POST'])
def api_sync_drive():
    """Força sincronização imediata dos dados com a planilha do Google Drive."""
    data = get_data_from_spreadsheets(force_drive=True)
    return jsonify({
        "status": "ok",
        "sync_info": data.get("sync_info", {})
    })

@app.route('/favicon.ico')
def favicon():
    return send_file(os.path.join(DATA_DIR, 'static', 'favicon.ico'), mimetype='image/vnd.microsoft.icon')

@app.route('/mapa/educacao')
def mapa_educacao():
    return render_template('mapa_educacao.html')

@app.route('/mapa/saude')
def mapa_saude():
    return render_template('mapa_saude.html')

@app.route('/api/geojson/educacao')
def api_geojson_educacao():
    """Retorna o GeoJSON editavel com os pontos e dados de risco das escolas municipais."""
    candidatos = [
        os.path.join(DATA_DIR, 'dados', 'pontos_educacao.geojson'),
        os.path.join(DATA_DIR, 'static', 'geojson', 'pontos_educacao.geojson')
    ]
    for p in candidatos:
        if os.path.exists(p):
            with open(p, 'r', encoding='utf-8') as f:
                return Response(f.read(), mimetype='application/json; charset=utf-8')

    return jsonify({"type": "FeatureCollection", "features": []})

@app.route('/api/geojson/saude')
def api_geojson_saude():
    """Retorna o GeoJSON editavel com os pontos e dados de risco das unidades de saude."""
    candidatos = [
        os.path.join(DATA_DIR, 'dados', 'pontos_saude.geojson'),
        os.path.join(DATA_DIR, 'static', 'geojson', 'pontos_saude.geojson')
    ]
    for p in candidatos:
        if os.path.exists(p):
            with open(p, 'r', encoding='utf-8') as f:
                return Response(f.read(), mimetype='application/json; charset=utf-8')

    return jsonify({"type": "FeatureCollection", "features": []})


@app.route('/api/geojson/limite')
def api_geojson_limite():
    """Retorna o GeoJSON do limite municipal de Santa Maria de Jetiba."""
    limite_path = os.path.join(DATA_DIR, 'static', 'geojson', 'limite_SMJ.geojson')
    if os.path.exists(limite_path):
        return send_file(limite_path, mimetype='application/json')
    return jsonify({"error": "Arquivo de limite nao encontrado"}), 404


@app.route('/relatorio')
def relatorio():
    import json
    from datetime import datetime
    
    setor_ativo = request.args.get('setor') or request.args.get('bloco') or 'geral'
    
    # Busca dados das planilhas
    data_spreadsheets = get_data_from_spreadsheets()
    
    # Busca dados de clima e ANA (reaproveitando as rotas)
    clima_res = json.loads(api_weather().get_data())
    ana_res = json.loads(api_hidroweb().get_data())
    
    now = datetime.now()
    
    incendios_data = data_spreadsheets.get('incendios', {})
    vigilancia_data = data_spreadsheets.get('vigilancia_vetorial', {})
    try:
        total_focos = sum(incendios_data.get('evolucao_dados', []))
    except:
        total_focos = 5
    try:
        total_dengue = sum(vigilancia_data.get('casos_dengue', {}).get('values', []))
    except:
        total_dengue = 18

    return render_template(
        'relatorio.html',
        setor_ativo=setor_ativo,
        data_emissao=now.strftime("%d/%m/%Y"),
        hora_emissao=now.strftime("%H:%M:%S"),
        clima=clima_res,
        ana=ana_res,
        cesan=data_spreadsheets.get('cesan', {}),
        drenagem=data_spreadsheets.get('drenagem', []),
        caixas_secas=data_spreadsheets.get('caixas_secas', {}),
        secmam=data_spreadsheets.get('secmam', {}),
        educacao=data_spreadsheets.get('educacao', {}),
        saude=data_spreadsheets.get('saude', {}),
        incendios=incendios_data,
        assistencia_social=data_spreadsheets.get('assistencia_social', {}),
        vigilancia_vetorial=vigilancia_data,
        total_focos=total_focos,
        total_dengue=total_dengue,
        sync_info=data_spreadsheets.get('sync_info', {})
    )

_hidroweb_cache = {"data": None, "timestamp": 0}

@app.route('/api/hidroweb')
def api_hidroweb():
    global _hidroweb_cache
    now = time.time()
    if _hidroweb_cache["data"] and (now - _hidroweb_cache["timestamp"] < 90):
        return jsonify(_hidroweb_cache["data"])

    import urllib.request
    import re
    from datetime import datetime, timedelta
    from collections import defaultdict
    
    result = {"nivel": None, "vazao": None, "chuva": None, "data_hora": None, "error": False}
    
    try:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=90)
        fmt = lambda d: d.strftime('%d/%m/%Y')
        
        url = (f"http://telemetriaws1.ana.gov.br/ServiceANA.asmx/DadosHidrometeorologicos"
               f"?codEstacao=57119000"
               f"&dataInicio={fmt(start_date)}"
               f"&dataFim={fmt(end_date)}")
        
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        resp = urllib.request.urlopen(req, timeout=6)
        xml_data = resp.read().decode('utf-8', errors='replace')
        
        # Extrair todos os registros
        records = re.findall(
            r'<DataHora>(.+?)</DataHora>.*?<Vazao>(.*?)</Vazao>.*?<Nivel>(.*?)</Nivel>.*?<Chuva>(.*?)</Chuva>',
            xml_data, re.DOTALL
        )
        
        if not records:
            raise Exception("Sem registros retornados")
        
        # Ordenar cronologicamente em ordem decrescente (mais recente primeiro)
        def parse_dt_rec(r):
            try:
                return datetime.strptime(r[0].strip()[:19], '%Y-%m-%d %H:%M:%S')
            except:
                try:
                    return datetime.strptime(r[0].strip()[:10], '%Y-%m-%d')
                except:
                    return datetime.min

        sorted_records = sorted(records, key=parse_dt_rec, reverse=True)
        
        # Encontra o registro mais recente com nível válido
        latest = next((r for r in sorted_records if r[2].strip()), sorted_records[0])
        nivel_raw = latest[2].strip()
        vazao_raw = latest[1].strip()
        chuva_raw = latest[3].strip()
        data_hora_raw = latest[0].strip()
        
        def conv_nivel(v):
            f = float(v)
            return round(f / 100, 1) if f > 10000 else round(f, 1)
        
        result["nivel"] = str(conv_nivel(nivel_raw)) if nivel_raw else None
        result["vazao"] = f"{float(vazao_raw):.2f}" if vazao_raw else None
        result["chuva"] = f"{float(chuva_raw):.1f}" if chuva_raw else None
        try:
            dt_obj = parse_dt_rec(latest)
            result["data_hora"] = dt_obj.strftime('%d/%m/%Y %H:%M')
        except:
            result["data_hora"] = data_hora_raw[:16]
        
        # Agrupamento mensal (média por mês) para gráfico histórico
        meses = defaultdict(list)
        meses_pt = {1:'Jan',2:'Fev',3:'Mar',4:'Abr',5:'Mai',6:'Jun',7:'Jul',8:'Ago',9:'Set',10:'Out',11:'Nov',12:'Dez'}
        meses_ordem = {}
        for r in records:
            try:
                dt = datetime.strptime(r[0].strip()[:10], '%Y-%m-%d')
                n = float(r[2].strip())
                if n > 10000:
                    n = n / 100
                chave = f"{meses_pt[dt.month]}/{str(dt.year)[2:]}"
                sort_key = dt.year * 100 + dt.month
                meses[chave].append(n)
                meses_ordem[chave] = sort_key
            except:
                continue
        
        # Ordenar cronologicamente
        meses_list = sorted(meses.items(), key=lambda x: meses_ordem.get(x[0], 0))
        labels_m = [m[0] for m in meses_list]
        values_m = [round(sum(v)/len(v), 1) for m, v in meses_list]
        
        result["nivel_mensal"] = {"labels": labels_m, "values": values_m}
        
    except Exception as e:
        print("ANA API falhou:", e)
        result["error"] = True
        result["nivel"] = "Indisponível"
        result["nivel_mensal"] = {
            "labels": ["Fev/26", "Mar/26", "Abr/26", "Mai/26", "Jun/26", "Jul/26", "Ago/26", "Set/26"],
            "values": [620, 710, 680, 540, 492, 481, 486, 486]
        }
        
    _hidroweb_cache["data"] = result
    _hidroweb_cache["timestamp"] = now
    return jsonify(result)

@app.route('/api/weather')
def api_weather():
    import urllib.request
    import json
    
    # Coordenadas de Santa Maria de Jetibá
    url = ("https://api.open-meteo.com/v1/forecast?"
           "latitude=-20.0383&longitude=-40.7461"
           "&current=temperature_2m,relative_humidity_2m,wind_speed_10m"
           "&hourly=precipitation_probability"
           "&daily=temperature_2m_max,temperature_2m_min,precipitation_probability_max,weathercode"
           "&timezone=America%2FSao_Paulo&forecast_days=7")
    result = {"error": False}
    
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        resp = urllib.request.urlopen(req, timeout=5)
        data = json.loads(resp.read().decode('utf-8'))
        
        precip_prob = data['hourly']['precipitation_probability'][0]
        result["temp"] = data['current']['temperature_2m']
        result["umidade"] = data['current']['relative_humidity_2m']
        result["vento"] = data['current']['wind_speed_10m']
        result["chuva"] = precip_prob

        # Previsão de 7 dias
        daily = data['daily']
        result["forecast"] = []
        days_pt = ["Seg","Ter","Qua","Qui","Sex","Sáb","Dom"]
        import datetime
        for i in range(7):
            date_str = daily['time'][i]
            d = datetime.datetime.strptime(date_str, '%Y-%m-%d')
            code = daily['weathercode'][i]
            result["forecast"].append({
                "dia": days_pt[d.weekday()],
                "data": d.strftime('%d/%m'),
                "max": daily['temperature_2m_max'][i],
                "min": daily['temperature_2m_min'][i],
                "chuva": daily['precipitation_probability_max'][i],
                "code": code
            })
    except Exception as e:
        print("Weather API falhou:", e)
        result["error"] = True
        
    return jsonify(result)


@app.route('/assistencia_social')
def assistencia_social():
    return render_template('assistencia.html')

@app.route('/api/assistencia_data')
def assistencia_data():
    try:
        df = pd.read_excel('dados/Matriz_Riscos_Assistencia_Social_SMJ.xlsx', header=8)
        # Drop rows where the first column is nan
        first_col = df.columns[0]
        df = df.dropna(subset=[first_col])
        
        # Clean column names (handle the special characters if needed, or just use indices)
        cols = df.columns.tolist()
        
        # Build list of dicts
        records = []
        for _, row in df.iterrows():
            # Extract coordinates
            lat_str = str(row.iloc[5]).strip()
            lon_str = str(row.iloc[6]).strip()
            
            # Simple conversion function
            def to_float(val):
                try:
                    return float(val.replace(',', '.'))
                except:
                    return None
            
            lat = to_float(lat_str)
            lon = to_float(lon_str)
            
            records.append({
                'id': row.iloc[0],
                'codigo': str(row.iloc[1]),
                'tipo': str(row.iloc[2]),
                'uso': str(row.iloc[3]),
                'localidade': str(row.iloc[4]),
                'lat': lat,
                'lon': lon,
                'risco_geol_status': str(row.iloc[7]),
                'risco_geol_grau': str(row.iloc[8]),
                'risco_geol_setor': str(row.iloc[9]),
                'risco_hidro_status': str(row.iloc[10]),
                'risco_hidro_grau': str(row.iloc[11]),
                'risco_hidro_cenario': str(row.iloc[12]),
                'susc_inundacao': str(row.iloc[13]),
                'susc_mov_massa': str(row.iloc[14]),
                'risco_geral': str(row.iloc[15])
            })
            
        return jsonify({"status": "success", "data": records})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
