# pipeline/02_roteamento.py
# Fase 3 - Roteamento: enriquece os elegíveis com os campos da gold e classifica
# a qualidade do identificador por linha (deterministico = click ID / probabilistico = PII).
# Não decide plataforma (Fase 2 já decidiu); decide COM QUE IDENTIDADE cada linha viaja.

def rotear(spark, df_elegiveis):
    df_elegiveis.createOrReplaceTempView("elegiveis_in")

    query = """
    SELECT
      e.lead_id,
      e.etapa_funil,
      e.plataforma,
      e.data_hora_conversao,
      g.email_hashed,
      g.phone_hashed,
      g.gclid, g.fbclid, g.msclkid,
      g.campaign_id,
      g.vl_faturamento_estimado,
      -- identificador principal que o payload vai usar
      CASE e.plataforma
        WHEN 'google' THEN CASE
            WHEN g.gclid IS NOT NULL THEN 'gclid'
            WHEN g.email_hashed IS NOT NULL THEN 'email_hash'
            WHEN g.phone_hashed IS NOT NULL THEN 'phone_hash'
            ELSE 'sem_identificador' END
        WHEN 'meta' THEN CASE
            WHEN g.fbclid IS NOT NULL THEN 'fbclid'
            WHEN g.email_hashed IS NOT NULL THEN 'email_hash'
            WHEN g.phone_hashed IS NOT NULL THEN 'phone_hash'
            ELSE 'sem_identificador' END
        WHEN 'bing' THEN CASE
            WHEN g.msclkid IS NOT NULL THEN 'msclkid'
            WHEN g.email_hashed IS NOT NULL THEN 'email_hash'
            WHEN g.phone_hashed IS NOT NULL THEN 'phone_hash'
            ELSE 'sem_identificador' END
      END AS identificador_usado,
      -- qualidade do match que esse identificador compra
      CASE
        WHEN (e.plataforma = 'google' AND g.gclid   IS NOT NULL)
          OR (e.plataforma = 'meta'   AND g.fbclid  IS NOT NULL)
          OR (e.plataforma = 'bing'   AND g.msclkid IS NOT NULL)
        THEN 'deterministico'
        WHEN g.email_hashed IS NOT NULL OR g.phone_hashed IS NOT NULL
        THEN 'probabilistico'
        ELSE 'sem_identificador'
      END AS qualidade_match
    FROM elegiveis_in e
    JOIN gold.mkt_conversoes_offline_b2b g
      ON  e.lead_id     = g.lead_id
      AND e.etapa_funil = g.etapa_funil
    """
    return spark.sql(query)


# --- uso no notebook ---
df_roteado = rotear(spark, calcular_elegiveis(spark))
df_roteado.createOrReplaceTempView("roteados")   # 03_transformacao lê daqui
df_roteado.groupBy("plataforma", "qualidade_match").count().orderBy("plataforma").show()