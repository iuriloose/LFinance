from banco.banco import inserir_despesa
from modelos.despesa import Despesa


class Financeiro:

    @staticmethod
    def adicionar_despesa(despesa: Despesa):
        inserir_despesa(
            despesa.descricao,
            despesa.valor,
            despesa.vencimento,
            despesa.categoria,
            despesa.tipo
        )