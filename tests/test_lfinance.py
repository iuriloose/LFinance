import json
import os
import sqlite3
import tempfile
import unittest
from contextlib import closing
from pathlib import Path
from unittest import mock


LOCALAPPDATA_REAL = Path(os.environ.get("LOCALAPPDATA", ""))
BANCO_REAL = LOCALAPPDATA_REAL / "LFinance" / "lfinance.db"
PERFIL_TEMPORARIO = tempfile.TemporaryDirectory(
    prefix="lfinance-testes-", ignore_cleanup_errors=True
)
os.environ["LOCALAPPDATA"] = PERFIL_TEMPORARIO.name
os.environ["QT_QPA_PLATFORM"] = "offscreen"

from banco import banco
from servicos.backup import (
    copiar_banco_sqlite,
    criar_backup_automatico,
    restaurar_banco_sqlite,
    validar_backup_lfinance,
)
from servicos.configuracoes_app import CAMINHO_BANCO, CAMINHO_CONFIG, salvar_configuracoes
from servicos.valores import converter_texto_moeda


class TesteLFinanceIsolado(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.estado_real_antes = cls._estado_banco_real()

    @classmethod
    def tearDownClass(cls):
        if cls.estado_real_antes != cls._estado_banco_real():
            raise AssertionError("O banco real mudou durante os testes isolados.")
        PERFIL_TEMPORARIO.cleanup()

    @staticmethod
    def _estado_banco_real():
        if not BANCO_REAL.exists():
            return None
        estado = BANCO_REAL.stat()
        return estado.st_size, estado.st_mtime_ns

    def setUp(self):
        CAMINHO_BANCO.unlink(missing_ok=True)
        CAMINHO_CONFIG.unlink(missing_ok=True)
        banco.criar_tabelas()

    def test_esquema_e_conversao_monetaria(self):
        self.assertEqual(CAMINHO_BANCO.parent, Path(PERFIL_TEMPORARIO.name) / "LFinance")
        with closing(sqlite3.connect(CAMINHO_BANCO)) as conexao:
            self.assertEqual(conexao.execute("PRAGMA quick_check").fetchone()[0], "ok")
            self.assertEqual(conexao.execute("PRAGMA user_version").fetchone()[0], 3)

        self.assertEqual(converter_texto_moeda("1.234,56"), 1234.56)
        self.assertEqual(converter_texto_moeda("1234.56"), 1234.56)
        for invalido in ("", "0", "-1", "abc"):
            with self.subTest(valor=invalido):
                with self.assertRaises(ValueError):
                    converter_texto_moeda(invalido)

    def test_fluxos_financeiros_e_desfazer_pagamento(self):
        banco.inserir_receita("Receita de teste", 1000.0, "2026-07-01", "Teste")
        banco.inserir_gasto("Gasto de teste", 25.5, "2026-07-02", "Teste")

        banco.inserir_despesa(
            "Conta simples de teste", 100.0, "2026-07-10", "Teste", "Conta"
        )
        simples = banco.listar_despesas()[0][0]
        ok, mensagem = banco.pagar_despesa(
            simples, valor_pago=105.0, data_pagamento="2026-07-10"
        )
        self.assertTrue(ok, mensagem)
        pagamento = banco.buscar_ultimo_pagamento_da_despesa(simples)[0]
        self.assertTrue(banco.desfazer_pagamento(pagamento)[0])

        banco.inserir_despesa(
            "Conta fixa de teste", 80.0, "2026-07-15", "Teste", "Conta fixa"
        )
        fixa = next(item[0] for item in banco.listar_despesas() if item[1] == "Conta fixa de teste")
        self.assertTrue(banco.pagar_despesa(fixa, data_pagamento="2026-07-15")[0])
        self.assertEqual(banco.buscar_despesa_por_id(fixa)[3], "2026-08-15")
        pagamento = banco.buscar_ultimo_pagamento_da_despesa(fixa)[0]
        self.assertTrue(banco.desfazer_pagamento(pagamento)[0])
        self.assertEqual(banco.buscar_despesa_por_id(fixa)[3], "2026-07-15")

        banco.inserir_despesa(
            "Parcela de teste", 50.0, "2026-07-20", "Teste", "Parcelamento",
            parcela_atual=1, total_parcelas=3, valor_total=150.0,
        )
        parcela = next(item[0] for item in banco.listar_despesas() if item[1] == "Parcela de teste")
        self.assertTrue(banco.pagar_despesa(parcela, data_pagamento="2026-07-20")[0])
        atual = banco.buscar_despesa_por_id(parcela)
        self.assertEqual((atual[3], atual[6]), ("2026-08-20", 2))
        pagamento = banco.buscar_ultimo_pagamento_da_despesa(parcela)[0]
        self.assertTrue(banco.desfazer_pagamento(pagamento)[0])
        atual = banco.buscar_despesa_por_id(parcela)
        self.assertEqual((atual[3], atual[6]), ("2026-07-20", 1))

    def test_backup_validado_e_restauracao_com_copia_de_seguranca(self):
        banco.inserir_receita("Estado anterior", 10.0, "2026-07-01", "Teste")
        origem = Path(PERFIL_TEMPORARIO.name) / "origem.db"

        banco.inserir_receita("Estado restaurado", 20.0, "2026-07-02", "Teste")
        copiar_banco_sqlite(CAMINHO_BANCO, origem)
        self.assertEqual(validar_backup_lfinance(origem), (True, ""))

        banco.excluir_receita(banco.listar_receitas()[0][0])
        seguranca = criar_backup_automatico(CAMINHO_BANCO, "antes_teste")
        restaurar_banco_sqlite(origem, CAMINHO_BANCO, seguranca)

        descricoes = {item[1] for item in banco.listar_receitas()}
        self.assertIn("Estado restaurado", descricoes)
        self.assertEqual(validar_backup_lfinance(seguranca), (True, ""))

        antes_limpeza = criar_backup_automatico(CAMINHO_BANCO, "antes_limpeza_teste")
        banco.limpar_todos_os_dados()
        self.assertEqual(banco.listar_receitas(), [])
        self.assertEqual(validar_backup_lfinance(antes_limpeza), (True, ""))

    def test_falha_na_restauracao_recupera_o_banco_anterior(self):
        banco.inserir_receita("Original protegido", 30.0, "2026-07-01", "Teste")
        seguranca = criar_backup_automatico(CAMINHO_BANCO, "rollback_teste")
        origem = Path(PERFIL_TEMPORARIO.name) / "origem-rollback.db"
        copiar_banco_sqlite(CAMINHO_BANCO, origem)

        substituir_real = os.replace
        chamadas = 0

        def falhar_na_primeira_troca(*argumentos):
            nonlocal chamadas
            chamadas += 1
            if chamadas == 1:
                raise PermissionError("Falha simulada")
            return substituir_real(*argumentos)

        with mock.patch("servicos.backup.os.replace", side_effect=falhar_na_primeira_troca):
            with self.assertRaises(PermissionError):
                restaurar_banco_sqlite(origem, CAMINHO_BANCO, seguranca)

        descricoes = {item[1] for item in banco.listar_receitas()}
        self.assertIn("Original protegido", descricoes)

    def test_backup_incompleto_e_rejeitado(self):
        incompleto = Path(PERFIL_TEMPORARIO.name) / "incompleto.db"
        with closing(sqlite3.connect(incompleto)) as conexao:
            for tabela in ("despesas", "receitas", "gastos", "pagamentos"):
                conexao.execute(f"CREATE TABLE {tabela} (id INTEGER PRIMARY KEY)")
            conexao.commit()
        valido, motivo = validar_backup_lfinance(incompleto)
        self.assertFalse(valido)
        self.assertIn("colunas", motivo)

    def test_configuracao_salva_em_json_valido(self):
        resultado = salvar_configuracoes({"nome_usuario": "Pessoa de teste"})
        self.assertEqual(resultado["nome_usuario"], "Pessoa de teste")
        with CAMINHO_CONFIG.open("r", encoding="utf-8") as arquivo:
            salvo = json.load(arquivo)
        self.assertEqual(salvo["nome_usuario"], "Pessoa de teste")

    def test_as_nove_telas_sao_construidas(self):
        from PySide6.QtWidgets import QApplication
        from main import TelaPrincipal

        app = QApplication.instance() or QApplication([])
        janela = TelaPrincipal()
        self.assertEqual(janela.paginas.count(), 9)
        self.assertEqual(
            set(janela.menu.botoes),
            {
                "tela_inicial", "pesquisar", "receitas", "gastos", "despesas",
                "contas_fixas", "parcelamentos", "relatorios", "configuracoes",
            },
        )
        for botao in janela.menu.botoes.values():
            self.assertTrue(botao.accessibleName())
            self.assertTrue(botao.accessibleDescription())
        janela.close()
        janela.deleteLater()
        app.processEvents()


if __name__ == "__main__":
    unittest.main()
