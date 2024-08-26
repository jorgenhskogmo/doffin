import requests
from datetime import datetime, timedelta

API_URL = "https://dof-notices-prod-api.azure-api.net/api/v2/notice/notices/search-esentool"
API_KEY = ""  # Din API-nøkkel

# Konfigurer søkekriteriene
params = {
    "publishedAfter": (datetime.now() - timedelta(days=1)).isoformat(),  # Utlysninger publisert de siste 24 timene
    "statuses": "SUBMITTED",
    "size": 10,  # Hvor mange resultater du vil ha per side
    "sortDirection": "DESC",
    "sortProperty": "publishedDate"
}

headers = {
    "Ocp-Apim-Subscription-Key": API_KEY
}

# Gjør API-forespørselen
response = requests.get(API_URL, params=params, headers=headers)

if response.status_code == 200:
    notices = response.json()  # Håndterer responsen
    # Send utlysningene via e-post, lagre dem, eller hva som er ønskelig
    print(notices)
else:
    print(f"Feil ved henting av utlysninger: {response.status_code}")
