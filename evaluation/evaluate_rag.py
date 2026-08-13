"""
Deterministic evaluation for the AI Sales & Support Assistant.

This module executes predefined RAG test cases and evaluates:
- knowledge-base routing
- expected answer content
- retrieved sources
- source citations

Run from the project root with:

    python -m evaluation.evaluate_rag
"""

import re

from backend.app.services.rag_service import ask_rag
from backend.app.services.graph_service import get_route
from evaluation.test_cases import TEST_CASES

from evaluation.judge_service import evaluate_with_llm

def contains_expected_terms(answer: str, expected_terms: list[str]) -> tuple[bool, list[str]]:
    """
    Check whether all expected terms are present in the generated answer.

    Args:
        answer: Generated assistant answer.
        expected_terms: Terms expected to appear in the answer.

    Returns:
        Tuple containing:
        - whether all terms were found
        - list of missing terms
    """

    answer_lower = answer.lower()

    missing_terms = [
        term 
        for term in expected_terms
        if term.lower() not in answer_lower
    ]

    return len(missing_terms) == 0, missing_terms

def contains_source_citation(answer: str) -> bool:
    """
    Check whether the answer contains a source citation.

    Expected citation format:
        [Source 1]
        [Source 2]
        ...

    Args:
        answer: Generated assistant answer.

    Returns:
        True when at least one source citation exists.
    """

    return bool(
        re.search(r"\[Source\s+\d+\]", answer, re.IGNORECASE)
    )


def evaluate_test_case(test_case: dict) -> dict:
    """
    Execute and evaluate a single RAG test case.

    Args:
        test_case: Test case configuration.

    Returns:
        Dictionary containing evaluation results.
    """

    question = test_case["question"]
    history = test_case.get("history", [])
    expected_route = test_case["expected_route"]
    expected_terms = test_case.get("expected_terms", [])
    expect_citation = test_case.get("expect_citation", False)

    # Use the same LangGraph routing used by the FastAPI endpoint
    selected_route = get_route(question)

    # Generic follow-up questions may need the previous route from history
    if selected_route == "faqs" and history:
        selected_route = None

    # Execute the existing RAG pipeline
    result = ask_rag(
        question=question,
        history=history,
        forced_route=selected_route,
    )

    answer = result["answer"]
    actual_route = result["route"]
    sources = result["sources"]

    context = result["context"]

    judge_result = evaluate_with_llm(
        question=question,
        context=context,
        answer=answer
    )

    # Deterministic checks
    route_passed = actual_route == expected_route

    content_passed, missing_terms = contains_expected_terms(
        answer,
        expected_terms,
    )

    sources_passed = len(sources) > 0

    citation_found = contains_source_citation(answer)

    # A citation is required only when the test case expects one
    citation_passed = (
        citation_found
        if expect_citation
        else True
    )

    overall_passed = all(
        [
            route_passed,
            content_passed,
            sources_passed,
            citation_passed,
        ]
    )

    return {
        "name": test_case["name"],
        "question": question,
        "answer": answer,
        "expected_route": expected_route,
        "actual_route": actual_route,
        "route_passed": route_passed,
        "content_passed": content_passed,
        "missing_terms": missing_terms,
        "sources_count": len(sources),
        "sources_passed": sources_passed,
        "expect_citation": expect_citation,
        "citation_found": citation_found,
        "citation_passed": citation_passed,
        "overall_passed": overall_passed,
        "judge": judge_result,
    }


def print_test_result(result: dict) -> None:
    """
    Print the result of a single evaluation test.

    Args:
        result: Evaluation result dictionary.
    """

    status = "PASS" if result["overall_passed"] else "FAIL"

    print("\n" + "=" * 70)
    print(f"TEST: {result['name']}")
    print("=" * 70)

    print(f"\nQuestion:\n{result['question']}")

    print("\nRoute:")
    print(f"  Expected: {result['expected_route']}")
    print(f"  Actual:   {result['actual_route']}")
    print(
        f"  Result:   "
        f"{'PASS' if result['route_passed'] else 'FAIL'}"
    )

    print("\nExpected content:")
    if result["content_passed"]:
        print("  PASS - All expected terms were found.")
    else:
        print("  FAIL")
        print(
            "  Missing terms: "
            + ", ".join(result["missing_terms"])
        )

    print("\nSources:")
    print(f"  Retrieved: {result['sources_count']}")
    print(
        f"  Result:    "
        f"{'PASS' if result['sources_passed'] else 'FAIL'}"
    )

    print("\nCitation:")
    print(f"  Required: {result['expect_citation']}")
    print(f"  Found:    {result['citation_found']}")
    print(
        f"  Result:   "
        f"{'PASS' if result['citation_passed'] else 'FAIL'}"
    )

    print("\nGenerated answer:")
    print(result["answer"])

    judge = result["judge"]

    print("\nLLM-as-a-Judge:")
    print(f"  Relevance:    {judge.get('relevance', 0)}/5")
    print(f"  Groundedness: {judge.get('groundedness', 0)}/5")
    print(f"  Completeness: {judge.get('completeness', 0)}/5")
    print(f"  Reason:       {judge.get('reason', '')}")

    print(f"\nFINAL RESULT: {status}")


def print_summary(results: list[dict]) -> None:
    """
    Print aggregate deterministic evaluation metrics.

    Args:
        results: Results from all executed test cases.
    """

    total = len(results)

    passed = sum(
        result["overall_passed"]
        for result in results
    )

    route_passed = sum(
        result["route_passed"]
        for result in results
    )

    content_passed = sum(
        result["content_passed"]
        for result in results
    )

    sources_passed = sum(
        result["sources_passed"]
        for result in results
    )

    citation_tests = [
        result
        for result in results
        if result["expect_citation"]
    ]

    citation_passed = sum(
        result["citation_passed"]
        for result in citation_tests
    )

    avg_relevance = sum(
        result["judge"].get("relevance", 0)
        for result in results
    ) / total

    avg_groundedness = sum(
        result["judge"].get("groundedness", 0)
        for result in results
    ) / total

    avg_completeness = sum(
        result["judge"].get("completeness", 0)
        for result in results
    ) / total    

    print("\n\n" + "=" * 70)
    print("RAG EVALUATION SUMMARY")
    print("=" * 70)

    print(f"\nTests passed:       {passed}/{total}")
    print(
        f"Route accuracy:     "
        f"{route_passed / total * 100:.1f}%"
    )
    print(
        f"Content accuracy:   "
        f"{content_passed / total * 100:.1f}%"
    )
    print(
        f"Source retrieval:   "
        f"{sources_passed / total * 100:.1f}%"
    )

    print("\nLLM-as-a-Judge:")
    print(f"Average relevance:    {avg_relevance:.2f}/5")
    print(f"Average groundedness: {avg_groundedness:.2f}/5")
    print(f"Average completeness: {avg_completeness:.2f}/5")

    if citation_tests:
        print(
            f"Citation accuracy:  "
            f"{citation_passed / len(citation_tests) * 100:.1f}%"
        )


def main() -> None:
    """
    Run all deterministic RAG evaluation test cases.
    """

    print("=" * 70)
    print("AI SALES & SUPPORT ASSISTANT - RAG EVALUATION")
    print("=" * 70)

    results = []

    for test_case in TEST_CASES:
        result = evaluate_test_case(test_case)
        results.append(result)

        print_test_result(result)

    print_summary(results)


if __name__ == "__main__":
    main()