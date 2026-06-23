def setup_project(client, auth_headers):
    workspace_response = client.post(
        "/workspaces/",
        json={
            "name": "TaskFlow Team",
            "description": "Main workspace"
        },
        headers=auth_headers
    )

    workspace_id = workspace_response.json()["id"]

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

    return workspace_id, project_id


def create_task(client, auth_headers, project_id):
    response = client.post(
        "/tasks/",
        json={
            "title": "Create login API",
            "description": "Build JWT authentication",
            "priority": "high",
            "status": "todo",
            "due_date": "2026-06-30",
            "project_id": project_id,
            "assignee_id": 1
        },
        headers=auth_headers
    )

    return response


def test_create_task(client, auth_headers):
    workspace_id, project_id = setup_project(client, auth_headers)

    response = create_task(client, auth_headers, project_id)

    assert response.status_code == 200

    data = response.json()

    assert data["title"] == "Create login API"
    assert data["priority"] == "high"
    assert data["status"] == "todo"
    assert data["project_id"] == project_id


def test_get_tasks(client, auth_headers):
    workspace_id, project_id = setup_project(client, auth_headers)

    create_task(client, auth_headers, project_id)

    response = client.get(
        "/tasks/",
        headers=auth_headers
    )

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)
    assert len(data) == 1


def test_get_single_task(client, auth_headers):
    workspace_id, project_id = setup_project(client, auth_headers)

    task_response = create_task(client, auth_headers, project_id)

    task_id = task_response.json()["id"]

    response = client.get(
        f"/tasks/{task_id}",
        headers=auth_headers
    )

    assert response.status_code == 200
    assert response.json()["id"] == task_id


def test_update_task(client, auth_headers):
    workspace_id, project_id = setup_project(client, auth_headers)

    task_response = create_task(client, auth_headers, project_id)

    task_id = task_response.json()["id"]

    response = client.patch(
        f"/tasks/{task_id}",
        json={
            "status": "in_progress"
        },
        headers=auth_headers
    )

    assert response.status_code == 200
    assert response.json()["status"] == "in_progress"


def test_delete_task(client, auth_headers):
    workspace_id, project_id = setup_project(client, auth_headers)

    task_response = create_task(client, auth_headers, project_id)

    task_id = task_response.json()["id"]

    response = client.delete(
        f"/tasks/{task_id}",
        headers=auth_headers
    )

    assert response.status_code == 200
    assert response.json()["message"] == "Task deleted successfully"


def test_filter_tasks_by_status(client, auth_headers):
    workspace_id, project_id = setup_project(client, auth_headers)

    create_task(client, auth_headers, project_id)

    response = client.get(
        "/tasks/?status=todo",
        headers=auth_headers
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["status"] == "todo"


def test_invalid_task_priority_fails(client, auth_headers):
    workspace_id, project_id = setup_project(client, auth_headers)

    response = client.post(
        "/tasks/",
        json={
            "title": "Create login API",
            "description": "Build JWT authentication",
            "priority": "super_high",
            "status": "todo",
            "due_date": "2026-06-30",
            "project_id": project_id,
            "assignee_id": 1
        },
        headers=auth_headers
    )

    assert response.status_code == 422