"""
Deterministic evaluation for the AI Sales & Support Assistant.

This module executes predefined RAG test cases and evaluates:
- knowledge-base routing
- expected answer content
- retrieved sources
- source citations

It also integrates LLM-as-a-Judge evaluation for:
- relevance
- groundedness
- completeness

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

    The comparison is case-insensitive so that differences in capitalization do not cause an otherwise correct answer to fail.

    Args:
        answer: Generated assistant answer.
        expected_terms: Terms expected to appear in the answer.

    Returns:
        Tuple containing:
        - whether all terms were found
        - list of missing terms
    """

    answer_lower = answer.lower()

    # Collect only the expected terms that do not appear in the answer.
    missing_terms = [
        term 
        for term in expected_terms
        if term.lower() not in answer_lower
    ]

    # The content check passes only when no required terms are missing.
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
        re.search(
            r"\[Source\s+\d+\]", 
            answer, 
            re.IGNORECASE,
            )
    )


def evaluate_test_case(test_case: dict) -> dict:
    """
    Execute and evaluate one predefined RAG test case.

    This function runs the same routing and RAG workflow used by
    the real FastAPI chat endpoint.

    The generated result is evaluated using:
    - route correctness
    - expected answer content
    - source retrieval
    - citation presence
    - LLM-as-a-Judge scoring

    Args:
        test_case: Test case configuration from TEST_CASES.

    Returns:
        Dictionary containing the complete evaluation result.
    """

    question = test_case["question"]

    # Single-turn tests do not define history, so they default to [].
    # Multi-turn tests provide previous user/assistant messages here.
    history = test_case.get("history", [])
    
    expected_route = test_case["expected_route"]
    expected_terms = test_case.get("expected_terms", [])
    expect_citation = test_case.get("expect_citation", False)

    # Use the same LangGraph routing used by the FastAPI endpoint
    selected_route = get_route(question)

    # Generic follow-up questions may be classified as the default "faqs" route.
    # Setting the route to None allows rag_service.py to inspect the conversation history and recover the previous meaningful route.
    if selected_route == "faqs" and history:
        selected_route = None

    # Execute the existing RAG pipeline
    result = ask_rag(
        question=question,
        history=history,
        forced_route=selected_route,
    )

    # Extract the values returned by rag_service.py.
    answer = result["answer"]
    actual_route = result["route"]
    sources = result["sources"]

    context = result["context"]

    # LLM-as-a-Judge evaluation
    judge_result = evaluate_with_llm(
        question=question,
        context=context,
        answer=answer
    )

    # Deterministic evaluation checks
    # Check whether the actual route matches the expected route.
    route_passed = actual_route == expected_route

    # Check whether all required answer terms are present.
    content_passed, missing_terms = contains_expected_terms(
        answer,
        expected_terms,
    )

    # The retrieval check passes when at least one document was retrieved.
    sources_passed = len(sources) > 0

    # Detect whether the generated answer contains a [Source N] citation.
    citation_found = contains_source_citation(answer)

    # A citation is required only when the test case expects one.
    citation_passed = (
        citation_found
        if expect_citation
        else True
    )

    # The deterministic test succeeds only when all required checks pass.
    # LLM-as-a-Judge scores are intentionally NOT included here because they are a separate qualitative evaluation layer.
    overall_passed = all(
        [
            route_passed,
            content_passed,
            sources_passed,
            citation_passed,
        ]
    )

    # Return all information required for individual reporting and aggregate summary calculations.
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
    Print the complete result of one evaluation test.

    Args:
        result: Evaluation result dictionary returned by evaluate_test_case().
    """

    # Convert the overall boolean result into a readable label.
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
    Print aggregate deterministic evaluation metrics for all executed test cases.

    Args:
        results: Results returned by all evaluation test cases.
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

    # Citation accuracy should only include test cases where citations were explicitly required.
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

    # Avoid division by zero if no test cases require citations.
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

    # Execute every predefined single-turn and multi-turn test case
    for test_case in TEST_CASES:
        result = evaluate_test_case(test_case)
        results.append(result)

        # Print detailed results immediately after each test.
        print_test_result(result)

    # After all tests have run, print aggregate deterministic and LLM-as-a-Judge metrics.
    print_summary(results)


if __name__ == "__main__":
    main()