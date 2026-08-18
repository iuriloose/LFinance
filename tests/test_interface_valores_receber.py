import unittest

try:
    import test_lfinance as ambiente
except ModuleNotFoundError:
    from tests import test_lfinance as ambiente

from banco import banco
from banco.valores_receber import buscar_valor_receber_por_id, inserir_valor_receber
from servicos.configuracoes_app import CAMINHO_BANCO, CAMINHO_CONFIG


class TesteInterfaceValoresReceberIsolada(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.estado_real_antes = cls._estado_banco_real()

    @classmethod
    def tearDownClass(cls):
        if cls.estado_real_antes != cls._estado_banco_real():
            raise AssertionError("O banco real mudou durante o teste visual da versão 2.0.")

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
        self.id_valor = inserir_valor_receber(
            "Empresa visual de teste",
            "Salário visual de teste",
            2500,
            "2099-05-10",
            "Salário",
            recorrente=True,
        )

    def test_decima_tela_menu_responsividade_e_pesquisa(self):
        from PySide6.QtTest import QTest
        from PySide6.QtWidgets import QApplication

        from componentes.tabela_registros import TabelaRegistros
        from main import TelaPrincipal

        app = QApplication.instance() or QApplication([])
        janela = TelaPrincipal()
        try:
            self.assertEqual(janela.paginas.count(), 10)
            self.assertIn("a_receber", janela.menu.botoes)
            self.assertIs(
                janela.paginas.currentWidget(),
                janela.pagina_inicial,
            )

            janela.resize(1000, 620)
            janela.show()
            janela.menu_clicado("a_receber")
            QTest.qWait(50)
            tabela = janela.pagina_valores_receber.findChild(TabelaRegistros)
            self.assertIsNotNone(tabela)
            self.assertGreater(tabela.rowCount(), 0)
            for coluna in (2, 3, 5):
                self.assertTrue(tabela.isColumnHidden(coluna))
            self.assertFalse(tabela.isColumnHidden(7))

            janela.resize(1700, 900)
            QTest.qWait(50)
            for coluna in (2, 3, 5):
                self.assertFalse(tabela.isColumnHidden(coluna))

            janela.menu_clicado("pesquisar")
            janela.pagina_pesquisa.filtro_tipo.setCurrentIndex(
                janela.pagina_pesquisa.filtro_tipo.findData("a_receber")
            )
            QTest.qWait(30)
            self.assertEqual(janela.pagina_pesquisa.tabela.rowCount(), 1)
            self.assertIn(
                "Empresa visual de teste",
                janela.pagina_pesquisa.tabela.item(0, 1).text(),
            )
        finally:
            janela.close()
            janela.deleteLater()
            app.processEvents()


    def test_formulario_aceita_quinzena_e_valor_real_maior(self):
        from PySide6.QtWidgets import QApplication

        from telas.novo_valor_receber import NovoValorReceber
        from telas.receber_valor import ReceberValor

        app = QApplication.instance() or QApplication([])
        formulario = NovoValorReceber()
        dialogo = ReceberValor(buscar_valor_receber_por_id(self.id_valor))
        try:
            self.assertGreaterEqual(formulario.recorrencia.findData("quinzenal"), 0)
            self.assertGreater(dialogo.valor.maximum(), 2500)
            self.assertEqual(dialogo.valor.value(), 2500)
        finally:
            formulario.close()
            dialogo.close()
            formulario.deleteLater()
            dialogo.deleteLater()
            app.processEvents()

    def test_detalhes_e_filtro_usam_padrao_visual_e_texto_formatado(self):
        from PySide6.QtWidgets import QApplication, QFrame, QLabel

        from telas.detalhes_valor_receber import DetalhesValorReceber
        from telas.valores_receber import TelaValoresReceber

        app = QApplication.instance() or QApplication([])
        tela = TelaValoresReceber()
        detalhes = DetalhesValorReceber(self.id_valor)
        try:
            self.assertIsNotNone(tela.findChild(QFrame, "seletorValores"))
            self.assertEqual(tela.filtro.currentData(), "ativos")
            self.assertEqual(tela.tabela.altura_linha, 42)
            self.assertEqual(tela.tabela.limite_compacto, 1200)
            self.assertEqual(
                tela.findChild(QLabel, "valorResumoReceber").text(),
                "R$ 2.500,00",
            )
            self.assertEqual(
                len(tela.findChildren(QFrame, "cardAReceberPrincipal"))
                + len(tela.findChildren(QFrame, "cardPrevistoMes"))
                + len(tela.findChildren(QFrame, "cardAtrasadosReceber"))
                + len(tela.findChildren(QFrame, "cardRecebidoMes")),
                4,
            )
            mes_inicial = tela.mes_referencia
            tela.mes_proximo()
            self.assertNotEqual(tela.mes_referencia, mes_inicial)
            self.assertIn(str(tela.mes_referencia.year), tela.findChild(QLabel, "periodoValores").text())
            tela.voltar_mes_atual()
            valores_resumo = detalhes.findChildren(QLabel, "valorResumo")
            self.assertEqual(len(valores_resumo), 6)
            self.assertEqual(
                [item.text() for item in valores_resumo],
                ["R$ 2.500,00", "R$ 0,00", "R$ 2.500,00", "10/05/2099", "Em aberto", "Mensal"],
            )
            self.assertTrue(all("<" not in item.text() for item in valores_resumo))
        finally:
            tela.close()
            detalhes.close()
            tela.deleteLater()
            detalhes.deleteLater()
            app.processEvents()

if __name__ == "__main__":
    unittest.main()
