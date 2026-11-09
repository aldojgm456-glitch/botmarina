"""Extrai os campos da planilha de movimentações a partir do e-mail automático do INSS.
O corpo chega em uma linha só (HTML achatado), então os campos são cortados pelo próximo rótulo."""
import re
from datetime import date

# Onde um campo termina (próximo rótulo ou rodapé)
_FIM = (r"(?=\s*(?:Data do Protocolo|Unidade respons[aá]vel|Status atual|Despacho\s*:|"
        r"Servi[cç]o\s*:|Protocolo\s*:|É poss[ií]vel acompanhar|O atendimento deste|Atenciosamente)|\s*$)")

# Status do INSS -> status usado na planilha
_MAPA_STATUS = {"EXIGÊNCIA": "PENDENTE", "EXIGENCIA": "PENDENTE"}


def _campo(texto, rotulo):
    m = re.search(rf"{rotulo}\s*:\s*(.+?){_FIM}", texto, re.I | re.S)
    return re.sub(r"\s+", " ", m.group(1)).strip() if m else ""


def extrair_cliente(texto):
    m = re.search(r"Prezado\(a\)\s*Sr\(a\)\s+(.+?)\s*,", texto, re.I)
    return m.group(1).strip().upper() if m else ""


def extrair_protocolo(texto):
    m = re.search(r"\d{8,}", _campo(texto, r"(?<!Data do )Protocolo"))
    return m.group(0) if m else ""


def extrair_servico(texto, assunto):
    return (_campo(texto, r"Servi[cç]o") or assunto).upper()


def extrair_status(texto):
    s = _campo(texto, r"Status atual").upper()
    if s:
        return _MAPA_STATUS.get(s, s)
    if re.search(r"realizado com sucesso", texto, re.I):
        return "REQUERIMENTO REALIZADO"
    return "A CLASSIFICAR"


def extrair_despacho(texto):
    d = _campo(texto, r"Despacho")
    if d:
        d = re.sub(r"(?i)^prezado(?:\(a\))?\s*sr(?:\.|\(a\)|\.\(a\))*\s*(?:\(a\))?\.?,?\s*", "", d)
        d = re.sub(r"(?i)^prezado\(a\)\s*senhor\(a\),?\s*", "", d)
        return d[:600]
    m = re.search(r"requerimento solicitado pela Internet no dia ([\d/]+) às ([\d:]+) foi realizado com sucesso", texto, re.I)
    if m:
        return f"Requerimento realizado com sucesso em {m.group(1)} às {m.group(2)}."
    return ""


def processar(em):
    texto = em["corpo"]
    return {
        "Data Análise": date.today(),
        "Data E-mail": em["data"].date() if em["data"] else None,
        "Cliente": extrair_cliente(texto),
        "Protocolo": extrair_protocolo(texto),
        "Tipo de Serviço": extrair_servico(texto, em["assunto"]),
        "Status Atual": extrair_status(texto),
        "Resumo do Despacho": extrair_despacho(texto),
        "ID": em["id"],
    }
