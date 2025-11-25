import base64
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

class GmailClient:
    def __init__(self, token_file="token.json"):
        scopes = ["https://mail.google.com/"]
        self.creds = Credentials.from_authorized_user_file(token_file, scopes)
        self.service = build("gmail", "v1", credentials=self.creds)

    def list_messages(self):
        result = self.service.users().messages().list(userId="me").execute()
        return result.get("messages", [])

    def get_message(self, msg_id):
        return self.service.users().messages().get(userId="me", id=msg_id, format="full").execute()

    def extract_subject(self, msg):
        headers = msg["payload"]["headers"]
        for h in headers:
            if h["name"].lower() == "subject":
                return h["value"]
        return ""

    def extract_body(self, msg) -> str:
        """
        Safely extract the email body text.
        Gmail message payloads can have different formats (single-part, 
        multi-part, nested parts), so this function tries multiple strategies
        to find the actual body content.
        """
        payload = msg.get("payload", {})

        # 1. First try to get body.data directly from payload['body']
        body = payload.get("body", {})
        data = body.get("data")

        # 2. If not found, walk through parts recursively
        if not data:
            parts = payload.get("parts", [])

            def walk_parts(parts_list):
                for part in parts_list:
                    # Try to extract text/plain or text/html content
                    mime_type = part.get("mimeType", "")
                    body = part.get("body", {})
                    part_data = body.get("data")

                    if part_data and (
                        mime_type.startswith("text/plain")
                        or mime_type.startswith("text/html")
                    ):
                        return part_data

                    # If part contains nested parts (multipart/alternative)
                    inner = part.get("parts", [])
                    if inner:
                        nested_data = walk_parts(inner)
                        if nested_data:
                            return nested_data

                return None

            data = walk_parts(parts)

        # 3. If still nothing was found, return empty string
        if not data:
            return ""

        # 4. Decode base64-encoded email body into readable text
        decoded_bytes = base64.urlsafe_b64decode(data)
        return decoded_bytes.decode("utf-8", errors="ignore")

