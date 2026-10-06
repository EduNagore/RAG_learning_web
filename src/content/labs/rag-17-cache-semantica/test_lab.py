from ragkit.testing import expect_close, expect_equal

# Vectores unitarios elegidos a mano: cos(a, b) = 0.9, cos(a, c) = 0.0
VECTORES = {
    "a": [1.0, 0.0],
    "b": [0.9, 0.435889894],
    "c": [0.0, 1.0],
    "d": [0.6, 0.8],
}


def embed(texto):
    return VECTORES[texto]


def test_acierta_con_la_misma_consulta(student):
    """Una consulta idéntica a una guardada es un acierto"""
    cache = student.SemanticCache(embed, threshold=0.95)
    cache.put("a", "respuesta A")
    expect_equal(cache.get("a"), "respuesta A", what="acierto exacto")


def test_el_umbral_decide_entre_acierto_y_fallo(student):
    """Con similitud 0.9: acierto si threshold <= 0.9 y fallo si es mayor"""
    laxa = student.SemanticCache(embed, threshold=0.9)
    laxa.put("a", "A")
    expect_equal(laxa.get("b"), "A", what="similitud 0.9 con umbral 0.9")
    estricta = student.SemanticCache(embed, threshold=0.95)
    estricta.put("a", "A")
    expect_equal(estricta.get("b"), None, what="similitud 0.9 con umbral 0.95")


def test_devuelve_la_entrada_mas_parecida(student):
    """Entre varias entradas por encima del umbral gana la más similar"""
    cache = student.SemanticCache(embed, threshold=0.5)
    cache.put("d", "D")
    cache.put("a", "A")
    expect_equal(cache.get("b"), "A", what="b se parece más a «a» (0.90) que a «d» (0.89)")
    otra = student.SemanticCache(embed, threshold=0.5)
    otra.put("a", "A")
    otra.put("d", "D")
    expect_equal(otra.get("b"), "A", what="el orden de inserción no debe importar")


def test_acepta_la_similitud_exacta_del_umbral_y_normaliza_los_vectores(student):
    """Con threshold=1.0 un vector idéntico es acierto; los vectores se normalizan antes de comparar"""
    cache = student.SemanticCache(embed, threshold=1.0)
    cache.put("a", "A")
    expect_equal(cache.get("a"), "A", what="similitud 1.0 con umbral 1.0")
    sin_normalizar = {"x": [1.0, 0.0], "y": [0.5, 0.0]}
    cache2 = student.SemanticCache(lambda t: sin_normalizar[t], threshold=0.99)
    cache2.put("x", "X")
    expect_equal(cache2.get("y"), "X", what="misma dirección, distinta longitud")


def test_las_estadisticas_cuentan_aciertos_y_fallos(student):
    """stats devuelve hits, misses, hit_rate y size"""
    cache = student.SemanticCache(embed, threshold=0.95)
    expect_equal(cache.stats()["hit_rate"], 0.0, what="hit_rate sin consultas")
    cache.put("a", "A")
    cache.get("a")
    cache.get("c")
    cache.get("a")
    s = cache.stats()
    expect_equal((s["hits"], s["misses"], s["size"]), (2, 1, 1), what="contadores")
    expect_close(s["hit_rate"], 2 / 3, what="hit_rate")


def test_lru_expulsa_la_menos_usada(student):
    """Al superar max_size se expulsa la menos usada recientemente, no la más antigua sin más"""
    cache = student.SemanticCache(embed, threshold=0.99, max_size=2)
    cache.put("a", "A")
    cache.put("c", "C")
    cache.get("a")  # a pasa a ser la más reciente
    cache.put("d", "D")  # debe expulsar c
    expect_equal(cache.get("c"), None, what="c debería haberse expulsado")
    expect_equal(cache.get("a"), "A", what="a se conserva")
    expect_equal(cache.stats()["size"], 2, what="tamaño")


def test_ttl_caduca_las_entradas(student):
    """now - created > ttl caduca; justo igual no"""
    cache = student.SemanticCache(embed, threshold=0.99, ttl=10)
    cache.put("a", "A", now=100)
    expect_equal(cache.get("a", now=110), "A", what="en el límite no caduca")
    expect_equal(cache.get("a", now=111), None, what="pasado el ttl caduca")
    expect_equal(cache.stats()["size"], 0, what="la entrada caducada se elimina")


def test_hidden_sin_ttl_nunca_caduca(student):
    """Caso adicional: ttl=None no caduca por mucho que pase el tiempo"""
    cache = student.SemanticCache(embed, threshold=0.99)
    cache.put("a", "A", now=0)
    expect_equal(cache.get("a", now=10**9), "A", what="sin ttl")


def test_hidden_un_fallo_no_altera_el_orden_lru(student):
    """Caso adicional: una consulta que falla no cambia qué entrada se expulsa"""
    cache = student.SemanticCache(embed, threshold=0.99, max_size=2)
    cache.put("a", "A")
    cache.put("c", "C")
    cache.get("d")  # fallo
    cache.put("d", "D")  # expulsa a, la más antigua sin uso
    expect_equal(cache.get("a"), None, what="a expulsada")
    expect_equal(cache.get("c"), "C", what="c conservada")
