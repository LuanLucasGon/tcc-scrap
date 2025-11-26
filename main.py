import os
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

def extractQuestions(questionList):
    items = questionList.locator(".q-question-item")
    totalItems = items.count()

    questions = []

    for i in range (totalItems):
        card = items.nth(i)
        questionTexxt = card.locator(".q-question-body").inner_text().strip()

        questions.append({
            "text": questionTexxt,
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

    printQuestions(questionsList)

    questions = extractQuestions(questionsList)
    saveToJson(questions, "questions.json")

    browser.close()

if __name__ == "__main__":
    with sync_playwright() as playwright:
        run(playwright)