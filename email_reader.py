import imaplib
import email
from email.header import decode_header
from email.utils import parsedate_to_datetime
from datetime import datetime, timedelta
import re
import html

import config


def _decode(valor):
    if not valor:
        return ""
    partes = []
    for texto, charset in decode_header(valor):
        if isinstance(texto, bytes):
            texto = texto.decode(charset or "utf-8", errors="replace")
        partes.append(texto)
    return "".join(partes)


def _corpo(msg):
    """Extrai texto puro (ou HTML limpo) do e-mail."""
    texto, htmltxt = "", ""
    partes = msg.walk() if msg.is_multipart() else [msg]
    for p in partes:
        tipo = p.get_content_type()
        if p.get_content_disposition() == "attachment":
            continue
        if tipo in ("text/plain", "text/html"):
            payload = p.get_payload(decode=True) or b""
            conteudo = payload.decode(p.get_content_charset() or "utf-8", errors="replace")
            if tipo == "text/plain":
                texto += conteudo
            else:
                htmltxt += conteudo
    if texto.strip():
        return texto.strip()
    limpo = re.sub(r"(?is)<(script|style).*?>.*?</\1>", " ", htmltxt)
    limpo = re.sub(r"(?s)<[^>]+>", " ", limpo)
    return re.sub(r"\s+", " ", html.unescape(limpo)).strip()


def buscar_emails_inss(inicio=None, fim=None):
    """Retorna os e-mails do INSS. Com inicio/fim (datetime local) filtra pela janela;
    sem eles, usa os últimos DIAS_ATRAS dias."""
    if inicio:
        desde = (inicio - timedelta(days=1)).strftime("%d-%b-%Y")  # folga p/ fuso do servidor
    else:
        desde = (datetime.now() - timedelta(days=config.DIAS_ATRAS)).strftime("%d-%b-%Y")
    resultados = []
    with imaplib.IMAP4_SSL(config.IMAP_HOST) as imap:
        imap.login(config.EMAIL_USER, config.EMAIL_PASSWORD)
        imap.select(config.PASTA, readonly=True)
        _, dados = imap.search(None, f'(SINCE "{desde}")')
        for num in dados[0].split():
            _, d = imap.fetch(num, "(RFC822)")
            msg = email.message_from_bytes(d[0][1])
            remetente = _decode(msg.get("From", ""))
            cabecalhos = " ".join(_decode(msg.get(h, "")) for h in ("From", "To", "Cc", "Delivered-To", "X-Original-To")).lower()
            if config.ENDERECO_FILTRO and not any(f in cabecalhos for f in config.ENDERECO_FILTRO):
                continue
            if not any(f in remetente.lower() for f in config.REMETENTE_FILTRO):
                continue
            if config.EXIGIR_INSS and "inss" not in (cabecalhos + _decode(msg.get("Subject", "")).lower() + _corpo(msg).lower()):
                continue
            try:
                data = parsedate_to_datetime(msg.get("Date"))
                if data.tzinfo:
                    data = data.astimezone().replace(tzinfo=None)  # converte p/ horário local
            except Exception:
                data = None
            if (inicio or fim) and (data is None or (inicio and data < inicio) or (fim and data >= fim)):
                continue
            resultados.append({
                "id": msg.get("Message-ID", "").strip(),
                "data": data,
                "remetente": remetente,
                "assunto": _decode(msg.get("Subject", "")),
                "corpo": _corpo(msg),
                "anexos": sum(1 for p in msg.walk() if p.get_content_disposition() == "attachment"),
            })
    return resultados
