"""
LangGraph utilities for integrating LLMs with LangGraph and visualization.
"""

from typing import Callable, Dict, Any
from langgraph.graph import StateGraph
from langchain_core.runnables.graph import MermaidDrawMethod
from pathlib import Path


def with_llm_node(llm, node_func: Callable) -> Callable:
    """
    Wrap a node function with LLM access.
    
    Args:
        llm: LLM instance
        node_func: Node function to wrap
        
    Returns:
        Wrapped function with LLM access
    """
    def wrapped(state: Dict[str, Any]) -> Dict[str, Any]:
        return node_func(state, llm)
    return wrapped


def save_graph_visualization(
    graph: StateGraph,
    output_path: Path,
    draw_method: MermaidDrawMethod = MermaidDrawMethod.API
):
    """
    Save graph visualization as PNG.
    
    Args:
        graph: StateGraph instance
        output_path: Path to save PNG file
        draw_method: Mermaid draw method
    """
    try:
        # Get the graph as mermaid
        mermaid_code = graph.draw_mermaid()
        
        # Draw and save
        png_data = graph.draw_mermaid_png(draw_method=draw_method)
        
        with open(output_path, 'wb') as f:
            f.write(png_data)
        
        print(f"Graph visualization saved to: {output_path}")
    except Exception as e:
        print(f"Could not save graph visualization: {e}")
        print("Mermaid code:")
        print(mermaid_code if 'mermaid_code' in locals() else "Could not generate mermaid code")
