import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.datavalidation import DataValidation
import os

wb = openpyxl.Workbook()
ws = wb.active
ws.title = 'Usuarios'
ws.sheet_properties.tabColor = '0F172A'
ws.views.sheetView[0].showGridLines = True
ws.freeze_panes = 'A2'

font_header = Font(name='Segoe UI', size=11, bold=True, color='FFFFFF')
font_body = Font(name='Segoe UI', size=10)
fill_hdr = PatternFill(start_color='0F172A', end_color='0F172A', fill_type='solid')
fill_stripe = PatternFill(start_color='F8FAFC', end_color='F8FAFC', fill_type='solid')

thin_border = Border(
    left=Side(style='thin', color='CBD5E1'),
    right=Side(style='thin', color='CBD5E1'),
    top=Side(style='thin', color='CBD5E1'),
    bottom=Side(style='thin', color='CBD5E1')
)

headers = ['Nome', 'CPF', 'Senha', 'Setor_Orgao', 'Email', 'Status', 'Data_Cadastro', 'Ultimo_Acesso', 'Observacoes']

ws.row_dimensions[1].height = 28
for col_i, h in enumerate(headers, start=1):
    c = ws.cell(row=1, column=col_i, value=h)
    c.font = font_header
    c.fill = fill_hdr
    c.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
    c.border = thin_border

# Dados de exemplo com CPFs validos de teste
usuarios = [
    ['Administrador Geral', '000.000.000-00', 'Admin@2026', 'Defesa Civil', 'admin.defesacivil@pmsmj.es.gov.br', 'Ativo', '10/09/2026', '—', 'Acesso administrativo'],
    ['Defesa Civil Municipal', '111.222.333-44', 'DefesaCivil@2026', 'Defesa Civil', 'defesacivil@pmsmj.es.gov.br', 'Ativo', '10/09/2026', '—', 'Coordenação Municipal de Proteção'],
    ['Equipe Educação (SEMED)', '222.333.444-55', 'EduSMJ@2026', 'Educação', 'educacao@pmsmj.es.gov.br', 'Ativo', '10/09/2026', '—', 'Acesso Secretaria de Educação'],
    ['Equipe Saúde (SEMUS)', '333.444.555-66', 'SaudeSMJ@2026', 'Saúde', 'saude@pmsmj.es.gov.br', 'Ativo', '10/09/2026', '—', 'Acesso Secretaria de Saúde'],
    ['Equipe Assistência Social', '444.555.666-77', 'SocialSMJ@2026', 'Assistência Social', 'social@pmsmj.es.gov.br', 'Ativo', '10/09/2026', '—', 'Acesso Assistência Social'],
    ['Gabinete do Prefeito', '555.666.777-88', 'Gabinete@2026', 'Gabinete', 'gabinete@pmsmj.es.gov.br', 'Ativo', '10/09/2026', '—', 'Consulta Executiva'],
    ['Usuário de Teste / Convidado', '123.456.789-00', '123456', 'Defesa Civil', 'teste@pmsmj.es.gov.br', 'Ativo', '10/09/2026', '—', 'Usuário rápido de teste (CPF: 12345678900 | Senha: 123456)']
]

for r_i, row in enumerate(usuarios, start=2):
    ws.row_dimensions[r_i].height = 20
    use_stripe = (r_i % 2 == 0)
    for col_i, val in enumerate(row, start=1):
        c = ws.cell(row=r_i, column=col_i, value=val)
        c.font = font_body
        if use_stripe:
            c.fill = fill_stripe
        c.border = thin_border
        col_name = headers[col_i - 1].lower()
        if 'cpf' in col_name or 'data' in col_name or 'status' in col_name:
            c.alignment = Alignment(horizontal='center', vertical='center')
        else:
            c.alignment = Alignment(horizontal='left', vertical='center')

ws.auto_filter.ref = f'A1:{get_column_letter(len(headers))}100'

# Validação do campo Status
dv = DataValidation(type='list', formula1='"Ativo,Bloqueado,Inativo"', allow_blank=True)
ws.add_data_validation(dv)
dv.add('F2:F500')

for col in ws.columns:
    max_len = max(len(str(cell.value or '')) for cell in col)
    col_letter = get_column_letter(col[0].column)
    ws.column_dimensions[col_letter].width = max(max_len + 4, 16)

os.makedirs('dados', exist_ok=True)
wb.save('Planilha_Usuarios_Controle_Acesso.xlsx')
wb.save('dados/Planilha_Usuarios_Controle_Acesso.xlsx')
print('Planilha de usuários salva com sucesso com chave CPF!')
