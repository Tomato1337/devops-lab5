from fastapi.testclient import TestClient

from src.main import app

client = TestClient(app)

# Существующие пользователи
users = [
    {
        "id": 1,
        "name": "Ivan Ivanov",
        "email": "i.i.ivanov@mail.com",
    },
    {
        "id": 2,
        "name": "Petr Petrov",
        "email": "p.p.petrov@mail.com",
    },
]


def test_get_existed_user():
    """Получение существующего пользователя"""
    response = client.get("/api/v1/user", params={"email": users[0]["email"]})
    assert response.status_code == 200
    assert response.json() == users[0]


def test_get_unexisted_user():
    """Получение несуществующего пользователя"""
    response = client.get("/api/v1/user", params={"email": "nonexistent@example.com"})
    assert response.status_code == 404
    assert response.json() == {"detail": "User not found"}


def test_create_user_with_valid_email():
    """Создание пользователя с уникальной почтой"""
    new_user = {"name": "Sergey Sidorov", "email": "s.sidorov@mail.com"}
    response = client.post("/api/v1/user", json=new_user)
    assert response.status_code == 201
    # Проверка, что возвращается ID нового пользователя (должен быть 3, так как в БД уже есть 2 пользователя)
    assert response.json() == 3

    # Дополнительно проверяем, что пользователь действительно создан
    get_response = client.get("/api/v1/user", params={"email": new_user["email"]})
    assert get_response.status_code == 200
    assert get_response.json()["name"] == new_user["name"]
    assert get_response.json()["email"] == new_user["email"]


def test_create_user_with_invalid_email():
    """Создание пользователя с почтой, которую использует другой пользователь"""
    existing_user = {
        "name": "Duplicate User",
        "email": users[0]["email"],  # Используем email существующего пользователя
    }
    response = client.post("/api/v1/user", json=existing_user)
    assert response.status_code == 409
    assert response.json() == {"detail": "User with this email already exists"}


def test_delete_user():
    """Удаление пользователя"""
    # Сначала создаем пользователя для удаления
    user_to_delete = {"name": "To Delete", "email": "to.delete@mail.com"}
    create_response = client.post("/api/v1/user", json=user_to_delete)
    assert create_response.status_code == 201

    # Удаляем созданного пользователя
    delete_response = client.delete(
        "/api/v1/user", params={"email": user_to_delete["email"]}
    )
    assert delete_response.status_code == 204

    # Проверяем, что пользователь действительно удален
    get_response = client.get("/api/v1/user", params={"email": user_to_delete["email"]})
    assert get_response.status_code == 404
