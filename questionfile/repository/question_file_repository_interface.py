from __future__ import annotations

from abc import ABC, abstractmethod
from uuid import UUID

from questionfile.dtos.question_file_dto import QuestionFileDTO


class QuestionFileRepositoryInterface(ABC):
    """Porta de persistência para arquivos de imagem referenciados por questões.

    A identidade de cada arquivo é o par ``(question_number_id, url)``.
    """

    @abstractmethod
    def get_ids_by_pairs(
        self, pairs: list[tuple[str, str]]
    ) -> dict[tuple[str, str], UUID]:
        """Devolve ``{(question_number_id, url): id}`` só para os pares já salvos."""

    @abstractmethod
    def get_contents_by_urls(self, urls: list[str]) -> dict[str, bytes]:
        """Devolve ``{url: content}`` para as URLs que já têm binário salvo.

        Ignora a questão — serve para reaproveitar bytes já baixados por outra
        questão em vez de baixar a mesma imagem de novo.
        """

    @abstractmethod
    def create_missing(
        self, content_by_pair: dict[tuple[str, str], bytes]
    ) -> dict[tuple[str, str], UUID]:
        """Cria uma linha para cada par — assume que nenhum deles já existe.

        Quem chama é responsável por filtrar antes com ``get_ids_by_pairs``;
        criar um par que já existe viola a constraint de unicidade.
        Devolve ``{(question_number_id, url): id}`` das linhas criadas.
        """

    @abstractmethod
    def get_by_question_and_url(
        self, question_number_id: str, url: str
    ) -> QuestionFileDTO | None:
        """Busca o arquivo pelo par ``(question_number_id, url)``."""
