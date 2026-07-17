# get_bing_tokens.py — roda UMA vez; guarda o refresh_token no .env
import requests, json
from urllib.parse import unquote

CLIENT_ID = "token"
CLIENT_SECRET = "token"   # do .env
CODE = unquote("M.C541_BL2.2.U.MsaArtifacts.DhXshwex9dI8bEatM9!wPe9rxEmmeH!aCQtyBicXcEhq6zJKW8DCZEbcZA*r9c6McEJCeKa6bHXtX!hc3XTvkXePjUMY3hk1MbXG8U8PJ!JBTyWME3wQlohw1DY*Of3ZeJBj!MlEpk50kn0yhPy2MYWPnM1o2no8*Lx5MQF5cdP3doToNS0l*BkQ8cWllU6b2OG4xXHGaBU77vGNpugqgKc7sUA!gyz73hCSsorOA2FRbNWyoZ1jyyI3n4N8SypjaZAAJ1CrYxT37k4LCIqvr8CDP3tiozCeyXPk1AR4nEQcmTDiCF27mmkbc!r6amDtbdwem88jnovSjaAcYQDK8TmJyqWRFD3a6y5P2sDktHltraF6ZRZlmCe1oU0DMu!5UfJu6VgRINpzCvsZMMGJ9L6hUvgV37NpVPGWcBAfZqA61CqS!kX*D0caxxrcqcCWyrH1VoHsu62PRjQ9ry5fr9yPN8WyOsKn0Ycv!1NBq!*IpJ8hp6GntwaDHJ05lECi5xcnjgkERs7LGnyekZi6kHxTN*uJB!G3PPDuiIXQzu1PWgbgZ!Fn2B2EOLjAyPd0mg9FcF!so*rkeHjoc5uzXhD7LvBwMfQz5TSrngv2tkeTMJDYq7P5yXT1mbWqnlkqLg%24%24")   # cola cru; unquote converte %24 -> $ etc.

resp = requests.post(
    "https://login.microsoftonline.com/common/oauth2/v2.0/token",
    data={
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "code": CODE,
        "grant_type": "authorization_code",
        "redirect_uri": "http://localhost:8080",
        "scope": "https://ads.microsoft.com/msads.manage offline_access",
    },
    timeout=30,
)
tokens = resp.json()
print(f"HTTP {resp.status_code}")
print("access_token :", tokens.get("access_token", "")[:25] + "...")
print("refresh_token:", tokens.get("refresh_token", "")[:25] + "...")
print("expires_in   :", tokens.get("expires_in"))
# print(json.dumps(tokens, indent=2))   # imprime o corpo inteiro da resposta
# copia o refresh_token COMPLETO pro .env (BING_REFRESH_TOKEN) — não deixa em print de notebook