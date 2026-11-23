import os
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.datavalidation import DataValidation

def criar_todas_as_planilhas():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    output_principal = os.path.join(base_dir, 'Planilha_Alimentacao_Dashboard_ElNino_SMJ.xlsx')
    output_dados = os.path.join(base_dir, 'dados', 'Planilha_Alimentacao_Dashboard_ElNino_SMJ.xlsx')
    output_apenas_educacao = os.path.join(base_dir, 'Planilha_Abas_Educacao_Novas.xlsx')
    output_usuarios = os.path.join(base_dir, 'Planilha_Usuarios_Controle_Acesso.xlsx')
    output_usuarios_dados = os.path.join(base_dir, 'dados', 'Planilha_Usuarios_Controle_Acesso.xlsx')

    # =========================================================================
    # 1. PLANILHA PRINCIPAL DO DASHBOARD (COM NOMES ATUALIZADOS DO GOOGLE DRIVE)
    # =========================================================================
    wb = openpyxl.Workbook()
    wb.remove(wb.active)

    dept_colors = {
        'Dren.': {'tab': '2563EB', 'header': '1E40AF'},
        'Urb_CaixasSecas': {'tab': 'D97706', 'header': 'B45309'},
        'Ass_Acoes': {'tab': '7C3AED', 'header': '6D28D9'},
        'Ass_Indicadores': {'tab': '7C3AED', 'header': '6D28D9'},
        'Ass_Estoque': {'tab': '7C3AED', 'header': '6D28D9'},
        'Vig_Acoes': {'tab': '0F766E', 'header': '0D9488'},
        'Vig_Casos': {'tab': 'BE185D', 'header': '9D174D'},
        'Vig_Indicadores': {'tab': '059669', 'header': '047857'},
        'Vig_Estoque': {'tab': '0F766E', 'header': '0D9488'},
        'Inc_Focos': {'tab': 'DC2626', 'header': 'B91C1C'},
        'Ab_Cesan': {'tab': 'D97706', 'header': 'B45309'},
        'Edu_Ocorrencias': {'tab': '1D4ED8', 'header': '1E3A8A'},
        'Edu_Indicadores': {'tab': '2563EB', 'header': '1E40AF'},
        'Edu_Planejamento': {'tab': '0284C7', 'header': '0369A1'},
        'Edu_Absenteismo': {'tab': '3B82F6', 'header': '1D4ED8'},
        'Env_Arborizacao': {'tab': '15803D', 'header': '166534'},
        'Env_Indicadores': {'tab': '16A34A', 'header': '15803D'},
        'Auxiliar_Listas': {'tab': '64748B', 'header': '334155'}
    }

    font_header = Font(name='Segoe UI', size=11, bold=True, color='FFFFFF')
    font_body = Font(name='Segoe UI', size=10)
    fill_stripe = PatternFill(start_color='F8FAFC', end_color='F8FAFC', fill_type='solid')

    thin_border = Border(
        left=Side(style='thin', color='CBD5E1'),
        right=Side(style='thin', color='CBD5E1'),
        top=Side(style='thin', color='CBD5E1'),
        bottom=Side(style='thin', color='CBD5E1')
    )

    # 1.1 ABA AUXILIAR_LISTAS
    ws_aux = wb.create_sheet(title='Auxiliar_Listas')
    ws_aux.sheet_properties.tabColor = dept_colors['Auxiliar_Listas']['tab']

    aux_data = {
        'Localidades_SMJ': [
            'Centro', 'Garrafão', 'Rio Possmoser', 'São Sebastião de Belém',
            'Caramuru', 'Alto Santa Maria', 'Vila Jetibá', 'Recreio',
            'São Luís', 'Alto Rio Possmoser', 'Córrego do Ouro'
        ],
        'Status_Geral': ['Concluído', 'Em Andamento', 'Planejado', 'Suspenso'],
        'Niveis_Alerta': ['Adequado', 'Normal', 'Atenção', 'Alerta', 'Crítico'],
        'Tipos_Intervencao': ['Manutenção', 'Construção', 'Desobstrução', 'Desassoreamento'],
        'Tipos_Acao_Social': ['Benefício Eventual', 'Acolhimento Provisório', 'Cesta Básica', 'Atualização CadÚnico', 'PAIF / Visita'],
        'Motivos_Ocorrencia': ['Alagamento', 'Deslizamento', 'Estiagem', 'Vulnerabilidade Geral', 'Enxurrada'],
        'Tipos_Acao_Vigilancia': ['Eliminação de Criadouros', 'Visita Casa a Casa', 'Nebulização Perifocal', 'LIRAa', 'Mutirão Pós-Chuva'],
        'Agravos_Saude': ['Dengue', 'Chikungunya', 'Zika'],
        'Origem_Registro_Fogo': ['SCBV', 'CBMES', 'SCBV (Bombeiros Voluntários)', 'CBMES (6º Batalhão)', 'Satélite (INPE/BDQueimadas)', 'Patrulha Municipal'],
        'Status_Combate_Fogo': ['Controlado/Extinto', 'Em Combate', 'Monitorado'],
        'Motivos_Educacao': [
            'Onda de Calor', 'Infiltração / Alagamento', 'Dano Estrutural',
            'Falta de Água', 'Destelhamento / Vento', 'Acesso Interrompido'
        ],
        'Categorias_Indicador_Edu': ['KPI', 'Complementar'],
        'Status_Onda_Calor': ['Dentro da média', 'Atenção', 'Onda de calor (>32°C)'],
        'Setores_Responsaveis_Edu': ['SEMED', 'Defesa Civil', 'SEMED / Obras', 'SEMED / Transporte', 'SEMUS', 'SEMAS'],
        'Risco_Arboreo': ['Elevado', 'Alto', 'Moderado', 'Baixo', 'Pendente de Avaliação'],
        'Intervencao_Arboreo': ['Poda de Redução de Copa', 'Poda de Limpeza', 'Supressão', 'Poda de Condução', 'Apenas Monitoramento'],
        'Fiacao_EDP': ['Contato Direto', 'Proximidade Crítica', 'Sem Conflito'],
        'Tipos_Servico_CaixasSecas': ['Abertura', 'Manutenção / Limpeza', 'Adequação de Enxurrada', 'Desobstrução'],
        'Equipes_Servicos_Urbanos': ['Equipe Serviços Urbanos 01', 'Equipe Serviços Urbanos 02', 'Patrulha Mecanizada SEMOSU', 'Equipe Obras / Caixas Secas'],
        'Unidades_Assistencia': ['CRAS I', 'CRAS II', 'CREAS', 'Geral', 'Central']
    }

    col_idx = 1
    for col_name, values in aux_data.items():
        c_hdr = ws_aux.cell(row=1, column=col_idx, value=col_name)
        c_hdr.font = font_header
        c_hdr.fill = PatternFill(start_color=dept_colors['Auxiliar_Listas']['header'], end_color=dept_colors['Auxiliar_Listas']['header'], fill_type='solid')
        c_hdr.alignment = Alignment(horizontal='center', vertical='center')
        c_hdr.border = thin_border
        for r_idx, v in enumerate(values, start=2):
            cell = ws_aux.cell(row=r_idx, column=col_idx, value=v)
            cell.font = font_body
            cell.border = thin_border
            cell.alignment = Alignment(horizontal='left', vertical='center')
        col_idx += 1

    ws_aux.views.sheetView[0].showGridLines = True
    ws_aux.freeze_panes = 'A2'
    ws_aux.auto_filter.ref = f"A1:{get_column_letter(len(aux_data))}20"
    for col in ws_aux.columns:
        max_len = max(len(str(cell.value or '')) for cell in col)
        col_letter = get_column_letter(col[0].column)
        ws_aux.column_dimensions[col_letter].width = max(max_len + 4, 16)

    # Fórmulas de validação
    val_localidade_formula = 'Auxiliar_Listas!$A$2:$A$20'
    val_status_formula = 'Auxiliar_Listas!$B$2:$B$10'
    val_niveis_formula = 'Auxiliar_Listas!$C$2:$C$10'
    val_intervencao_formula = 'Auxiliar_Listas!$D$2:$D$10'
    val_acao_social_formula = 'Auxiliar_Listas!$E$2:$E$10'
    val_motivo_formula = 'Auxiliar_Listas!$F$2:$F$10'
    val_acao_vigilancia_formula = 'Auxiliar_Listas!$G$2:$G$10'
    val_agravos_formula = 'Auxiliar_Listas!$H$2:$H$10'
    val_origem_fogo_formula = 'Auxiliar_Listas!$I$2:$I$10'
    val_status_fogo_formula = 'Auxiliar_Listas!$J$2:$J$10'
    val_motivo_edu_formula = 'Auxiliar_Listas!$K$2:$K$15'
    val_categoria_edu_formula = 'Auxiliar_Listas!$L$2:$L$10'
    val_status_onda_formula = 'Auxiliar_Listas!$M$2:$M$10'
    val_setor_edu_formula = 'Auxiliar_Listas!$N$2:$N$10'
    val_risco_arboreo_formula = 'Auxiliar_Listas!$O$2:$O$10'
    val_intervencao_arboreo_formula = 'Auxiliar_Listas!$P$2:$P$10'
    val_fiacao_edp_formula = 'Auxiliar_Listas!$Q$2:$Q$10'
    val_tipo_caixas_formula = 'Auxiliar_Listas!$R$2:$R$10'
    val_equipes_urb_formula = 'Auxiliar_Listas!$S$2:$S$10'
    val_unidades_as_formula = 'Auxiliar_Listas!$T$2:$T$10'

    sheets_config = [
        {
            'title': 'Dren.',
            'headers': ['Data', 'Localidade', 'Tipo_Intervencao', 'Descricao_Servico', 'Extensao_Metros', 'Status', 'Responsavel_Equipe'],
            'validations': [
                (val_localidade_formula, 'B'),
                (val_intervencao_formula, 'C'),
                (val_status_formula, 'F')
            ],
            'data': [
                ['10/08/2026', 'Centro', 'Manutenção', 'Limpeza de bocas de lobo e desobstrução de galerias pluviais', 320, 'Concluído', 'Equipe SEMOSU 01'],
                ['15/08/2026', 'Garrafão', 'Manutenção', 'Desassoreamento de canal lateral à margem da ES-080', 180, 'Concluído', 'Equipe SEMOSU 02'],
                ['20/08/2026', 'Rio Possmoser', 'Construção', 'Extensão de galeria pluvial em zona de histórico de alagamento', 90, 'Concluído', 'Equipe Obras'],
                ['25/08/2026', 'São Sebastião de Belém', 'Manutenção', 'Roçagem e limpeza de valetas e sarjetas rurais', 450, 'Concluído', 'Equipe SEMOSU 01'],
                ['01/09/2026', 'Alto Santa Maria', 'Construção', 'Implantação de caixa de contenção para controle de enxurrada', 60, 'Em Andamento', 'Equipe Obras'],
                ['05/09/2026', 'Caramuru', 'Manutenção', 'Desobstrução emergencial após chuvas de agosto', 210, 'Concluído', 'Equipe SEMOSU 02'],
                ['08/09/2026', 'Centro', 'Construção', 'Ampliação de galeria pluvial na Rua Dez de Agosto', 130, 'Em Andamento', 'Equipe Obras']
            ]
        },
        {
            'title': 'Urb_CaixasSecas',
            'headers': ['Data', 'Localidade', 'Estrada_Trecho', 'Tipo_Servico', 'Quantidade_Caixas', 'Volume_Retencao_m3', 'Status', 'Equipe_Responsavel', 'Observacoes'],
            'validations': [
                (val_localidade_formula, 'B'),
                (val_tipo_caixas_formula, 'D'),
                (val_status_formula, 'G'),
                (val_equipes_urb_formula, 'H')
            ],
            'data': [
                ['03/08/2026', 'Garrafão', 'Estrada Garrafão x Recreio - Km 4', 'Abertura', 12, 240, 'Concluído', 'Patrulha Mecanizada SEMOSU', 'Abertura de caixas secas em curva de nível para retenção pluvial'],
                ['07/08/2026', 'Rio Possmoser', 'Acesso Córrego Albert - Km 2', 'Manutenção / Limpeza', 18, 360, 'Concluído', 'Equipe Serviços Urbanos 01', 'Desassoreamento e limpeza mecanizada de caixas secas antes das chuvas'],
                ['14/08/2026', 'São Sebastião de Belém', 'Estrada Principal Belém - Km 6', 'Abertura', 15, 300, 'Concluído', 'Patrulha Mecanizada SEMOSU', 'Novas bacias de contenção para proteção do leito viário'],
                ['21/08/2026', 'Alto Santa Maria', 'Estrada Alto Santa Maria x Garrafão', 'Manutenção / Limpeza', 22, 440, 'Concluído', 'Equipe Serviços Urbanos 02', 'Limpeza preventiva e remoção de sedimentos acumulados'],
                ['28/08/2026', 'Caramuru', 'Estrada Geral do Caramuru - Km 3.5', 'Abertura', 10, 200, 'Em Andamento', 'Patrulha Mecanizada SEMOSU', 'Abertura de caixas conjugadas com bueiros de transposição'],
                ['04/09/2026', 'Centro', 'Estrada de Contorno Periurbano', 'Manutenção / Limpeza', 14, 280, 'Concluído', 'Equipe Serviços Urbanos 01', 'Desobstrução e ampliação de capacidade de amortecimento'],
                ['11/09/2026', 'São Luís', 'Trecho São Luís x Alto Rio Possmoser', 'Abertura', 16, 320, 'Em Andamento', 'Patrulha Mecanizada SEMOSU', 'Novos pontos de infiltração e recarga de lençol freático'],
                ['18/09/2026', 'Vila Jetibá', 'Estrada Vicinal Vila Jetibá - Km 1.8', 'Manutenção / Limpeza', 8, 160, 'Planejado', 'Equipe Serviços Urbanos 02', 'Manutenção programada no cronograma quinzenal']
            ]
        },
        {
            'title': 'Ass_Acoes',
            'headers': ['Data', 'Localidade', 'Tipo_Acao', 'Motivo_Ocorrencia', 'Familias_Atendidas', 'Pessoas_Atendidas', 'Status', 'Observacao'],
            'validations': [
                (val_localidade_formula, 'B'),
                (val_acao_social_formula, 'C'),
                (val_motivo_formula, 'D'),
                (val_status_formula, 'G')
            ],
            'data': [
                ['22/08/2026', 'Rio Possmoser', 'Acolhimento Provisório', 'Alagamento', 6, 24, 'Em Andamento', 'Famílias alojadas em abrigo temporário'],
                ['25/08/2026', 'Centro', 'Benefício Eventual', 'Vulnerabilidade Geral', 14, 42, 'Concluído', 'Auxílio funeral e vulnerabilidade eventual'],
                ['27/08/2026', 'Garrafão', 'Atualização CadÚnico', 'Vulnerabilidade Geral', 22, 66, 'Concluído', 'Mutirão volante CadÚnico'],
                ['01/09/2026', 'Alto Santa Maria', 'Cesta Básica', 'Estiagem', 31, 110, 'Concluído', 'Entrega a famílias de pequenos agricultores'],
                ['04/09/2026', 'São Sebastião de Belém', 'PAIF / Visita', 'Vulnerabilidade Geral', 5, 18, 'Em Andamento', 'Acompanhamento sistemático CRAS'],
                ['08/09/2026', 'Caramuru', 'PAIF / Visita', 'Estiagem', 0, 0, 'Planejado', 'Agendado para próxima semana']
            ]
        },
        {
            'title': 'Ass_Indicadores',
            'headers': ['Indicador', 'Valor', 'Unidade_Periodo', 'Categoria', 'Data_Atualizacao'],
            'validations': [],
            'data': [
                ['Família Incluída no ultimo mês no Cadastro Único', 25, 'Famílias', 'CadÚnico', '13/10/2026'],
                ['Número de Família em situação de extrema pobreza no Cadastro único', 1420, 'Famílias', 'CadÚnico', '13/10/2026'],
                ['CRAS I - Famílias referenciadas', 7622, 'Famílias', 'CRAS I', '13/10/2026'],
                ['CRAS I - Acompanhadas pelo PAIF', 137, 'Famílias', 'CRAS I', '13/10/2026'],
                ['CRAS II - Famílias referenciadas', 2425, 'Famílias', 'CRAS II', '13/10/2026'],
                ['CRAS II - Acompanhadas pelo PAIF', 33, 'Famílias', 'CRAS II', '13/10/2026'],
                ['CREAS - Famílias em Acompanhamento PAEFI', 143, 'Famílias', 'CREAS', '13/10/2026'],
                ['CREAS - Pessoas em situação de rua abordadas no último mês', 23, 'Pessoas', 'CREAS', '13/10/2026'],
                ['Total Famílias Referenciadas (CRAS I + II)', 10047, 'Famílias', 'Rede CRAS', '13/10/2026'],
                ['Total Famílias Acompanhadas PAIF (CRAS I + II)', 170, 'Famílias', 'Rede CRAS', '13/10/2026'],
                ['Total Acompanhamentos Familiares (PAIF + PAEFI)', 313, 'Famílias', 'Rede Socioassistencial', '13/10/2026'],
                ['Pessoas em Acolhimento Provisório', 18, 'Pessoas', 'Abrigamento', '13/10/2026'],
                ['Benefícios Eventuais Concedidos (mês)', 88, 'Benefícios', 'Concessões', '13/10/2026'],
                ['Atendimentos CRAS/CREAS (semana)', 313, 'Atendimentos', 'Rede CRAS/CREAS', '13/10/2026']
            ]
        },
        {
            'title': 'Ass_Estoque',
            'headers': ['Item', 'Unidade', 'Quantidade_Atual', 'Unidade_Medida', 'Cobertura_Estimada', 'Nivel_Status', 'Data_Atualizacao'],
            'validations': [
                (val_unidades_as_formula, 'B'),
                (val_niveis_formula, 'F')
            ],
            'data': [
                # CRAS I
                ['Cesta Básica', 'CRAS I', 73, 'Unidades', '73 famílias vulneráveis', 'Adequado', '13/10/2026'],
                ['Kit Limpeza', 'CRAS I', 72, 'Kits', '72 famílias', 'Adequado', '13/10/2026'],
                ['Colchão Solteiro', 'CRAS I', 6, 'Unidades', '6 pessoas', 'Atenção', '13/10/2026'],
                ['Colchão Casal', 'CRAS I', 5, 'Unidades', '5 famílias/casais', 'Atenção', '13/10/2026'],
                ['Mantas', 'CRAS I', 53, 'Unidades', '53 pessoas', 'Adequado', '13/10/2026'],
                ['Filtro', 'CRAS I', 17, 'Unidades', '17 famílias', 'Adequado', '13/10/2026'],
                ['Passagem', 'CRAS I', 2, 'Passagens', '2 concessões eventuais', 'Atenção', '13/10/2026'],

                # CRAS II
                ['Cesta Básica', 'CRAS II', 12, 'Unidades', '12 famílias vulneráveis', 'Atenção', '13/10/2026'],
                ['Kit Limpeza', 'CRAS II', 12, 'Kits', '12 famílias', 'Atenção', '13/10/2026'],
                ['Mantas', 'CRAS II', 2, 'Unidades', '2 pessoas', 'Crítico', '13/10/2026'],
                ['Filtro', 'CRAS II', 1, 'Unidades', '1 família', 'Crítico', '13/10/2026'],

                # CREAS
                ['Cesta Básica', 'CREAS', 3, 'Unidades', '3 famílias vulneráveis', 'Atenção', '13/10/2026'],
                ['Kit Limpeza', 'CREAS', 2, 'Kits', '2 famílias', 'Atenção', '13/10/2026'],
                ['Filtro', 'CREAS', 1, 'Unidades', '1 família', 'Crítico', '13/10/2026'],
                ['Colchão Casal', 'CREAS', 1, 'Unidades', '1 família', 'Crítico', '13/10/2026'],
                ['Kit Higiene', 'CREAS', 1, 'Kits', '1 pessoa/família em trânsito', 'Crítico', '13/10/2026'],
                ['Passagem', 'CREAS', 3, 'Passagens', '3 passagens de trânsito', 'Atenção', '13/10/2026']
            ]
        },
        {
            'title': 'Vig_Acoes',
            'headers': ['Data', 'Localidade', 'Tipo_Acao', 'Focos_Eliminados', 'Imoveis_Trabalhados', 'Status'],
            'validations': [
                (val_localidade_formula, 'B'),
                (val_acao_vigilancia_formula, 'C'),
                (val_status_formula, 'F')
            ],
            'data': [
                ['25/08/2026', 'Centro', 'Eliminação de Criadouros', 34, 120, 'Concluído'],
                ['27/08/2026', 'Garrafão', 'LIRAa', 28, 95, 'Concluído'],
                ['01/09/2026', 'Rio Possmoser', 'Nebulização Perifocal', 19, 60, 'Em Andamento'],
                ['04/09/2026', 'São Sebastião de Belém', 'Visita Casa a Casa', 41, 150, 'Concluído'],
                ['08/09/2026', 'Alto Santa Maria', 'Mutirão Pós-Chuva', 27, 85, 'Em Andamento'],
                ['15/09/2026', 'Caramuru', 'LIRAa', 0, 0, 'Planejado']
            ]
        },
        {
            'title': 'Vig_Casos',
            'headers': ['Ano', 'Semana_Epi', 'Localidade', 'Agravo', 'Casos_Notificados', 'Casos_Confirmados', 'Indice_LIRAa_Pct'],
            'validations': [
                (val_localidade_formula, 'C'),
                (val_agravos_formula, 'D')
            ],
            'data': [
                [2026, 'SE33', 'Centro', 'Dengue', 5, 3, 0.6],
                [2026, 'SE33', 'Garrafão', 'Dengue', 4, 2, 1.8],
                [2026, 'SE34', 'Centro', 'Dengue', 7, 4, 0.6],
                [2026, 'SE34', 'Rio Possmoser', 'Dengue', 3, 2, 3.4],
                [2026, 'SE35', 'Centro', 'Dengue', 8, 6, 0.6],
                [2026, 'SE35', 'Garrafão', 'Dengue', 6, 4, 1.8],
                [2026, 'SE36', 'Centro', 'Dengue', 11, 8, 0.6],
                [2026, 'SE36', 'Garrafão', 'Dengue', 7, 5, 1.8],
                [2026, 'SE36', 'Rio Possmoser', 'Dengue', 6, 4, 3.4],
                [2026, 'SE36', 'São Sebastião de Belém', 'Dengue', 4, 3, 2.1],
                [2026, 'SE36', 'Alto Santa Maria', 'Dengue', 2, 1, 4.6],
                [2026, 'SE36', 'Caramuru', 'Dengue', 1, 1, 1.2]
            ]
        },
        {
            'title': 'Vig_Indicadores',
            'headers': ['Indicador', 'Valor', 'Unidade_Periodo', 'Categoria', 'Data_Atualizacao'],
            'validations': [],
            'data': [
                ['Índice LIRAa Municipal', '2,7%', '%', 'Infestação Vetorial', '08/09/2026'],
                ['Focos Eliminados (mês)', 184, 'Focos', 'Controle Vetorial', '08/09/2026'],
                ['Cobertura de Visitas — Agentes', '76%', '%', 'Cobertura de Campo', '08/09/2026'],
                ['Casos de Leptospirose (mês)', 4, 'Casos', 'Agravos Correlatos', '08/09/2026'],
                ['Atend. Doenças Diarreicas Agudas (semana)', 17, 'Atendimentos', 'Agravos Correlatos', '08/09/2026'],
                ['Atend. Desidratação / Exaustão Térmica (semana)', 9, 'Atendimentos', 'Onda de Calor', '08/09/2026']
            ]
        },
        {
            'title': 'Vig_Estoque',
            'headers': ['Item', 'Quantidade_Atual', 'Unidade_Medida', 'Cobertura_Estimada', 'Nivel_Status', 'Data_Atualizacao'],
            'validations': [
                (val_niveis_formula, 'E')
            ],
            'data': [
                ['Larvicida (Aedes)', 150, 'Frascos', 'Cobertura estimada: 5 semanas', 'Adequado', '08/09/2026'],
                ['Sais de Reidratação Oral', 300, 'Envelopes', 'Cobertura estimada: 3 semanas', 'Atenção', '08/09/2026'],
                ['Hipoclorito de Sódio', 400, 'Litros', 'Cobertura estimada: 6 semanas', 'Adequado', '08/09/2026'],
                ['Testes Diagnósticos (Dengue)', 40, 'Testes', 'Cobertura estimada: 2 semanas', 'Crítico', '08/09/2026'],
                ['EPIs — Equipes de Campo', 60, 'Kits', 'Cobertura estimada: 8 semanas', 'Adequado', '08/09/2026']
            ]
        },
        {
            'title': 'Inc_Focos',
            'headers': ['Data_Ocorrencia', 'Localidade', 'Origem_Registro', 'Area_Estimada_Ha', 'Status_Fogo', 'Risco_Meteorologico', 'Observacoes'],
            'validations': [
                (val_localidade_formula, 'B'),
                (val_origem_fogo_formula, 'C'),
                (val_status_fogo_formula, 'E'),
                (val_niveis_formula, 'F')
            ],
            'data': [
                ['05/08/2026', 'Garrafão', 'SCBV', 4.5, 'Controlado/Extinto', 'Alto', 'Fogo em encosta de pastagem seca combatido por Bombeiros Voluntários (SCBV)'],
                ['12/08/2026', 'Rio Possmoser', 'CBMES', 2.0, 'Controlado/Extinto', 'Atenção', 'Vegetação rasteira combatida pelo CBMES 6º Batalhão'],
                ['22/08/2026', 'São Sebastião de Belém', 'SCBV', 1.2, 'Controlado/Extinto', 'Atenção', 'Queima em vegetação debelada por Bombeiros Voluntários'],
                ['28/08/2026', 'Caramuru', 'CBMES', 3.8, 'Controlado/Extinto', 'Alto', 'Foco de calor em topo de morro combatido pelo CBMES 6º Batalhão'],
                ['04/09/2026', 'Alto Santa Maria', 'SCBV', 0.8, 'Controlado/Extinto', 'Normal', 'Foco debelado rapidamente por Bombeiros Voluntários (SCBV)'],
                ['10/09/2026', 'Centro', 'CBMES', 1.5, 'Controlado/Extinto', 'Atenção', 'Princípio de incêndio florestal combatido pelo CBMES 6º Batalhão'],
                ['18/09/2026', 'Vila Jetibá', 'SCBV', 2.3, 'Controlado/Extinto', 'Alto', 'Atendimento rápido por Bombeiros Voluntários (SCBV) em área de mata'],
                ['25/09/2026', 'Recreio', 'CBMES', 1.9, 'Controlado/Extinto', 'Atenção', 'Combate a foco em encosta pelo 6º Batalhão CBMES']
            ]
        },
        {
            'title': 'Ab_Cesan',
            'headers': ['Data', 'Manancial_Ponto', 'Status_Abastecimento', 'Vazao_L_s', 'Numero_Boletim_CICC', 'Observacoes'],
            'validations': [
                (val_niveis_formula, 'C')
            ],
            'data': [
                ['27/07/2026', 'Alto Rio Possmoser / Córrego Albert', 'Normal', 65.0, '2º Boletim CICC', 'Captação operando em capacidade normal'],
                ['27/07/2026', 'Rio Santa Maria da Vitória', 'Normal', 80.0, '2º Boletim CICC', 'Operação normal'],
                ['27/07/2026', 'Rio São Sebastião de Cima', 'Normal', 55.0, '2º Boletim CICC', 'Operação normal'],
                ['03/08/2026', 'Alto Rio Possmoser / Córrego Albert', 'Normal', 60.5, '3º Boletim CICC', 'Vazão dentro da média histórica'],
                ['03/08/2026', 'Rio Santa Maria da Vitória', 'Normal', 78.0, '3º Boletim CICC', 'Sem alterações'],
                ['03/08/2026', 'Rio São Sebastião de Cima', 'Normal', 54.0, '3º Boletim CICC', 'Sem alterações'],
                ['10/08/2026', 'Alto Rio Possmoser / Córrego Albert', 'Atenção', 48.0, '4º Boletim CICC', 'Redução da vazão de estiagem'],
                ['10/08/2026', 'Rio Santa Maria da Vitória', 'Normal', 75.0, '4º Boletim CICC', 'Nível estável'],
                ['10/08/2026', 'Rio São Sebastião de Cima', 'Normal', 50.0, '4º Boletim CICC', 'Nível estável'],
                ['17/08/2026', 'Alto Rio Possmoser / Córrego Albert', 'Crítico', 30.0, '5º Boletim CICC', 'Captação muito baixa'],
                ['17/08/2026', 'Rio Santa Maria da Vitória', 'Atenção', 60.0, '5º Boletim CICC', 'Redução perceptível'],
                ['17/08/2026', 'Rio São Sebastião de Cima', 'Normal', 48.0, '5º Boletim CICC', 'Operação normal'],
                ['25/08/2026', 'Alto Rio Possmoser / Córrego Albert', 'Crítico', 28.0, '6º Boletim CICC', 'Fase crítica prolongada'],
                ['25/08/2026', 'Rio Santa Maria da Vitória', 'Atenção', 58.0, '6º Boletim CICC', 'Mantém atenção'],
                ['25/08/2026', 'Rio São Sebastião de Cima', 'Atenção', 45.0, '6º Boletim CICC', 'Redução contínua'],
                ['31/08/2026', 'Alto Rio Possmoser / Córrego Albert', 'Atenção', 41.0, '7º Boletim CICC', 'Leve recuperação'],
                ['31/08/2026', 'Rio Santa Maria da Vitória', 'Normal', 65.0, '7º Boletim CICC', 'Normalizado'],
                ['31/08/2026', 'Rio São Sebastião de Cima', 'Normal', 50.0, '7º Boletim CICC', 'Normalizado']
            ]
        },
        {
            'title': 'Edu_Ocorrencias',
            'headers': ['Data', 'Escola_Localidade', 'Motivo', 'Acao_Adotada', 'Status', 'Observacoes'],
            'validations': [
                (val_localidade_formula, 'B'),
                (val_motivo_edu_formula, 'C'),
                (val_status_formula, 'E')
            ],
            'data': [
                ['20/08/2026', 'Centro', 'Onda de Calor', 'Adequação de Horário e Climatização Emergencial', 'Concluído', 'Ajuste de turno e ventilação móvel'],
                ['24/08/2026', 'Garrafão', 'Falta de Água', 'Fornecimento de Caminhão Pipa e Limpeza de Reservatório', 'Concluído', 'Abastecimento emergencial SEMAS/Defesa Civil'],
                ['02/09/2026', 'Rio Possmoser', 'Infiltração / Alagamento', 'Desobstrução de Calha e Impermeabilização Parcial', 'Em Andamento', 'Equipe de manutenção em atuação'],
                ['05/09/2026', 'São Sebastião de Belém', 'Dano Estrutural', 'Vistoria Técnica da Defesa Civil e Escoramento Preventivo', 'Concluído', 'Sem risco iminente, reparo programado'],
                ['08/09/2026', 'Caramuru', 'Destelhamento / Vento', 'Substituição de Telhas e Fixação de Estrutura Metálica', 'Planejado', 'Agendado após término do período chuvoso']
            ]
        },
        {
            'title': 'Edu_Indicadores',
            'headers': ['Categoria', 'Item', 'Valor', 'Unidade_Meta', 'Status'],
            'validations': [
                (val_categoria_edu_formula, 'A'),
                (val_niveis_formula, 'E')
            ],
            'data': [
                ['KPI', 'Escolas em Área de Risco', 9, 'Escolas', 'Alerta'],
                ['KPI', 'Escolas Sem Climatização Adequada', 14, 'Escolas', 'Atenção'],
                ['KPI', 'Dias de Aula Suspensos no Mês', 3, 'Dias', 'Normal'],
                ['KPI', 'Absenteísmo em Onda de Calor', '8.4%', '%', 'Atenção'],
                ['Complementar', 'Escolas com Reservatório Insuficiente', 6, 'Escolas', 'Atenção'],
                ['Complementar', 'Estudantes em Ensino Remoto/Híbrido', 340, 'Alunos', 'Normal'],
                ['Complementar', 'Escolas em Uso como Abrigo', 1, 'Escolas', 'Adequado']
            ]
        },
        {
            'title': 'Edu_Planejamento',
            'headers': ['Item_ID', 'Acao_Planejada', 'Detalhamento_Descricao', 'Responsavel_Setor', 'Prazo_Meta', 'Status', 'Observacoes'],
            'validations': [
                (val_setor_edu_formula, 'D'),
                (val_status_formula, 'F')
            ],
            'data': [
                ['4.6.1', 'Instalação de climatizadores de ar e bebedouros industriais', 'Prioridade para creches e escolas de tempo integral', 'SEMED / Obras', '30/10/2026', 'Em Andamento', 'Em fase de aquisição e instalação nos blocos'],
                ['4.6.2', 'Capacitação das equipes escolares para protocolo de ondas de calor', 'Treinamento conjunto Defesa Civil e SEMED', 'Defesa Civil', '15/09/2026', 'Concluído', '4 turmas capacitadas com diretrizes clínicas'],
                ['4.6.3', 'Plano de contingência de transporte escolar em caso de enxurrada', 'Mapeamento de rotas alternativas rurais', 'SEMED / Transporte', '20/10/2026', 'Planejado', 'Mapeamento preliminar de vias rurais concluído'],
                ['4.6.4', 'Reforço preventivo de calhas e escoamento em unidades vulneráveis', 'Desobstrução e ampliação de calhas pluviais nas escolas de encosta', 'SEMED / Obras', '10/11/2026', 'Planejado', 'Aguardando cronograma da equipe SEMOSU']
            ]
        },
        {
            'title': 'Edu_Absenteismo',
            'headers': ['Semana', 'Taxa_Absenteismo_Pct', 'Temp_Max_Media', 'Status_Onda_Calor'],
            'validations': [
                (val_status_onda_formula, 'D')
            ],
            'data': [
                ['SE29', 4.1, 28.5, 'Dentro da média'],
                ['SE30', 4.6, 29.2, 'Dentro da média'],
                ['SE31', 5.0, 31.0, 'Atenção'],
                ['SE32', 4.8, 30.1, 'Dentro da média'],
                ['SE33', 6.2, 32.5, 'Onda de calor (>32°C)'],
                ['SE34', 7.5, 34.2, 'Onda de calor (>32°C)'],
                ['SE35', 7.9, 35.0, 'Onda de calor (>32°C)'],
                ['SE36', 8.4, 36.1, 'Onda de calor (>32°C)']
            ]
        },
        {
            'title': 'Env_Arborizacao',
            'headers': ['Tombamento', 'Especie', 'Localidade_Logradouro', 'Coordenadas_UTM', 'Classe_Risco', 'Intervencao_Recomendada', 'Interferencia_EDP', 'Prioridade_Prazo', 'Status_Execucao', 'Data_Vistoria'],
            'validations': [
                (val_localidade_formula, 'C'),
                (val_risco_arboreo_formula, 'E'),
                (val_intervencao_arboreo_formula, 'F'),
                (val_fiacao_edp_formula, 'G'),
                (val_status_formula, 'I')
            ],
            'data': [
                ['CAR-006', 'Espatodea (Spathodea campanulata)', 'Centro urbano', 'E 324698 / N 7776756', 'Elevado', 'Supressão', 'Contato Direto', 'Imediato (P1)', 'Em Andamento', '10/09/2026'],
                ['SED-362', 'Sibipiruna (Caesalpinia pluviosa)', 'Av. Frederico Grulke - Centro', 'E 317342 / N 7785907', 'Alto', 'Supressão', 'Proximidade Crítica', 'Duas primeiras semanas (P2)', 'Em Andamento', '12/09/2026'],
                ['CAR-008', 'Sibipiruna (Caesalpinia pluviosa)', 'Centro urbano', 'E 324703 / N 7776770', 'Alto', 'Poda de Redução de Copa', 'Contato Direto', 'Duas primeiras semanas (P2)', 'Em Andamento', '12/09/2026'],
                ['POS-014', 'Oiti (Licania tomentosa)', 'Rio Possmoser', 'E 321150 / N 7781200', 'Moderado', 'Poda de Limpeza', 'Proximidade Crítica', 'Programado (P3)', 'Planejado', '15/09/2026'],
                ['GAR-022', 'Flamboyant (Delonix regia)', 'Garrafão', 'E 312400 / N 7790100', 'Moderado', 'Poda de Condução', 'Sem Conflito', 'Programado (P3)', 'Planejado', '18/09/2026'],
                ['STB-005', 'Ipê Amarelo (Handroanthus chrysotrichus)', 'São Sebastião de Belém', 'E 329800 / N 7771500', 'Baixo', 'Apenas Monitoramento', 'Sem Conflito', 'Programado (P4)', 'Concluído', '20/09/2026']
            ]
        },
        {
            'title': 'Env_Indicadores',
            'headers': ['Indicador', 'Valor', 'Unidade_Medida', 'Categoria', 'Observacoes'],
            'validations': [],
            'data': [
                ['Árvores Inventariadas Total', 720, 'Exemplares', 'KPI Geral', 'Total de exemplares catalogados no município'],
                ['Árvores Ativas Inventariadas', 666, 'Exemplares', 'KPI Geral', 'Exemplares mantidos em acompanhamento'],
                ['Supressões Históricas', 54, 'Exemplares', 'KPI Geral', 'Árvores removidas em ações preventivas/emergenciais'],
                ['Intervenções Programadas (2026/2027)', 198, 'Intervenções', 'Cronograma', 'Plano preventivo de poda e manejo'],
                ['Risco Elevado / Alto (Prioritários)', 3, 'Exemplares', 'Risco', 'Atendimento de emergência SECMAM / Defesa Civil'],
                ['Conflito com Redes EDP', 129, 'Exemplares', 'Interferência', '92 com contato direto e 37 com proximidade crítica']
            ]
        }
    ]

    for cfg in sheets_config:
        ws = wb.create_sheet(title=cfg['title'])
        cfg_dept = dept_colors.get(cfg['title'], {'tab': '1E3A8A', 'header': '1E3A8A'})
        ws.sheet_properties.tabColor = cfg_dept['tab']
        ws.views.sheetView[0].showGridLines = True
        ws.freeze_panes = 'A2'

        ws.row_dimensions[1].height = 28
        fill_hdr = PatternFill(start_color=cfg_dept['header'], end_color=cfg_dept['header'], fill_type='solid')
        for col_i, h in enumerate(cfg['headers'], start=1):
            c = ws.cell(row=1, column=col_i, value=h)
            c.font = font_header
            c.fill = fill_hdr
            c.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
            c.border = thin_border

        for r_i, row_data in enumerate(cfg['data'], start=2):
            ws.row_dimensions[r_i].height = 20
            use_stripe = (r_i % 2 == 0)
            for col_i, val in enumerate(row_data, start=1):
                c = ws.cell(row=r_i, column=col_i, value=val)
                c.font = font_body
                if use_stripe:
                    c.fill = fill_stripe
                c.border = thin_border
                
                col_name = cfg['headers'][col_i - 1].lower()
                if isinstance(val, (int, float)):
                    c.alignment = Alignment(horizontal='right', vertical='center')
                elif 'data' in col_name or 'semana' in col_name or 'status' in col_name or 'item_id' in col_name:
                    c.alignment = Alignment(horizontal='center', vertical='center')
                else:
                    c.alignment = Alignment(horizontal='left', vertical='center')

        last_col_letter = get_column_letter(len(cfg['headers']))
        last_row = max(len(cfg['data']) + 1, 100)
        ws.auto_filter.ref = f"A1:{last_col_letter}{last_row}"

        for formula, col_letter in cfg['validations']:
            dv = DataValidation(type='list', formula1=formula, allow_blank=True)
            ws.add_data_validation(dv)
            dv.add(f'{col_letter}2:{col_letter}500')

        for col in ws.columns:
            max_len = 0
            col_letter = get_column_letter(col[0].column)
            for cell in col:
                val_str = str(cell.value or '')
                if len(val_str) > max_len:
                    max_len = len(val_str)
            ws.column_dimensions[col_letter].width = max(max_len + 5, 16)

    try:
        wb.save(output_principal)
        print(f"Planilha principal atualizada: {output_principal}")
    except Exception as err_save:
        print(f"Aviso ao salvar {output_principal} (arquivo em uso pelo Excel): {err_save}")
    os.makedirs(os.path.dirname(output_dados), exist_ok=True)
    wb.save(output_dados)
    print(f"Planilha de contingência atualizada: {output_dados}")

    # =========================================================================
    # 2. PLANILHA ISOLADA DE EDUCAÇÃO (Abas Novas + Planejamento 4.6)
    # =========================================================================
    wb_edu = openpyxl.Workbook()
    wb_edu.remove(wb_edu.active)

    ws_aux_edu = wb_edu.create_sheet(title='Auxiliar_Listas')
    ws_aux_edu.sheet_properties.tabColor = dept_colors['Auxiliar_Listas']['tab']
    for row in ws_aux.iter_rows(values_only=False):
        for cell in row:
            nc = ws_aux_edu.cell(row=cell.row, column=cell.column, value=cell.value)
            if cell.has_style:
                nc.font = Font(name=cell.font.name, size=cell.font.size, bold=cell.font.bold, color=cell.font.color)
                nc.fill = PatternFill(fill_type=cell.fill.fill_type, start_color=cell.fill.start_color, end_color=cell.fill.end_color)
                nc.alignment = Alignment(horizontal=cell.alignment.horizontal, vertical=cell.alignment.vertical)
                nc.border = thin_border
    ws_aux_edu.views.sheetView[0].showGridLines = True
    ws_aux_edu.freeze_panes = 'A2'
    ws_aux_edu.auto_filter.ref = f"A1:{get_column_letter(len(aux_data))}20"
    for col in ws_aux_edu.columns:
        max_len = max(len(str(cell.value or '')) for cell in col)
        col_letter = get_column_letter(col[0].column)
        ws_aux_edu.column_dimensions[col_letter].width = max(max_len + 4, 16)

    edu_titles = ['Edu_Indicadores', 'Edu_Planejamento', 'Edu_Ocorrencias', 'Edu_Absenteismo']
    for cfg in [c for c in sheets_config if c['title'] in edu_titles]:
        ws_e = wb_edu.create_sheet(title=cfg['title'])
        cfg_dept = dept_colors.get(cfg['title'], {'tab': '1E3A8A', 'header': '1E3A8A'})
        ws_e.sheet_properties.tabColor = cfg_dept['tab']
        ws_e.views.sheetView[0].showGridLines = True
        ws_e.freeze_panes = 'A2'
        ws_e.row_dimensions[1].height = 28

        fill_hdr = PatternFill(start_color=cfg_dept['header'], end_color=cfg_dept['header'], fill_type='solid')
        for col_i, h in enumerate(cfg['headers'], start=1):
            c = ws_e.cell(row=1, column=col_i, value=h)
            c.font = font_header
            c.fill = fill_hdr
            c.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
            c.border = thin_border

        for r_i, row_data in enumerate(cfg['data'], start=2):
            ws_e.row_dimensions[r_i].height = 20
            use_stripe = (r_i % 2 == 0)
            for col_i, val in enumerate(row_data, start=1):
                c = ws_e.cell(row=r_i, column=col_i, value=val)
                c.font = font_body
                if use_stripe:
                    c.fill = fill_stripe
                c.border = thin_border
                col_name = cfg['headers'][col_i - 1].lower()
                if isinstance(val, (int, float)):
                    c.alignment = Alignment(horizontal='right', vertical='center')
                elif 'data' in col_name or 'semana' in col_name or 'status' in col_name or 'item_id' in col_name:
                    c.alignment = Alignment(horizontal='center', vertical='center')
                else:
                    c.alignment = Alignment(horizontal='left', vertical='center')

        last_col_letter = get_column_letter(len(cfg['headers']))
        last_row = max(len(cfg['data']) + 1, 100)
        ws_e.auto_filter.ref = f"A1:{last_col_letter}{last_row}"

        for formula, col_letter in cfg['validations']:
            dv = DataValidation(type='list', formula1=formula, allow_blank=True)
            ws_e.add_data_validation(dv)
            dv.add(f'{col_letter}2:{col_letter}500')

        for col in ws_e.columns:
            max_len = 0
            col_letter = get_column_letter(col[0].column)
            for cell in col:
                val_str = str(cell.value or '')
                if len(val_str) > max_len:
                    max_len = len(val_str)
            ws_e.column_dimensions[col_letter].width = max(max_len + 5, 16)

    wb_edu.save(output_apenas_educacao)
    print(f"Planilha exclusiva de Educação atualizada: {output_apenas_educacao}")

    # =========================================================================
    # 2.B PLANILHA ISOLADA DE MEIO AMBIENTE (SECMAM)
    # =========================================================================
    output_apenas_secmam = os.path.join(base_dir, 'Planilha_Abas_MeioAmbiente_Novas.xlsx')
    wb_env = openpyxl.Workbook()
    wb_env.remove(wb_env.active)

    ws_aux_env = wb_env.create_sheet(title='Auxiliar_Listas')
    ws_aux_env.sheet_properties.tabColor = dept_colors['Auxiliar_Listas']['tab']
    for row in ws_aux.iter_rows(values_only=False):
        for cell in row:
            nc = ws_aux_env.cell(row=cell.row, column=cell.column, value=cell.value)
            if cell.has_style:
                nc.font = Font(name=cell.font.name, size=cell.font.size, bold=cell.font.bold, color=cell.font.color)
                nc.fill = PatternFill(fill_type=cell.fill.fill_type, start_color=cell.fill.start_color, end_color=cell.fill.end_color)
                nc.alignment = Alignment(horizontal=cell.alignment.horizontal, vertical=cell.alignment.vertical)
                nc.border = thin_border
    ws_aux_env.views.sheetView[0].showGridLines = True
    ws_aux_env.freeze_panes = 'A2'
    ws_aux_env.auto_filter.ref = f"A1:{get_column_letter(len(aux_data))}20"
    for col in ws_aux_env.columns:
        max_len = max(len(str(cell.value or '')) for cell in col)
        col_letter = get_column_letter(col[0].column)
        ws_aux_env.column_dimensions[col_letter].width = max(max_len + 4, 16)

    env_titles = ['Env_Arborizacao', 'Env_Indicadores']
    for cfg in [c for c in sheets_config if c['title'] in env_titles]:
        ws_ev = wb_env.create_sheet(title=cfg['title'])
        cfg_dept = dept_colors.get(cfg['title'], {'tab': '15803D', 'header': '15803D'})
        ws_ev.sheet_properties.tabColor = cfg_dept['tab']
        ws_ev.views.sheetView[0].showGridLines = True
        ws_ev.freeze_panes = 'A2'
        ws_ev.row_dimensions[1].height = 28

        fill_hdr = PatternFill(start_color=cfg_dept['header'], end_color=cfg_dept['header'], fill_type='solid')
        for col_i, h in enumerate(cfg['headers'], start=1):
            c = ws_ev.cell(row=1, column=col_i, value=h)
            c.font = font_header
            c.fill = fill_hdr
            c.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
            c.border = thin_border

        for r_i, row_data in enumerate(cfg['data'], start=2):
            ws_ev.row_dimensions[r_i].height = 20
            use_stripe = (r_i % 2 == 0)
            for col_i, val in enumerate(row_data, start=1):
                c = ws_ev.cell(row=r_i, column=col_i, value=val)
                c.font = font_body
                if use_stripe:
                    c.fill = fill_stripe
                c.border = thin_border
                col_name = cfg['headers'][col_i - 1].lower()
                if isinstance(val, (int, float)):
                    c.alignment = Alignment(horizontal='right', vertical='center')
                elif 'data' in col_name or 'semana' in col_name or 'status' in col_name or 'item_id' in col_name:
                    c.alignment = Alignment(horizontal='center', vertical='center')
                else:
                    c.alignment = Alignment(horizontal='left', vertical='center')

        last_col_letter = get_column_letter(len(cfg['headers']))
        last_row = max(len(cfg['data']) + 1, 100)
        ws_ev.auto_filter.ref = f"A1:{last_col_letter}{last_row}"

        for formula, col_letter in cfg['validations']:
            dv = DataValidation(type='list', formula1=formula, allow_blank=True)
            ws_ev.add_data_validation(dv)
            dv.add(f'{col_letter}2:{col_letter}500')

        for col in ws_ev.columns:
            max_len = 0
            col_letter = get_column_letter(col[0].column)
            for cell in col:
                val_str = str(cell.value or '')
                if len(val_str) > max_len:
                    max_len = len(val_str)
            ws_ev.column_dimensions[col_letter].width = max(max_len + 5, 16)

    wb_env.save(output_apenas_secmam)
    print(f"Planilha exclusiva de Meio Ambiente atualizada: {output_apenas_secmam}")

    # =========================================================================
    # 3. PLANILHA DE CONTROLE DE ACESSO, USUÁRIOS E SENHAS (LOGIN & PERMISSÕES)
    # =========================================================================
    wb_usr = openpyxl.Workbook()
    wb_usr.remove(wb_usr.active)

    # Cores de controle de acesso
    usr_colors = {
        'Usuarios': {'tab': '0F172A', 'header': '0F172A'},
        'Perfis_Permissoes': {'tab': '1E3A8A', 'header': '1E3A8A'},
        'Auxiliar_Usuarios': {'tab': '475569', 'header': '334155'}
    }

    # 3.1 Aba Auxiliar_Usuarios
    ws_aux_usr = wb_usr.create_sheet('Auxiliar_Usuarios')
    ws_aux_usr.sheet_properties.tabColor = usr_colors['Auxiliar_Usuarios']['tab']

    aux_usr_data = {
        'Perfis_Acesso': [
            'Administrador Geral',
            'Defesa Civil (Master)',
            'Operador SEMED (Educação)',
            'Operador SEMUS (Saúde)',
            'Operador SEMAS (Social)',
            'Operador SEMOSU (Obras)',
            'Visualizador Geral (Consulta)'
        ],
        'Setores_Lotacao': [
            'Defesa Civil',
            'SEMED - Educação',
            'SEMUS - Saúde',
            'SEMAS - Assistência Social',
            'SEMOSU - Obras e Serviços',
            'Gabinete do Prefeito',
            'CICC - Centro Integrado'
        ],
        'Niveis_Permissao': [
            'Acesso Total (Admin)',
            'Edição Setorial',
            'Apenas Leitura'
        ],
        'Status_Conta': [
            'Ativo',
            'Bloqueado',
            'Inativo / Pendente'
        ]
    }

    for col_i, (col_name, vals) in enumerate(aux_usr_data.items(), start=1):
        c = ws_aux_usr.cell(row=1, column=col_i, value=col_name)
        c.font = font_header
        c.fill = PatternFill(start_color=usr_colors['Auxiliar_Usuarios']['header'], end_color=usr_colors['Auxiliar_Usuarios']['header'], fill_type='solid')
        c.alignment = Alignment(horizontal='center', vertical='center')
        c.border = thin_border
        for r_i, v in enumerate(vals, start=2):
            cell = ws_aux_usr.cell(row=r_i, column=col_i, value=v)
            cell.font = font_body
            cell.border = thin_border
            cell.alignment = Alignment(horizontal='left', vertical='center')

    ws_aux_usr.views.sheetView[0].showGridLines = True
    ws_aux_usr.freeze_panes = 'A2'
    ws_aux_usr.auto_filter.ref = f"A1:{get_column_letter(len(aux_usr_data))}20"
    for col in ws_aux_usr.columns:
        max_len = max(len(str(cell.value or '')) for cell in col)
        col_letter = get_column_letter(col[0].column)
        ws_aux_usr.column_dimensions[col_letter].width = max(max_len + 4, 18)

    val_perfil_usr = 'Auxiliar_Usuarios!$A$2:$A$10'
    val_setor_usr = 'Auxiliar_Usuarios!$B$2:$B$10'
    val_nivel_usr = 'Auxiliar_Usuarios!$C$2:$C$10'
    val_status_usr = 'Auxiliar_Usuarios!$D$2:$D$10'

    # 3.2 Aba Usuarios
    ws_u = wb_usr.create_sheet('Usuarios')
    ws_u.sheet_properties.tabColor = usr_colors['Usuarios']['tab']
    ws_u.views.sheetView[0].showGridLines = True
    ws_u.freeze_panes = 'A2'
    ws_u.row_dimensions[1].height = 28

    u_headers = [
        'ID', 'Nome_Completo', 'Login', 'Senha_Acesso', 'Email_Institucional',
        'Perfil_Acesso', 'Setor_Lotacao', 'Nivel_Permissao', 'Status_Conta',
        'Data_Cadastro', 'Ultimo_Acesso', 'Observacoes'
    ]

    fill_hdr_u = PatternFill(start_color=usr_colors['Usuarios']['header'], end_color=usr_colors['Usuarios']['header'], fill_type='solid')
    for col_i, h in enumerate(u_headers, start=1):
        c = ws_u.cell(row=1, column=col_i, value=h)
        c.font = font_header
        c.fill = fill_hdr_u
        c.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
        c.border = thin_border

    usuarios_iniciais = [
        [1, 'Administrador Geral do Sistema', 'admin', 'Admin@SMJ2026', 'admin.defesacivil@pmsmj.es.gov.br', 'Administrador Geral', 'Defesa Civil', 'Acesso Total (Admin)', 'Ativo', '10/09/2026', '10/09/2026', 'Acesso irrestrito a todos os módulos e planilhas'],
        [2, 'Coordenador Municipal de Defesa Civil', 'defesacivil', 'DefesaCivil@2026', 'defesacivil@pmsmj.es.gov.br', 'Defesa Civil (Master)', 'Defesa Civil', 'Acesso Total (Admin)', 'Ativo', '10/09/2026', '10/09/2026', 'Gestão master operacional do Painel El Niño'],
        [3, 'Equipe de Gestão da Educação (SEMED)', 'educacao', 'EduSMJ@2026', 'educacao@pmsmj.es.gov.br', 'Operador SEMED (Educação)', 'SEMED - Educação', 'Edição Setorial', 'Ativo', '10/09/2026', '—', 'Alimentação de incidentes, absenteísmo e plano 4.6'],
        [4, 'Equipe de Vigilância em Saúde (SEMUS)', 'saude', 'SaudeSMJ@2026', 'saude@pmsmj.es.gov.br', 'Operador SEMUS (Saúde)', 'SEMUS - Saúde', 'Edição Setorial', 'Ativo', '10/09/2026', '—', 'Alimentação de casos de arboviroses, LIRAa e estoque'],
        [5, 'Equipe da Secretaria de Assistência Social', 'social', 'SocialSMJ@2026', 'social@pmsmj.es.gov.br', 'Operador SEMAS (Social)', 'SEMAS - Assistência Social', 'Edição Setorial', 'Ativo', '10/09/2026', '—', 'Alimentação de atendimentos e estoque de abrigo'],
        [6, 'Equipe de Obras e Serviços Urbanos', 'obras', 'ObrasSMJ@2026', 'obras@pmsmj.es.gov.br', 'Operador SEMOSU (Obras)', 'SEMOSU - Obras e Serviços', 'Edição Setorial', 'Ativo', '10/09/2026', '—', 'Alimentação de intervenções de drenagem e canais'],
        [7, 'Gabinete do Prefeito / Consulta CICC', 'gabinete', 'Gabinete@2026', 'gabinete@pmsmj.es.gov.br', 'Visualizador Geral (Consulta)', 'Gabinete do Prefeito', 'Apenas Leitura', 'Ativo', '10/09/2026', '—', 'Acesso de consulta executiva e relatórios PDF']
    ]

    for r_i, row_data in enumerate(usuarios_iniciais, start=2):
        ws_u.row_dimensions[r_i].height = 20
        use_stripe = (r_i % 2 == 0)
        for col_i, val in enumerate(row_data, start=1):
            c = ws_u.cell(row=r_i, column=col_i, value=val)
            c.font = font_body
            if use_stripe:
                c.fill = fill_stripe
            c.border = thin_border
            col_name = u_headers[col_i - 1].lower()
            if isinstance(val, (int, float)):
                c.alignment = Alignment(horizontal='center', vertical='center')
            elif 'data' in col_name or 'status' in col_name or 'login' in col_name:
                c.alignment = Alignment(horizontal='center', vertical='center')
            else:
                c.alignment = Alignment(horizontal='left', vertical='center')

    ws_u.auto_filter.ref = f"A1:{get_column_letter(len(u_headers))}100"

    # Validações suspensas na aba Usuarios
    u_validations = [
        (val_perfil_usr, 'F'),
        (val_setor_usr, 'G'),
        (val_nivel_usr, 'H'),
        (val_status_usr, 'I')
    ]
    for formula, col_letter in u_validations:
        dv = DataValidation(type='list', formula1=formula, allow_blank=True)
        ws_u.add_data_validation(dv)
        dv.add(f'{col_letter}2:{col_letter}500')

    for col in ws_u.columns:
        max_len = 0
        col_letter = get_column_letter(col[0].column)
        for cell in col:
            val_str = str(cell.value or '')
            if len(val_str) > max_len:
                max_len = len(val_str)
        ws_u.column_dimensions[col_letter].width = max(max_len + 5, 16)

    # 3.3 Aba Perfis_Permissoes (Regras de Travamentos do Sistema)
    ws_p = wb_usr.create_sheet('Perfis_Permissoes')
    ws_p.sheet_properties.tabColor = usr_colors['Perfis_Permissoes']['tab']
    ws_p.views.sheetView[0].showGridLines = True
    ws_p.freeze_panes = 'A2'
    ws_p.row_dimensions[1].height = 28

    p_headers = [
        'Perfil', 'Nivel_Hierarquia', 'Pode_Editar_Planilhas', 'Pode_Gerar_Relatorios',
        'Acesso_Mapas_Cartografia', 'Setores_Permitidos_Edicao', 'Descricao_Regra_Bloqueio'
    ]

    fill_hdr_p = PatternFill(start_color=usr_colors['Perfis_Permissoes']['header'], end_color=usr_colors['Perfis_Permissoes']['header'], fill_type='solid')
    for col_i, h in enumerate(p_headers, start=1):
        c = ws_p.cell(row=1, column=col_i, value=h)
        c.font = font_header
        c.fill = fill_hdr_p
        c.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
        c.border = thin_border

    perfis_regras = [
        ['Administrador Geral', 1, 'SIM (Total)', 'SIM (Todos)', 'SIM (Todos)', 'Todos os Setores', 'Sem qualquer restrição no sistema e nas rotas'],
        ['Defesa Civil (Master)', 2, 'SIM (Total)', 'SIM (Todos)', 'SIM (Todos)', 'Todos os Setores', 'Gestão operacional e emissão de alertas meteorológicos'],
        ['Operador SEMED (Educação)', 3, 'SIM (Setorial)', 'SIM (Setorial)', 'SIM (Educação)', 'Apenas Educação (Edu_*)', 'Bloqueado para edição de Saúde, Drenagem e Social'],
        ['Operador SEMUS (Saúde)', 3, 'SIM (Setorial)', 'SIM (Setorial)', 'SIM (Saúde)', 'Apenas Saúde (Vig_*)', 'Bloqueado para edição de Educação, Obras e Social'],
        ['Operador SEMAS (Social)', 3, 'SIM (Setorial)', 'SIM (Setorial)', 'SIM (Social)', 'Apenas Social (Ass_*)', 'Bloqueado para edição de Saúde, Obras e Educação'],
        ['Operador SEMOSU (Obras)', 3, 'SIM (Setorial)', 'SIM (Setorial)', 'SIM (Drenagem)', 'Apenas Obras (Dren.*)', 'Bloqueado para edição de Educação e Saúde'],
        ['Visualizador Geral (Consulta)', 4, 'NÃO', 'SIM (Leitura)', 'SIM (Leitura)', 'Nenhum (Apenas Consulta)', 'Modo somente leitura, sem permissão de alteração']
    ]

    for r_i, row_data in enumerate(perfis_regras, start=2):
        ws_p.row_dimensions[r_i].height = 20
        use_stripe = (r_i % 2 == 0)
        for col_i, val in enumerate(row_data, start=1):
            c = ws_p.cell(row=r_i, column=col_i, value=val)
            c.font = font_body
            if use_stripe:
                c.fill = fill_stripe
            c.border = thin_border
            if isinstance(val, int):
                c.alignment = Alignment(horizontal='center', vertical='center')
            else:
                c.alignment = Alignment(horizontal='left', vertical='center')

    ws_p.auto_filter.ref = f"A1:{get_column_letter(len(p_headers))}20"
    for col in ws_p.columns:
        max_len = 0
        col_letter = get_column_letter(col[0].column)
        for cell in col:
            val_str = str(cell.value or '')
            if len(val_str) > max_len:
                max_len = len(val_str)
        ws_p.column_dimensions[col_letter].width = max(max_len + 5, 18)

    wb_usr.save(output_usuarios)
    os.makedirs(os.path.dirname(output_usuarios_dados), exist_ok=True)
    wb_usr.save(output_usuarios_dados)
    print(f"Planilha de Usuários e Controle de Acesso gerada em:\n  -> {output_usuarios}\n  -> {output_usuarios_dados}")

if __name__ == '__main__':
    criar_todas_as_planilhas()
