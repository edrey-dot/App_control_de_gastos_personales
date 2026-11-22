from uuid import uuid4

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_registro_login_por_celular_y_perfil_con_foto():
    correo = f"perfil-{uuid4().hex}@correo.com"
    telefono = "3001112233"
    contrasena = "clave-segura-123"

    registro = client.post(
        "/usuarios",
        json={
            "nombre_usuario": "Andrea",
            "telefono": telefono,
            "correo": correo,
            "contrasena": contrasena,
        },
    )
    assert registro.status_code == 201

    login = client.post(
        "/sesiones",
        json={"identificador": "+57 300 111 2233", "contrasena": contrasena},
    )
    assert login.status_code == 200
    headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

    perfil = client.get("/usuarios/me", headers=headers)
    assert perfil.status_code == 200
    assert perfil.json()["nombre_usuario"] == "Andrea"
    assert perfil.json()["telefono"] == telefono
    assert perfil.json()["tiene_foto"] is False

    actualizar = client.put(
        "/usuarios/me",
        headers=headers,
        json={"nombre_usuario": "Andrea G"},
    )
    assert actualizar.status_code == 200
    assert actualizar.json()["nombre_usuario"] == "Andrea G"
    assert actualizar.json()["telefono"] == telefono

    png = b"\x89PNG\r\n\x1a\ncontenido-de-prueba"
    subir_foto = client.put(
        "/usuarios/me/foto",
        headers=headers,
        files={"foto": ("perfil.png", png, "image/png")},
    )
    assert subir_foto.status_code == 200
    assert subir_foto.json()["tiene_foto"] is True

    obtener_foto = client.get("/usuarios/me/foto", headers=headers)
    assert obtener_foto.status_code == 200
    assert obtener_foto.headers["content-type"] == "image/png"
    assert obtener_foto.content == png


def test_no_permite_registrar_el_mismo_celular_dos_veces():
    telefono = "3012223344"
    primer_registro = client.post(
        "/usuarios",
        json={
            "nombre_usuario": "Usuario uno",
            "telefono": telefono,
            "correo": f"uno-{uuid4().hex}@correo.com",
            "contrasena": "clave-segura-123",
        },
    )
    segundo_registro = client.post(
        "/usuarios",
        json={
            "nombre_usuario": "Usuario dos",
            "telefono": telefono,
            "correo": f"dos-{uuid4().hex}@correo.com",
            "contrasena": "clave-segura-123",
        },
    )

    assert primer_registro.status_code == 201
    assert segundo_registro.status_code == 409
    assert segundo_registro.json()["detail"] == "El celular ya está registrado"


def test_usuario_existente_puede_agregar_celular_y_entrar_con_el():
    correo = f"existente-{uuid4().hex}@correo.com"
    contrasena = "clave-segura-123"
    client.post(
        "/usuarios",
        json={"correo": correo, "contrasena": contrasena},
    )
    login = client.post(
        "/sesiones",
        json={"correo": correo, "contrasena": contrasena},
    )
    headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

    actualizar = client.put(
        "/usuarios/me",
        headers=headers,
        json={"nombre_usuario": "Usuario existente", "telefono": "3023334455"},
    )
    login_celular = client.post(
        "/sesiones",
        json={"identificador": "3023334455", "contrasena": contrasena},
    )

    assert actualizar.status_code == 200
    assert actualizar.json()["telefono"] == "3023334455"
    assert login_celular.status_code == 200
