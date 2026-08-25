import unittest
from datetime import date

try:
    import test_lfinance as ambiente
except ModuleNotFoundError:
    from tests import test_lfinance as ambiente

from banco import banco
from banco.valores_receber import (
    buscar_valor_receber_por_id,
    inserir_valor_receber,
    listar_valores_receber,
)
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

    def test_mes_futuro_projeta_quinzenas_sem_criar_lancamentos(self):
        from PySide6.QtWidgets import QApplication

        from telas.valores_receber import TelaValoresReceber

        app = QApplication.instance() or QApplication([])
        inserir_valor_receber(
            "Empresa quinzenal de teste",
            "Recebimento quinzenal de teste",
            2000,
            "2099-08-30",
            "Salário",
            recorrente=True,
            frequencia="quinzenal",
        )
        antes = listar_valores_receber("todos")
        tela = TelaValoresReceber()
        try:
            tela.mes_referencia = date(2099, 9, 1)
            tela.montar_tela()
            previsoes = tela.previsoes_ativas_no_mes(listar_valores_receber("ativos"))
            previsoes_quinzenais = [
                entrada for entrada in previsoes
                if entrada[0][1] == "Empresa quinzenal de teste"
            ]

            self.assertEqual(len(previsoes_quinzenais), 2)
            self.assertEqual(
                [item[4] for item, _projecao in previsoes_quinzenais],
                ["2099-09-14", "2099-09-29"],
            )
            self.assertTrue(all(eh_projecao for _item, eh_projecao in previsoes_quinzenais))
            self.assertEqual(sum(item[10] for item, _projecao in previsoes_quinzenais), 4000)
            self.assertEqual(tela.tabela.rowCount(), 3)
            self.assertEqual(tela.tabela.item(1, 4).text(), "Previsão")
            self.assertEqual(antes, listar_valores_receber("todos"))
        finally:
            tela.close()
            tela.deleteLater()
            app.processEvents()
    def test_detalhes_e_filtro_usam_padrao_visual_e_texto_formatado(self):
        from PySide6.QtCore import Qt
        from PySide6.QtWidgets import QApplication, QComboBox, QFrame, QLabel, QPushButton, QTableWidget

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

    def test_relatorios_resumo_comparacao_e_categorias(self):
        from PySide6.QtCore import Qt
        from PySide6.QtWidgets import QApplication, QComboBox, QFrame, QLabel, QPushButton, QTableWidget

        from telas.relatorios import GraficoBarrasInterativo, TelaRelatorios

        app = QApplication.instance() or QApplication([])
        tela = TelaRelatorios()
        try:
            cards = (
                tela.findChildren(QFrame, "cardReceitaRelatorio")
                + tela.findChildren(QFrame, "cardPagoRelatorio")
                + tela.findChildren(QFrame, "cardSaldoRelatorio")
                + tela.findChildren(QFrame, "cardPendenteRelatorio")
            )
            self.assertEqual(len(cards), 4)
            textos = [label.text() for label in tela.findChildren(QLabel)]
            self.assertIn("Gastos por categoria", textos)
            graficos = tela.findChildren(GraficoBarrasInterativo)
            self.assertEqual(len(graficos), 1)
            self.assertEqual(len(graficos[0].meses), 6)
            self.assertLessEqual(len(graficos[0].series), 4)
            self.assertEqual(graficos[0].minimumHeight(), 224)
            self.assertEqual(graficos[0].maximumHeight(), 224)
            self.assertTrue(all(card.minimumHeight() == 76 for card in cards))
            self.assertEqual(tela.quantidade_colunas_cartoes(900), 2)
            self.assertEqual(tela.quantidade_colunas_cartoes(1600), 4)
            botao_anterior = tela.findChildren(QPushButton, "btnMesRelatorio")[0]
            botao_mes_atual = tela.findChild(QPushButton, "btnMesAtualRelatorio")
            botao_atualizar = tela.findChild(QPushButton, "btnAtualizarRelatorio")
            self.assertEqual(botao_anterior.maximumWidth(), 42)
            self.assertEqual(botao_mes_atual.minimumWidth(), 126)
            self.assertEqual(botao_mes_atual.maximumWidth(), 126)
            self.assertEqual(botao_atualizar.minimumWidth(), 128)
            self.assertEqual(botao_atualizar.maximumWidth(), 128)
            detalhes = tela.criar_janela_detalhes_lancamentos(
                "Categoria de teste — Maio de 2099",
                [{
                    "data": date(2099, 5, 10),
                    "data_texto": "10/05",
                    "descricao": "Lançamento visual de teste",
                    "categoria": "Teste",
                    "tipo": "Gasto",
                    "valor": 123.45,
                }],
            )
            tabela = detalhes.findChild(QTableWidget, "tabelaDetalhesRelatorio")
            self.assertEqual(tabela.selectionMode(), QTableWidget.NoSelection)
            self.assertEqual(tabela.columnCount(), 6)
            self.assertTrue(tabela.item(0, 0).flags() & Qt.ItemIsUserCheckable)
            tabela.item(0, 0).setCheckState(Qt.Checked)
            app.processEvents()
            selecao = detalhes.findChild(QLabel, "selecaoDetalhes")
            self.assertIn("R$ 123,45", selecao.text())
            filtro = detalhes.findChild(QComboBox, "filtroCategoriaDetalhesRelatorio")
            self.assertEqual(filtro.currentText(), "Todas as categorias")
            self.assertLessEqual(detalhes.height(), 630)
            detalhes.close()

            detalhes_por_categoria = tela.criar_janela_detalhes_lancamentos(
                "Bebidas — Julho de 2026",
                [
                    {
                        "data": date(2026, 7, 20),
                        "data_texto": "20/07",
                        "descricao": "Bebidas ZN",
                        "categoria": "Bebidas",
                        "tipo": "Gasto",
                        "valor": 70.00,
                    },
                    {
                        "data": date(2026, 7, 19),
                        "data_texto": "19/07",
                        "descricao": "Lanche",
                        "categoria": "Lanche",
                        "tipo": "Gasto",
                        "valor": 25.00,
                    },
                ],
            )
            filtro = detalhes_por_categoria.findChild(
                QComboBox, "filtroCategoriaDetalhesRelatorio"
            )
            filtro.setCurrentText("Bebidas")
            app.processEvents()
            tabela = detalhes_por_categoria.findChild(QTableWidget, "tabelaDetalhesRelatorio")
            self.assertEqual(tabela.rowCount(), 1)
            total = detalhes_por_categoria.findChild(QLabel, "totalDetalhes")
            self.assertIn("R$ 70,00", total.text())
            detalhes_por_categoria.close()
            dados_anterior = tela.dados_mes(tela.referencia_mes_anterior())
            self.assertIn("total_pago", dados_anterior)
        finally:
            tela.close()
            tela.deleteLater()
            app.processEvents()


if __name__ == "__main__":
    unittest.main()
