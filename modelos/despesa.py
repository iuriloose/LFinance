from dataclasses import dataclass


@dataclass
class Despesa:
    descricao: str
    valor: float
    vencimento: str
    categoria: str
    tipo: str
    status: str = "aberta"
    id: int | None = None