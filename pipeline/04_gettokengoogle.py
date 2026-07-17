# roda UMA vez: abre o navegador, você loga com a conta Owner do projeto,
# e ele grava o arquivo de ADC que google.auth.default() encontra sozinho.
from google_auth_oauthlib.flow import InstalledAppFlow
import json, os

flow = InstalledAppFlow.from_client_config(
    {
        "installed": {
            "client_id": "764086051850-6qr4p6gpi6hn506pt8ejuq83di341hur.apps.googleusercontent.com",
            "client_secret": "xxxxxxxxxxxxxx",
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
        }
    },
    scopes=["https://www.googleapis.com/auth/cloud-platform"],
)
creds = flow.run_local_server(port=8081)

adc_path = os.path.join(os.environ["APPDATA"], "gcloud", "application_default_credentials.json")
os.makedirs(os.path.dirname(adc_path), exist_ok=True)
with open(adc_path, "w") as f:
    json.dump({
        "client_id": flow.client_config["client_id"],
        "client_secret": flow.client_config["client_secret"],
        "refresh_token": creds.refresh_token,
        "type": "authorized_user",
    }, f)
print("ADC gravado em", adc_path)