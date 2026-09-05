import re
from dataclasses import asdict
from urllib.parse import urljoin

import json
from bs4 import BeautifulSoup
from playwright.sync_api import Browser, Locator, Page, Playwright, sync_playwright
from sqlalchemy.orm import Session

from infra.database import SessionLocal
from question.dtos.question_scraped_dto import QuestionScrapedDTO
from question.repository.question_repository import QuestionRepository
from question.repository.upsert_result import UpsertResult
from subject.repository.subject_repository import SubjectRepository
from topic.repository.topic_repository import TopicRepository

BASE_URL: str = "https://www.qconcursos.com"
URL_ENEM: str = "https://www.qconcursos.com/questoes-do-enem/questoes"

EXAM_INFO_LABELS: dict[str, str] = {
    "Ano": "year",
    "Banca": "exam_board",
    "Órgão": "organization",
    "Prova": "exam_title",
}


def open_browser(playwright: Playwright) -> tuple[Browser, Page]:
    """Abre um Chromium visível e devolve o browser e uma aba nova."""
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
    return browser, page


def load_page(page: Page) -> None:
    """Navega até a listagem de questões do ENEM e aguarda ela carregar."""
    page.goto(URL_ENEM)
    page.wait_for_selector(".q-questions-list", timeout=15000)


def get_question_list(page: Page) -> Locator:
    """Retorna o locator do container que envolve os cards de questão."""
    return page.locator(".q-questions-list")


def count_items(question_list: Locator) -> int:
    """Conta quantos cards de questão existem na listagem."""
    return question_list.locator(".q-question-item").count()


def extract_question_id(card: Locator) -> str:
    """Extrai o identificador da questão (ex.: ``Q3761251``) de um card."""
    return card.locator(".q-ref .q-id a").inner_text().strip()


def extract_subject_and_topics(card: Locator) -> tuple[str, list[str]]:
    """Extrai a matéria (primeiro item) e os tópicos (demais) do breadcrumb."""
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


def extract_exam_info(card: Locator) -> dict[str, str]:
    """Extrai ano, banca, órgão, prova e URL da prova a partir dos ``<span>``."""
    info = {key: "" for key in EXAM_INFO_LABELS.values()}
    info["exam_url"] = ""

    info_spans = card.locator(".q-question-info > span").all()

    for span in info_spans:
        strong_locator = span.locator("strong")
        if strong_locator.count() == 0:
            continue

        label = strong_locator.inner_text().strip().rstrip(":").strip()
        key = EXAM_INFO_LABELS.get(label)
        if not key:
            continue

        if key == "exam_title":
            exam_link = span.locator("a")
            if exam_link.count() > 0:
                info["exam_title"] = exam_link.inner_text().strip()
                href = (exam_link.first.get_attribute("href") or "").strip()
                if href:
                    info["exam_url"] = urljoin(BASE_URL, href)
        else:
            full_text = span.text_content() or ""
            strong_text = strong_locator.text_content() or ""
            value = full_text.replace(strong_text, "", 1)
            info[key] = re.sub(r"\s+", " ", value).strip()

    return info


def extract_question_enunciation(card: Locator) -> str:
    """Extrai o enunciado da questão, com imagens citadas como ``[IMAGE] <src>``."""
    enunciation = card.locator(".q-question-body .q-question-enunciation")
    if enunciation.count() == 0:
        return ""

    node = enunciation.first
    text = node.inner_text().strip()

    parts = [text] if text else []
    for img in node.locator("img").all():
        src = (img.get_attribute("src") or "").strip()
        parts.append(f"[IMAGE] {src}" if src else "[IMAGE]")

    return "\n".join(parts).strip()


def extract_associated_text(card: Locator) -> str:
    """Extrai o texto-base associado à questão (quando existir), com imagens."""
    selector = (
        '.q-question-body .q-question-text '
        'div[id^="question-"][id$="-text"]'
    )
    content = card.locator(selector)
    if content.count() == 0:
        return ""

    parts = []

    blocks = content.first.locator(":scope > div").all()
    for block in blocks:
        has_image = block.locator("img").count() > 0
        text = (block.text_content() or "").replace(" ", " ").strip()

        if text:
            parts.append(text)

        if has_image:
            src = (block.locator("img").first.get_attribute("src") or "").strip()
            parts.append(f"[IMAGE] {src}" if src else "[IMAGE]")

    return "\n".join(parts).strip()


def extract_alternative(option: Locator) -> tuple[str, str, list[str]]:
    """Extrai letra, texto normalizado e imagens de uma alternativa."""
    letter = option.locator("span.q-option-item").inner_text().strip()

    content = option.locator("div.q-item-enum.js-alternative-content").first

    text = (content.text_content() or "").replace(" ", " ").strip()
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    normalized_text = "\n".join(lines).strip()

    images = []
    for img in content.locator("img").all():
        src = (img.get_attribute("src") or "").strip()
        if src:
            images.append(src)

    return letter, normalized_text, images


