import sqlite3
import unittest
from contextlib import closing
from pathlib import Path
from datetime import date

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
            self.assertEqual(conexao.execute("PRAGMA user_version").fetchone()[0], 5)
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

    def test_quinzenal_ajusta_valor_real_e_preserva_proxima_previsao(self):
        id_valor = inserir_valor_receber(
            "Empresa fictícia",
            "Salário quinzenal",
            2000,
            "2099-01-15",
            "Salário",
            frequencia="quinzenal",
        )
        previsto = buscar_valor_receber_por_id(id_valor)
        self.assertEqual((previsto[3], previsto[12]), (2000, "quinzenal"))

        sucesso, mensagem = registrar_recebimento(
            id_valor, 2300, "2099-01-15", "Adicional fictício"
        )
        self.assertTrue(sucesso)
        self.assertIn("ajustado", mensagem)
        recebido = buscar_valor_receber_por_id(id_valor)
        self.assertEqual(
            (recebido[3], recebido[9], recebido[10], recebido[11]),
            (2300, 2300, 0, "recebido"),
        )

        proximos = listar_valores_receber("ativos")
        self.assertEqual(len(proximos), 1)
        self.assertEqual(
            (proximos[0][3], proximos[0][4], proximos[0][12]),
            (2000, "2099-01-30", "quinzenal"),
        )

        self.assertTrue(desfazer_ultimo_recebimento(id_valor)[0])
        restaurado = buscar_valor_receber_por_id(id_valor)
        self.assertEqual(
            (restaurado[3], restaurado[9], restaurado[10], restaurado[11]),
            (2000, 0, 2000, "em_aberto"),
        )
        self.assertEqual(listar_valores_receber("ativos"), [restaurado])
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
            self.assertEqual(conexao.execute("PRAGMA user_version").fetchone()[0], 5)
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



    def test_relatorio_separa_valores_previstos_das_receitas(self):
        from telas.relatorios import TelaRelatorios

        inserir_valor_receber(
            "Empresa fict?cia",
            "Comiss?o prevista",
            500,
            "2000-01-10",
            "Comiss?o",
        )
        inserir_valor_receber(
            "Cliente fict?cio",
            "Servi?o previsto",
            200,
            "2000-01-15",
            "Servi?os",
        )
        tela = TelaRelatorios.__new__(TelaRelatorios)
        tela.mes_referencia = date(2000, 1, 1)
        dados = tela.dados_mes()

        self.assertEqual(dados["total_receitas"], 0)
        self.assertEqual(dados["total_a_receber"], 700)
        self.assertEqual(dados["total_a_receber_atrasado"], 700)
        self.assertEqual(len(dados["valores_receber"]), 2)
        self.assertEqual(dados["resultado_planejado"], dados["resultado_previsto"] + 700)

if __name__ == "__main__":
    unittest.main()
