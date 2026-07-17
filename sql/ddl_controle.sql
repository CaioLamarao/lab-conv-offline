-- Fase 1 - CREATE TABLE ops.conversoes_offline_controle (Delta)
CREATE SCHEMA ops;
USE ops;
CREATE TABLE IF NOT EXISTS gold.mkt_conversoes_offline_b2b_mock (
    lead_id STRING NOT NULL COMMENT 'ID do lead no CRM/Salesforce',
    email_hashed STRING COMMENT 'E-mail normalizado e hasheado em SHA-256',
    phone_hashed STRING COMMENT 'Telefone normalizado e hasheado em SHA-256',
    data_hora_conversao TIMESTAMP NOT NULL COMMENT 'Data/hora em que a etapa ocorreu no CRM',
    etapa_funil STRING NOT NULL COMMENT 'MQL | SQL | Proposta | Venda',
    vl_faturamento_estimado DECIMAL(18, 2) COMMENT 'Valor estimado associado à conversão',
    gclid STRING COMMENT 'Google Click ID',
    fbclid STRING COMMENT 'Facebook Click ID',
    msclkid STRING COMMENT 'Microsoft/Bing Click ID',
    origem_midia STRING COMMENT 'Origem/canal de mídia',
    campaign_id STRING COMMENT 'ID da campanha de mídia',
    produto STRING COMMENT 'Produto de interesse',
    porte_cliente STRING COMMENT 'Porte do cliente'
) USING DELTA COMMENT 'Base mock para simular a view gold.mkt_conversoes_offline_b2b do case';
CREATE TABLE IF NOT EXISTS ops.conversoes_offline_controle (
    lead_id STRING NOT NULL COMMENT 'ID do lead na origem (Salesforce/gold)',
    etapa_funil STRING NOT NULL COMMENT 'MQL | SQL | Proposta | Venda — cada etapa é um evento distinto',
    plataforma STRING NOT NULL COMMENT 'google | meta | bing — destino do envio',
    data_hora_conversao TIMESTAMP NOT NULL COMMENT 'Quando a conversão ocorreu no CRM — base do cálculo de latência e da checagem de janela',
    campaign_id STRING COMMENT 'Mantido p/ debug; cortes de negócio vêm de JOIN com a gold',
    valor_enviado DECIMAL(18, 2) COMMENT 'vl_faturamento_estimado efetivamente enviado no payload',
    identificador_usado STRING NOT NULL COMMENT 'gclid | fbclid | msclkid | email_hash | phone_hash',
    status_envio STRING NOT NULL COMMENT 'aceito | erro | dead_letter',
    http_status INT COMMENT 'Código HTTP da API',
    codigo_erro STRING COMMENT 'Categoria do erro',
    mensagem_resposta STRING COMMENT 'Resposta crua da API',
    tentativas INT NOT NULL COMMENT 'Nº de tentativas de envio',
    ts_primeiro_envio TIMESTAMP COMMENT 'Primeira tentativa',
    ts_ultimo_envio TIMESTAMP NOT NULL COMMENT 'Última tentativa',
    status_match STRING COMMENT 'casado | nao_casado | pendente — NULL até a reconciliação rodar',
    ts_reconciliacao TIMESTAMP COMMENT 'Quando a reconciliação cruzou este envio com o reporting da plataforma',
    dt_atualizacao TIMESTAMP NOT NULL COMMENT 'Última escrita nesta linha',
    CONSTRAINT pk_controle PRIMARY KEY (lead_id, etapa_funil, plataforma)
) USING DELTA COMMENT 'Controle dos envios de conversão offline. 1 linha por (lead_id, etapa_funil, plataforma). Upsert via MERGE.' TBLPROPERTIES (
    'delta.enableChangeDataFeed' = 'true',
    'delta.autoOptimize.optimizeWrite' = 'true',
    'delta.autoOptimize.autoCompact' = 'true'
);
ALTER TABLE ops.conversoes_offline_controle
ADD CONSTRAINT chk_etapa CHECK (etapa_funil IN ('MQL', 'SQL', 'Proposta', 'Venda'));
ALTER TABLE ops.conversoes_offline_controle
ADD CONSTRAINT chk_plataforma CHECK (plataforma IN ('google', 'meta', 'bing'));
ALTER TABLE ops.conversoes_offline_controle
ADD CONSTRAINT chk_status CHECK (status_envio IN ('aceito', 'erro', 'dead_letter'));