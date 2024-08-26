import requests
import xml.etree.ElementTree as ET

# Sett riktig API URL og API-nøkkel
SEARCH_API_URL = "https://api.doffin.no/public/v2/search"
DOWNLOAD_API_URL = "https://api.doffin.no/public/v2/download/{doffinId}"
API_KEY = "aa599b89f9884063afb32b71eda08ec3"  # Din API-nøkkel

# Konfigurer søkekriterier
params = {
    "numHitsPerPage": 5,
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
    
    if search_results.get('hits'):
        doffin_id = search_results['hits'][0]['id']
        print(f"Fant doffinId: {doffin_id}")
        
        # Last ned spesifikke detaljer ved hjelp av doffinId
        download_url = DOWNLOAD_API_URL.format(doffinId=doffin_id)
        download_response = requests.get(download_url, headers=headers)
        
        # Sjekk om responsen er XML
        if download_response.status_code == 200 and download_response.headers['Content-Type'] == 'application/xml':
            try:
                # Parse XML-innholdet
                root = ET.fromstring(download_response.content)
                print("XML-data hentet og parslet.")
                
                # Eksempel på hvordan du kan trekke ut informasjon fra XML
                namespaces = {
                    'cbc': "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
                    'cac': "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
                }
                
                # Hente ut spesifikke data, f.eks. "ContractFolderID"
                contract_id = root.find('.//cbc:ContractFolderID', namespaces)
                if contract_id is not None:
                    print(f"ContractFolderID: {contract_id.text}")
                
                # Hente ut "Buyer" informasjon
                buyer_name = root.find('.//cac:PartyName/cbc:Name', namespaces)
                if buyer_name is not None:
                    print(f"Kjøper: {buyer_name.text}")
                
            except ET.ParseError as e:
                print(f"Feil ved parsing av XML: {e}")
        else:
            print(f"Feil ved nedlasting av data: {download_response.status_code}")
            print("Rårespons:", download_response.text)
    else:
        print("Ingen utlysninger funnet.")
        print("Full respons fra API:", search_results)
else:
    print(f"Feil ved søk: {response.status_code}")
    print("Detaljert respons:", response.text)
