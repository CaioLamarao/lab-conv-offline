# send_google_test.py — token da SA via impersonation (sem gcloud) + events:ingest
import requests, json
import google.auth
from google.auth.transport.requests import Request
from google.auth import impersonated_credentials

SA = "sa-conversao-offline@lab-conversao-offline-vr.iam.gserviceaccount.com"
PROJETO = "lab-conversao-offline-vr"

# --- 1) tuas credenciais de usuário (Application Default Credentials) ---
source_creds, _ = google.auth.default()

# --- 2) impersonation: troca tua credencial por um token de 1h DA SA ---
target_creds = impersonated_credentials.Credentials(
    source_credentials=source_creds,
    target_principal=SA,
    target_scopes=["https://www.googleapis.com/auth/datamanager"],
    lifetime=3600,
)
target_creds.refresh(Request())
ACCESS_TOKEN = target_creds.token
print("token da SA obtido via impersonation")

# --- 3) envio (igual ao script anterior) ---
OPERATING_ACCOUNT = "2778985841"
CONVERSION_ACTION_ID = "7687456722"   # ctId da etapa do payload

evento = json.loads("""
{
  "transactionId": "lead_0024_Venda",
  "eventTimestamp": "2026-07-09T08:02:00.863977Z",
  "eventSource": "OTHER",
  "conversionValue": 25757.97,
  "currency": "BRL",
  "userData": {
    "userIdentifiers": [
      {
        "emailAddress": "36fbdcb2d50a9084edb42189e7fb793a7c24b062f65b825b0cc531d06af1cfd0"
      },
      {
        "phoneNumber": "42f726e7a74f1954323fba7f6483c80ddfcbe25a2772bababad25c7578244355"
      }
    ]
  },
  "adIdentifiers": {
    "gclid": "gclid_0024"
  }
}
""")

body = {
    "destinations": [{
        "operatingAccount": {"product": "GOOGLE_ADS", "accountId": OPERATING_ACCOUNT},
        "productDestinationId": CONVERSION_ACTION_ID,
    }],
    "encoding": "HEX",
    "events": [evento],
}

resp = requests.post(
    "https://datamanager.googleapis.com/v1/events:ingest",
    headers={
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "x-goog-user-project": PROJETO,
        "Content-Type": "application/json",
    },
    json=body,
    timeout=30,
)
print(f"HTTP {resp.status_code}")
print(json.dumps(resp.json(), indent=2))