def test_member_cannot_create_project(
    client,
    auth_headers,
    second_user_data,
    third_user_data
):
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
            "role": "member"
        },
        headers=auth_headers
    )

    login_response = client.post(
        "/auth/login",
        json={
            "email": second_user_data["email"],
            "password": second_user_data["password"]
        }
    )

    member_token = login_response.json()["access_token"]

    member_headers = {
        "Authorization": f"Bearer {member_token}"
    }

    response = client.post(
        "/projects/",
        json={
            "name": "Member Project",
            "description": "Should fail",
            "workspace_id": workspace_id
        },
        headers=member_headers
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "You do not have permission to perform this action"


def test_manager_can_create_project(
    client,
    auth_headers,
    second_user_data
):
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

    login_response = client.post(
        "/auth/login",
        json={
            "email": second_user_data["email"],
            "password": second_user_data["password"]
        }
    )

    manager_token = login_response.json()["access_token"]

    manager_headers = {
        "Authorization": f"Bearer {manager_token}"
    }

    response = client.post(
        "/projects/",
        json={
            "name": "Manager Project",
            "description": "Should pass",
            "workspace_id": workspace_id
        },
        headers=manager_headers
    )

    assert response.status_code == 200
    assert response.json()["name"] == "Manager Project"


def test_member_cannot_delete_task(
    client,
    auth_headers,
    second_user_data
):
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
            "role": "member"
        },
        headers=auth_headers
    )

    project_response = client.post(
        "/projects/",
        json={
            "name": "Backend API",
            "description": "FastAPI backend project",
            "workspace_id": workspace_id
        },
        headers=auth_headers
    )

    project_id = project_response.json()["id"]

    client.post(
        f"/projects/{project_id}/members",
        json={
            "email": second_user_data["email"]
        },
        headers=auth_headers
    )

    task_response = client.post(
        "/tasks/",
        json={
            "title": "Create login API",
            "description": "Build JWT authentication",
            "priority": "high",
            "status": "todo",
            "due_date": "2026-06-30",
            "project_id": project_id,
            "assignee_id": 2
        },
        headers=auth_headers
    )

    task_id = task_response.json()["id"]

    login_response = client.post(
        "/auth/login",
        json={
            "email": second_user_data["email"],
            "password": second_user_data["password"]
        }
    )

    member_token = login_response.json()["access_token"]

    member_headers = {
        "Authorization": f"Bearer {member_token}"
    }

    response = client.delete(
        f"/tasks/{task_id}",
        headers=member_headers
    )

    assert response.status_code == 403