# Fase 4 - envio meta

import requests, json

META_DATASET_ID = "xxxxxxxxxxxxxx"
META_ACCESS_TOKEN = "xxxxxxxxxxxxxx"       # do .env; não commita
TEST_EVENT_CODE  = "xxxxxxxxxxxxxx"    # da aba Testar eventos

evento = json.loads("""
{   "event_name": "Lead_Venda",   "event_time": 1783773201,   "action_source": "system_generated",   "event_id": "lead_0120_Venda",   "user_data": {     "em": [       "4c50a8a0738447d24c017ba029d94a27065e9102ddd4f0e099d3b6e53534681e"     ],     "ph": [       "eea5d6b55d7bd09d498f9b8221340c403bfac4d29459e4d07f7cd166ca4910a1"     ],     "fbc": "fb.1.1783773201650.fbclid_0120"   },   "custom_data": {     "value": 46734.8,     "currency": "BRL"   } }
""")

body = {"data": [evento], "test_event_code": TEST_EVENT_CODE}

resp = requests.post(
    f"https://graph.facebook.com/v21.0/{META_DATASET_ID}/events",
    params={"access_token": META_ACCESS_TOKEN},
    json=body,
    timeout=30,
)
print(f"HTTP {resp.status_code}")
print(json.dumps(resp.json(), indent=2))


# ## Response da request: HTTP 200
# # HTTP 200
# # {
# #   "events_received": 1,
# #   "messages": [],
# #   "fbtrace_id": "AL6vIankyRtcayTUmcPbBLr"
# # }
