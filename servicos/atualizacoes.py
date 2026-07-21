import json
import re
import urllib.error
import urllib.request
from dataclasses import dataclass

from PySide6.QtCore import QObject, Signal, Slot

from servicos.configuracoes_app import APP_VERSAO

GITHUB_REPOSITORIO = "iuriloose/LFinance"
URL_API_ULTIMA_RELEASE = f"https://api.github.com/repos/{GITHUB_REPOSITORIO}/releases/latest"
URL_RELEASES = f"https://github.com/{GITHUB_REPOSITORIO}/releases/latest"


@dataclass(frozen=True)
class ResultadoAtualizacao:
    disponivel: bool
    versao_atual: str
    nova_versao: str = ""
    nome_release: str = ""
    descricao: str = ""
    url_download: str = ""
    url_release: str = URL_RELEASES


def _normalizar_versao(valor):
    texto = str(valor or "").strip().lower().lstrip("v")
    numeros = re.findall(r"\d+", texto)
    return tuple(int(numero) for numero in numeros[:4]) or (0,)


def _versao_mais_nova(nova, atual):
    nova_partes = list(_normalizar_versao(nova))
    atual_partes = list(_normalizar_versao(atual))
    tamanho = max(len(nova_partes), len(atual_partes))
    nova_partes.extend([0] * (tamanho - len(nova_partes)))
    atual_partes.extend([0] * (tamanho - len(atual_partes)))
    return tuple(nova_partes) > tuple(atual_partes)


def consultar_ultima_versao(timeout=8):
    requisicao = urllib.request.Request(
        URL_API_ULTIMA_RELEASE,
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": f"LFinance/{APP_VERSAO}",
            "X-GitHub-Api-Version": "2022-11-28",
        },
    )

    with urllib.request.urlopen(requisicao, timeout=timeout) as resposta:
        dados = json.loads(resposta.read().decode("utf-8"))

    tag = str(dados.get("tag_name") or "").strip()
    nova_versao = tag.lstrip("vV")
    assets = dados.get("assets") or []

    url_download = ""
    for asset in assets:
        nome = str(asset.get("name") or "").lower()
        if nome.endswith(".exe") and "setup" in nome:
            url_download = str(asset.get("browser_download_url") or "")
            break

    if not url_download:
        for asset in assets:
            nome = str(asset.get("name") or "").lower()
            if nome.endswith(".exe"):
                url_download = str(asset.get("browser_download_url") or "")
                break

    url_release = str(dados.get("html_url") or URL_RELEASES)

    return ResultadoAtualizacao(
        disponivel=_versao_mais_nova(nova_versao, APP_VERSAO),
        versao_atual=APP_VERSAO,
        nova_versao=nova_versao,
        nome_release=str(dados.get("name") or f"LFinance {tag}"),
        descricao=str(dados.get("body") or "").strip(),
        url_download=url_download,
        url_release=url_release,
    )


class VerificadorAtualizacoes(QObject):
    concluido = Signal(object)
    falhou = Signal(str)

    @Slot()
    def executar(self):
        try:
            self.concluido.emit(consultar_ultima_versao())
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, OSError, ValueError) as erro:
            self.falhou.emit(str(erro))
        except Exception as erro:
            self.falhou.emit(str(erro))
