from collections import Counter
from typing import List, Tuple

def get_top_tools(tool_counter: Counter, top_n: int = 5) -> List[Tuple[str, int]]:
    """
    Returns the top N most frequently mentioned tool names and their counts.
    """
    return tool_counter.most_common(top_n)
