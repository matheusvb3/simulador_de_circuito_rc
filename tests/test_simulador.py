from simulador_de_circuito_rc.simulador import calcular_tensao, calcular_corrente

def test_calcular_tensao():
    assert calcular_tensao(5, 1, 1, 0) == 5
    assert calcular_tensao(5, 1, 1, 1) < 5

def test_calcular_corrente():
    assert calcular_corrente(5, 1, 1, 0) == 5
    assert calcular_corrente(5, 1, 1, 1) < 5
