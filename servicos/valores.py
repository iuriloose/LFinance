from decimal import Decimal, InvalidOperation, ROUND_HALF_UP


def converter_texto_moeda(texto):
    """Converte valores digitados nos formatos brasileiro ou internacional."""
    valor_texto = str(texto or "").strip()
    valor_texto = valor_texto.replace("R$", "").replace(" ", "")

    if not valor_texto:
        raise ValueError("Valor vazio")

    if "," in valor_texto:
        normalizado = valor_texto.replace(".", "").replace(",", ".")
    elif valor_texto.count(".") > 1:
        partes = valor_texto.split(".")
        if len(partes[-1]) in (1, 2):
            normalizado = "".join(partes[:-1]) + "." + partes[-1]
        else:
            normalizado = "".join(partes)
    elif "." in valor_texto:
        inteiro, decimal = valor_texto.rsplit(".", 1)
        normalizado = inteiro + decimal if len(decimal) == 3 else valor_texto
    else:
        normalizado = valor_texto

    try:
        valor = Decimal(normalizado)
    except InvalidOperation as erro:
        raise ValueError("Valor inválido") from erro

    if not valor.is_finite() or valor <= 0:
        raise ValueError("O valor deve ser maior que zero")

    return float(valor.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))
