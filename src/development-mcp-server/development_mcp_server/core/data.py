from enum import Enum
from pathlib import Path

RULES_PATH = Path(__file__).parent.parent / 'static'

class DevelopmentRule(str, Enum):
    """Development Rules path"""
    SECURITY = 'CODE_SECURITY_RULES.md'
    
def read_markdown(rule:DevelopmentRule) -> str:
    """Read a rule from a markdown file"""
    path = RULES_PATH / rule
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return f'Error: File Not found {rule}'
    except Exception as e:
        return f'Error: Failed to read guideline'
