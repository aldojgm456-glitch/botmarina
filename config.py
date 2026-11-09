import os
from dotenv import load_dotenv

load_dotenv()

IMAP_HOST = os.getenv("IMAP_HOST", "imap.gmail.com")
EMAIL_USER = os.getenv("EMAIL_USER", "")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD", "")
# Endereço(s) que identificam os e-mails (procurado em De/Para/Cc/Delivered-To)
ENDERECO_FILTRO = [r.strip().lower() for r in os.getenv("ENDERECO_FILTRO", "").split(",") if r.strip()]
# Só considera e-mails cujo remetente (De) contenha um destes trechos
REMETENTE_FILTRO = [r.strip().lower() for r in os.getenv("REMETENTE_FILTRO", "inss.gov.br").split(",") if r.strip()]
# Só considera e-mails que mencionem INSS no assunto, remetente ou corpo
EXIGIR_INSS = os.getenv("EXIGIR_INSS", "1") == "1"
PASTA = os.getenv("PASTA", "INBOX")
DIAS_ATRAS = int(os.getenv("DIAS_ATRAS", "1"))
ARQUIVO_EXCEL = os.getenv("ARQUIVO_EXCEL", "inss_movimentacoes.xlsx")

# Status padronizados (ordem importa: o primeiro que casar vence)
STATUS = [
    ("PENDENTE", ["exigência", "exigencia", "pendente", "pendência", "pendencia", "cumpriu a exig"]),
    ("EM ANÁLISE", ["em análise", "em analise", "agendamento de perícia", "agendamento de pericia", "compareça", "compareca"]),
    ("CONCLUÍDA", ["concluíd", "concluid", "foi prorrogado", "não foi prorrogado", "nao foi prorrogado",
                   "deferid", "indeferid", "concedid", "crédito referente", "credito referente"]),
]
