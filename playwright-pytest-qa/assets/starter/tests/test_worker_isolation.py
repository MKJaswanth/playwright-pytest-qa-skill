def test_resource_names_include_worker_id(resource_name, worker_id, api, track):
    assert track.worker_id == worker_id
    name = resource_name("role")
    assert name.startswith(f"role-{worker_id}-")
    response = api.post("/api/roles", json={"name": name})
    assert response.status_code == 201
    track("role", response.json()["id"])
    assert response.json()["name"] == name
