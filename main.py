import sys
import os
import argparse
from datetime import datetime, date, time, timedelta

import config
from email_reader import buscar_emails_inss, marcar_como_lidos
from summarizer import processar
from excel_writer import salvar
from mailer import enviar_resumo

DESTINO_PADRAO = os.getenv("DESTINO_RESUMO", "previdenciario@roneelyfeitosa.com.br")
PASTA_RELATORIOS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "relatorios")


def janela_automatica(hoje):
    """Regra do escritório (executa às 7h, de segunda a sexta, lê e envia em seguida):
    - terça a sexta: de ontem 07:00 até hoje 07:00;
    - segunda: de sexta 07:00 até segunda 07:00 (sexta + sábado + domingo).
    Sábado e domingo não geram envio."""
    dow = hoje.weekday()  # 0=segunda ... 6=domingo
    if dow >= 5:
        return None
    fim = datetime.combine(hoje, time(7, 0))
    dias = 3 if dow == 0 else 1
    return fim - timedelta(days=dias), fim


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--auto", action="store_true", help="modo agendado: calcula a janela pelo dia da semana e envia")
    ap.add_argument("--hoje", help="simula a data de hoje (AAAA-MM-DD), só para teste do --auto")
    ap.add_argument("--sem-enviar", action="store_true", help="não envia o e-mail (teste)")
    ap.add_argument("--inicio", help='manual, ex: "2026-11-08 07:00"')
    ap.add_argument("--fim", help='manual, ex: "2026-11-09 07:00"')
    ap.add_argument("--excel", help="arquivo Excel de saída")
    ap.add_argument("--so-nao-lidos", action="store_true", help="considera apenas e-mails ainda não lidos")
    ap.add_argument("--nao-marcar-lido", action="store_true", help="não marca os e-mails do relatório como lidos")
    ap.add_argument("--enviar-para", help="envia o resumo por e-mail para este endereço")
    a = ap.parse_args()

    if not config.EMAIL_USER or not config.EMAIL_PASSWORD:
        sys.exit("Configure EMAIL_USER e EMAIL_PASSWORD no arquivo .env")

    fmt = "%Y-%m-%d %H:%M"
    destino = a.enviar_para
    if a.auto:
        hoje = date.fromisoformat(a.hoje) if a.hoje else date.today()
        janela = janela_automatica(hoje)
        if not janela:
            print("Fim de semana: nada a enviar.")
            return
        inicio, fim = janela
        os.makedirs(PASTA_RELATORIOS, exist_ok=True)
        excel = a.excel or os.path.join(PASTA_RELATORIOS, f"inss_{inicio:%Y-%m-%d}_07h_a_{fim:%Y-%m-%d}_07h.xlsx")
        destino = None if a.sem_enviar else DESTINO_PADRAO
    else:
        inicio = datetime.strptime(a.inicio, fmt) if a.inicio else None
        fim = datetime.strptime(a.fim, fmt) if a.fim else None
        excel = a.excel or config.ARQUIVO_EXCEL

    emails = buscar_emails_inss(inicio, fim, a.so_nao_lidos)
    print(f"Janela: {inicio} -> {fim} | {len(emails)} e-mail(s) do INSS encontrados.")
    registros = sorted((processar(e) for e in emails), key=lambda r: r["Data E-mail"] or datetime.min.date())
    novos = salvar(registros, excel)
    print(f"{novos} novo(s) registro(s) gravado(s) em {excel}")

    if destino:
        periodo = f"{inicio:%d/%m %H:%M} a {fim:%d/%m %H:%M}" if inicio and fim else "últimas 24h"
        enviar_resumo(registros, periodo, destino, excel)
        print(f"Resumo enviado para {destino}")

    # Só marca como lido depois que o relatório foi gravado (e enviado, se for o caso)
    if emails and not a.nao_marcar_lido and not a.sem_enviar:
        n = marcar_como_lidos([e["uid"] for e in emails])
        print(f"{n} e-mail(s) marcado(s) como lido(s) na caixa de entrada.")


if __name__ == "__main__":
    main()
