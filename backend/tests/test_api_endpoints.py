from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)


def test_api_salud():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["estado"] == "operativo"


def test_flujo_autenticacion_y_gastos():
    # 1. Registro de usuario (HU-10)
    correo_test = "usuario_demo@correo.com"
    resp_reg = client.post(
        "/usuarios", json={"correo": correo_test, "contrasena": "secreto1234"}
    )
    assert resp_reg.status_code in [201, 409]

    # 2. Inicio de sesión (HU-10)
    resp_login = client.post(
        "/sesiones", json={"correo": correo_test, "contrasena": "secreto1234"}
    )
    assert resp_login.status_code == 200
    token = resp_login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 3. Listar categorías (HU-04)
    resp_cat = client.get("/categorias", headers=headers)
    assert resp_cat.status_code == 200
    categorias = resp_cat.json()
    assert len(categorias) >= 3
    id_cat = categorias[0]["id_categoria"]

    # 4. Crear gasto válido (HU-02 Escenario 1)
    gasto_data = {
        "comercio": "Supermercado Central",
        "fecha": "2026-10-15",
        "monto": 85000.0,
        "id_categoria": id_cat,
    }
    # Dado: un usuario autenticado y una categoría disponible.
    # Cuando: registra un gasto con los datos del escenario HU-02.
    resp_gasto = client.post("/gastos", json=gasto_data, headers=headers)
    # Entonces: se crea y devuelve el gasto con todos sus datos.
    assert resp_gasto.status_code == 201
    assert "Location" in resp_gasto.headers
    gasto_creado = resp_gasto.json()
    id_gasto = gasto_creado["id_gasto"]
    assert gasto_creado["comercio"] == gasto_data["comercio"]
    assert gasto_creado["fecha"] == gasto_data["fecha"]
    assert gasto_creado["monto"] == gasto_data["monto"]
    assert gasto_creado["id_categoria"] == id_cat

    # 5. Obtener gasto creado
    resp_get = client.get(f"/gastos/{id_gasto}", headers=headers)
    assert resp_get.status_code == 200
    assert resp_get.json() == gasto_creado

    resp_rango = client.get(
        "/gastos?fecha_inicio=2026-10-01&fecha_fin=2026-10-31",
        headers=headers,
    )
    assert resp_rango.status_code == 200
    assert resp_rango.json() == [gasto_creado]

    resp_rango_invalido = client.get(
        "/gastos?fecha_inicio=2026-10-31&fecha_fin=2026-10-01",
        headers=headers,
    )
    assert resp_rango_invalido.status_code == 400

    # 6. Rechazar campos prohibidos con 400 (R-01, R-03, HU-09)
    gasto_con_datos_sensibles = {
        "comercio": "Supermercado Central",
        "fecha": "2026-10-15",
        "monto": 85000.0,
        "id_categoria": id_cat,
        "nombre": "Carlos Mora",
        "tarjeta": "4821",
    }
    resp_sensible = client.post(
        "/gastos", json=gasto_con_datos_sensibles, headers=headers
    )
    assert resp_sensible.status_code == 400

    # 7. Rechazar monto inválido (HU-03)
    resp_monto_cero = client.post(
        "/gastos",
        json={
            "comercio": "Tienda",
            "fecha": "2026-10-15",
            "monto": 0,
            "id_categoria": id_cat,
        },
        headers=headers,
    )
    assert resp_monto_cero.status_code == 422
    assert resp_monto_cero.json()["detail"] == "El monto debe ser un número mayor a 0"

    # 8. Rechazar fecha futura con mensaje exacto (HU-02)
    # Dado: una solicitud de gasto con fecha 01/01/2099.
    # Cuando: el usuario intenta registrarla.
    resp_fecha_futura = client.post(
        "/gastos",
        json={
            "comercio": "Tienda",
            "fecha": "2099-01-01",
            "monto": 50000.0,
            "id_categoria": id_cat,
        },
        headers=headers,
    )
    # Entonces: se rechaza y no aparece en el historial.
    assert resp_fecha_futura.status_code == 422
    assert resp_fecha_futura.json()["detail"] == "La fecha no puede ser posterior a hoy"
    gastos_futuros = client.get("/gastos?fecha=2099-01-01", headers=headers)
    assert gastos_futuros.status_code == 200
    assert gastos_futuros.json() == []

    # 8a. Validar los mensajes exactos cuando faltan datos obligatorios
    resp_sin_categoria = client.post(
        "/gastos",
        json={
            "comercio": "Tienda",
            "fecha": "2026-10-15",
            "monto": 50000.0,
        },
        headers=headers,
    )
    assert resp_sin_categoria.status_code == 422
    assert resp_sin_categoria.json()["detail"] == "Elige una categoría"

    resp_sin_comercio = client.post(
        "/gastos",
        json={
            "fecha": "2026-10-15",
            "monto": 50000.0,
            "id_categoria": id_cat,
        },
        headers=headers,
    )
    assert resp_sin_comercio.status_code == 422
    assert resp_sin_comercio.json()["detail"] == "El comercio es obligatorio"

    resp_json_mal_formado = client.post(
        "/gastos",
        content='{"comercio":',
        headers={**headers, "Content-Type": "application/json"},
    )
    assert resp_json_mal_formado.status_code == 400

    # 9. Topes y alertas (HU-07, HU-08)
    resp_tope = client.put(
        "/topes",
        json={"id_categoria": id_cat, "anio": 2026, "mes": 10, "monto_tope": 100000.0},
        headers=headers,
    )
    assert resp_tope.status_code == 200
    assert resp_tope.json()["alerta_80"] is True
    assert "Llevas el 85 % de tu tope" in resp_tope.json()["mensaje_alerta"]

    # 10. Eliminar gasto
    resp_delete = client.delete(f"/gastos/{id_gasto}", headers=headers)
    assert resp_delete.status_code == 204
    assert resp_delete.content == b""
    assert client.get(f"/gastos/{id_gasto}", headers=headers).status_code == 404
