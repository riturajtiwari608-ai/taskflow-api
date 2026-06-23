def setup_task(client, auth_headers):
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

    task_response = client.post(
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

    task_id = task_response.json()["id"]

    return workspace_id, project_id, task_id


def create_comment(client, auth_headers, task_id):
    response = client.post(
        f"/tasks/{task_id}/comments",
        json={
            "content": "I have started this task."
        },
        headers=auth_headers
    )

    return response


def test_create_comment(client, auth_headers):
    workspace_id, project_id, task_id = setup_task(client, auth_headers)

    response = create_comment(client, auth_headers, task_id)

    assert response.status_code == 200

    data = response.json()

    assert data["content"] == "I have started this task."
    assert data["task_id"] == task_id


def test_get_task_comments(client, auth_headers):
    workspace_id, project_id, task_id = setup_task(client, auth_headers)

    create_comment(client, auth_headers, task_id)

    response = client.get(
        f"/tasks/{task_id}/comments",
        headers=auth_headers
    )

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)
    assert len(data) == 1


def test_update_own_comment(client, auth_headers):
    workspace_id, project_id, task_id = setup_task(client, auth_headers)

    comment_response = create_comment(client, auth_headers, task_id)

    comment_id = comment_response.json()["id"]

    response = client.patch(
        f"/comments/{comment_id}",
        json={
            "content": "Updated comment"
        },
        headers=auth_headers
    )

    assert response.status_code == 200
    assert response.json()["content"] == "Updated comment"


def test_delete_own_comment(client, auth_headers):
    workspace_id, project_id, task_id = setup_task(client, auth_headers)

    comment_response = create_comment(client, auth_headers, task_id)

    comment_id = comment_response.json()["id"]

    response = client.delete(
        f"/comments/{comment_id}",
        headers=auth_headers
    )

    assert response.status_code == 200
    assert response.json()["message"] == "Comment deleted successfully"


def test_empty_comment_fails(client, auth_headers):
    workspace_id, project_id, task_id = setup_task(client, auth_headers)

    response = client.post(
        f"/tasks/{task_id}/comments",
        json={
            "content": ""
        },
        headers=auth_headers
    )

    assert response.status_code == 422