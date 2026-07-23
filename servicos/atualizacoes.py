import json
import re
import urllib.error
import urllib.request
from dataclasses import dataclass
from urllib.parse import unquote, urlparse

from PySide6.QtCore import QObject, Signal, Slot

from servicos.configuracoes_app import APP_VERSAO

GITHUB_REPOSITORIO = "iuriloose/LFinance"
URL_API_ULTIMA_RELEASE = f"https://api.github.com/repos/{GITHUB_REPOSITORIO}/releases/latest"
URL_RELEASES = f"https://github.com/{GITHUB_REPOSITORIO}/releases/latest"
_PADRAO_TAG_VERSAO = re.compile(r"^v?(\d+\.\d+\.\d+(?:\.\d+)?)$", re.IGNORECASE)
_PADRAO_SHA256 = re.compile(r"^[0-9a-f]{64}$", re.IGNORECASE)


@dataclass(frozen=True)
class ResultadoAtualizacao:
    disponivel: bool
    versao_atual: str
    nova_versao: str = ""
    nome_release: str = ""
    descricao: str = ""
    url_download: str = ""
    url_release: str = URL_RELEASES
    nome_arquivo: str = ""
    hash_sha256: str = ""


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


def _extrair_versao_publicada(tag):
    texto = str(tag or "").strip()
    correspondencia = _PADRAO_TAG_VERSAO.fullmatch(texto)
    if not correspondencia:
        raise ValueError("A Release mais recente possui uma tag de versao invalida.")
    return correspondencia.group(1)


def _url_release_confiavel(valor):
    url = str(valor or "").strip()
    parsed = urlparse(url)
    prefixo = f"/{GITHUB_REPOSITORIO}/releases/".casefold()
    if (
        parsed.scheme == "https"
        and parsed.hostname == "github.com"
        and parsed.path.casefold().startswith(prefixo)
        and not parsed.username
        and not parsed.password
    ):
        return url
    return URL_RELEASES


def _selecionar_instalador(assets, tag, nova_versao):
    nome_esperado = f"LFinance_Setup_v{nova_versao}.exe"
    prefixo = f"/{GITHUB_REPOSITORIO}/releases/download/{tag}/".casefold()

    for asset in assets or []:
        nome = str(asset.get("name") or "").strip()
        if nome.casefold() != nome_esperado.casefold():
            continue

        url = str(asset.get("browser_download_url") or "").strip()
        parsed = urlparse(url)
        nome_url = unquote(parsed.path.rsplit("/", 1)[-1])
        if not (
            parsed.scheme == "https"
            and parsed.hostname == "github.com"
            and parsed.path.casefold().startswith(prefixo)
            and nome_url.casefold() == nome_esperado.casefold()
            and not parsed.query
            and not parsed.fragment
            and not parsed.username
            and not parsed.password
        ):
            continue

        digest = str(asset.get("digest") or "").strip().lower()
        hash_sha256 = ""
        if digest.startswith("sha256:"):
            candidato = digest.split(":", 1)[1]
            if _PADRAO_SHA256.fullmatch(candidato):
                hash_sha256 = candidato

        return url, nome, hash_sha256

    return "", "", ""


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
    nova_versao = _extrair_versao_publicada(tag)
    url_download, nome_arquivo, hash_sha256 = _selecionar_instalador(
        dados.get("assets") or [], tag, nova_versao
    )

    return ResultadoAtualizacao(
        disponivel=_versao_mais_nova(nova_versao, APP_VERSAO),
        versao_atual=APP_VERSAO,
        nova_versao=nova_versao,
        nome_release=str(dados.get("name") or f"LFinance {tag}"),
        descricao=str(dados.get("body") or "").strip(),
        url_download=url_download,
        url_release=_url_release_confiavel(dados.get("html_url")),
        nome_arquivo=nome_arquivo,
        hash_sha256=hash_sha256,
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
