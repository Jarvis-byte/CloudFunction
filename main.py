import requests
import firebase_admin
from firebase_admin import credentials, messaging, firestore

# Initialize Firebase Admin SDK with your service account JSON file
cred = credentials.Certificate("quotify-30a6c-firebase-adminsdk-nm88g-6862fb19f7.json")
firebase_admin.initialize_app(cred)


def fetch_quote_and_send_notification():
    # Initialize Firestore
    db = firestore.client()

    # Reference to the "DeviceToken" collection
    device_tokens_ref = db.collection("DeviceToken")

    # Fetch all documents (device tokens) from the collection
    device_tokens = device_tokens_ref.stream()

    # Create a list to store responses
    responses = []
    # Fetch data from the API
    api_url = "https://api.quotable.io/quotes/random"
    response = requests.get(api_url)

    for token_doc in device_tokens:
        device_token = token_doc.get("token")
        print(device_token)

        try:
            # Attempt to fetch data from the API
            response = requests.get(api_url)
            if response.status_code == 200:
                # Extract content and author from the response
                data = response.json()
                content = f" \n  ❝ {data[0]['content']} ❞  \n\n  👉🏻 🎤 {data[0]['author']}  "
                author = f" 🌞 Good Morning 🌻 "
                print(content)

                # Create a message to send
                message = messaging.Message(
                    notification=messaging.Notification(
                        title=author,
                        body=content,
                    ),
                    token=device_token,
                )

                try:
                    # Send the message
                    responseMessage = messaging.send(message)
                    responses.append(responseMessage)
                except Exception as send_error:
                    print(f"Error sending message to token {device_token}: {send_error}")

            else:
                print(f"Error: Received status code {response.status_code} from API")


        except Exception as e:
            print(f"Error occurred: {e}")


# Deploy this function as a Google Cloud Function

fetch_quote_and_send_notification()
