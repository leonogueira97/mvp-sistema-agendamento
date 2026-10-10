def test_home_page_loads(tmp_path):
    from app.web import create_app
    db_path = tmp_path / "web-test.db"
    app = create_app(f"sqlite:///{db_path}", testing=True)
    client = app.test_client()
    response = client.get("/")
    assert response.status_code == 200
    assert b"Sistema de Agendamento" in response.data


def test_create_client_from_form(tmp_path):
    from app.web import create_app
    db_path = tmp_path / "web-test.db"
    app = create_app(f"sqlite:///{db_path}", testing=True)
    client = app.test_client()
    response = client.post("/clients", data={"name": "Joao", "phone": "11912345678"})
    assert response.status_code == 200
    assert b"Joao" in response.data
