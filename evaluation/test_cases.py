"""
Evaluation test cases for the AI Sales & Support Assistant.

Each test case defines:
- the user question
- the expected knowledge-base route
- important content expected in the answer
- whether a source citation is expected
"""

TEST_CASES = [
    {
        "name": "Gaming laptop within 900 euro budget",
        "question": "Θέλω laptop για gaming μέχρι 900€",
        "expected_route": "products",
        "expected_terms": [
            "GamePro 15",
            "899€",
        ],
        "expect_citation": False,
    },
    {
        "name": "Gaming laptop recommendations",
        "question": "Θέλω laptop για gaming μέχρι 1900€",
        "expected_route": "products",
        "expected_terms": [
            "GamePro 15",
            "NitroPlay 15",
            "Titan Gaming G17",
        ],
        "expect_citation": False,
    },
    {
        "name": "Product comparison",
        "question": "Σύγκρινε GamePro 15 με NitroPlay 15",
        "expected_route": "products",
        "expected_terms": [
            "GamePro 15",
            "NitroPlay 15",
            "899€",
            "1099€",
        ],
        "expect_citation": False,
    },
    {
        "name": "Design monitor recommendation",
        "question": "Έχετε monitor για design;",
        "expected_route": "products",
        "expected_terms": [
            "ProColor 32",
        ],
        "expect_citation": False,
    },
    {
        "name": "Laptop warranty",
        "question": "Πόσα χρόνια εγγύηση έχουν τα laptops;",
        "expected_route": "policies",
        "expected_terms": [
            "2",
        ],
        "expect_citation": True,
    },
    {
        "name": "Installment payment policy",
        "question": "Σε πόσες δόσεις μπορώ να πληρώσω;",
        "expected_route": "policies",
        "expected_terms": [
            "12",
            "300",
        ],
        "expect_citation": True,
    },
    {
        "name": "Technical support",
        "question": "Υπάρχει τεχνική υποστήριξη;",
        "expected_route": "faqs",
        "expected_terms": [
            "τεχνική υποστήριξη",
        ],
        "expect_citation": True,
    },
    {
        "name": "Box Now shipping",
        "question": "Υποστηρίζετε Box Now;",
        "expected_route": "policies",
        "expected_terms": [
            "Box Now",
        ],
        "expect_citation": True,
    }, 
    {
        "name": "Out of scope question",
        "question": "Ποιος κέρδισε το Champions League;",
        "expected_route": "faqs",
        "expected_any_terms": [
        "προϊόντα",
        ],
        "expect_citation": False,
    },

    {
        "name": "Follow-up previous recommendation",
        "question": "Τι μου πρότεινες τελικά;",
        "history": [
            {
                "role": "user",
                "content": "Θέλω laptop για gaming μέχρι 900€",
            },
            {
                "role": "assistant",
                "content": "Σας πρότεινα το GamePro 15 στα 899€.",
            },
        ],
        "expected_route": "products",
        "expected_terms": [
            "GamePro 15",
            "899€",
        ],
        "expect_citation": False,
    },
    {
        "name": "Follow-up changed budget",
        "question": "Και μέχρι 1200€;",
        "history": [
            {
                "role": "user",
                "content": "Θέλω laptop για gaming μέχρι 1900€",
            },
            {
                "role": "assistant",
                "content": (
                    "Σας πρότεινα τα GamePro 15, NitroPlay 15 "
                    "και Titan Gaming G17."
                ),
            },
        ],
        "expected_route": "products",
        "expected_terms": [
            "GamePro 15",
            "NitroPlay 15",
        ],
        "expect_citation": False,
    },
]