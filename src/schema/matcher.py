import re
from difflib import SequenceMatcher


class SchemaMatcher:
    SYNONYMS = {
        "id": "identifier",
        "customer_id": "identifier",
        "client_id": "identifier",
        "user_id": "identifier",
        "name": "name",
        "full_name": "name",
        "customer_name": "name",
        "email": "email",
        "email_address": "email",
        "phone": "phone",
        "phone_number": "phone",
        "amount": "amount",
        "total": "amount",
        "price": "amount",
        "date": "date",
        "created_at": "date",
        "order_date": "date"
    }

    @staticmethod
    def normalize(name):
        name = str(name).lower().strip()
        name = re.sub(r"[^a-z0-9]+", "_", name)
        return name.strip("_")

    @classmethod
    def semantic_name(cls, name):
        normalized = cls.normalize(name)
        return cls.SYNONYMS.get(normalized, normalized)

    @classmethod
    def similarity(cls, a, b):
        return SequenceMatcher(
            None,
            cls.semantic_name(a),
            cls.semantic_name(b),
        ).ratio()

    @classmethod
    def column_mapping(cls, columns):
        return {column: cls.semantic_name(column) for column in columns}

    @classmethod
    def table_similarity(cls, columns_a, columns_b):
        a = {cls.semantic_name(c) for c in columns_a}
        b = {cls.semantic_name(c) for c in columns_b}

        if not a or not b:
            return 0.0

        return len(a & b) / len(a | b)
