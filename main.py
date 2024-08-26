import requests
import xml.etree.ElementTree as ET
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import os

# Sett riktig API URL og API-nøkkel
SEARCH_API_URL = "https://api.doffin.no/public/v2/search"
DOWNLOAD_API_URL = "https://api.doffin.no/public/v2/download/{doffinId}"
API_KEY = os.getenv('DOFFIN_API_KEY')  # Heroku environment variable

headers = {
    "Ocp-Apim-Subscription-Key": API_KEY
}

# Funksjon for å søke etter nøkkelord i XML-data og returnere hele forelder-elementer
def find_relevant_keywords(root, keywords):
    relevant_entries = []
    for elem in root.iter():
        if elem.text:
            for keyword in keywords:
                if keyword.lower() in elem.text.lower():
                    relevant_entries.append(ET.tostring(elem.getparent(), encoding='unicode').strip())
                    break
    return relevant_entries

# Funksjon for å hente og filtrere data fra API
def fetch_and_filter_data(status):
    params = {
        "numHitsPerPage": 10,
        "page": 1,
        "status": status
    }

    response = requests.get(SEARCH_API_URL, headers=headers, params=params)
    relevant_entries = []

    if response.status_code == 200:
        search_results = response.json()
        if search_results.get('hits'):
            for hit in search_results['hits']:
                doffin_id = hit['id']
                print(f"Fant doffinId: {doffin_id} med status {status}")

                download_url = DOWNLOAD_API_URL.format(doffinId=doffin_id)
                download_response = requests.get(download_url, headers=headers)

                if download_response.status_code == 200 and download_response.headers['Content-Type'] == 'application/xml':
                    try:
                        xml_data = download_response.content
                        root = ET.fromstring(xml_data)
                        print("XML-data hentet og parslet.")
                        keywords = ["droner", "UAV", "drone", "UTM", "droneflyging", "RFI"]
                        relevant_entries.extend(find_relevant_keywords(root, keywords))
                    except ET.ParseError as e:
                        print(f"Feil ved parsing av XML: {e}")
                else:
                    print(f"Feil ved nedlasting av data: {download_response.status_code}")
                    print("Rårespons:", download_response.text)
        else:
            print(f"Ingen utlysninger funnet for status {status}.")
    else:
        print(f"Feil ved søk for status {status}: {response.status_code}")
    return relevant_entries

# Funksjon for å sende e-post via SendGrid
def send_email(subject, body, to_email):
    message = Mail(
        from_email='din_email@gmail.com',  # Bytt til din SendGrid-verifiserte e-post
        to_emails=to_email,
        subject=subject,
        plain_text_content=body
    )
    try:
        sg = SendGridAPIClient(os.getenv('SENDGRID_API_KEY'))  # Henter SendGrid API-nøkkelen fra miljøvariabler
        response = sg.send(message)
        print(f"E-post sendt! Statuskode: {response.status_code}")
    except Exception as e:
        print(f"Feil ved sending av e-post: {e}")

# Hovedlogikken
def main():
    all_relevant_entries = []

    all_relevant_entries.extend(fetch_and_filter_data("ACTIVE"))
    all_relevant_entries.extend(fetch_and_filter_data("EXPIRED"))

    if all_relevant_entries:
        email_body = "\n\n".join(all_relevant_entries)
        send_email("Relevante utlysninger fra Doffin", email_body, "mottaker_email@gmail.com")
    else:
        print("Ingen relevante treff funnet.")

if __name__ == "__main__":
    main()
