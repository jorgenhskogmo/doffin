import requests
import xml.etree.ElementTree as ET

# Sett riktig API URL og API-nøkkel
SEARCH_API_URL = "https://api.doffin.no/public/v2/search"
DOWNLOAD_API_URL = "https://api.doffin.no/public/v2/download/{doffinId}"
API_KEY = "aa599b89f9884063afb32b71eda08ec3"  # Din API-nøkkel

headers = {
    "Ocp-Apim-Subscription-Key": API_KEY
}

# Funksjon for å søke etter nøkkelord i XML-data og returnere hele forelder-elementer
def find_relevant_keywords(root, keywords):
    relevant_entries = []
    
    # Gå gjennom alle elementene i XML-treet og sjekk om teksten inneholder nøkkelordene
    for elem in root.iter():
        if elem.text:  # Sjekk om elementet har tekst
            for keyword in keywords:
                if keyword.lower() in elem.text.lower():
                    # Lagre hele forelder-elementet hvis nøkkelordet blir funnet
                    relevant_entries.append(ET.tostring(elem.getparent(), encoding='unicode').strip())
                    break  # Stop iterating through keywords once a match is found
    
    return relevant_entries

# Funksjon for å hente og filtrere data fra API
def fetch_and_filter_data(status):
    params = {
        "numHitsPerPage": 10,
        "page": 1,
        "status": status
    }

    response = requests.get(SEARCH_API_URL, headers=headers, params=params)

    if response.status_code == 200:
        search_results = response.json()
        
        if search_results.get('hits'):
            for hit in search_results['hits']:
                doffin_id = hit['id']
                print(f"Fant doffinId: {doffin_id} med status {status}")
                
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
                        keywords = ["droner", "UAV", "drone", "UTM", "droneflyging"]
                        
                        # Finn relevante treff
                        relevant_entries = find_relevant_keywords(root, keywords)
                        
                        if relevant_entries:
                            print("Relevante treff funnet:")
                            for entry in relevant_entries:
                                print(entry)
                        else:
                            print("Ingen relevante treff funnet.")
                    
                    except ET.ParseError as e:
                        print(f"Feil ved parsing av XML: {e}")
                else:
                    print(f"Feil ved nedlasting av data: {download_response.status_code}")
                    print("Rårespons:", download_response.text)
        else:
            print(f"Ingen utlysninger funnet for status {status}.")
            print("Full respons fra API:", search_results)
    else:
        print(f"Feil ved søk for status {status}: {response.status_code}")
        print("Detaljert respons:", response.text)

# Hovedlogikken
def main():
    # Hent data for aktive utlysninger
    fetch_and_filter_data("ACTIVE")
    
    # Hent data for utgåtte utlysninger
    fetch_and_filter_data("EXPIRED")

# Kjør hovedfunksjonen
if __name__ == "__main__":
    main()
