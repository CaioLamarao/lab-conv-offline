# Fase 4 - primeiro envio real Bing (1 Venda via ApplyOfflineConversions REST)
import requests, json
from urllib.parse import unquote

CLIENT_ID     = "xxxxxxxxxxxxxxxxx"
CLIENT_SECRET = "xxxxxxxxxxxxxxxxx"         # .env
REFRESH_TOKEN = "xxxxxxxxxxxxxxxxx"  # .env
DEV_TOKEN     = "xxxxxxxxxxxxxxxxx"
CUSTOMER_ID   = "xxxxxxxxxxxxxxxxx"           # CID
ACCOUNT_ID    = "xxxxxxxxxxxxxxxxx"           # AID

# 1) refresh -> access token (o ciclo que teu código fará em toda execução)
tok = requests.post(
    "https://login.microsoftonline.com/common/oauth2/v2.0/token",
    data={
        "client_id": CLIENT_ID, "client_secret": CLIENT_SECRET,
        "refresh_token": REFRESH_TOKEN, "grant_type": "refresh_token",
        "scope": "https://ads.microsoft.com/msads.manage offline_access",
    }, timeout=30,
).json()
access_token = tok["access_token"]
print("access token renovado, expira em", tok.get("expires_in"), "s")

# 2) payload (cola o JSON do montar_payload_bing impresso no Databricks - etapa Venda, data <= hoje)
conversao_msclickid = json.loads("""
{
  "ConversionName": "Lead_Venda",
  "ConversionTime": "2026-05-06T04:51:27.107385Z",
  "ConversionValue": 12643.8,
  "ConversionCurrencyCode": "BRL",
  "MicrosoftClickId": "msclkid_0083",
  "HashedEmailAddress": "e7a5f971097079ced9dcbd5b39f579d0215f0b9160d79d536d5361403a055e6e",
  "HashedPhoneNumber": "a009a8385262a44153ded9902ef5d1dec1d3c4a572803547a3a0125bad8c97e4"
}
""")

# 2) payload (cola o JSON do montar_payload_bing impresso no Databricks - etapa Venda, data <= hoje)
conversao = json.loads("""
{
  "ConversionName": "Lead_MQL",
  "ConversionTime": "2026-07-05T04:20:38.495535Z",
  "ConversionValue": 658.07,
  "ConversionCurrencyCode": "BRL",
  "HashedEmailAddress": "5a607f6d0526ccbe720f7c38bf7afbabb0d9906c46ba78c7795da1eccdc2aa4f",
  "HashedPhoneNumber": "93321e7887d523306ce072736c31606bc585490e331daa628a5be3a74d166ed3"
}
""")



# 3) envio
resp = requests.post(
    "https://campaign.api.bingads.microsoft.com/CampaignManagement/v13/OfflineConversions/Apply",
    headers={
        "Authorization": f"Bearer {access_token}",
        "DeveloperToken": DEV_TOKEN,
        "CustomerId": CUSTOMER_ID,
        "CustomerAccountId": ACCOUNT_ID,
        "Content-Type": "application/json",
    },
    json={"OfflineConversions": [conversao]},
    timeout=30,
)
print(f"HTTP {resp.status_code}")
print(json.dumps(resp.json(), indent=2))
body = {"OfflineConversions": [conversao]}
print("--- body exato que vai viajar ---")
print(json.dumps(body, indent=2))
print("--- tipo de 'conversao':", type(conversao))