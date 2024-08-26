import requests
import xml.etree.ElementTree as ET
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

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

# Funksjon for å søke etter nøkkelord
def find_relevant_notices(xml_data, keywords):
    root = ET.fromstring(xml_data)
    relevant_notices = []

    for elem in root.iter():
        if elem.text:  # Sjekk om elementet har tekst
            for keyword in keywords:
                if keyword.lower() in elem.text.lower():
                    relevant_notices.append(elem.text)
    
    return relevant_notices

# Funksjon for å sende e-post
def send_email(subject, body, to_email):
    from_email = os.environ.get('EMAIL')  # Henter e-post fra miljøvariabler
    password = os.environ.get('PASSWORD')  # Henter passord fra miljøvariabler

    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(from_email, password)
        text = msg.as_string()
        server.sendmail(from_email, to_email, text)
        server.quit()
        print("E-post sendt!")
    except Exception as e:
        print(f"Feil ved sending av e-post: {e}")

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
                    print("XML-data hentet og parslet.")
                    
                    # Definer søkeordene
                    keywords = ["droner", "UAV", "drone"]
                    
                    # Finn relevante utlysninger
                    relevant_notices = find_relevant_notices(xml_data, keywords)
                    
                    if relevant_notices:
                        # Lag e-postinnholdet
                        email_body = "\n".join(relevant_notices)
                        send_email("Relevante utlysninger fra Doffin", email_body, "mottaker_email@gmail.com")
                    else:
                        print("Ingen relevante utlysninger funnet.")
                
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
