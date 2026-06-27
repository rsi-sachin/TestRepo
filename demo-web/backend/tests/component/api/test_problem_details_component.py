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


def test_problem_details_component_shape_for_policy_type_not_found() -> None:
    """_problem() must produce a correctly shaped ProblemDetails for a policy-type 404 per §5.2.3.3."""
    payload = _problem(
        status_code=404,
        title="Policy Type Not Found",
        detail="Policy type not found: nonexistent-type",
        instance="/a1/policytypes/nonexistent-type",
    )

    assert payload["type"] == "about:blank"
    assert payload["status"] == 404
    assert payload["title"] == "Policy Type Not Found"
    assert payload["instance"] == "/a1/policytypes/nonexistent-type"
    assert "nonexistent-type" in payload["detail"]
