from typing import TypedDict, Literal

from langgraph.graph import StateGraph, START, END


class GraphState(TypedDict):
    """
    State shared across the graph execution.
    """

    question: str
    route: str


def route_node(state: GraphState) -> dict:
    """
    Determine which knowledge base should be used.

    Args:
        state: Current graph state.

    Returns:
        Updated state containing the selected route.
    """

    question = state["question"].lower()

    product_keywords = [
        "laptop",
        "gaming",
        "monitor",
        "smartphone",
        "tablet",
        "προϊόν",
        "προϊόντα",
        "αγορά",
        "πρότεινε",
        "budget",
        "σύγκρινε",
        "συγκρινε",
    ]

    policy_keywords = [
        "επιστροφή",
        "επιστροφές",
        "εγγύηση",
        "πολιτική",
        "box now",
        "courier",
        "πληρωμή",
        "δόσεις",
        "δοσεις",
    ]

    faq_keywords = [
        "ώρες", "ωρες", "λειτουργίας", "λειτουργιας",
        "τηλέφωνο", "τηλεφωνο", "παραγγελία", "παραγγελια",
        "παραλαβή", "παραλαβη", "τεχνική υποστήριξη",
        "τεχνικη υποστηριξη", "υποστήριξη","υποστηριξη", "τεχνική", "τεχνικη","support", "κατάστημα", "καταστημα", 
    ]

    if any(keyword in question for keyword in policy_keywords):
        return {"route": "policies"}

    if any(keyword in question for keyword in product_keywords):
        return {"route": "products"}

    if any(keyword in question for keyword in faq_keywords):
        return {"route": "faqs"}
    
    return {"route": "faqs"}


def route_decision(
    state: GraphState,
) -> Literal["products", "policies", "faqs"]:
    """
    Select the next graph node.

    Args:
        state: Current graph state.

    Returns:
        Node name.
    """

    return state["route"]


def products_node(state: GraphState) -> dict:
    """
    Product route node.
    """

    return {"route": "products"}


def policies_node(state: GraphState) -> dict:
    """
    Policies route node.
    """

    return {"route": "policies"}


def faqs_node(state: GraphState) -> dict:
    """
    FAQ route node.
    """

    return {"route": "faqs"}


# Create graph builder
builder = StateGraph(GraphState)

# Register nodes
builder.add_node("router", route_node)
builder.add_node("products", products_node)
builder.add_node("policies", policies_node)
builder.add_node("faqs", faqs_node)

# Add edges
builder.add_edge(START, "router")

builder.add_conditional_edges(
    "router",
    route_decision,
    {
        "products": "products",
        "policies": "policies",
        "faqs": "faqs",
    },
)

builder.add_edge("products", END)
builder.add_edge("policies", END)
builder.add_edge("faqs", END)

# Compile graph
graph = builder.compile()

def get_route(question: str) -> str:
    """
    Execute the graph and return the selected route.

    Args:
        question: User question.

    Returns:
        Selected route.
    """

    result = graph.invoke(
        {
            "question": question,
        }
    )

    return result["route"]