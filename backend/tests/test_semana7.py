from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def contexto_sintetico():
    """Crea un usuario y reutiliza categorías locales para estas pruebas."""
    client = TestClient(app)
    correo = f"semana7-{uuid4().hex}@prueba.local"
    contrasena = "clave-sintetica-semana7"

    registro = client.post(
        "/usuarios",
        json={
            "nombre_usuario": "Pruebas Semana 7",
            "correo": correo,
            "contrasena": contrasena,
        },
    )
    assert registro.status_code == 201

    login = client.post(
        "/sesiones",
        json={"correo": correo, "contrasena": contrasena},
    )
    assert login.status_code == 200
    headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

    categorias = client.get("/categorias", headers=headers)
    assert categorias.status_code == 200
    ids_categoria = {
        categoria["nombre"]: categoria["id_categoria"]
        for categoria in categorias.json()
    }

    return {
        "client": client,
        "headers": headers,
        "ids_categoria": ids_categoria,
        "datos": {
            "comercio": "Mercado Ñandú d'Oliva",
            "comercio_vacio": "",
            "monto_valido": 85000,
            "monto_cero": 0,
            "monto_no_numerico": "abc",
        },
    }


@pytest.mark.parametrize(
    ("caso_monto", "estado_esperado", "detalle_esperado"),
    [
        # HU-03 escenario 1: se acepta el monto corregido de $85.000.
        ("monto_valido", 201, None),
        # HU-03 escenario 2: cero no es un monto válido.
        ("monto_cero", 422, "El monto debe ser un número mayor a 0"),
        # HU-03 escenario 2: el texto no numérico se rechaza en la API.
        # El mensaje exacto corresponde a la vista previa de la interfaz.
        ("monto_no_numerico", 422, None),
    ],
)
def test_hu03_valida_monto_al_guardar(
    contexto_sintetico, caso_monto, estado_esperado, detalle_esperado
):
    client = contexto_sintetico["client"]
    headers = contexto_sintetico["headers"]
    ids_categoria = contexto_sintetico["ids_categoria"]
    datos = contexto_sintetico["datos"]
    # Dado: un usuario autenticado y el monto especificado para cada caso HU-03.
    # Cuando: intenta registrar el gasto mediante la API.
    respuesta = client.post(
        "/gastos",
        headers=headers,
        json={
            "comercio": datos["comercio"],
            "fecha": "2026-10-15",
            "monto": datos[caso_monto],
            "id_categoria": ids_categoria["Comida"],
        },
    )

    # Entonces: se acepta el monto válido o se rechaza el inválido según HU-03.
    assert respuesta.status_code == estado_esperado
    gastos = client.get("/gastos?fecha=2026-10-15", headers=headers)
    assert gastos.status_code == 200
    if estado_esperado == 201:
        assert respuesta.json()["monto"] == pytest.approx(85000.0)
        assert respuesta.json()["comercio"] == datos["comercio"]
        assert respuesta.json()["fecha"] == "2026-10-15"
        assert respuesta.json()["id_categoria"] == ids_categoria["Comida"]
        assert gastos.json() == [respuesta.json()]
    else:
        if detalle_esperado is not None:
            assert respuesta.json()["detail"] == detalle_esperado
        assert gastos.json() == []


@pytest.mark.parametrize(
    ("elegir_categoria", "estado_esperado", "detalle_esperado"),
    [
        # HU-04 escenario 1: elegir «Comida» permite guardar en esa categoría.
        (True, 201, None),
        # HU-04 escenario 2: guardar sin categoría debe rechazarse.
        (False, 422, "Elige una categoría"),
    ],
)
def test_hu04_categoria_requerida(
    contexto_sintetico, elegir_categoria, estado_esperado, detalle_esperado
):
    client = contexto_sintetico["client"]
    headers = contexto_sintetico["headers"]
    ids_categoria = contexto_sintetico["ids_categoria"]
    datos = contexto_sintetico["datos"]
    gasto = {
        "comercio": datos["comercio"],
        "fecha": "2026-10-15",
        "monto": 85000,
    }
    if elegir_categoria:
        gasto["id_categoria"] = ids_categoria["Comida"]

    # Dado: un usuario autenticado y una solicitud con o sin «Comida».
    # Cuando: intenta guardar el gasto.
    respuesta = client.post("/gastos", headers=headers, json=gasto)

    # Entonces: la categoría queda asociada al gasto o se rechaza sin persistir.
    assert respuesta.status_code == estado_esperado
    gastos = client.get("/gastos?fecha=2026-10-15", headers=headers)
    assert gastos.status_code == 200
    if estado_esperado == 201:
        assert respuesta.json()["id_categoria"] == ids_categoria["Comida"]
        assert gastos.json() == [respuesta.json()]
    else:
        assert respuesta.json()["detail"] == detalle_esperado
        assert gastos.json() == []


