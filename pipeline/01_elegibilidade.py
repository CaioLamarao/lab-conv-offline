# pipeline/01_elegibilidade.py
# Fase 2 - Elegibilidade: candidatos (gold expandida por plataforma, dentro da janela)
#          MENOS o que já foi enviado com sucesso (anti-join com a control table).
# Não escreve nada; devolve a lista do que enviar agora.

def calcular_elegiveis(spark):
    query = """
    WITH candidatos AS (
      -- Google (ECL via Data Manager): >63d após o clique não é importado
      SELECT lead_id, etapa_funil, data_hora_conversao, 'google' AS plataforma
      FROM gold.mkt_conversoes_offline_b2b
      WHERE (gclid IS NOT NULL OR origem_midia = 'google_ads')
        AND data_hora_conversao >= current_timestamp() - INTERVAL 63 DAYS
      UNION ALL
      -- Meta (CAPI): event_time >7d no passado faz a Meta rejeitar o request INTEIRO
      SELECT lead_id, etapa_funil, data_hora_conversao, 'meta'
      FROM gold.mkt_conversoes_offline_b2b
      WHERE (fbclid IS NOT NULL OR origem_midia = 'meta_ads')
        AND data_hora_conversao >= current_timestamp() - INTERVAL 7 DAYS
      UNION ALL
      -- Bing (Bulk/OCI): data da conversão fora de 90d faz o upload falhar
      SELECT lead_id, etapa_funil, data_hora_conversao, 'bing'
      FROM gold.mkt_conversoes_offline_b2b
      WHERE (msclkid IS NOT NULL OR origem_midia = 'bing_ads')
        AND data_hora_conversao >= current_timestamp() - INTERVAL 90 DAYS
    )
    SELECT c.*
    FROM candidatos c
    LEFT ANTI JOIN ops.conversoes_offline_controle ctrl
      ON  c.lead_id       = ctrl.lead_id
      AND c.etapa_funil   = ctrl.etapa_funil
      AND c.plataforma    = ctrl.plataforma
      AND ctrl.status_envio = 'aceito'
    """
    return spark.sql(query)


# --- uso no notebook / orquestração ---
df_elegiveis = calcular_elegiveis(spark)
df_elegiveis.createOrReplaceTempView("elegiveis")   # Fase 3 lê daqui, na mesma execução
print(f"Elegíveis: {df_elegiveis.count()}")
df_elegiveis.groupBy("plataforma").count().show()