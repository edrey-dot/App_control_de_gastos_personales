"""Pruebas de seguridad y abuso (H-04).

Verifica controles de acceso, aislamiento entre usuarios (BOLA/IDOR),
rechazo de solicitudes no autenticadas y protección contra inyección de campos sensibles.
"""

from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)


def test_abuso_acceso_no_autenticado_retorna_401():
    """Verifica que endpoints privados rechacen peticiones sin token con 401."""
    # Intentar listar gastos sin token
    resp_gastos = client.get("/gastos")
    assert resp_gastos.status_code == 401

    # Intentar crear gasto sin token
    resp_crear = client.post(
        "/gastos",
        json={
            "comercio": "Tienda",
            "fecha": "2026-10-15",
            "monto": 10000.0,
            "id_categoria": 1,
        },
    )
    assert resp_crear.status_code == 401

    # Intentar ver categorías sin token
    resp_cat = client.get("/categorias")
    assert resp_cat.status_code == 401

    # Intentar ver topes sin token
    resp_topes = client.get("/topes?anio=2026&mes=10")
    assert resp_topes.status_code == 401


def test_abuso_token_falsificado_retorna_401():
    """Verifica que un token JWT inválido o manipulado sea rechazado con 401."""
    headers_falsos = {"Authorization": "Bearer token_completamente_invalido_xyz123"}
    resp = client.get("/gastos", headers=headers_falsos)
    assert resp.status_code == 401


def test_abuso_bola_usuario_no_puede_ver_gasto_ajeno():
    """Verifica protección BOLA (Broken Object Level Authorization, RNF-06).

    El usuario A crea un gasto. El usuario B intenta acceder al gasto de A.
    Debe recibir 404 Not Found (aislamiento de datos entre usuarios).
    """
    # 1. Crear Usuario A y registrar gasto
    email_a = "victima_a@correo.com"
    client.post("/usuarios", json={"correo": email_a, "contrasena": "clave_segura_a1"})
    token_a = client.post(
        "/sesiones", json={"correo": email_a, "contrasena": "clave_segura_a1"}
    ).json()["access_token"]
    headers_a = {"Authorization": f"Bearer {token_a}"}

    resp_gasto_a = client.post(
        "/gastos",
        json={
            "comercio": "Restaurante Secreto",
            "fecha": "2026-10-15",
            "monto": 120000.0,
            "id_categoria": 1,
        },
        headers=headers_a,
    )
    assert resp_gasto_a.status_code == 201
    id_gasto_a = resp_gasto_a.json()["id_gasto"]

    # 2. Crear Usuario B (Atacante)
    email_b = "atacante_b@correo.com"
    client.post("/usuarios", json={"correo": email_b, "contrasena": "clave_segura_b2"})
    token_b = client.post(
        "/sesiones", json={"correo": email_b, "contrasena": "clave_segura_b2"}
    ).json()["access_token"]
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # 3. Usuario B intenta leer el gasto del Usuario A por ID
    resp_abuso_b = client.get(f"/gastos/{id_gasto_a}", headers=headers_b)
    assert resp_abuso_b.status_code == 404
    assert resp_abuso_b.json()["detail"] == "Gasto no encontrado"


def test_abuso_inyeccion_datos_sensibles_prohibidos_retorna_400():
    """Verifica que campos no permitidos (tarjeta, cvv, direccion) se rechacen con 400.

    Reglas R-01, R-03, HU-09.
    """
    email_c = "usuario_test_c@correo.com"
    client.post("/usuarios", json={"correo": email_c, "contrasena": "clave_segura_c3"})
    token_c = client.post(
        "/sesiones", json={"correo": email_c, "contrasena": "clave_segura_c3"}
    ).json()["access_token"]
    headers_c = {"Authorization": f"Bearer {token_c}"}

    cuerpo_malicioso = {
        "comercio": "Farmacia Central",
        "fecha": "2026-10-15",
        "monto": 45000.0,
        "id_categoria": 1,
        "numero_tarjeta": "4532-1111-2222-3333",
        "cvv": "123",
        "direccion": "Calle 100 # 15-20",
    }
    resp = client.post("/gastos", json=cuerpo_malicioso, headers=headers_c)
    assert resp.status_code == 400
    assert "Campo no permitido" in resp.json()["detail"]
