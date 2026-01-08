import os
import re

import requests
from bs4 import BeautifulSoup
import json
import time
from playwright.sync_api import sync_playwright, Playwright

URL_ENEM = "https://www.qconcursos.com/questoes-do-enem/questoes"

def openBrowser(playwright: Playwright):
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
    return browser, page

def loadPage(page):
    page.goto(URL_ENEM)
    page.wait_for_selector(".q-questions-list", timeout=15000)

def getQuestionList(page):
    return page.locator(".q-questions-list")

def countItens(questionsList):
    items = questionsList.locator(".q-question-item")
    return items.count()

def printQuestions(questionsList):
    items = questionsList.locator(".q-question-item")
    totalItems = items.count()

    for i in range (totalItems):
        card = items.nth(i)
        questionTexxt = card.locator(".q-question-body").inner_text().strip()
        print(f"Question {i+1}: {questionTexxt}")

def extractQuestionEnunciation(card):
    return card.locator(".q-question-body .q-question-enunciation").inner_text().strip()

def extractAssociatedText(card):
    content = card.locator('.q-question-body .q-question-text div[id^="question-"][id$="-text"]')
    if content.count() == 0:
        return ""

    parts = []

    blocks = content.first.locator(":scope > div").all()
    for block in blocks:
        hasImage = block.locator("img").count() > 0
        text = (block.text_content() or "").replace("\u00a0", " ").strip()

        if text:
            parts.append(text)

        if hasImage:
            src = (block.locator("img").first.get_attribute("src") or "").strip()
            if src:
                parts.append(f"[IMAGE] {src}")
            else:
                parts.append("[IMAGE]")

    return "\n".join(parts).strip()

def extractAlternative(option):
    letter = option.locator("span.q-option-item").inner_text().strip()

    content = option.locator("div.q-item-enum.js-alternative-content").first

    text = (content.text_content() or "").replace("\u00a0", " ").strip()
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    normalizedText = "\n".join(lines).strip()

    images = []
    for img in content.locator("img").all():
        src = (img.get_attribute("src") or "").strip()
        if src:
            images.append(src)

    return letter, normalizedText, images

def extractAlternatives(card):
    alternatives = {}

    optionLabels = card.locator(
        ".q-question-options label.q-radio-button.js-choose-alternative"
    )

    for option in optionLabels.all():
        letter, text, images = extractAlternative(option)

        if not letter:
            continue

        alternatives[letter] = {
            "text": text,
            "images": images,
        }

    return alternatives

def extractQuestions(questionList):
    questions = []

    questionItems = questionList.locator(".q-question-item")

    for card in questionItems.all():
        questions.append({
            "associatedText": extractAssociatedText(card),
            "enunciation": extractQuestionEnunciation(card),
            "alternatives": extractAlternatives(card),
        })

    return questions

def saveToJson(data, fileName):
    with open(fileName, 'w', encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)
    print(f"Saved {len(data)} question to file: {fileName}")

def run(playwright: Playwright):
    browser, page = openBrowser(playwright)
    loadPage(page)

    questionsList = getQuestionList(page)
    print(f"Lista encontrada? {questionsList.count() > 0}")

    totalItems = countItens(questionsList)
    print(f"Itens na lista: {totalItems}")

    questions = extractQuestions(questionsList)
    saveToJson(questions, "questions.json")

    browser.close()

if __name__ == "__main__":
    with sync_playwright() as playwright:
        run(playwright)