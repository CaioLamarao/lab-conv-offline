# pipeline/03_transformacao.py
# Fase 3 - Transformação: normalização de PII, hash SHA-256 e montagem de payload
# por plataforma (Meta CAPI / Google Data Manager / Bing OfflineConversion).
#
# Python puro de propósito: testável local (pytest), sem dependência de Spark.
# Verificado contra doc oficial em 09/07/2026:
#   Meta:   developers.facebook.com/documentation/ads-commerce/conversions-api
#   Google: developers.google.com/data-manager/api/devguides/events/send-events
#   Bing:   learn.microsoft.com/en-us/advertising/bulk-service/offline-conversion

import hashlib
import re

# ============================================================
# PARTE 1 - NORMALIZAÇÃO E HASH
# Regra de ouro: normalizar ANTES de hashear. Hash de valor sujo
# tem formato válido, é aceito (200) e nunca casa - falha invisível.
# ============================================================

def normalizar_email(email: str) -> str | None:
    """Trim + lowercase. None se inválido (não normalizável)."""
    if email is None:
        return None
    e = email.strip().lower()
    if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", e):
        return None
    return e

def normalizar_telefone(telefone: str, ddi_padrao: str = "55") -> str | None:
    """E.164 (+5541999999999). None se não dá pra inferir com segurança."""
    if telefone is None:
        return None
    digitos = re.sub(r"\D", "", telefone)
    if digitos.startswith("00"):
        digitos = digitos[2:]
    if digitos.startswith(ddi_padrao) and len(digitos) >= 12:
        pass
    elif len(digitos) in (10, 11):
        digitos = ddi_padrao + digitos
    else:
        return None
    return "+" + digitos

def sha256_hex(valor: str) -> str:
    """SHA-256 hexadecimal minúsculo."""
    return hashlib.sha256(valor.encode("utf-8")).hexdigest()

def hash_email(email_cru: str) -> str | None:
    e = normalizar_email(email_cru)
    return sha256_hex(e) if e else None

def hash_telefone(telefone_cru: str) -> str | None:
    t = normalizar_telefone(telefone_cru)
    return sha256_hex(t) if t else None

# ============================================================
# PARTE 2 - PAYLOAD META (Conversions API)
# PII hasheada em listas; fbc SEM hash; action_source system_generated.
# Envelope da Fase 4: {"data": [eventos]} + access_token.
# ============================================================

def montar_payload_meta(linha: dict) -> dict:
    user_data = {}

    if linha.get("email_hashed"):
        user_data["em"] = [linha["email_hashed"]]      # lista: múltiplos valores melhoram match
    if linha.get("phone_hashed"):
        user_data["ph"] = [linha["phone_hashed"]]

    # fbc reconstruído do fbclid - NÃO hashear (identificador de clique, não PII)
    if linha.get("fbclid"):
        ts_ms = int(linha["data_hora_conversao"].timestamp() * 1000)
        user_data["fbc"] = f"fb.1.{ts_ms}.{linha['fbclid']}"

    return {
        "event_name": f"Lead_{linha['etapa_funil']}",
        "event_time": int(linha["data_hora_conversao"].timestamp()),  # unix SEGUNDOS; janela 7d
        "action_source": "system_generated",                          # evento de CRM/backend
        "event_id": f"{linha['lead_id']}_{linha['etapa_funil']}",     # dedup (par com event_name)
        "user_data": user_data,
        "custom_data": {
            "value": float(linha["vl_faturamento_estimado"] or 0),
            "currency": "BRL",
        },
    }

# ============================================================
# PARTE 3 - PAYLOAD GOOGLE (Data Manager API / ECL)
# CORRIGIDO pós-verificação:
#   - campos são emailAddress/phoneNumber (hash DENTRO; encoding
#     declarado no request como "HEX", nível envelope - Fase 4)
#   - eventSource obrigatório para offline/ECL
# Regra da API: evento precisa de adIdentifiers OU userData;
# "send both if you have both".
# ============================================================

def montar_payload_google(linha: dict) -> dict:
    user_identifiers = []

    if linha.get("email_hashed"):
        user_identifiers.append({"emailAddress": linha["email_hashed"]})
    if linha.get("phone_hashed"):
        user_identifiers.append({"phoneNumber": linha["phone_hashed"]})

    evento = {
        "transactionId": f"{linha['lead_id']}_{linha['etapa_funil']}",  # dedup
        "eventTimestamp": linha["data_hora_conversao"].isoformat() + "Z",  # ISO 8601
        "eventSource": "OTHER",            # obrigatório p/ offline; CRM = OTHER (validar na Fase 4)
        "conversionValue": float(linha["vl_faturamento_estimado"] or 0),
        "currency": "BRL",
        "userData": {"userIdentifiers": user_identifiers},
    }

    if linha.get("gclid"):
        evento["adIdentifiers"] = {"gclid": linha["gclid"]}   # determinístico + probabilístico juntos

    return evento

# ============================================================
# PARTE 4 - PAYLOAD BING (OfflineConversion - REST)
# Estrutura plana PascalCase. MicrosoftClickId obrigatório APENAS
# se não houver PII hasheada. ConversionName = nome EXATO do
# OfflineConversionGoal na conta (Fase 4). ConversionTime em UTC.
# Dedup: SEM campo dedicado - goal Unique (msclkid+goal+tempo);
# a control table é a proteção real contra reenvio.
# ============================================================

def montar_payload_bing(linha: dict, goal_name: str = None) -> dict:
    evento = {
        "ConversionName": goal_name or f"Lead_{linha['etapa_funil']}",
        "ConversionTime": linha["data_hora_conversao"].isoformat() + "Z",  # UTC obrigatório
        "ConversionValue": float(linha["vl_faturamento_estimado"] or 0),
        "ConversionCurrencyCode": "BRL",
    }

    if linha.get("msclkid"):
        evento["MicrosoftClickId"] = linha["msclkid"]
    if linha.get("email_hashed"):
        evento["HashedEmailAddress"] = linha["email_hashed"]
    if linha.get("phone_hashed"):
        evento["HashedPhoneNumber"] = linha["phone_hashed"]

    return evento

# ============================================================
# DISPATCHER - a Fase 4/5 chama isto por linha roteada
# ============================================================

MONTADORES = {
    "meta": montar_payload_meta,
    "google": montar_payload_google,
    "bing": montar_payload_bing,
}

def montar_payload(linha: dict) -> dict:
    return MONTADORES[linha["plataforma"]](linha)