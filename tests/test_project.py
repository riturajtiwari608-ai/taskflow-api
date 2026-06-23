def create_workspace(client, auth_headers):
    response = client.post(
        "/workspaces/",
        json={
            "name": "TaskFlow Team",
            "description": "Main workspace"
        },
        headers=auth_headers
    )

    return response.json()["id"]


def create_project(client, auth_headers, workspace_id):
    response = client.post(
        "/projects/",
        json={
            "name": "Backend API",
            "description": "FastAPI backend project",
            "workspace_id": workspace_id
        },
        headers=auth_headers
    )

    return response


def test_create_project(client, auth_headers):
    workspace_id = create_workspace(client, auth_headers)

    response = create_project(client, auth_headers, workspace_id)

    assert response.status_code == 200

    data = response.json()

    assert data["name"] == "Backend API"
    assert data["workspace_id"] == workspace_id


def test_get_projects(client, auth_headers):
    workspace_id = create_workspace(client, auth_headers)

    create_project(client, auth_headers, workspace_id)

    response = client.get(
        "/projects/",
        headers=auth_headers
    )

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)
    assert len(data) == 1


def test_get_single_project(client, auth_headers):
    workspace_id = create_workspace(client, auth_headers)

    project_response = create_project(client, auth_headers, workspace_id)

    project_id = project_response.json()["id"]

    response = client.get(
        f"/projects/{project_id}",
        headers=auth_headers
    )

    assert response.status_code == 200
    assert response.json()["id"] == project_id


def test_update_project(client, auth_headers):
    workspace_id = create_workspace(client, auth_headers)

    project_response = create_project(client, auth_headers, workspace_id)

    project_id = project_response.json()["id"]

    response = client.patch(
        f"/projects/{project_id}",
        json={
            "name": "Updated Backend API"
        },
        headers=auth_headers
    )

    assert response.status_code == 200
    assert response.json()["name"] == "Updated Backend API"


def test_delete_project(client, auth_headers):
    workspace_id = create_workspace(client, auth_headers)

    project_response = create_project(client, auth_headers, workspace_id)

    project_id = project_response.json()["id"]

    response = client.delete(
        f"/projects/{project_id}",
        headers=auth_headers
    )

    assert response.status_code == 200
    assert response.json()["message"] == "Project deleted successfully"