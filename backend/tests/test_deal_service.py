from app.services import deal_service


def test_generate_public_id_is_bounded_and_year_prefixed():
    public_id = deal_service._generate_public_id()
    assert public_id.startswith("LD-")
    assert len(public_id) <= 20


def test_same_status_transition_is_allowed():
    deal_service._assert_transition("quote_added", "quote_added")
