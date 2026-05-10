"""Smoke tests for Phase 2 ORM models — structure only, no DB required."""

import uuid

from sqlalchemy import inspect

from app.models import Company, Deal, Organization, Profile, UserRole


def column_names(model) -> set[str]:
    return {c.key for c in inspect(model).mapper.column_attrs}


class TestOrganization:
    def test_import(self):
        assert Organization is not None

    def test_tablename(self):
        assert Organization.__tablename__ == "organizations"

    def test_columns(self):
        cols = column_names(Organization)
        assert {"id", "type", "legal_name", "trade_name", "siren", "siret",
                "address", "status", "created_at"} <= cols

    def test_default_id_type(self):
        org = Organization(type="partner", legal_name="Acme")
        # default callable produces a UUID
        assert org.id is None  # not yet set via default (constructor only)


class TestProfile:
    def test_import(self):
        assert Profile is not None

    def test_tablename(self):
        assert Profile.__tablename__ == "profiles"

    def test_columns(self):
        cols = column_names(Profile)
        assert {"id", "full_name", "phone", "avatar_url", "status",
                "created_at", "updated_at"} <= cols


class TestUserRole:
    def test_import(self):
        assert UserRole is not None

    def test_tablename(self):
        assert UserRole.__tablename__ == "user_roles"

    def test_columns(self):
        cols = column_names(UserRole)
        assert {"user_id", "role_code", "organization_id"} <= cols


class TestCompany:
    def test_import(self):
        assert Company is not None

    def test_tablename(self):
        assert Company.__tablename__ == "companies"

    def test_columns(self):
        cols = column_names(Company)
        assert {"id", "siren", "siret", "legal_name", "trade_name", "address",
                "activity_code", "creation_date", "legal_status", "is_active",
                "enrichment_source", "enrichment_payload", "created_at"} <= cols


class TestDeal:
    def test_import(self):
        assert Deal is not None

    def test_tablename(self):
        assert Deal.__tablename__ == "deals"

    def test_columns(self):
        cols = column_names(Deal)
        assert {"id", "public_id", "company_id", "partner_org_id",
                "submitted_by_user_id", "status", "amount_cents", "currency",
                "duration_months", "risk_score", "risk_band",
                "monthly_payment_cents", "created_at", "updated_at"} <= cols
