# botmarina – Resumo diário de e-mails do INSS

Lê os e-mails do INSS recebidos em previdenciario@roneelyfeitosa (IMAP) e grava em Excel (`inss_movimentacoes.xlsx`)
com as colunas: Data Análise, Data E-mail, Cliente, Protocolo, Tipo de Serviço, Status Atual, Resumo do Despacho. Sem duplicar.

## Uso
```
pip install -r requirements.txt
copy .env.example .env     # preencha e-mail e senha de app
python main.py
```

## Estrutura
- `config.py` – configurações e categorias por palavra-chave
- `email_reader.py` – conecta no e-mail e filtra remetentes do INSS
- `summarizer.py` – categoria, protocolo, prazo e resumo (por regras)
- `excel_writer.py` – grava/atualiza o Excel
- `main.py` – orquestra tudo

## Próximos passos
1. Testar com e-mails reais e ajustar filtro/categorias
2. Agendar execução diária (Agendador de Tarefas do Windows)
3. (Opcional) Resumo por IA, aba com totais por categoria, envio do Excel por e-mail
