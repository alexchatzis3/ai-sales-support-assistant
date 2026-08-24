"""
LLM-as-a-Judge evaluation service.

The judge evaluates generated RAG answers using the original question and the retrieved context.

Metrics:
- relevance
- groundedness
- completeness
"""

import json

from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from backend.app.core.settings import CHAT_MODEL

judge_llm = ChatOpenAI(
    model = CHAT_MODEL,
    temperature=0,
)

JUDGE_PROMPT = ChatPromptTemplate.from_template("""
You are evaluating an AI Sales & Support Assistant.

Evaluate the generated answer using ONLY:
1. The user's question
2. The retrieved context

Do not use your own external knowledge.

Important evaluation rules:

- This assistant is specifically designed for a technology store.
- Questions unrelated to the store are intentionally out of scope.
- For out-of-scope questions, the correct behavior is to politely refuse
  or redirect the user to store-related topics.
- Do NOT penalize relevance or completeness when the assistant correctly refuses an out-of-scope question.
- Evaluate whether the response fulfills the intended behavior of the store assistant, not whether it answers general-knowledge questions.

- Carefully verify numerical constraints before scoring.
- For budget questions, compare the product price numerically with the user's budget.
- A product priced below or equal to the stated budget is within budget.
- Do not claim that a product exceeds the budget unless its numeric price is actually greater than the user's numeric budget.

Evaluation criteria:

1. Relevance
Does the answer directly address the user's question?

2. Groundedness
Are all factual claims supported by the retrieved context?
Penalize invented facts, unsupported conclusions, performance claims, comparisons or specifications.

3. Completeness
Does the answer include the important information needed to answer the question based on the retrieved context?

Score each criterion from 1 to 5:

1 = very poor
2 = poor
3 = acceptable
4 = good
5 = excellent

Return ONLY valid JSON in exactly this format:

{{
    "relevance": 5,
    "groundedness": 5,
    "completeness": 5,
    "reason": "Short explanation of the scores."
}}

Question:
{question}

Retrieved context:
{context}

Generated answer:
{answer}
""")

def evaluate_with_llm(
    question: str,
    context: str,
    answer: str,
) -> dict:
    """
    Evaluate a generated RAG answer using an LLM-as-a-Judge.

    Args:
        question: Original user question.
        context: Retrieved RAG context.
        answer: Generated assistant answer.

    Returns:
        Dictionary containing judge scores and reasoning.    
    """

    chain = JUDGE_PROMPT | judge_llm

    response = chain.invoke(
        {
            "question": question,
            "context": context,
            "answer": answer,
        }
    )

    try:
        return json.loads(response.content)

    except json.JSONDecodeError:
        return {
            "relevance": 0,
            "groundedness": 0,
            "completeness": 0,
            "reason": (
                "The judge did not return valid JSON. "
                f"Raw response: {response.content}"
            ),
        }