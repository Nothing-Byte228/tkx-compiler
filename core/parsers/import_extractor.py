"""Module for extracting imports from Python AST."""
import ast
from typing import List


class ImportExtractor:
    """Extracts import statements from Python AST."""
    
    def __init__(self, source_code: str):
        """Initialize with source code.
        
        Args:
            source_code: Python source code to parse
        """
        self.tree = ast.parse(source=source_code)
    
    def get_imports(self) -> List[str]:
        """Extract names of imported modules.
        
        Returns:
            List of module names that are imported
        """
        imports = []
        for node in ast.walk(self.tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imports.append(node.module)
        return imports
    
    def get_syntax_tree(self) -> str:
        """Get string representation of AST.
        
        Returns:
            String dump of the AST
        """
        return ast.dump(self.tree, indent=4)
