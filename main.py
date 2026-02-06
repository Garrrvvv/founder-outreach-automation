
print("🚀 RUNNING GITHUB CANDIDATE AUTOMATION")

import requests
import base64
import os
import pickle
from dotenv import load_dotenv
load_dotenv()
from email.mime.text import MIMEText

from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request


# CONFIG

TO_EMAIL = "neelamgulati235@gmail.com"
EMAIL_SUBJECT = "Strong Founding Engineer Candidates (via GitHub Signals)"

import os
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
 

SCOPES = ["https://www.googleapis.com/auth/gmail.send"]


# GMAIL AUTH


def get_gmail_service():
    creds = None

    if os.path.exists("token.pickle"):
        with open("token.pickle", "rb") as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json",
                SCOPES
            )
            creds = flow.run_local_server(port=0)

        with open("token.pickle", "wb") as token:
            pickle.dump(creds, token)

    return build("gmail", "v1", credentials=creds)  


# FETCH REAL CANDIDATES FROM GITHUB 

def fetch_github_candidates(limit=5):#number of candidates
    search_url = "https://api.github.com/search/users"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }

    params = {
        "q": "language:python location:india",
        "sort": "followers",
        "order": "desc",
        "per_page": limit
    }

    response = requests.get(search_url, headers=headers, params=params, timeout=10)
    response.raise_for_status()

    users = response.json().get("items", [])
    candidates = []

    for user in users:
        profile_url = user["url"]
        profile_resp = requests.get(profile_url, headers=headers, timeout=10)
        profile_resp.raise_for_status()
        profile = profile_resp.json()

        candidates.append({
            "name": profile.get("name") or profile.get("login"),
            "profile": profile.get("html_url"),
            "proof": f"{profile.get('followers')} followers, {profile.get('public_repos')} repos"
        })

    print(f"🟢 GitHub candidates fetched: {len(candidates)}")
    return candidates

# EMAIL BODY

def build_email_body(candidates):
    lines = []

    for c in candidates:
        lines.append(
            f"- {c['name']}\n"
            f"  GitHub: {c['profile']}\n"
            f"  Signal: {c['proof']}\n"
        )

    return f"""
Heyy Founder,

Instead of pitching blindly, I put together a short list of engineers I’d personally
consider for early-stage / founding roles.

These candidates were sourced automatically using "public GitHub signals"
(activity, followers, repositories):

{chr(10).join(lines)}

Sharing this as proof of work to demonstrate how I curate strong engineers.

Happy to help on a success-fee basis:
• 0 upfront
• 15% only if hired
• Free otherwise

Best,
Garv
"""


# SEND EMAIL


def send_email(to, subject, body):
    service = get_gmail_service()

    message = MIMEText(body)
    message["to"] = to
    message["subject"] = subject

    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()

    service.users().messages().send(
        userId="me",
        body={"raw": raw}
    ).execute()

    print(f" Email sent to {to}")


# MAIN


def main():
    candidates = fetch_github_candidates()

    if not candidates:
        print(" No GitHub candidates found. Exiting.")
        return

    email_body = build_email_body(candidates)
    send_email(TO_EMAIL, EMAIL_SUBJECT, email_body)

if __name__ == "__main__":
    main()
