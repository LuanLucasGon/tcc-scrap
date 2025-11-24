import os
import requests
from bs4 import BeautifulSoup
import json
import time
from playwright.sync_api import sync_playwright, Playwright

def run(playwright: Playwright):
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()

    page.goto("https://www.qconcursos.com/questoes-do-enem/questoes")

    page.wait_for_selector(".q-questions-list", timeout=15000)

    lista = page.locator(".q-questions-list")
    print(f"Lista encontrada? {lista.count() > 0}")

    itens = lista.locator(".q-question-item")
    print(f"Itens na lista: {itens.count()}")

    browser.close()

with sync_playwright() as playwright:
    run(playwright)