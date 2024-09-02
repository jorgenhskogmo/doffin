import requests

def fetch_data():
    url = "https://betaapi.doffin.no/public/v2/search?searchString=drone"
    headers = {
        "Cache-Control": "no-cache",
        "Ocp-Apim-Subscription-Key": "de0c08076a7a4bd69c1d52aad359ef43"
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        # Lagre responsen i en fil
        with open("api_response.txt", "w") as file:
            file.write(response.text)
        print("Data fetched and saved successfully.")
    else:
        print(f"Failed to fetch data. Status code: {response.status_code}")

if __name__ == "__main__":
    fetch_data()