@pytest.mark.parametrize(
    ("monto_tope", "estado_esperado", "detalle_esperado"),
    [
        # HU-07 escenario 1: el tope de $400.000 es positivo y se guarda.
        (400000, 200, None),
        # HU-07 escenario 2: un tope negativo se rechaza.
        (-50000, 422, "El tope debe ser mayor a $0"),
        # HU-07 escenario 2: un tope igual a cero se rechaza.
        (0, 422, "El tope debe ser mayor a $0"),
    ],
)
def test_hu07_valida_tope_mensual(
    contexto_sintetico, monto_tope, estado_esperado, detalle_esperado
):
    client = contexto_sintetico["client"]
    headers = contexto_sintetico["headers"]
    ids_categoria = contexto_sintetico["ids_categoria"]
    # Dado: el monto de tope indicado por HU-07 para «Comida», octubre de 2026.
    # Cuando: se crea el tope mediante la API.
    respuesta = client.put(
        "/topes",
        headers=headers,
        json={
            "id_categoria": ids_categoria["Comida"],
            "anio": 2026,
            "mes": 10,
            "monto_tope": monto_tope,
        },
    )

    # Entonces: se guarda el tope positivo o se rechaza el monto no permitido.
    assert respuesta.status_code == estado_esperado
    topes = client.get(
        "/topes?anio=2026&mes=10",
        headers=headers,
    )
    assert topes.status_code == 200
    if estado_esperado == 200:
        assert respuesta.json()["monto_tope"] == pytest.approx(400000.0)
        assert respuesta.json()["categoria"] == "Comida"
        assert respuesta.json()["anio"] == 2026
        assert respuesta.json()["mes"] == 10
        assert respuesta.json()["total_gastado"] == pytest.approx(0.0)
        assert respuesta.json()["alerta_80"] is True
        assert respuesta.json()["mensaje_alerta"]
        assert len(topes.json()) == 1
        assert topes.json()[0]["id_categoria"] == ids_categoria["Comida"]
        assert topes.json()[0]["monto_tope"] == pytest.approx(400000.0)
    else:
        assert respuesta.json()["detail"] == detalle_esperado
        assert topes.json() == []


@pytest.mark.parametrize(
    (
        "categoria",
        "monto_tope",
        "montos_gastos",
        "alerta_esperada",
        "mensaje_esperado",
    ),
    [
        # HU-08 escenario 1: $300.000 + $25.000 de $400.000 genera la alerta.
        ("Comida", 400000, [300000, 25000], True, "Llevas el 81 % de tu tope en Comida"),
        # Aclaración del usuario: exactamente 80 % no genera alerta.
        ("Comida", 400000, [320000], False, None),
        # Aclaración del usuario: un gasto menor al 80 % sí genera alerta.
        ("Comida", 400000, [300000], True, None),
        # HU-08 escenario 2: sin tope no debe existir una alerta para «Ocio».
        ("Ocio", None, [50000], False, None),
    ],
)
def test_hu08_alerta_depende_de_tope_y_gasto(
    contexto_sintetico,
    categoria,
    monto_tope,
    montos_gastos,
    alerta_esperada,
    mensaje_esperado,
):
    client = contexto_sintetico["client"]
    headers = contexto_sintetico["headers"]
    ids_categoria = contexto_sintetico["ids_categoria"]
    datos = contexto_sintetico["datos"]
    id_categoria = ids_categoria[categoria]

    # Dado: el tope y el gasto acumulado definidos para cada escenario HU-08.
    if monto_tope is not None:
        respuesta_tope = client.put(
            "/topes",
            headers=headers,
            json={
                "id_categoria": id_categoria,
                "anio": 2026,
                "mes": 10,
                "monto_tope": monto_tope,
            },
        )
        assert respuesta_tope.status_code == 200

    # Cuando: se registran esos gastos y se consulta el tope del período.
    for monto in montos_gastos:
        respuesta_gasto = client.post(
            "/gastos",
            headers=headers,
            json={
                "comercio": datos["comercio"],
                "fecha": "2026-10-15",
                "monto": monto,
                "id_categoria": id_categoria,
            },
        )
        assert respuesta_gasto.status_code == 201

    respuesta_topes = client.get(
        "/topes?anio=2026&mes=10",
        headers=headers,
    )
    # Entonces: se confirma la alerta definida o su ausencia si no existe tope.
    assert respuesta_topes.status_code == 200
    topes_categoria = [
        tope
        for tope in respuesta_topes.json()
        if tope["id_categoria"] == id_categoria
    ]

    if monto_tope is None:
        assert topes_categoria == []
    else:
        assert len(topes_categoria) == 1
        assert topes_categoria[0]["alerta_80"] is alerta_esperada
        assert topes_categoria[0]["total_gastado"] == pytest.approx(sum(montos_gastos))
        if alerta_esperada and mensaje_esperado is not None:
            assert topes_categoria[0]["mensaje_alerta"] == mensaje_esperado
        elif alerta_esperada:
            assert topes_categoria[0]["mensaje_alerta"]
        else:
            assert topes_categoria[0]["mensaje_alerta"] is None
