# QA Automation Assignment – Gmail ↔ Trello Sync

This repository contains automated tests (API + UI) for a **fictional system** that:

- Watches a **Gmail inbox**
- Creates / updates cards on a **Trello board**
- Applies extra logic such as:
  - “Urgent” emails → cards with an **Urgent** label
  - Emails with the same subject → **merged** into one Trello card
  - Card status ↔ Gmail folder (Inbox / Trash / etc.)

The goal of this project is to validate this behavior using:

- **Python + pytest**
- **Trello REST API**
- **Gmail API**
- **Playwright** for Trello UI tests
- **Allure** for reporting

---

## 🧱 Project Structure

```text
qa-gmail-trello-sync-tests/
  gmail/
    gmail_client.py        # Wrapper around Gmail API
  trello/
    trello_client.py       # Wrapper around Trello API (you configure keys here)
  tests/
    test_sync.py           # API tests (Gmail ↔ Trello sync logic)
    ui/
      conftest.py          # Playwright config, auth_state usage
      test_trello_ui.py    # Trello board UI tests (labels, status, etc.)
      test_save_auth.py    # One-time helper to save Trello login state
  pytest.ini               # pytest configuration, markers (api, ui)
  requirements.txt         # Python dependencies
