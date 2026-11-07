from datetime import date
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_api_salud():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["estado"] == "operativo"


def test_flujo_autenticacion_y_gastos():
    # 1. Registro de usuario (HU-10)
    correo_test = "usuario_demo@correo.com"
    resp_reg = client.post("/usuarios", json={"correo": correo_test, "contrasena": "secreto1234"})
    assert resp_reg.status_code in [201, 409]

    # 2. Inicio de sesión (HU-10)
    resp_login = client.post("/sesiones", json={"correo": correo_test, "contrasena": "secreto1234"})
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
        "id_categoria": id_cat
    }
    resp_gasto = client.post("/gastos", json=gasto_data, headers=headers)
    assert resp_gasto.status_code == 201
    assert "Location" in resp_gasto.headers
    id_gasto = resp_gasto.json()["id_gasto"]

    # 5. Obtener gasto creado
    resp_get = client.get(f"/gastos/{id_gasto}", headers=headers)
    assert resp_get.status_code == 200
    assert resp_get.json()["comercio"] == "Supermercado Central"

    # 6. Rechazar campos prohibidos con 400 (R-01, R-03, HU-09)
    gasto_con_datos_sensibles = {
        "comercio": "Supermercado Central",
        "fecha": "2026-10-15",
        "monto": 85000.0,
        "id_categoria": id_cat,
        "nombre": "Carlos Mora",
        "tarjeta": "4821"
    }
    resp_sensible = client.post("/gastos", json=gasto_con_datos_sensibles, headers=headers)
    assert resp_sensible.status_code == 400

    # 7. Rechazar monto inválido (HU-03)
    resp_monto_cero = client.post("/gastos", json={
        "comercio": "Tienda",
        "fecha": "2026-10-15",
        "monto": 0,
        "id_categoria": id_cat
    }, headers=headers)
    assert resp_monto_cero.status_code == 422
    assert resp_monto_cero.json()["detail"] == "El monto debe ser un numero mayor a 0"

    # 8. Rechazar fecha futura con mensaje exacto (HU-02)
    resp_fecha_futura = client.post("/gastos", json={
        "comercio": "Tienda",
        "fecha": "2099-01-01",
        "monto": 50000.0,
        "id_categoria": id_cat
    }, headers=headers)
    assert resp_fecha_futura.status_code == 422
    assert resp_fecha_futura.json()["detail"] == "La fecha no puede ser posterior a hoy"

    # 9. Topes y alertas (HU-07, HU-08)
    resp_tope = client.put("/topes", json={
        "id_categoria": id_cat,
        "anio": 2026,
        "mes": 10,
        "monto_tope": 100000.0
    }, headers=headers)
    assert resp_tope.status_code == 200
    assert resp_tope.json()["alerta_80"] is True
    assert "Llevas el 85 % de tu tope" in resp_tope.json()["mensaje_alerta"]
