import os
import requests
from bs4 import BeautifulSoup
import json
import time
from playwright.sync_api import sync_playwright, Playwright

URL_ENEM = "https://www.qconcursos.com/questoes-do-enem/questoes"

def openBrowser():
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

def run(playwright: Playwright):
    browser, page = openBrowser()
    loadPage(page)

    questionsList = getQuestionList(page)
    print(f"Lista encontrada? {questionsList.count() > 0}")

    totalItems = countItens(questionsList)
    print(f"Itens na lista: {totalItems}")

    printQuestions(questionsList)

    browser.close()

if __name__ == "__main__":
    with sync_playwright() as playwright:
        run(playwright)