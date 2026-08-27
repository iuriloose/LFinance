import sqlite3
import unittest
from contextlib import closing

try:
    import test_lfinance as ambiente
except ModuleNotFoundError:
    from tests import test_lfinance as ambiente

from banco import banco
from servicos.configuracoes_app import CAMINHO_BANCO, CAMINHO_CONFIG
from servicos.sincronizacao.contrato import build_desktop_snapshot


class TesteContratoSincronizacaoIsolado(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.estado_real_antes = cls._estado_banco_real()

    @classmethod
    def tearDownClass(cls):
        if cls.estado_real_antes != cls._estado_banco_real():
            raise AssertionError("O banco real mudou durante os testes de sincronização.")

    @staticmethod
    def _estado_banco_real():
        if not ambiente.BANCO_REAL.exists():
            return None
        estado = ambiente.BANCO_REAL.stat()
        return estado.st_size, estado.st_mtime_ns

    def setUp(self):
        CAMINHO_BANCO.unlink(missing_ok=True)
        CAMINHO_CONFIG.unlink(missing_ok=True)
        banco.criar_tabelas()

    def test_snapshot_preserva_identidade_e_separa_pagamento(self):
        banco.inserir_despesa(
            "Energia", 100, "2026-08-20", "Casa", "Conta"
        )
        despesa_id = banco.listar_despesas()[0][0]
        self.assertTrue(
            banco.pagar_despesa(
                despesa_id, valor_pago=105, data_pagamento="2026-08-21"
            )[0]
        )
        banco.inserir_gasto("Água", 5.5, "2026-08-21", "Alimentação")

        with closing(sqlite3.connect(CAMINHO_BANCO)) as conexao:
            primeiro = build_desktop_snapshot(conexao, "desktop-teste")
            segundo = build_desktop_snapshot(conexao, "desktop-teste")

        self.assertEqual(primeiro["contract_version"], 1)
        tipos = [item["type"] for item in primeiro["entities"]]
        self.assertIn("payable", tipos)
        self.assertIn("payment", tipos)
        self.assertIn("expense", tipos)

        pagamento = next(
            item for item in primeiro["entities"] if item["type"] == "payment"
        )
        self.assertEqual(pagamento["data"]["planned_amount_cents"], 10000)
        self.assertEqual(pagamento["data"]["actual_amount_cents"], 10500)
        self.assertEqual(pagamento["data"]["interest_cents"], 500)

        identidades_1 = {(item["type"], item["id"]) for item in primeiro["entities"]}
        identidades_2 = {(item["type"], item["id"]) for item in segundo["entities"]}
        self.assertEqual(identidades_1, identidades_2)

    def test_exclusao_vira_marcador_sem_recriar_registro(self):
        banco.inserir_gasto("Duplicado", 10, "2026-08-21", "Teste")
        gasto_id = banco.listar_gastos()[0][0]
        with closing(sqlite3.connect(CAMINHO_BANCO)) as conexao:
            primeiro = build_desktop_snapshot(conexao)
        sync_id = next(
            item["id"] for item in primeiro["entities"] if item["type"] == "expense"
        )

        banco.excluir_gasto(gasto_id)
        with closing(sqlite3.connect(CAMINHO_BANCO)) as conexao:
            segundo = build_desktop_snapshot(conexao)
        excluido = next(item for item in segundo["entities"] if item["id"] == sync_id)
        self.assertIsNotNone(excluido["deleted_at"])
        self.assertEqual(excluido["data"], {})


if __name__ == "__main__":
    unittest.main()