import re
import allure
import pytest
from playwright.sync_api import Page, expect

BOARD_URL = "https://trello.com/b/OPIvELsg/droxi-ui-test"


@pytest.mark.ui
def test_urgent_cards_validation(page: Page):
    page.goto(BOARD_URL)

    # Wait for the board to load
    expect(page.get_by_test_id("card-name").first).to_be_visible()

    urgent_cards = []

    cards = page.get_by_test_id("card-name")
    cards_count = cards.count()

    for i in range(cards_count):
        card = cards.nth(i)

        # ---------- COLUMN STATUS ----------
        list_title_el = card.locator(
            "xpath=ancestor::*[.//*[@data-testid='list-name']][1]//*[@data-testid='list-name']"
        )
        status = list_title_el.inner_text().strip()

        # ---------- OPEN CARD ----------
        card.click()
        modal = page.get_by_role("dialog")
        expect(modal).to_be_visible()

        # ---------- TITLE ----------
        title_input = page.get_by_test_id("card-back-title-input")
        title = title_input.input_value().strip()

        # ---------- LABELS INSIDE MODAL ----------
        label_elements = page.get_by_test_id("card-label")
        label_texts = [el.inner_text().strip() for el in label_elements.all()]
        label_texts_lower = [lbl.lower() for lbl in label_texts]
        is_urgent = any("urgent" in lbl for lbl in label_texts_lower)
        print(f"Labels found: {label_texts}")
        print("Is urgent:", is_urgent)

        if is_urgent:
           print(">>> This card is URGENT <<<")
           page.get_by_test_id("description-edit-button").click()
           # ---------- DESCRIPTION ----------
           # Get editor container
           editor = page.get_by_test_id("editor-content-container")
           editor.wait_for()

          # Extract text
           description = editor.inner_text().strip()
           urgent_cards.append(
        {
            "title": title,
            "description": description,
            "labels": label_texts,
            "status": status,
        }
          )
        else:
             print("This card is NOT urgent")
  


       
        # ---------- CLOSE MODAL ----------
        page.get_by_role("button", name="Close dialog").click()
        expect(modal).not_to_be_visible()

    print("Urgent cards:", urgent_cards)
    assert urgent_cards, "No cards with 'urgent' label found"


@pytest.mark.ui
def test_specific_card_summarize_meeting(page: Page):
    page.goto(BOARD_URL)

    expected_title = "summarize the meeting"
    expected_description = "For all of us Please do so"
    expected_status = "To Do"
    expected_label = "New"

    # Wait for board to load
    cards = page.get_by_test_id("card-name")
    expect(cards.first).to_be_visible()

    # -------- Locate card on board --------
    target_card = cards.filter(has_text=expected_title).first
    expect(target_card).to_be_visible()

    # ----- Get column name (status) on board -----
    list_title_el = target_card.locator(
        "xpath=ancestor::*[.//*[@data-testid='list-name']][1]//*[@data-testid='list-name']"
    )
    status = list_title_el.inner_text().strip()
    print("Column (status) on board:", status)
    assert status == expected_status, f"Expected status '{expected_status}', got '{status}'"

    # -------- Open card modal --------
    target_card.click()
    modal = page.get_by_role("dialog")
    expect(modal).to_be_visible()

    # -------- Title in modal --------
    title_input = page.get_by_test_id("card-back-title-input")
    title = title_input.input_value().strip()
    print("Modal title:", title)
    assert title == expected_title

    # -------- Description in modal --------
    # Open description edit mode (if needed)
    page.get_by_test_id("description-edit-button").click()

    editor = page.get_by_test_id("editor-content-container")
    editor.wait_for()
    description = editor.inner_text().strip()

    print("Description:", description)
    assert description == expected_description

    # -------- Labels in modal --------
    label_elements = page.get_by_test_id("card-label")
    label_texts = [el.inner_text().strip() for el in label_elements.all()]
    print("Labels:", label_texts)
    assert any(lbl == expected_label for lbl in label_texts), (
        f"Label '{expected_label}' not found in {label_texts}"
    )

    # -------- Close modal and return to board view --------
    page.get_by_role("button", name="Close dialog").click()
    expect(modal).not_to_be_visible()

    # Ensure we are back on board and card is visible again
    expect(
        page.get_by_test_id("card-name").filter(has_text=expected_title).first
    ).to_be_visible()
