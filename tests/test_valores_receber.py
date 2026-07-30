import sqlite3
import unittest
from contextlib import closing
from pathlib import Path

try:
    import test_lfinance as ambiente
except ModuleNotFoundError:
    from tests import test_lfinance as ambiente

from banco import banco
from banco.valores_receber import (
    buscar_valor_receber_por_id,
    cancelar_valor_receber,
    desfazer_ultimo_recebimento,
    excluir_valor_receber,
    inserir_valor_receber,
    listar_ids_receitas_vinculadas,
    listar_recebimentos_valor,
    listar_valores_receber,
    registrar_recebimento,
)
from servicos.backup import copiar_banco_sqlite, validar_backup_lfinance
from servicos.configuracoes_app import CAMINHO_BANCO, CAMINHO_CONFIG


class TesteValoresReceberIsolado(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.estado_real_antes = cls._estado_banco_real()

    @classmethod
    def tearDownClass(cls):
        if cls.estado_real_antes != cls._estado_banco_real():
            raise AssertionError("O banco real mudou durante os testes de valores a receber.")

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

    def test_esquema_2_0_e_integridade(self):
        with closing(sqlite3.connect(CAMINHO_BANCO)) as conexao:
            self.assertEqual(conexao.execute("PRAGMA quick_check").fetchone()[0], "ok")
            self.assertEqual(conexao.execute("PRAGMA user_version").fetchone()[0], 4)
            tabelas = {
                linha[0]
                for linha in conexao.execute(
                    "SELECT name FROM sqlite_master WHERE type = 'table'"
                )
            }
        self.assertIn("valores_receber", tabelas)
        self.assertIn("recebimentos", tabelas)

    def test_recebimento_parcial_total_recorrente_e_desfazer(self):
        id_valor = inserir_valor_receber(
            "Empresa de teste",
            "Salário de teste",
            1000,
            "2099-01-31",
            "Salário",
            recorrente=True,
            observacao="Dado fictício",
        )
        atual = buscar_valor_receber_por_id(id_valor)
        self.assertEqual((atual[9], atual[10], atual[11]), (0, 1000, "em_aberto"))

        sucesso, _ = registrar_recebimento(
            id_valor, 400, "2099-01-31", "Parcial fictício"
        )
        self.assertTrue(sucesso)
        parcial = buscar_valor_receber_por_id(id_valor)
        self.assertEqual((parcial[9], parcial[10], parcial[11]), (400, 600, "parcial"))
        self.assertEqual(len(banco.listar_receitas()), 1)
        self.assertEqual(len(listar_ids_receitas_vinculadas()), 1)

        sucesso, _ = registrar_recebimento(
            id_valor, 600, "2099-01-31", "Conclusão fictícia"
        )
        self.assertTrue(sucesso)
        concluido = buscar_valor_receber_por_id(id_valor)
        self.assertEqual((concluido[9], concluido[10], concluido[11]), (1000, 0, "recebido"))
        self.assertEqual(len(listar_recebimentos_valor(id_valor)), 2)

        ativos = listar_valores_receber("ativos")
        self.assertEqual(len(ativos), 1)
        self.assertEqual(ativos[0][4], "2099-02-28")
        self.assertEqual(ativos[0][2], "Salário de teste")

        sucesso, _ = desfazer_ultimo_recebimento(id_valor)
        self.assertTrue(sucesso)
        parcial = buscar_valor_receber_por_id(id_valor)
        self.assertEqual((parcial[9], parcial[10], parcial[11]), (400, 600, "parcial"))
        self.assertEqual(listar_valores_receber("ativos"), [parcial])
        self.assertEqual(len(banco.listar_receitas()), 1)

        self.assertTrue(desfazer_ultimo_recebimento(id_valor)[0])
        self.assertEqual(len(banco.listar_receitas()), 0)
        self.assertTrue(excluir_valor_receber(id_valor)[0])
        self.assertIsNone(buscar_valor_receber_por_id(id_valor))

    def test_cancelamento_preserva_receita_e_bloqueia_exclusao(self):
        id_valor = inserir_valor_receber(
            "Cliente fictício",
            "Comissão de teste",
            300,
            "2099-03-10",
            "Comissão",
        )
        self.assertTrue(registrar_recebimento(id_valor, 100, "2099-03-01")[0])
        self.assertTrue(cancelar_valor_receber(id_valor)[0])
        cancelado = buscar_valor_receber_por_id(id_valor)
        self.assertEqual(cancelado[11], "cancelado")
        self.assertEqual(len(banco.listar_receitas()), 1)
        self.assertFalse(excluir_valor_receber(id_valor)[0])

        self.assertTrue(desfazer_ultimo_recebimento(id_valor)[0])
        self.assertTrue(excluir_valor_receber(id_valor)[0])

    def test_migracao_1_0_7_preserva_dados_existentes(self):
        banco.inserir_receita(
            "Receita preservada",
            1234.56,
            "2099-04-01",
            "Salário",
            "Registro fictício anterior à versão 2.0",
        )
        with closing(sqlite3.connect(CAMINHO_BANCO)) as conexao:
            conexao.execute("DROP TABLE recebimentos")
            conexao.execute("DROP TABLE valores_receber")
            conexao.execute("PRAGMA user_version = 3")
            conexao.commit()

        banco.criar_tabelas()

        with closing(sqlite3.connect(CAMINHO_BANCO)) as conexao:
            self.assertEqual(conexao.execute("PRAGMA user_version").fetchone()[0], 4)
            tabelas = {
                linha[0]
                for linha in conexao.execute(
                    "SELECT name FROM sqlite_master WHERE type = 'table'"
                )
            }
        self.assertIn("valores_receber", tabelas)
        self.assertIn("recebimentos", tabelas)
        self.assertEqual(banco.listar_receitas()[0][1], "Receita preservada")

    def test_backup_1_0_7_continua_compativel(self):
        legado = Path(ambiente.PERFIL_TEMPORARIO.name) / "backup-1.0.7.db"
        copiar_banco_sqlite(CAMINHO_BANCO, legado)
        with closing(sqlite3.connect(legado)) as conexao:
            conexao.execute("DROP TABLE recebimentos")
            conexao.execute("DROP TABLE valores_receber")
            conexao.execute("PRAGMA user_version = 3")
            conexao.commit()

        self.assertEqual(validar_backup_lfinance(legado), (True, ""))


if __name__ == "__main__":
    unittest.main()
