import os
from openpyxl import Workbook, load_workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter

ABA = "Movimentações INSS"
COLUNAS = ["Data Análise", "Data E-mail", "Cliente", "Protocolo",
           "Tipo de Serviço", "Status Atual", "Resumo do Despacho", "ID"]
LARGURAS = [14, 14, 34, 20, 34, 16, 80, 6]


def _novo():
    wb = Workbook()
    ws = wb.active
    ws.title = ABA
    ws.append(COLUNAS)
    for i, w in enumerate(LARGURAS, start=1):
        cel = ws.cell(row=1, column=i)
        cel.font = Font(bold=True, color="FFFFFF")
        cel.fill = PatternFill("solid", fgColor="107C41")
        cel.alignment = Alignment(horizontal="center", vertical="center")
        ws.column_dimensions[get_column_letter(i)].width = w
    ws.column_dimensions["H"].hidden = True  # coluna técnica (anti-duplicidade)
    ws.freeze_panes = "A2"
    return wb


def salvar(registros, caminho):
    """Acrescenta só e-mails novos (dedupe pelo ID do e-mail + protocolo)."""
    wb = load_workbook(caminho) if os.path.exists(caminho) else _novo()
    ws = wb[ABA]
    existentes = {ws.cell(row=r, column=len(COLUNAS)).value for r in range(2, ws.max_row + 1)}

    novos = 0
    for r in registros:
        chave = f"{r['ID']}|{r['Protocolo']}"
        if chave in existentes:
            continue
        r = {**r, "ID": chave}
        ws.append([r[c] for c in COLUNAS])
        linha = ws.max_row
        for col in (1, 2):
            ws.cell(row=linha, column=col).number_format = "DD/MM/YYYY"
        for col in range(1, len(COLUNAS)):
            ws.cell(row=linha, column=col).alignment = Alignment(wrap_text=True, vertical="top")
        existentes.add(chave)
        novos += 1
    ws.auto_filter.ref = f"A1:G{ws.max_row}"
    wb.save(caminho)
    return novos
