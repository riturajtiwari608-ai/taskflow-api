def test_create_workspace(client, auth_headers):
    response = client.post(
        "/workspaces/",
        json={
            "name": "TaskFlow Team",
            "description": "Main workspace"
        },
        headers=auth_headers
    )

    assert response.status_code == 200

    data = response.json()

    assert data["name"] == "TaskFlow Team"
    assert data["description"] == "Main workspace"
    assert "id" in data


def test_get_my_workspaces(client, auth_headers):
    client.post(
        "/workspaces/",
        json={
            "name": "TaskFlow Team",
            "description": "Main workspace"
        },
        headers=auth_headers
    )

    response = client.get(
        "/workspaces/",
        headers=auth_headers
    )

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["name"] == "TaskFlow Team"


def test_update_workspace(client, auth_headers):
    create_response = client.post(
        "/workspaces/",
        json={
            "name": "TaskFlow Team",
            "description": "Main workspace"
        },
        headers=auth_headers
    )

    workspace_id = create_response.json()["id"]

    response = client.patch(
        f"/workspaces/{workspace_id}",
        json={
            "name": "Updated Workspace"
        },
        headers=auth_headers
    )

    assert response.status_code == 200
    assert response.json()["name"] == "Updated Workspace"


def test_delete_workspace(client, auth_headers):
    create_response = client.post(
        "/workspaces/",
        json={
            "name": "TaskFlow Team",
            "description": "Main workspace"
        },
        headers=auth_headers
    )

    workspace_id = create_response.json()["id"]

    response = client.delete(
        f"/workspaces/{workspace_id}",
        headers=auth_headers
    )

    assert response.status_code == 200
    assert response.json()["message"] == "Workspace deleted successfully"


def test_add_workspace_member(client, auth_headers, second_user_data):
    client.post("/auth/register", json=second_user_data)

    workspace_response = client.post(
        "/workspaces/",
        json={
            "name": "TaskFlow Team",
            "description": "Main workspace"
        },
        headers=auth_headers
    )

    workspace_id = workspace_response.json()["id"]

    response = client.post(
        f"/workspaces/{workspace_id}/members",
        json={
            "email": second_user_data["email"],
            "role": "manager"
        },
        headers=auth_headers
    )

    assert response.status_code == 200

    data = response.json()

    assert data["workspace_id"] == workspace_id
    assert data["role"] == "manager"


def test_get_workspace_members(client, auth_headers, second_user_data):
    client.post("/auth/register", json=second_user_data)

    workspace_response = client.post(
        "/workspaces/",
        json={
            "name": "TaskFlow Team",
            "description": "Main workspace"
        },
        headers=auth_headers
    )

    workspace_id = workspace_response.json()["id"]

    client.post(
        f"/workspaces/{workspace_id}/members",
        json={
            "email": second_user_data["email"],
            "role": "manager"
        },
        headers=auth_headers
    )

    response = client.get(
        f"/workspaces/{workspace_id}/members",
        headers=auth_headers
    )

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)
    assert len(data) == 2