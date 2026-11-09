import os
import smtplib
import html
from email.message import EmailMessage

import config

COLUNAS = ["Data E-mail", "Cliente", "Protocolo", "Tipo de Serviço", "Status Atual", "Resumo do Despacho"]
COR = {"CONCLUÍDA": "#c6efce", "PENDENTE": "#ffeb9c", "EM ANÁLISE": "#ddebf7"}


def _linha(r):
    cel = []
    for c in COLUNAS:
        v = r[c]
        v = v.strftime("%d/%m/%Y") if hasattr(v, "strftime") else (v or "")
        estilo = f' style="background:{COR.get(r["Status Atual"], "#fff")}"' if c == "Status Atual" else ""
        cel.append(f'<td{estilo} style="border:1px solid #ccc;padding:4px">{html.escape(str(v))}</td>')
    return "<tr>" + "".join(cel) + "</tr>"


def enviar_resumo(registros, periodo, destino, anexo=None):
    contagem = {}
    for r in registros:
        contagem[r["Status Atual"]] = contagem.get(r["Status Atual"], 0) + 1
    totais = " · ".join(f"{k}: {v}" for k, v in sorted(contagem.items())) or "nenhuma movimentação"

    cab = "".join(f'<th style="border:1px solid #ccc;padding:4px;background:#107C41;color:#fff">{c}</th>' for c in COLUNAS)
    corpo = "".join(_linha(r) for r in registros)
    tabela = f'<table style="border-collapse:collapse;font-family:Calibri,Arial;font-size:13px"><tr>{cab}</tr>{corpo}</table>' if registros else "<p>Nenhum e-mail do INSS no período.</p>"
    html_msg = (f"<p>Resumo das movimentações do INSS — {periodo}</p>"
                f"<p><b>{len(registros)}</b> e-mail(s) · {totais}</p>{tabela}"
                "<p style='color:#888;font-size:11px'>Gerado automaticamente pelo botmarina.</p>")

    msg = EmailMessage()
    msg["From"] = config.EMAIL_USER
    msg["To"] = destino
    msg["Subject"] = f"Resumo INSS — {periodo} ({len(registros)} movimentações)"
    msg.set_content(f"Resumo INSS {periodo}: {len(registros)} e-mail(s). {totais}. Veja a versão HTML/planilha em anexo.")
    msg.add_alternative(html_msg, subtype="html")
    if anexo and os.path.exists(anexo):
        with open(anexo, "rb") as f:
            msg.add_attachment(f.read(), maintype="application",
                               subtype="vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                               filename=os.path.basename(anexo))
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(config.EMAIL_USER, config.EMAIL_PASSWORD)
        smtp.send_message(msg)
