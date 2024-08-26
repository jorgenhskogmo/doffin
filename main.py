import os
import requests
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

API_URL = "https://dof-notices-prod-api.azure-api.net/api/v2/notice/notices/search-esentool"
API_KEY = os.getenv("OCP_APIM_SUBSCRIPTION_KEY")  # Henter API-nøkkelen fra miljøvariabler

# E-postkonfigurasjon fra miljøvariabler
SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))  # Standard TLS-port er 587
SMTP_USERNAME = os.getenv("SMTP_USERNAME")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
TO_EMAIL = os.getenv("TO_EMAIL")

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

def send_email(subject, body, to_email):
    msg = MIMEMultipart()
    msg['From'] = SMTP_USERNAME
    msg['To'] = to_email
    msg['Subject'] = subject

    # Legg til e-postinnhold
    msg.attach(MIMEText(body, 'plain'))

    try:
        # Koble til SMTP-serveren og send e-posten
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()  # Start TLS for sikker tilkobling
        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        server.sendmail(SMTP_USERNAME, to_email, msg.as_string())
        server.quit()
        print(f"E-post sendt til {to_email}")
    except Exception as e:
        print(f"Kunne ikke sende e-post: {e}")

if response.status_code == 200:
    notices = response.json()  # Håndterer responsen
    
    # Formaterer responsen til en lesbar tekst
    email_body = "Her er de siste utlysningene:\n\n"
    for notice in notices.get('notices', []):
        title = notice.get('title', 'Ingen tittel')
        published_date = notice.get('publishedDate', 'Ingen dato')
        email_body += f"Tittel: {title}\nPublisert: {published_date}\n\n"
    
    # Send e-post med resultatene
    send_email("Siste utlysninger fra Doffin", email_body, TO_EMAIL)
else:
    error_message = f"Feil ved henting av utlysninger: {response.status_code}"
    print(error_message)
    send_email("Feil ved henting av utlysninger", error_message, TO_EMAIL)
