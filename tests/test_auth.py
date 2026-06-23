from tests.conftest import register_user, login_user


def test_register_user(client, user_data):
    response = register_user(client, user_data)

    assert response.status_code == 200

    data = response.json()

    assert data["name"] == user_data["name"]
    assert data["email"] == user_data["email"]
    assert "id" in data
    assert "password" not in data
    assert "hashed_password" not in data


def test_register_duplicate_email_fails(client, user_data):
    register_user(client, user_data)

    response = register_user(client, user_data)

    assert response.status_code == 400
    assert response.json()["detail"] == "Email already registered"


def test_login_user(client, user_data):
    register_user(client, user_data)

    response = login_user(
        client,
        user_data["email"],
        user_data["password"]
    )

    assert response.status_code == 200

    data = response.json()

    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password_fails(client, user_data):
    register_user(client, user_data)

    response = login_user(
        client,
        user_data["email"],
        "wrongpassword"
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid email or password"


def test_get_current_user(client, auth_headers, user_data):
    response = client.get(
        "/auth/me",
        headers=auth_headers
    )

    assert response.status_code == 200

    data = response.json()

    assert data["name"] == user_data["name"]
    assert data["email"] == user_data["email"]


def test_get_current_user_without_token_fails(client):
    response = client.get("/auth/me")

    assert response.status_code == 401


def test_refresh_token(client, user_data):
    register_user(client, user_data)

    login_response = login_user(
        client,
        user_data["email"],
        user_data["password"]
    )

    refresh_token = login_response.json()["refresh_token"]

    response = client.post(
        "/auth/refresh",
        json={
            "refresh_token": refresh_token
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


def test_old_refresh_token_reuse_fails(client, user_data):
    register_user(client, user_data)

    login_response = login_user(
        client,
        user_data["email"],
        user_data["password"]
    )

    old_refresh_token = login_response.json()["refresh_token"]

    first_refresh = client.post(
        "/auth/refresh",
        json={
            "refresh_token": old_refresh_token
        }
    )

    assert first_refresh.status_code == 200

    second_refresh = client.post(
        "/auth/refresh",
        json={
            "refresh_token": old_refresh_token
        }
    )

    assert second_refresh.status_code == 401
    assert second_refresh.json()["detail"] == "Refresh token has been revoked"


def test_logout_revokes_refresh_token(client, user_data):
    register_user(client, user_data)

    login_response = login_user(
        client,
        user_data["email"],
        user_data["password"]
    )

    refresh_token = login_response.json()["refresh_token"]

    logout_response = client.post(
        "/auth/logout",
        json={
            "refresh_token": refresh_token
        }
    )

    assert logout_response.status_code == 200

    refresh_response = client.post(
        "/auth/refresh",
        json={
            "refresh_token": refresh_token
        }
    )

    assert refresh_response.status_code == 401

def test_forgot_password_generates_reset_token(client, user_data):
    register_user(client, user_data)

    response = client.post(
        "/auth/forgot-password",
        json={
            "email": user_data["email"]
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["message"] == "Password reset token generated successfully"
    assert "reset_token" in data


def test_reset_password_success(client, user_data):
    register_user(client, user_data)

    forgot_response = client.post(
        "/auth/forgot-password",
        json={
            "email": user_data["email"]
        }
    )

    reset_token = forgot_response.json()["reset_token"]

    reset_response = client.post(
        "/auth/reset-password",
        json={
            "reset_token": reset_token,
            "new_password": "newpassword123"
        }
    )

    assert reset_response.status_code == 200

    old_login = login_user(
        client,
        user_data["email"],
        user_data["password"]
    )

    assert old_login.status_code == 401

    new_login = login_user(
        client,
        user_data["email"],
        "newpassword123"
    )

    assert new_login.status_code == 200


def test_reset_token_reuse_fails(client, user_data):
    register_user(client, user_data)

    forgot_response = client.post(
        "/auth/forgot-password",
        json={
            "email": user_data["email"]
        }
    )

    reset_token = forgot_response.json()["reset_token"]

    first_reset = client.post(
        "/auth/reset-password",
        json={
            "reset_token": reset_token,
            "new_password": "newpassword123"
        }
    )

    assert first_reset.status_code == 200

    second_reset = client.post(
        "/auth/reset-password",
        json={
            "reset_token": reset_token,
            "new_password": "anotherpassword123"
        }
    )

    assert second_reset.status_code == 401
    assert second_reset.json()["detail"] == "Reset token has already been used"