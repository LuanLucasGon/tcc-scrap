import asyncio

import pytest


def test_question_controller_declares_get_by_id_route():
    from question.controller.question_controller import router

    paths = {route.path for route in router.routes}
    assert "/questions/{question_id}" in paths


def test_question_controller_endpoint_not_implemented_yet():
    from question.controller.question_controller import get_question_by_id

    with pytest.raises(NotImplementedError):
        asyncio.run(get_question_by_id("Q123"))


def test_question_router_is_not_mounted_on_the_app_yet():
    from app.main import app

    paths = {route.path for route in app.routes}
    assert "/questions/{question_id}" not in paths
