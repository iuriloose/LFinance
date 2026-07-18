import json
import os
import shutil
import sys
from pathlib import Path

APP_NOME = "LFinance"
APP_VERSAO = "1.0.2"
USUARIO_PADRAO = "Usuário"


def obter_pasta_dados():
    """Retorna a pasta segura para dados do usuário.

    No Windows usa %LOCALAPPDATA%/LFinance.
    Em outros sistemas, mantém uma pasta local no usuário.
    """
    if sys.platform.startswith("win"):
        base = os.environ.get("LOCALAPPDATA") or os.environ.get("APPDATA")
        if base:
            return Path(base) / APP_NOME

    return Path.home() / f".{APP_NOME.lower()}"


PASTA_DADOS = obter_pasta_dados()
CAMINHO_CONFIG = PASTA_DADOS / "config.json"
CAMINHO_BANCO = PASTA_DADOS / "lfinance.db"


def obter_pasta_projeto():
    return Path(__file__).resolve().parent.parent


def obter_banco_antigo_projeto():
    return obter_pasta_projeto() / "banco" / "lfinance.db"




def executando_como_exe():
    """Indica se o LFinance está rodando empacotado em EXE."""
    return bool(getattr(sys, "frozen", False))


def obter_pasta_base_app():
    """Retorna a pasta base correta tanto no Python quanto no EXE."""
    if executando_como_exe():
        return Path(getattr(sys, "_MEIPASS", Path(sys.executable).parent))
    return obter_pasta_projeto()


def caminho_recurso(*partes):
    """Monta o caminho de arquivos internos, como imagens e ícones.

    Funciona no projeto aberto pelo Python e também no executável gerado pelo PyInstaller.
    """
    return obter_pasta_base_app().joinpath(*partes)


def preparar_pasta_dados():
    PASTA_DADOS.mkdir(parents=True, exist_ok=True)


def migrar_banco_antigo_se_necessario():
    """Copia o banco antigo do projeto para a pasta de dados, se ainda não existir.

    Isso preserva os dados atuais ao preparar o LFinance para rodar instalado.
    """
    preparar_pasta_dados()

    if CAMINHO_BANCO.exists():
        return

    banco_antigo = obter_banco_antigo_projeto()
    if banco_antigo.exists():
        shutil.copy2(banco_antigo, CAMINHO_BANCO)


def carregar_configuracoes():
    preparar_pasta_dados()
    dados = {
        "nome_usuario": USUARIO_PADRAO,
        "nome_configurado": False,
        "versao": APP_VERSAO,
    }

    if CAMINHO_CONFIG.exists():
        try:
            with open(CAMINHO_CONFIG, "r", encoding="utf-8") as arquivo:
                dados_salvos = json.load(arquivo)
                if isinstance(dados_salvos, dict):
                    dados.update(dados_salvos)
        except Exception:
            pass

    dados["versao"] = APP_VERSAO
    return dados


def salvar_configuracoes(dados):
    preparar_pasta_dados()
    config_atual = carregar_configuracoes()
    config_atual.update(dados or {})
    config_atual["versao"] = APP_VERSAO

    with open(CAMINHO_CONFIG, "w", encoding="utf-8") as arquivo:
        json.dump(config_atual, arquivo, ensure_ascii=False, indent=4)

    return config_atual


def obter_nome_usuario():
    return carregar_configuracoes().get("nome_usuario") or USUARIO_PADRAO


def nome_inicial_precisa_ser_configurado():
    """Retorna True quando o usuário ainda não configurou o nome inicial."""
    config = carregar_configuracoes()
    nome = (config.get("nome_usuario") or "").strip()
    return not nome or nome == USUARIO_PADRAO

def salvar_nome_usuario(nome):
    """Salva o nome de exibição informado pelo usuário."""
    nome_limpo = (nome or "").strip() or USUARIO_PADRAO
    return salvar_configuracoes({
        "nome_usuario": nome_limpo,
        "nome_configurado": nome_limpo != USUARIO_PADRAO,
    })
