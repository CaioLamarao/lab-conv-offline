## lab-conversao-offline

Lab de conversão offline — Databricks -> Google (Data Manager API) / Meta (CAPI) / Bing (OCI).
Ver trilha-lab-conversao-offline.md no projeto para o passo a passo por fase.


## Notebooks (Databricks)

**seed_gold.py**
Gera o mundo sintético do lab: `gold.mkt_conversoes_offline_b2b_base` (seed v3, 500 leads / 1089 linhas, com defeitos plantados), a staging crua `ops.stg_crm_leads_raw` e o manifesto `ops.seed_manifest`, reapontando a view do case pra base. Reexecutável — overwrite total reseta tudo.

**Fase 2 - Prep**
Define `calcular_elegiveis` (janelas por plataforma + LEFT ANTI JOIN contra a control table) e prova a idempotência do loop: simula envios, verifica elegíveis zerando, insere leads novos e testa o Checkpoint 2 (elegibilidade por plataforma; `erro` não bloqueia reenvio). Inclui células de reset.

**Fase 3 - Roteamento** *(ex "Fase 3 - Prep", podado)*
Define `rotear`: enriquece os elegíveis com os campos da gold e classifica cada linha por `identificador_usado` e `qualidade_match` (deterministico/probabilistico/sem_identificador).

**Fase 3 - Trasnformacao**
Fonte da verdade da transformação: normalização de PII, hash SHA-256 e os montadores de payload das 3 plataformas (verificados contra doc oficial — Google com `emailAddress`/`phoneNumber` + `eventSource`), mais o dispatcher `montar_payload`. Python puro, espelhado em `pipeline/03_transformacao.py` no repo local.

**Fase 3 - testes por plataforma individuais**
Suíte verbosa de validação: normalização com casos sujos, payloads das 3 plataformas nos dois ramos (det/prob) com linhas reais do `df_roteado`, e o dispatcher. Autocontido — carrega cópias próprias das funções; se editar os canônicos, rode-os por último.

**Fase 4 - Envios**
Gerador de payloads pros envios manuais da Fase 4: filtra linha na janela (`data_hora_conversao <= current_timestamp()`), monta e imprime o JSON pra colar nos scripts locais `04_*.py` (o envio roda local — Free Edition bloqueia egress).


## Estrutura no Databricks

- DDL em sql/ddl_controle.sql

- Queries genéricas em sql/macro.sql

gold.mkt_conversoes_offline_b2b_mock 
50 registros do case, intocada

gold.mkt_conversoes_offline_b2b_base 
Seed v3: 1089 linhas, 500 leads (com o bug conhecido do event_time futuro)

gold.mkt_conversoes_offline_b2b
VIEW → aponta pra _base

ops.stg_crm_leads_raw
500 linhas cruas sujas

ops.seed_manifest
355 linhas — lacrado até a Fase 8

ops.conversoes_offline_controle
VAZIA (0 linhas) — os resets dos testes truncaram, e os envios da Fase 4 foram manuais, fora do pipeline (de propósito: gravar via MERGE é a Fase 5)

