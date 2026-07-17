SELECT lead_id,
    plataforma
FROM (
        WITH candidatos AS (
            -- Sobe a gold (grão lead+etapa) para lead+etapa+plataforma:
            -- 1 candidato por plataforma que o lead tem sinal de atingir.
            SELECT lead_id,
                etapa_funil,
                data_hora_conversao,
                'google' AS plataforma
            FROM gold.mkt_conversoes_offline_b2b
            WHERE gclid IS NOT NULL
                OR origem_midia = 'google_ads'
            UNION ALL
            SELECT lead_id,
                etapa_funil,
                data_hora_conversao,
                'meta'
            FROM gold.mkt_conversoes_offline_b2b
            WHERE fbclid IS NOT NULL
                OR origem_midia = 'meta_ads'
            UNION ALL
            SELECT lead_id,
                etapa_funil,
                data_hora_conversao,
                'bing'
            FROM gold.mkt_conversoes_offline_b2b
            WHERE msclkid IS NOT NULL
                OR origem_midia = 'bing_ads'
        )
        SELECT c.*
        FROM candidatos c LEFT ANTI
            JOIN ops.conversoes_offline_controle ctrl ON c.lead_id = ctrl.lead_id
            AND c.etapa_funil = ctrl.etapa_funil
            AND c.plataforma = ctrl.plataforma
            AND ctrl.status_envio = 'aceito'
    )
WHERE lead_id = 'lead_0040';
WITH candidatos AS (
    -- Google (ECL via Data Manager): >63d após o clique não é importado
    SELECT lead_id,
        etapa_funil,
        data_hora_conversao,
        'google' AS plataforma
    FROM gold.mkt_conversoes_offline_b2b
    WHERE (
            gclid IS NOT NULL
            OR origem_midia = 'google_ads'
        )
        AND data_hora_conversao >= current_timestamp() - INTERVAL 63 DAYS
    UNION ALL
    -- Meta (CAPI): event_time >7d no passado faz a Meta rejeitar o request INTEIRO
    SELECT lead_id,
        etapa_funil,
        data_hora_conversao,
        'meta'
    FROM gold.mkt_conversoes_offline_b2b
    WHERE (
            fbclid IS NOT NULL
            OR origem_midia = 'meta_ads'
        )
        AND data_hora_conversao >= current_timestamp() - INTERVAL 7 DAYS
    UNION ALL
    -- Bing (Bulk/OCI): data da conversão fora de 90d faz o upload falhar
    SELECT lead_id,
        etapa_funil,
        data_hora_conversao,
        'bing'
    FROM gold.mkt_conversoes_offline_b2b
    WHERE (
            msclkid IS NOT NULL
            OR origem_midia = 'bing_ads'
        )
        AND data_hora_conversao >= current_timestamp() - INTERVAL 90 DAYS
)
SELECT c.*
FROM candidatos c LEFT ANTI
    JOIN ops.conversoes_offline_controle ctrl ON c.lead_id = ctrl.lead_id
    AND c.etapa_funil = ctrl.etapa_funil
    AND c.plataforma = ctrl.plataforma
    AND ctrl.status_envio = 'aceito' -- 1. Leads distintos deve dar 500; linhas, ~1.050+
SELECT COUNT(DISTINCT lead_id) AS leads,
    COUNT(*) AS linhas
FROM gold.mkt_conversoes_offline_b2b;
-- 2. Deve existir lead com mais de uma etapa (o que faltava no seu mock)
SELECT lead_id,
    COUNT(*) AS etapas
FROM gold.mkt_conversoes_offline_b2b
GROUP BY lead_id
HAVING COUNT(*) > 1
ORDER BY etapas DESC
LIMIT 5;
-- 3. Hashes agora têm 64 caracteres (SHA-256 real, não placeholder)
SELECT LENGTH(email_hashed) AS tam,
    COUNT(*)
FROM gold.mkt_conversoes_offline_b2b
GROUP BY 1;
-- 4. Os três regimes de idade existem
SELECT CASE
        WHEN data_hora_conversao >= current_date() - INTERVAL 7 DAYS THEN '0-7d (todas)'
        WHEN data_hora_conversao >= current_date() - INTERVAL 63 DAYS THEN '8-63d (google/bing)'
        ELSE '64d+ (só bing ou nada)'
    END AS regime,
    COUNT(*)
FROM gold.mkt_conversoes_offline_b2b
GROUP BY 1;
SELECT origem_midia,
    COUNT(*) AS qtd,
    SUM(vl_faturamento_estimado) AS valor_estimado
FROM gold.mkt_conversoes_offline_b2b
GROUP BY origem_midia
ORDER BY qtd DESC;
SELECT etapa_funil,
    COUNT(*) AS qtd
FROM gold.mkt_conversoes_offline_b2b
GROUP BY etapa_funil
ORDER BY etapa_funil;
SELECT COUNT(*) AS total_leads,
    SUM(
        CASE
            WHEN gclid IS NOT NULL THEN 1
            ELSE 0
        END
    ) AS com_gclid,
    SUM(
        CASE
            WHEN fbclid IS NOT NULL THEN 1
            ELSE 0
        END
    ) AS com_fbclid,
    SUM(
        CASE
            WHEN msclkid IS NOT NULL THEN 1
            ELSE 0
        END
    ) AS com_msclkid,
    SUM(
        CASE
            WHEN gclid IS NULL
            AND fbclid IS NULL
            AND msclkid IS NULL
            AND (
                email_hashed IS NOT NULL
                OR phone_hashed IS NOT NULL
            ) THEN 1
            ELSE 0
        END
    ) AS sem_click_id_com_pii,
    SUM(
        CASE
            WHEN gclid IS NULL
            AND fbclid IS NULL
            AND msclkid IS NULL
            AND email_hashed IS NULL
            AND phone_hashed IS NULL THEN 1
            ELSE 0
        END
    ) AS sem_identificador
FROM gold.mkt_conversoes_offline_b2b;