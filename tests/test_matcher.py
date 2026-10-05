from src.schema.matcher import SchemaMatcher


def test_semantic_mapping():
    assert SchemaMatcher.semantic_name("full_name") == "name"
    assert SchemaMatcher.semantic_name("email_address") == "email"
    assert SchemaMatcher.semantic_name("customer_id") == "identifier"


def test_table_similarity():
    a = ["customer_id", "name", "email"]
    b = ["id", "full_name", "email_address"]
    assert SchemaMatcher.table_similarity(a, b) == 1.0
