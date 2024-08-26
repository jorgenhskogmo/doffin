import requests

# Sett riktig API URL og API-nøkkel
SEARCH_API_URL = "https://api.doffin.no/public/v2/search"
DOWNLOAD_API_URL = "https://api.doffin.no/public/v2/download/{doffinId}"
API_KEY = "aa599b89f9884063afb32b71eda08ec3"  # Din API-nøkkel

# Konfigurer søkekriterier
params = {
    "numHitsPerPage": 2,
    "page": 1,
    "status": "ACTIVE"
}

headers = {
    "Ocp-Apim-Subscription-Key": API_KEY
}

# Gjør søkeforespørselen
response = requests.get(SEARCH_API_URL, headers=headers, params=params)

if response.status_code == 200:
    search_results = response.json()
    if search_results.get('notices'):
        # Hent første doffinId fra søkeresultatene
        doffin_id = search_results['notices'][0]['doffinId']
        print(f"Fant doffinId: {doffin_id}")
        
        # Last ned spesifikke detaljer ved hjelp av doffinId
        download_url = DOWNLOAD_API_URL.format(doffinId=doffin_id)
        download_response = requests.get(download_url, headers=headers)
        
        if download_response.status_code == 200:
            print("Data hentet:", download_response.json())
        else:
            print(f"Feil ved nedlasting av data: {download_response.status_code}")
    else:
        print("Ingen utlysninger funnet.")
else:
    print(f"Feil ved søk: {response.status_code}")
