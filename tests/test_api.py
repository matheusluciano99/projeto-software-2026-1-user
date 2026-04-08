def test_get_user_404(client):

    # Teste de Recuperação
    get_response = client.get(f"/users/1")
    assert get_response.status_code == 404

def test_create_and_get_user_and_delete_user(client):
    # Criar usuário
    create_response = client.post("/users", json={
        "name": "Matheus",
        "email": "matheus@test.com"
    })
    assert create_response.status_code == 201
    data = create_response.get_json()
    assert data["name"] == "Matheus"
    assert data["email"] == "matheus@test.com"
    user_id = data["id"]

    # Buscar usuário por ID
    get_response = client.get(f"/users/{user_id}")
    assert get_response.status_code == 200
    get_data = get_response.get_json()
    assert get_data["id"] == user_id
    assert get_data["name"] == "Matheus"
    assert get_data["email"] == "matheus@test.com"

    # Deletar usuário
    delete_response = client.delete(f"/users/{user_id}")
    assert delete_response.status_code == 204

    # Verificar que foi deletado
    get_after_delete = client.get(f"/users/{user_id}")
    assert get_after_delete.status_code == 404

def test_create_and_delete_user(client):
    # Criar usuário
    create_response = client.post("/users", json={
        "name": "Lucas",
        "email": "lucas@test.com"
    })
    assert create_response.status_code == 201
    user_id = create_response.get_json()["id"]

    # Deletar usuário
    delete_response = client.delete(f"/users/{user_id}")
    assert delete_response.status_code == 204

    # Confirmar que não existe mais
    get_response = client.get(f"/users/{user_id}")
    assert get_response.status_code == 404

def test_create_two_users_and_list_and_delete_both_users(client):
    # Criar dois usuários
    resp1 = client.post("/users", json={
        "name": "User1",
        "email": "user1@test.com"
    })
    assert resp1.status_code == 201
    id1 = resp1.get_json()["id"]

    resp2 = client.post("/users", json={
        "name": "User2",
        "email": "user2@test.com"
    })
    assert resp2.status_code == 201
    id2 = resp2.get_json()["id"]

    # Listar usuários
    list_response = client.get("/users")
    assert list_response.status_code == 200
    users = list_response.get_json()
    user_ids = [u["id"] for u in users]
    assert id1 in user_ids
    assert id2 in user_ids

    # Deletar ambos
    assert client.delete(f"/users/{id1}").status_code == 204
    assert client.delete(f"/users/{id2}").status_code == 204

def test_get_user_by_email(client):
    # Criar usuário
    create_response = client.post("/users", json={
        "name": "Maria",
        "email": "maria@test.com"
    })
    assert create_response.status_code == 201
    user_id = create_response.get_json()["id"]

    # Buscar por email
    get_response = client.get("/users/maria@test.com/email")
    assert get_response.status_code == 200
    data = get_response.get_json()
    assert data["id"] == user_id
    assert data["name"] == "Maria"
    assert data["email"] == "maria@test.com"

    # Limpar
    client.delete(f"/users/{user_id}")

def test_get_user_by_email_404(client):
    get_response = client.get("/users/naoexiste@test.com/email")
    assert get_response.status_code == 404

def test_delete_user_404(client):
    import uuid
    fake_id = str(uuid.uuid4())
    delete_response = client.delete(f"/users/{fake_id}")
    assert delete_response.status_code == 404

def test_list_users_empty(client):
    list_response = client.get("/users")
    assert list_response.status_code == 200
    assert isinstance(list_response.get_json(), list)
