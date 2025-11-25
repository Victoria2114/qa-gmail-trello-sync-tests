import pytest
import allure

from gmail.gmail_client import GmailClient
from trello.trello_client import TrelloClient


SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

@allure.step("Normalize Gmail subject '{subject}' to Trello card title")
def normalize_subject_to_card_title(subject: str) -> str:
    """
    Convert Gmail subject to the Trello card title used by the sync.

    Example:
        "Task: summarize the meeting"  -> "summarize the meeting"
        "Task: Clean up mail"          -> "Clean up mail"
        "Hello"                        -> "Hello"
    """
    if not subject:
        return ""
    s = subject.strip()
    prefix = "task:"
    if s.lower().startswith(prefix):
        # remove "Task:" prefix (case-insensitive) and trim spaces
        s = s[len(prefix):].strip()
    return s


# Keywords that mark system / security / non-task emails we want to ignore
SYSTEM_KEYWORDS = [
    "security",
    "verify",
    "verification",
    "sign-in",
    "sign in",
    "google account",
    "you're trying to",
    "verifying it's you",
    "verification code",
    "התראת",   
    "אימות",   
    "Set your new Atlassian password",
]

@allure.feature("Gmail–Trello sync")
@allure.story("Urgent emails mapped to urgent Trello cards")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.api
def test_urgent_emails_have_urgent_trello_cards():
    """
    Requirement:
    Each mail whose *body* contains the word “Urgent” should appear
    as a Trello card with the “Urgent” label.
    """
    gmail = GmailClient()
    trello = TrelloClient()

    messages = gmail.list_messages()
    cards = trello.get_cards()

    urgent_emails = []

    # collect all Gmail messages that contain "urgent" in body
    for m in messages:
        msg = gmail.get_message(m["id"])
        subject = gmail.extract_subject(msg) or ""
        body = (gmail.extract_body(msg) or "").strip()

        # skip system / security / irrelevant mails
        subj_lower = subject.lower()
        if any(k in subj_lower for k in SYSTEM_KEYWORDS):
            continue

        if "urgent" in body.lower():
            urgent_emails.append((subject, body))

    if not urgent_emails:
        pytest.skip("No Gmail messages containing 'urgent' in body were found.")

    for subject, _ in urgent_emails:
        card_title = normalize_subject_to_card_title(subject)

        matching_cards = [
            c for c in cards
            if c.get("name", "").strip().lower() == card_title.lower()
        ]

        assert matching_cards, (
            f"No Trello card found for urgent Gmail email with subject '{subject}' "
            f"(expected card title '{card_title}')."
        )

        card = matching_cards[0]
        labels = [lbl.get("name") for lbl in card.get("labels", [])]

        assert "Urgent" in labels, (
            f"Card '{card['name']}' for urgent email '{subject}' does not have 'Urgent' label."
        )

@pytest.mark.api
def test_merging_emails_same_subject_single_trello_card():
    """
    Requirement:
    If multiple Gmail messages share the same subject but have different bodies,
    Trello must contain ONE card with:
        - the subject (normalized) as the card title
        - the description containing all of the email bodies.
    """
    gmail = GmailClient()
    trello = TrelloClient()

    messages = gmail.list_messages()
    cards = trello.get_cards()

    # Group emails by subject (raw subject from Gmail)
    subject_groups: dict[str, list[str]] = {}

    for m in messages:
        msg = gmail.get_message(m["id"])
        subject = (gmail.extract_subject(msg) or "").strip()
        body = (gmail.extract_body(msg) or "").strip()

        # Skip empty/garbage
        if not subject or not body:
            continue

        # Skip system / security / OTP emails
        subj_lower = subject.lower()
        if any(k.lower() in subj_lower for k in SYSTEM_KEYWORDS):
            continue

        subject_groups.setdefault(subject, []).append(body)

    # Keep only subjects where we have more than one email
    merge_required = {
        subject: bodies
        for subject, bodies in subject_groups.items()
        if len(bodies) > 1
    }

    if not merge_required:
        pytest.skip("No Gmail subjects with multiple messages to validate merging logic.")

    for subject, bodies in merge_required.items():
        # Subject -> Trello card title ("Task: X" -> "X")
        card_title = normalize_subject_to_card_title(subject)

        # Find card(s) with that title
        matching_cards = [
            c for c in cards
            if (c.get("name") or "").strip().lower() == card_title.lower()
        ]

        assert matching_cards, (
            f"No Trello card found for merged Gmail emails with subject '{subject}' "
            f"(expected card title '{card_title}')."
        )

        card = matching_cards[0]
        description = card.get("desc") or ""

        # Every email body for this subject should appear in description
        for body in bodies:
            if not body:
                continue
            assert body in description, (
                f"Body '{body}' from Gmail not found in Trello card description "
                f"for subject '{subject}' / card '{card_title}'."
            )
