"""
Script para gerar a Planilha Oficial de Usuários e Controle de Acesso
Pronta para upload no Google Drive ou integração com o Dashboard El Niño SMJ.
Colunas: Nome, CPF, Senha, Setor_Orgao, Email, Status, Data_Cadastro, Ultimo_Acesso, Observacoes
"""

import os
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.utils import get_column_letter

DATA_DIR = os.path.dirname(os.path.abspath(__file__))

def gerar_planilha_usuarios():
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Usuarios"
    ws.sheet_properties.tabColor = "1E3A8A" # Azul Escuro Oficial
    ws.views.sheetView[0].showGridLines = True
    ws.freeze_panes = "A2"
    ws.row_dimensions[1].height = 32

    # Cores e Estilos Oficiais
    font_header = Font(name="Segoe UI", size=11, bold=True, color="FFFFFF")
    font_body = Font(name="Segoe UI", size=10, color="0F172A")
    fill_header = PatternFill(start_color="1E3A8A", end_color="1E3A8A", fill_type="solid")
    fill_even = PatternFill(start_color="F8FAFC", end_color="F8FAFC", fill_type="solid")
    fill_odd = PatternFill(start_color="FFFFFF", end_color="FFFFFF", fill_type="solid")
    
    border_thin = Border(
        left=Side(style="thin", color="CBD5E1"),
        right=Side(style="thin", color="CBD5E1"),
        top=Side(style="thin", color="CBD5E1"),
        bottom=Side(style="thin", color="CBD5E1")
    )

    headers = [
        "Nome",
        "CPF",
        "Senha",
        "Setor_Orgao",
        "Email",
        "Status",
        "Data_Cadastro",
        "Ultimo_Acesso",
        "Observacoes"
    ]

    # Escreve cabeçalhos
    for col_idx, h in enumerate(headers, start=1):
        cell = ws.cell(row=1, column=col_idx, value=h)
        cell.font = font_header
        cell.fill = fill_header
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        cell.border = border_thin

    # Dados padrão de exemplo e acesso
    usuarios_iniciais = [
        (
            "Administrador Geral",
            "000.000.000-00",
            "Admin@2026",
            "Defesa Civil",
            "admin.defesacivil@pmsmj.es.gov.br",
            "Ativo",
            "10/09/2026",
            "-",
            "Acesso de gestão e suporte técnico do painel"
        ),
        (
            "Defesa Civil Municipal",
            "111.222.333-44",
            "DefesaCivil@2026",
            "Defesa Civil",
            "defesacivil@pmsmj.es.gov.br",
            "Ativo",
            "10/09/2026",
            "-",
            "Coordenação de resposta e monitoramento hidrometeorológico"
        ),
        (
            "Equipe Educação (SEMED)",
            "222.333.444-55",
            "EduSMJ@2026",
            "Educação",
            "educacao@pmsmj.es.gov.br",
            "Ativo",
            "10/09/2026",
            "-",
            "Monitoramento de risco nas escolas municipais e CMEIs"
        ),
        (
            "Equipe Saúde (SEMUS)",
            "333.444.555-66",
            "SaudeSMJ@2026",
            "Saúde",
            "saude@pmsmj.es.gov.br",
            "Ativo",
            "10/09/2026",
            "-",
            "Monitoramento de USFs, hospitais e vigilância em saúde"
        ),
        (
            "Equipe Assistência Social",
            "444.555.666-77",
            "SocialSMJ@2026",
            "Assistência Social",
            "social@pmsmj.es.gov.br",
            "Ativo",
            "10/09/2026",
            "-",
            "Acompanhamento de famílias e abrigos provisórios"
        ),
        (
            "Gabinete do Prefeito",
            "555.666.777-88",
            "Gabinete@2026",
            "Gabinete",
            "gabinete@pmsmj.es.gov.br",
            "Ativo",
            "10/09/2026",
            "-",
            "Visualização executiva e relatórios gerenciais"
        ),
        (
            "Usuário de Teste / Convidado",
            "123.456.789-00",
            "123456",
            "Defesa Civil",
            "teste@pmsmj.es.gov.br",
            "Ativo",
            "10/09/2026",
            "-",
            "Conta de homologação rápida e validação de login"
        )
    ]

    for row_idx, user_data in enumerate(usuarios_iniciais, start=2):
        ws.row_dimensions[row_idx].height = 22
        fill = fill_even if row_idx % 2 == 0 else fill_odd
        for col_idx, val in enumerate(user_data, start=1):
            cell = ws.cell(row=row_idx, column=col_idx, value=val)
            cell.font = font_body
            cell.fill = fill
            cell.border = border_thin

            # Alinhamento específico por coluna
            col_name = headers[col_idx - 1]
            if col_name in ["CPF", "Senha", "Status", "Data_Cadastro", "Ultimo_Acesso"]:
                cell.alignment = Alignment(horizontal="center", vertical="center")
            elif col_name == "Setor_Orgao":
                cell.alignment = Alignment(horizontal="center", vertical="center")
            else:
                cell.alignment = Alignment(horizontal="left", vertical="center")
                
            # Força formatação de texto para CPF e Senha para o Excel não converter em número
            if col_name in ["CPF", "Senha"]:
                cell.number_format = "@"

    # Validação suspensa na coluna Status ('Ativo', 'Bloqueado', 'Inativo')
    val_status = DataValidation(
        type="list",
        formula1='"Ativo,Bloqueado,Inativo"',
        allow_blank=False,
        showErrorMessage=True,
        errorTitle="Status Inválido",
        error="Escolha um dos valores permitidos: Ativo, Bloqueado ou Inativo."
    )
    ws.add_data_validation(val_status)
    val_status.add("F2:F1000")

    # Auto-ajuste de largura de colunas
    for col in ws.columns:
        max_len = 0
        col_letter = get_column_letter(col[0].column)
        for cell in col:
            val_str = str(cell.value or "")
            if len(val_str) > max_len:
                max_len = len(val_str)
        ws.column_dimensions[col_letter].width = max(max_len + 5, 14)

    # Filtro automático
    ws.auto_filter.ref = f"A1:I{len(usuarios_iniciais) + 1}"

    # Salva nos locais necessários
    out_files = [
        os.path.join(DATA_DIR, "Planilha_Usuarios_Controle_Acesso.xlsx"),
        os.path.join(DATA_DIR, "dados", "Planilha_Usuarios_Controle_Acesso.xlsx"),
        os.path.join(DATA_DIR, "Planilha_Controle_Acesso_Usuarios_SMJ.xlsx")
    ]
    for p in out_files:
        wb.save(p)
        print(f"Salvo com sucesso: {p}")

    # Também injeta a aba 'Usuarios' dentro da planilha principal Planilha_Alimentacao_Dashboard_ElNino_SMJ.xlsx
    main_sheets = [
        os.path.join(DATA_DIR, "Planilha_Alimentacao_Dashboard_ElNino_SMJ.xlsx"),
        os.path.join(DATA_DIR, "dados", "Planilha_Alimentacao_Dashboard_ElNino_SMJ.xlsx")
    ]
    for main_p in main_sheets:
        if os.path.exists(main_p):
            try:
                main_wb = openpyxl.load_workbook(main_p)
                if "Usuarios" in main_wb.sheetnames:
                    del main_wb["Usuarios"]
                new_ws = main_wb.create_sheet(title="Usuarios")
                new_ws.sheet_properties.tabColor = "1E3A8A"
                new_ws.views.sheetView[0].showGridLines = True
                new_ws.freeze_panes = "A2"
                new_ws.row_dimensions[1].height = 32

                for col_idx, h in enumerate(headers, start=1):
                    c = new_ws.cell(row=1, column=col_idx, value=h)
                    c.font = font_header
                    c.fill = fill_header
                    c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
                    c.border = border_thin

                for row_idx, user_data in enumerate(usuarios_iniciais, start=2):
                    new_ws.row_dimensions[row_idx].height = 22
                    fill = fill_even if row_idx % 2 == 0 else fill_odd
                    for col_idx, val in enumerate(user_data, start=1):
                        c = new_ws.cell(row=row_idx, column=col_idx, value=val)
                        c.font = font_body
                        c.fill = fill
                        c.border = border_thin
                        col_name = headers[col_idx - 1]
                        if col_name in ["CPF", "Senha", "Status", "Data_Cadastro", "Ultimo_Acesso", "Setor_Orgao"]:
                            c.alignment = Alignment(horizontal="center", vertical="center")
                        else:
                            c.alignment = Alignment(horizontal="left", vertical="center")
                        if col_name in ["CPF", "Senha"]:
                            c.number_format = "@"

                for col in new_ws.columns:
                    col_letter = get_column_letter(col[0].column)
                    max_len = max(len(str(c.value or "")) for c in col)
                    new_ws.column_dimensions[col_letter].width = max(max_len + 5, 14)

                new_ws.auto_filter.ref = f"A1:I{len(usuarios_iniciais) + 1}"
                main_wb.save(main_p)
                print(f"Aba 'Usuarios' injetada em: {main_p}")
            except Exception as e:
                print(f"Erro ao injetar na planilha principal {main_p}: {e}")

if __name__ == "__main__":
    gerar_planilha_usuarios()
