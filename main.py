import os
import re

import requests
from bs4 import BeautifulSoup
import json
import time
from urllib.parse import urljoin
from playwright.sync_api import sync_playwright, Playwright
from sqlalchemy import func, select
from sqlalchemy.dialects.postgresql import insert

from db.database import SessionLocal
from db.models import Questao

BASE_URL = "https://www.qconcursos.com"
URL_ENEM = "https://www.qconcursos.com/questoes-do-enem/questoes"

EXAM_INFO_LABELS = {
    "Ano": "year",
    "Banca": "examBoard",
    "Órgão": "organization",
    "Prova": "examTitle",
}

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

def extractQuestionId(card):
    return card.locator(".q-ref .q-id a").inner_text().strip()

def extractSubjectAndTopics(card):
    links = card.locator(".q-question-breadcrumb a").all()

    texts = []
    for link in links:
        text = re.sub(r"\s+", " ", link.inner_text()).strip()
        text = text.rstrip(",").strip()
        if text:
            texts.append(text)

    subject = texts[0] if texts else ""
    topics = texts[1:]

    return subject, topics

def extractExamInfo(card):
    info = {key: "" for key in EXAM_INFO_LABELS.values()}
    info["examUrl"] = ""

    infoSpans = card.locator(".q-question-info > span").all()

    for span in infoSpans:
        strongLocator = span.locator("strong")
        if strongLocator.count() == 0:
            continue

        label = strongLocator.inner_text().strip().rstrip(":").strip()
        key = EXAM_INFO_LABELS.get(label)
        if not key:
            continue

        if key == "examTitle":
            examLink = span.locator("a")
            if examLink.count() > 0:
                info["examTitle"] = examLink.inner_text().strip()
                href = (examLink.first.get_attribute("href") or "").strip()
                if href:
                    info["examUrl"] = urljoin(BASE_URL, href)
        else:
            fullText = span.text_content() or ""
            strongText = strongLocator.text_content() or ""
            value = fullText.replace(strongText, "", 1)
            info[key] = re.sub(r"\s+", " ", value).strip()

    return info

def extractQuestionEnunciation(card):
    enunciation = card.locator(".q-question-body .q-question-enunciation")
    if enunciation.count() == 0:
        return ""

    node = enunciation.first
    text = node.inner_text().strip()

    parts = [text] if text else []
    for img in node.locator("img").all():
        src = (img.get_attribute("src") or "").strip()
        if src:
            parts.append(f"[IMAGE] {src}")
        else:
            parts.append("[IMAGE]")

    return "\n".join(parts).strip()

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
        subject, topics = extractSubjectAndTopics(card)

        question = {
            "questionId": extractQuestionId(card),
            "subject": subject,
            "topics": topics,
        }
        question.update(extractExamInfo(card))
        question.update({
            "associatedText": extractAssociatedText(card),
            "enunciation": extractQuestionEnunciation(card),
            "alternatives": extractAlternatives(card),
        })

        questions.append(question)

    return questions

def saveToJson(data, fileName):
    with open(fileName, 'w', encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)
    print(f"Saved {len(data)} question to file: {fileName}")

QUESTION_COLUMN_MAP = {
    "questionId": "question_id",
    "subject": "subject",
    "topics": "topics",
    "year": "year",
    "examBoard": "exam_board",
    "organization": "organization",
    "examTitle": "exam_title",
    "examUrl": "exam_url",
    "associatedText": "associated_text",
    "enunciation": "enunciation",
    "alternatives": "alternatives",
}

def toQuestionRow(question):
    return {column: question.get(key) for key, column in QUESTION_COLUMN_MAP.items()}

def saveToDatabase(questions):
    rows = [toQuestionRow(question) for question in questions if question.get("questionId")]
    if not rows:
        print("Nenhuma questao para salvar no banco.")
        return

    questionIds = [row["question_id"] for row in rows]

    session = SessionLocal()
    try:
        existing = set(
            session.scalars(
                select(Questao.question_id).where(Questao.question_id.in_(questionIds))
            )
        )

        updatableColumns = [column for column in QUESTION_COLUMN_MAP.values() if column != "question_id"]
        stmt = insert(Questao).values(rows)
        stmt = stmt.on_conflict_do_update(
            index_elements=["question_id"],
            set_={
                **{column: stmt.excluded[column] for column in updatableColumns},
                "updated_at": func.now(),
            },
        )
        session.execute(stmt)
        session.commit()
    finally:
        session.close()

    inserted = sum(1 for questionId in questionIds if questionId not in existing)
    updated = len(questionIds) - inserted
    print(f"Banco: {inserted} inseridas, {updated} atualizadas (tabela questao).")

def run(playwright: Playwright):
    browser, page = openBrowser(playwright)
    loadPage(page)

    questionsList = getQuestionList(page)
    print(f"Lista encontrada? {questionsList.count() > 0}")

    totalItems = countItens(questionsList)
    print(f"Itens na lista: {totalItems}")

    questions = extractQuestions(questionsList)
    saveToJson(questions, "questions.json")
    saveToDatabase(questions)

    browser.close()

if __name__ == "__main__":
    with sync_playwright() as playwright:
        run(playwright)