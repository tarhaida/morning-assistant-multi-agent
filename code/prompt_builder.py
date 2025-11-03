"""
Prompt builder module.
Constructs modular prompts from configuration.
"""

from typing import Dict, Any, List


def build_prompt_body(prompt_config: Dict[str, Any]) -> str:
    """
    Build the main prompt body from configuration.
    
    Args:
        prompt_config: Dictionary containing prompt sections
        
    Returns:
        Formatted prompt string
    """
    sections = []
    
    # Role
    if "role" in prompt_config:
        sections.append(f"ROLE: {prompt_config['role']}")
    
    # Instruction
    if "instruction" in prompt_config:
        sections.append(f"INSTRUCTION:\n{prompt_config['instruction']}")
    
    # Context
    if "context" in prompt_config:
        sections.append(f"CONTEXT:\n{prompt_config['context']}")
    
    # Output constraints
    if "output_constraints" in prompt_config:
        sections.append(f"OUTPUT CONSTRAINTS:\n{prompt_config['output_constraints']}")
    
    # Output format
    if "output_format" in prompt_config:
        sections.append(f"OUTPUT FORMAT:\n{prompt_config['output_format']}")
    
    # Style or tone
    if "style_or_tone" in prompt_config:
        sections.append(f"STYLE/TONE: {prompt_config['style_or_tone']}")
    
    # Goal
    if "goal" in prompt_config:
        sections.append(f"GOAL:\n{prompt_config['goal']}")
    
    # Examples
    if "examples" in prompt_config:
        examples = prompt_config['examples']
        if isinstance(examples, list):
            examples_text = "\n".join([f"- {ex}" for ex in examples])
        else:
            examples_text = examples
        sections.append(f"EXAMPLES:\n{examples_text}")
    
    # Reasoning strategy
    if "reasoning_strategy" in prompt_config:
        sections.append(f"REASONING STRATEGY:\n{prompt_config['reasoning_strategy']}")
    
    return "\n\n".join(sections)


def build_system_prompt_message(prompt_config: Dict[str, Any]) -> str:
    """
    Build system prompt message.
    
    Args:
        prompt_config: Dictionary containing prompt configuration
        
    Returns:
        System prompt string
    """
    return build_prompt_body(prompt_config)


def build_one_shot_prompt(
    prompt_config: Dict[str, Any],
    user_input: str
) -> List[Dict[str, str]]:
    """
    Build a one-shot prompt with system and user messages.
    
    Args:
        prompt_config: Dictionary containing prompt configuration
        user_input: User input text
        
    Returns:
        List of message dictionaries
    """
    system_prompt = build_system_prompt_message(prompt_config)
    
    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_input}
    ]


def print_prompt_preview(prompt_config: Dict[str, Any], max_length: int = 500):
    """
    Print a preview of the prompt.
    
    Args:
        prompt_config: Dictionary containing prompt configuration
        max_length: Maximum length to display
    """
    prompt = build_prompt_body(prompt_config)
    
    if len(prompt) > max_length:
        prompt = prompt[:max_length] + "..."
    
    print("=" * 80)
    print("PROMPT PREVIEW")
    print("=" * 80)
    print(prompt)
    print("=" * 80)
