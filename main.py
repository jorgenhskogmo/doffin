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

# Funksjon for å søke etter nøkkelord i XML-data
def find_relevant_keywords(root, keywords):
    relevant_entries = []
    
    # Gå gjennom alle elementene i XML-treet og sjekk om teksten inneholder nøkkelordene
    for elem in root.iter():
        if elem.text:  # Sjekk om elementet har tekst
            for keyword in keywords:
                if keyword.lower() in elem.text.lower():
                    relevant_entries.append(elem.text.strip())
    
    return relevant_entries

# Hovedlogikken
def main():
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
                    xml_data = download_response.content
                    root = ET.fromstring(xml_data)
                    print("XML-data hentet og parslet.")
                    
                    # Definer søkeordene
                    keywords = ["droner", "UAV", "drone"]
                    
                    # Finn relevante treff
                    relevant_entries = find_relevant_keywords(root, keywords)
                    
                    if relevant_entries:
                        print("Relevante treff funnet:")
                        for entry in relevant_entries:
                            print(f"- {entry}")
                    else:
                        print("Ingen relevante treff funnet.")
                
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

# Kjør hovedfunksjonen
if __name__ == "__main__":
    main()
