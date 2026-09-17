import os
import httpx
import smtplib
from email.message import EmailMessage

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
DISCORD_WEBHOOK = os.environ.get("DISCORD_WEBHOOK")
SMTP_HOST = os.environ.get("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.environ.get("SMTP_PORT", 587))
ALERT_EMAIL = os.environ.get("ALERT_EMAIL")
EMAIL_PASSWORD = os.environ.get("EMAIL_PASSWORD")

# Unique signature string found in your monorepo architecture
SIGNATURE_QUERY = "BUG-Bounty-Xterminator"

async def search_github_for_clones():
    """Searches public GitHub repositories for code structure matches."""
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json"
    }
    url = f"https://api.github.com/search/code?q={SIGNATURE_QUERY}+in:file"

    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            return data.get("items", [])
        else:
            print(f"[-] GitHub API Error: {response.status_code} - {response.text}")
            return []

def send_alerts(matches):
    """Sends immediate Discord and Email alerts with infringing repository links."""
    if not matches:
        print("[+] No unauthorized clones found.")
        return

    for item in matches:
        repo_name = item["repository"]["full_name"]
        repo_url = item["repository"]["html_url"]
        file_path = item["path"]

        # Skip your own official repository
        if "your-github-username" in repo_name.lower():
            continue

        alert_message = (
            f"🚨 **COPYCAT DETECTED!** 🚨\n"
            f"Repository: `{repo_name}`\n"
            f"Matched File: `{file_path}`\n"
            f"URL: {repo_url}\n\n"
            f"Action required: Review for code theft and issue a DMCA notice if necessary."
        )

        # 1. Send Discord Notification
        if DISCORD_WEBHOOK:
            httpx.post(DISCORD_WEBHOOK, json={"content": alert_message})

        # 2. Send Email Notification
        if ALERT_EMAIL and EMAIL_PASSWORD:
            msg = EmailMessage()
            msg.set_content(alert_message)
            msg.Subject = f"⚠️ Intellectual Property Alert: Clone found in {repo_name}"
            msg.From = ALERT_EMAIL
            msg.To = ALERT_EMAIL

            with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
                server.starttls()
                server.login(ALERT_EMAIL, EMAIL_PASSWORD)
                server.send_message(msg)
            print(f"[+] Alert sent for infringing repo: {repo_name}")

if __name__ == "__main__":
    import asyncio
    print("[*] Running Code Sentinel scan...")
    matches = asyncio.run(search_github_for_clones())
    send_alerts(matches)