def extract_alternatives(card: Locator) -> dict[str, dict[str, object]]:
    """Extrai todas as alternativas de um card, indexadas pela letra."""
    alternatives: dict[str, dict[str, object]] = {}

    option_labels = card.locator(
        ".q-question-options label.q-radio-button.js-choose-alternative"
    )

    for option in option_labels.all():
        letter, text, images = extract_alternative(option)

        if not letter:
            continue

        alternatives[letter] = {
            "text": text,
            "images": images,
        }

    return alternatives


def extract_answers_from_html(html: str) -> dict[int, str]:
    """Extrai o gabarito (``numero -> letra``) do bloco "Respostas" do rodapé.

    A letra não é restrita a A-E: questões anuladas aparecem como ``X`` no
    site, e descartar esse número desalinharia a correlação por ordem de
    todas as questões seguintes na mesma página (ver ``correlate_answers_by_order``).
    """
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()

    text = soup.get_text("\n", strip=True)
    match = re.search(r"\bRespostas\b(.*)", text, re.DOTALL | re.IGNORECASE)
    if not match:
        return {}

    pairs = re.findall(r"(\d+)\s*:\s*([A-Za-z])", match.group(1))
    return {int(number): letter.upper() for number, letter in pairs}


def extract_answers(page: Page) -> dict[int, str]:
    """Extrai o gabarito da página atualmente carregada."""
    return extract_answers_from_html(page.content())


def correlate_answers_by_order(answers: dict[int, str], count: int) -> list[str | None]:
    """Associa cada uma das ``count`` questões (na ordem em que aparecem na
    página) à letra correspondente em ``answers``, pela ordem relativa dos
    números do gabarito — não pelo valor numérico em si, já que o gabarito
    de uma página não necessariamente começa em 1.
    """
    ordered_letters = [answers[number] for number in sorted(answers)]
    return [
        ordered_letters[i] if i < len(ordered_letters) else None
        for i in range(count)
    ]


def extract_questions(
    question_list: Locator, answers: dict[int, str]
) -> list[QuestionScrapedDTO]:
    """Percorre todos os cards da listagem e monta um DTO para cada questão."""
    questions = []

    cards = question_list.locator(".q-question-item").all()
    correct_answers = correlate_answers_by_order(answers, len(cards))

    for card, correct_answer in zip(cards, correct_answers):
        subject, topics = extract_subject_and_topics(card)

        payload = {
            "question_id": extract_question_id(card),
            "subject": subject,
            "topics": topics,
        }
        payload.update(extract_exam_info(card))
        payload.update({
            "associated_text": extract_associated_text(card),
            "enunciation": extract_question_enunciation(card),
            "alternatives": extract_alternatives(card),
            "correct_answer": correct_answer,
        })

        questions.append(QuestionScrapedDTO.from_scrape(payload))

    return questions


def save_to_json(questions: list[QuestionScrapedDTO], file_name: str) -> None:
    """Grava os DTOs extraídos em um arquivo JSON, para comparação/depuração."""
    data = [asdict(question) for question in questions]
    with open(file_name, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)
    print(f"Saved {len(data)} question to file: {file_name}")


def persist_questions(
    session: Session, questions: list[QuestionScrapedDTO]
) -> UpsertResult:
    """Orquestra a persistência: resolve subject/topics e faz upsert das questões.

    Preparação para um futuro Service — nenhum repositório resolve matéria ou
    tópico de outro repositório; quem orquestra essa resolução é quem chama.
    """
    if not questions:
        return UpsertResult(inserted=0, updated=0)

    for dto in questions:
        if not (dto.subject and dto.subject.strip()):
            raise ValueError(f"questão {dto.question_id!r} sem matéria")

    subjects = SubjectRepository(session=session)
    topics = TopicRepository(session=session)
    question_repository = QuestionRepository(session=session)

    subject_id_by_name = subjects.get_or_create_many([dto.subject for dto in questions])

    for dto in questions:
        if dto.topics:
            topics.get_or_create_many(subject_id_by_name[dto.subject], dto.topics)

    return question_repository.upsert_many(questions, subject_id_by_name)


def save_to_database(questions: list[QuestionScrapedDTO]) -> None:
    """Faz upsert das questões extraídas na tabela ``question``."""
    dtos = [question for question in questions if question.question_id]
    if not dtos:
        print("Nenhuma questao para salvar no banco.")
        return

    with SessionLocal() as session, session.begin():
        result = persist_questions(session, dtos)

    print(
        f"Banco: {result.inserted} inseridas, {result.updated} atualizadas "
        "(tabela questao)."
    )


def run(playwright: Playwright) -> None:
    """Orquestra a raspagem: abre o browser, extrai as questões e persiste."""
    browser, page = open_browser(playwright)
    load_page(page)

    question_list = get_question_list(page)
    print(f"Lista encontrada? {question_list.count() > 0}")

    total_items = count_items(question_list)
    print(f"Itens na lista: {total_items}")

    answers = extract_answers(page)
    questions = extract_questions(question_list, answers)
    save_to_json(questions, "questions.json")
    save_to_database(questions)

    browser.close()


if __name__ == "__main__":
    with sync_playwright() as playwright:
        run(playwright)
