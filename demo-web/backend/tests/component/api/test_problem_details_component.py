from app.api.oran import _problem


def test_problem_details_component_shape() -> None:
    payload = _problem(
        status_code=404,
        title="Policy Not Found",
        detail="Policy missing",
        instance="/a1/policytypes/default/policies/missing",
    )

    assert payload["type"] == "about:blank"
    assert payload["status"] == 404
    assert payload["title"] == "Policy Not Found"
    assert payload["instance"].endswith("/missing")
