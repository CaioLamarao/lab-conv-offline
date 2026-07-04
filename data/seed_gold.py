# data/seed_gold.py
# Seed v2 - gold.mkt_conversoes_offline_b2b_mock + staging crua + manifesto de defeitos
# Roda num notebook Databricks (Free Edition). Reexecutável: overwrite total.

import hashlib
import random
from datetime import datetime, timedelta

random.seed(42)  # reprodutível: mesmo dado a cada rodada

# ---------- CONFIG ----------
N_LEADS = 500
TBL_GOLD = "gold.mkt_conversoes_offline_b2b_base"   # tabela-base nova; a view aponta pra cá
TBL_RAW   = "ops.stg_crm_leads_raw"
TBL_SEED  = "ops.seed_manifest"

PCT_HASH_SUJO   = 0.10   # hash gerado SEM normalizar (o defeito do antecessor)
PCT_SEM_CLICKID = 0.12   # leads sem nenhum click ID (organico / crm_import)
PCT_MULTITOUCH  = 0.08   # leads com 2 click IDs

# ---------- HELPERS ----------
def sha256(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()

def normalizar_email(e: str) -> str:
    return e.strip().lower()

def normalizar_telefone(t: str) -> str:
    # E.164 BR: só dígitos, prefixo +55
    digitos = "".join(c for c in t if c.isdigit())
    if digitos.startswith("55"):
        digitos = digitos[2:]
    return "+55" + digitos

def email_sujo(nome: str, i: int) -> str:
    dominios = ["gmail.com", "outlook.com", "empresa.com.br", "yahoo.com.br"]
    base = f"{nome}{i}@{random.choice(dominios)}"
    sujeiras = [
        lambda s: s,                       # limpo
        lambda s: " " + s + "  ",          # espaços
        lambda s: s.upper(),               # maiúsculas
        lambda s: s.replace("@", " @ "),   # espaço interno (inválido de verdade)
        lambda s: s.capitalize(),          # primeira maiúscula
    ]
    return random.choice(sujeiras)(base)

def telefone_sujo() -> str:
    ddd = random.choice(["11", "21", "31", "41", "47", "51", "61", "81"])
    num = f"9{random.randint(4000,9999)}{random.randint(1000,9999)}"
    formatos = [
        lambda: f"({ddd}) {num[:5]}-{num[5:]}",     # (41) 99999-9999
        lambda: f"{ddd}{num}",                      # 41999999999
        lambda: f"+55 {ddd} {num[:5]} {num[5:]}",   # +55 41 99999 9999
        lambda: f"{ddd} {num}",
    ]
    return random.choice(formatos)()

# origem -> (click id que ela gera, campanhas)
ORIGENS = {
    "google_ads": ("gclid",   ["gads_search_b2b", "gads_pmax", "gads_brand"]),
    "meta_ads":   ("fbclid",  ["meta_leads", "meta_remarketing", "meta_video"]),
    "bing_ads":   ("msclkid", ["bing_search", "bing_b2b", "bing_competitor"]),
    "organico":   (None,      ["organic_direct", "organic_referral"]),
    "crm_import": (None,      ["crm_manual"]),
}
PRODUTOS = ["CRM", "ERP", "BI"]
PORTES   = ["pequeno", "medio", "grande", "enterprise"]
ETAPAS   = ["MQL", "SQL", "Proposta", "Venda"]

# jornada: até onde o lead avança (pesos)
JORNADAS = [(1, 0.40), (2, 0.25), (3, 0.15), (4, 0.20)]

def sortear_jornada() -> int:
    r, acc = random.random(), 0.0
    for n, p in JORNADAS:
        acc += p
        if r <= acc:
            return n
    return 1

def valor_por_etapa(etapa: str, porte: str) -> float:
    base = {"MQL": 1000, "SQL": 3500, "Proposta": 9000, "Venda": 25000}[etapa]
    mult = {"pequeno": 0.6, "medio": 1.0, "grande": 1.6, "enterprise": 2.5}[porte]
    return round(base * mult * random.uniform(0.8, 1.2), 2)

# ---------- GERAÇÃO ----------
agora = datetime.now()
rows_gold, rows_raw, rows_seed = [], [], []

for i in range(1, N_LEADS + 1):
    lead_id = f"lead_{i:04d}"

    # identidade crua (suja de propósito)
    raw_email = email_sujo("contato", i)
    raw_phone = telefone_sujo()

    # defeito plantado: hash sem normalizar em ~10% dos leads
    hash_defeituoso = random.random() < PCT_HASH_SUJO
    if hash_defeituoso:
        email_h = sha256(raw_email)                      # ERRADO de propósito: sujo direto
        phone_h = sha256(raw_phone)
    else:
        email_h = sha256(normalizar_email(raw_email))    # certo: normaliza antes
        phone_h = sha256(normalizar_telefone(raw_phone))

    # origem e click IDs
    origem = random.choice(list(ORIGENS.keys()))
    if random.random() < PCT_SEM_CLICKID:
        origem = random.choice(["organico", "crm_import"])
    clickid_tipo, campanhas = ORIGENS[origem]

    gclid = fbclid = msclkid = None
    if clickid_tipo == "gclid":   gclid   = f"gclid_{i:04d}"
    if clickid_tipo == "fbclid":  fbclid  = f"fbclid_{i:04d}"
    if clickid_tipo == "msclkid": msclkid = f"msclkid_{i:04d}"

    multitouch = clickid_tipo is not None and random.random() < PCT_MULTITOUCH
    if multitouch:
        extra = random.choice([t for t in ["gclid", "fbclid", "msclkid"] if t != clickid_tipo])
        if extra == "gclid":   gclid   = f"gclid_mt_{i:04d}"
        if extra == "fbclid":  fbclid  = f"fbclid_mt_{i:04d}"
        if extra == "msclkid": msclkid = f"msclkid_mt_{i:04d}"

    campaign_id = f"{random.choice(campanhas)}_{random.randint(1,9):03d}"
    produto = random.choice(PRODUTOS)
    porte   = random.choice(PORTES)

    # datas: 3 regimes de janela (7d Meta / 63d ECL / 90d Bing)
    r = random.random()
    if r < 0.40:   idade_dias = random.uniform(0, 6)     # dentro de tudo
    elif r < 0.75: idade_dias = random.uniform(8, 60)    # só Google/Bing
    else:          idade_dias = random.uniform(65, 100)  # só Bing ou nada

    n_etapas = sortear_jornada()
    ts_base = agora - timedelta(days=idade_dias)
    for e in range(n_etapas):
        etapa = ETAPAS[e]
        # cada avanço acontece dias depois do anterior (timestamps crescentes)
        ts_etapa = ts_base + timedelta(days=e * random.uniform(1, 5),
                                       hours=random.uniform(0, 8))
        rows_gold.append((
            lead_id, email_h, phone_h, ts_etapa, etapa,
            valor_por_etapa(etapa, porte),
            gclid, fbclid, msclkid, origem, campaign_id, produto, porte,
        ))

    rows_raw.append((lead_id, raw_email, raw_phone))

    if hash_defeituoso:
        rows_seed.append((lead_id, "hash_mal_normalizado",
                          "hash gerado sobre valor cru, sem lowercase/trim/E.164"))
    if multitouch:
        rows_seed.append((lead_id, "multitouch", "lead com 2 click IDs"))
    if clickid_tipo is None:
        rows_seed.append((lead_id, "sem_click_id", "roteamento só por PII hasheada"))

# ---------- ESCRITA (Delta, overwrite) ----------
spark.sql("CREATE SCHEMA IF NOT EXISTS gold")
spark.sql("CREATE SCHEMA IF NOT EXISTS ops")

cols_gold = ["lead_id","email_hashed","phone_hashed","data_hora_conversao","etapa_funil",
             "vl_faturamento_estimado","gclid","fbclid","msclkid","origem_midia",
             "campaign_id","produto","porte_cliente"]
spark.createDataFrame(rows_gold, cols_gold) \
     .write.format("delta").mode("overwrite").option("overwriteSchema","true") \
     .saveAsTable(TBL_GOLD)

spark.createDataFrame(rows_raw, ["lead_id","email_raw","phone_raw"]) \
     .write.format("delta").mode("overwrite").saveAsTable(TBL_RAW)

spark.createDataFrame(rows_seed, ["lead_id","tipo_defeito","descricao"]) \
     .write.format("delta").mode("overwrite").saveAsTable(TBL_SEED)

# Reaponta a view do case para a tabela-base do seed
spark.sql(f"""
    CREATE OR REPLACE VIEW gold.mkt_conversoes_offline_b2b AS
    SELECT * FROM {TBL_GOLD}
""")     

print(f"gold: {len(rows_gold)} linhas | raw: {len(rows_raw)} | manifesto: {len(rows_seed)}")