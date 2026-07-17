from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QComboBox, QMessageBox
)
from PySide6.QtCore import QDate

from banco.banco import inserir_despesa, atualizar_despesa, pagar_despesa, excluir_despesa_com_historico, excluir_despesa
from servicos.valores import converter_texto_moeda


class NovaDespesa(QDialog):
    def __init__(self, despesa=None):
        super().__init__()

        self.despesa = despesa
        self.modo_edicao = despesa is not None

        self.setWindowTitle("Editar despesa" if self.modo_edicao else "Nova despesa")
        self.setFixedSize(520, 460)

        self.aplicar_estilo()
        self.montar_tela()

    def aplicar_estilo(self):
        self.setStyleSheet("""
            QDialog { background-color: #0f1117; }

            QLabel {
                color: #f5f5f5;
                font-family: Segoe UI;
                font-size: 14px;
                background-color: transparent;
            }

            QLabel#titulo {
                font-size: 26px;
                font-weight: bold;
            }

            QLabel#subtitulo {
                color: #9aa2b8;
                font-size: 13px;
            }

            QLabel#valorTotal {
                color: #9aa2b8;
                font-size: 13px;
                font-weight: bold;
            }

            QLineEdit, QComboBox {
                background-color: #181d29;
                color: white;
                border: 1px solid #252b3a;
                border-radius: 8px;
                padding: 5px 10px;
                min-height: 28px;
                font-size: 14px;
            }

            QLineEdit:focus, QComboBox:focus {
                border: 1px solid #2d6cdf;
            }

            QComboBox::drop-down {
                border: none;
                background-color: #181d29;
                width: 28px;
            }

            QPushButton {
                min-height: 34px;
                border-radius: 9px;
                font-size: 14px;
                font-weight: bold;
                border: none;
            }

            QPushButton#cancelar {
                background-color: #202638;
                color: #d7dcf0;
            }

            QPushButton#salvar {
                background-color: #2d6cdf;
                color: white;
            }

            QPushButton#pagar {
                background-color: #16a34a;
                color: white;
            }

            QPushButton#pagar:hover {
                background-color: #22c55e;
            }

            QPushButton#excluir {
                background-color: #dc2626;
                color: white;
            }

            QPushButton#excluir:hover {
                background-color: #ef4444;
            }

            QDialog#confirmacaoPagamento {
                background-color: #0f1117;
            }

            QLabel#confirmacaoTitulo {
                font-size: 22px;
                font-weight: bold;
                color: #ffffff;
            }

            QLabel#confirmacaoTexto {
                font-size: 14px;
                color: #b8c0d6;
            }

            QLabel#confirmacaoIcone {
                font-size: 34px;
                min-width: 58px;
                max-width: 58px;
                min-height: 58px;
                max-height: 58px;
                border-radius: 29px;
                background-color: rgba(34, 197, 94, 0.12);
                border: 1px solid rgba(34, 197, 94, 0.35);
                qproperty-alignment: AlignCenter;
            }

            QPushButton#confirmacaoNao {
                background-color: #202638;
                color: #d7dcf0;
                border: 1px solid #293145;
            }

            QPushButton#confirmacaoSim {
                background-color: #16a34a;
                color: #ffffff;
                border: 1px solid #22c55e;
            }

            QPushButton#confirmacaoSim:hover {
                background-color: #22c55e;
            }
        """)

    def campo(self, titulo, widget):
        bloco = QVBoxLayout()
        bloco.setSpacing(4)

        label = QLabel(titulo)
        bloco.addWidget(label)
        bloco.addWidget(widget)

        return bloco, label

    def montar_tela(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 22, 24, 20)
        layout.setSpacing(10)

        titulo = QLabel("Editar despesa" if self.modo_edicao else "Nova despesa")
        titulo.setObjectName("titulo")

        subtitulo = QLabel(
            "Altere os dados da despesa" if self.modo_edicao else "Cadastre uma saída de dinheiro"
        )
        subtitulo.setObjectName("subtitulo")

        self.descricao = QLineEdit()
        self.descricao.setPlaceholderText("Ex: Internet, mercado, luz...")

        self.valor = QLineEdit()
        self.valor.setPlaceholderText("Valor da parcela. Ex: 108,80")
        self.valor.textChanged.connect(self.atualizar_valor_total)

        self.vencimento = QLineEdit()
        self.vencimento.setInputMask("00/00/0000")
        self.vencimento.setText(QDate.currentDate().toString("dd/MM/yyyy"))

        self.categoria = QComboBox()
        self.categoria.addItems(["Casa", "Mercado", "Internet", "Luz", "Água", "Carro", "Outros"])

        self.tipo = QComboBox()
        self.tipo.addItems(["Despesa única", "Conta fixa", "Parcelamento"])
        self.tipo.currentTextChanged.connect(self.atualizar_campos_parcela)

        self.parcela_atual = QLineEdit()
        self.parcela_atual.setPlaceholderText("Ex: 3")
        self.parcela_atual.textChanged.connect(self.atualizar_valor_total)

        self.total_parcelas = QLineEdit()
        self.total_parcelas.setPlaceholderText("Ex: 12")
        self.total_parcelas.textChanged.connect(self.atualizar_valor_total)

        self.valor_total_label = QLabel("Valor total: R$ 0,00")
        self.valor_total_label.setObjectName("valorTotal")

        self.valor.setMinimumWidth(220)
        self.vencimento.setMinimumWidth(220)
        self.categoria.setMinimumWidth(220)
        self.tipo.setMinimumWidth(220)
        self.parcela_atual.setMinimumWidth(220)
        self.total_parcelas.setMinimumWidth(220)

        if self.modo_edicao:
            self.preencher_campos()

        linha_valor_data = QHBoxLayout()
        linha_valor_data.setSpacing(12)
        campo_valor, _ = self.campo("Valor da parcela", self.valor)
        campo_vencimento, _ = self.campo("Vencimento", self.vencimento)
        linha_valor_data.addLayout(campo_valor)
        linha_valor_data.addLayout(campo_vencimento)

        linha_categoria_tipo = QHBoxLayout()
        linha_categoria_tipo.setSpacing(12)
        campo_categoria, _ = self.campo("Categoria", self.categoria)
        campo_tipo, _ = self.campo("Tipo", self.tipo)
        linha_categoria_tipo.addLayout(campo_categoria)
        linha_categoria_tipo.addLayout(campo_tipo)

        linha_parcelas = QHBoxLayout()
        linha_parcelas.setSpacing(12)
        campo_parcela_atual, self.lbl_parcela_atual = self.campo("Parcela atual", self.parcela_atual)
        campo_total_parcelas, self.lbl_total_parcelas = self.campo("Total de parcelas", self.total_parcelas)
        linha_parcelas.addLayout(campo_parcela_atual)
        linha_parcelas.addLayout(campo_total_parcelas)

        btn_cancelar = QPushButton("Cancelar")
        btn_cancelar.setObjectName("cancelar")
        btn_cancelar.setFixedWidth(120)
        btn_cancelar.clicked.connect(self.reject)

        btn_salvar = QPushButton("Salvar")
        btn_salvar.setObjectName("salvar")
        btn_salvar.setFixedWidth(120)
        btn_salvar.clicked.connect(self.salvar_despesa)

        botoes = QHBoxLayout()
        botoes.setSpacing(12)
        botoes.addStretch()

        if self.modo_edicao and self.despesa[-1] != "paga":
            btn_pagar = QPushButton("✓ Pagar")
            btn_pagar.setObjectName("pagar")
            btn_pagar.setFixedWidth(105)
            btn_pagar.clicked.connect(self.pagar)
            botoes.addWidget(btn_pagar)

        if self.modo_edicao:
            btn_excluir = QPushButton("🗑 Excluir")
            btn_excluir.setObjectName("excluir")
            btn_excluir.setFixedWidth(105)
            btn_excluir.clicked.connect(self.excluir)
            botoes.addWidget(btn_excluir)

        botoes.addWidget(btn_cancelar)
        botoes.addWidget(btn_salvar)

        campo_descricao, _ = self.campo("Descrição", self.descricao)

        layout.addWidget(titulo)
        layout.addWidget(subtitulo)
        layout.addSpacing(6)
        layout.addLayout(campo_descricao)
        layout.addLayout(linha_valor_data)
        layout.addLayout(linha_categoria_tipo)
        layout.addLayout(linha_parcelas)
        layout.addWidget(self.valor_total_label)
        layout.addStretch()
        layout.addLayout(botoes)

        self.atualizar_campos_parcela()
        self.atualizar_valor_total()
        self.descricao.setFocus()

    def atualizar_campos_parcela(self):
        mostrar = self.tipo.currentText() == "Parcelamento"

        self.parcela_atual.setVisible(mostrar)
        self.total_parcelas.setVisible(mostrar)
        self.lbl_parcela_atual.setVisible(mostrar)
        self.lbl_total_parcelas.setVisible(mostrar)
        self.valor_total_label.setVisible(mostrar)

        self.atualizar_valor_total()

    def calcular_valor_total(self):
        if self.tipo.currentText() != "Parcelamento":
            return None

        try:
            valor = converter_texto_moeda(self.valor.text())
            total_parcelas = int(self.total_parcelas.text().strip())
            return valor * total_parcelas
        except ValueError:
            return None

    def atualizar_valor_total(self):
        total = self.calcular_valor_total()

        if total is None:
            self.valor_total_label.setText("Valor total: R$ 0,00")
        else:
            self.valor_total_label.setText(
                f"Valor total: R$ {total:.2f}".replace(".", ",")
            )

    def separar_despesa(self):
        if len(self.despesa) == 10:
            return self.despesa

        if len(self.despesa) == 9:
            id_despesa, descricao, valor, vencimento, categoria, tipo, parcela_atual, total_parcelas, status = self.despesa
            return id_despesa, descricao, valor, vencimento, categoria, tipo, parcela_atual, total_parcelas, None, status

        id_despesa, descricao, valor, vencimento, categoria, tipo, status = self.despesa
        return id_despesa, descricao, valor, vencimento, categoria, tipo, None, None, None, status

    def preencher_campos(self):
        (
            id_despesa,
            descricao,
            valor,
            vencimento,
            categoria,
            tipo,
            parcela_atual,
            total_parcelas,
            valor_total,
            status,
        ) = self.separar_despesa()

        self.descricao.setText(descricao)
        self.valor.setText(f"{valor:.2f}".replace(".", ","))

        data = QDate.fromString(vencimento, "yyyy-MM-dd")
        self.vencimento.setText(data.toString("dd/MM/yyyy"))

        self.categoria.setCurrentText(categoria)
        self.tipo.setCurrentText(tipo)

        if parcela_atual:
            self.parcela_atual.setText(str(parcela_atual))

        if total_parcelas:
            self.total_parcelas.setText(str(total_parcelas))

    def confirmar_pagamento(self):
        janela = QDialog(self)
        janela.setObjectName("confirmacaoPagamento")
        janela.setWindowTitle("Pagar despesa")
        janela.setFixedSize(420, 230)
        janela.setModal(True)
        janela.setStyleSheet(self.styleSheet())

        layout = QVBoxLayout(janela)
        layout.setContentsMargins(22, 20, 22, 18)
        layout.setSpacing(14)

        topo = QHBoxLayout()
        topo.setSpacing(14)

        icone = QLabel("✓")
        icone.setObjectName("confirmacaoIcone")

        textos = QVBoxLayout()
        textos.setSpacing(5)

        titulo = QLabel("Confirmar pagamento?")
        titulo.setObjectName("confirmacaoTitulo")

        texto = QLabel("Esta despesa será marcada como paga.")
        texto.setObjectName("confirmacaoTexto")
        texto.setWordWrap(True)

        textos.addWidget(titulo)
        textos.addWidget(texto)

        topo.addWidget(icone)
        topo.addLayout(textos, 1)

        botoes = QHBoxLayout()
        botoes.setSpacing(12)
        botoes.addStretch()

        btn_nao = QPushButton("Cancelar")
        btn_nao.setObjectName("confirmacaoNao")
        btn_nao.setFixedWidth(130)
        btn_nao.clicked.connect(janela.reject)

        btn_sim = QPushButton("✓ Confirmar")
        btn_sim.setObjectName("confirmacaoSim")
        btn_sim.setFixedWidth(140)
        btn_sim.clicked.connect(janela.accept)

        botoes.addWidget(btn_nao)
        botoes.addWidget(btn_sim)

        layout.addLayout(topo)
        layout.addStretch()
        layout.addLayout(botoes)

        return janela.exec() == QDialog.Accepted


    def confirmar_exclusao(self):
        caixa = QMessageBox(self)
        caixa.setWindowTitle("Excluir despesa")
        caixa.setText("Tem certeza que deseja excluir esta despesa?")
        caixa.setInformativeText("Esta ação não poderá ser desfeita.")
        caixa.setIcon(QMessageBox.Warning)

        btn_excluir = caixa.addButton("Excluir", QMessageBox.YesRole)
        btn_cancelar = caixa.addButton("Cancelar", QMessageBox.NoRole)

        caixa.setStyleSheet("""
            QMessageBox { background-color: #0f1117; border: 2px solid #1f2937; border-top: 4px solid #ef4444; border-radius: 10px; }
            QLabel { color: #d7dcf0; font-family: 'Segoe UI'; font-size: 13px; padding-left: 6px; }
            QPushButton { background-color: #1f2937; color: #ffffff; border: 1px solid #334155; border-radius: 6px; padding: 6px 16px; font-weight: bold; font-size: 12px; min-width: 85px; }
            QPushButton:hover { background-color: #ef4444; border: 1px solid #ef4444; }
        """)

        caixa.exec()
        return caixa.clickedButton() == btn_excluir

    def confirmar_exclusao_paga(self):
        caixa = QMessageBox(self)
        caixa.setWindowTitle("Excluir despesa paga")
        caixa.setText("Esta despesa já foi paga.")
        caixa.setInformativeText(
            "Ela já foi considerada no saldo do sistema.\n\n"
            "Escolha se deseja manter o saldo atual ou estornar este pagamento."
        )
        caixa.setIcon(QMessageBox.Warning)

        btn_manter = caixa.addButton("Manter saldo", QMessageBox.YesRole)
        btn_estornar = caixa.addButton("Estornar pagamento", QMessageBox.DestructiveRole)
        btn_cancelar = caixa.addButton("Cancelar", QMessageBox.NoRole)

        caixa.setStyleSheet("""
            QMessageBox { background-color: #0f1117; border: 2px solid #1f2937; border-top: 4px solid #ef4444; border-radius: 10px; }
            QLabel { color: #d7dcf0; font-family: 'Segoe UI'; font-size: 13px; padding-left: 6px; }
            QPushButton { background-color: #1f2937; color: #ffffff; border: 1px solid #334155; border-radius: 6px; padding: 6px 16px; font-weight: bold; font-size: 12px; min-width: 170px; }
            QPushButton:hover { background-color: #ef4444; border: 1px solid #ef4444; }
        """)

        caixa.setMinimumSize(760, 280)
        btn_manter.setMinimumWidth(180)
        btn_estornar.setMinimumWidth(210)
        btn_cancelar.setMinimumWidth(180)

        caixa.exec()
        clicado = caixa.clickedButton()
        if clicado == btn_manter:
            return "manter_saldo"
        if clicado == btn_estornar:
            return "estornar"
        return "cancelar"

    def excluir(self):
        if not self.modo_edicao:
            return

        id_despesa = self.despesa[0]
        status = str(self.despesa[-1]).lower() if self.despesa else ""

        if status == "paga":
            escolha = self.confirmar_exclusao_paga()
            if escolha == "cancelar":
                return
            if escolha == "manter_saldo":
                excluir_despesa(id_despesa)
            else:
                excluir_despesa_com_historico(id_despesa)
        else:
            if not self.confirmar_exclusao():
                return
            excluir_despesa(id_despesa)

        self.accept()

    def pagar(self):
        if not self.confirmar_pagamento():
            return

        id_despesa = self.despesa[0]
        pagar_despesa(id_despesa)
        self.accept()

    def salvar_despesa(self):
        descricao = self.descricao.text().strip()
        data_texto = self.vencimento.text().strip()
        categoria = self.categoria.currentText()
        tipo = self.tipo.currentText()

        parcela_atual = None
        total_parcelas = None
        valor_total = None

        if not descricao:
            QMessageBox.warning(self, "Atenção", "Preencha a descrição.")
            self.descricao.setFocus()
            return

        try:
            valor = converter_texto_moeda(self.valor.text())
        except ValueError:
            QMessageBox.warning(self, "Atenção", "Digite um valor maior que zero. Ex: 129,90")
            self.valor.setFocus()
            return

        data = QDate.fromString(data_texto, "dd/MM/yyyy")
        if not data.isValid():
            QMessageBox.warning(self, "Atenção", "Digite uma data válida. Ex: 30/06/2026")
            self.vencimento.setFocus()
            return

        if tipo == "Parcelamento":
            try:
                parcela_atual = int(self.parcela_atual.text().strip())
                total_parcelas = int(self.total_parcelas.text().strip())
            except ValueError:
                QMessageBox.warning(self, "Atenção", "Preencha as parcelas corretamente. Ex: 3 de 12")
                self.parcela_atual.setFocus()
                return

            if parcela_atual <= 0 or total_parcelas <= 0 or parcela_atual > total_parcelas:
                QMessageBox.warning(self, "Atenção", "A parcela atual não pode ser maior que o total.")
                self.parcela_atual.setFocus()
                return

            valor_total = valor * total_parcelas

        vencimento = data.toString("yyyy-MM-dd")

        if self.modo_edicao:
            id_despesa = self.despesa[0]
            atualizar_despesa(
                id_despesa, descricao, valor, vencimento, categoria, tipo,
                parcela_atual, total_parcelas, valor_total
            )
        else:
            inserir_despesa(
                descricao, valor, vencimento, categoria, tipo,
                parcela_atual, total_parcelas, valor_total
            )

        self.accept()
