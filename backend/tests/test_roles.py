import pytest
from app.core.roles import UserRole


def test_all_roles_defined():
    assert {r.value for r in UserRole} == {
        "partner", "client", "admin", "ops", "risk", "financier", "cfo"
    }


def test_role_is_string_enum():
    assert UserRole.admin == "admin"
    assert isinstance(UserRole.partner, str)


def test_invalid_role_raises():
    with pytest.raises(ValueError):
        UserRole("superadmin")
