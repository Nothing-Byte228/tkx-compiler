"""Module for rewriting import statements in Python AST."""
import ast
from core.parsers.stdlib_checker import StdlibChecker
from core.logger import get_logger


class ImportRewriter(ast.NodeTransformer):
    """AST transformer that rewrites import paths."""
    
    def __init__(self, stdlib_checker: StdlibChecker):
        """Initialize with stdlib checker.
        
        Args:
            stdlib_checker: StdlibChecker instance
        """
        super().__init__()
        self.stdlib_checker = stdlib_checker
        self.logger = get_logger()
    
    def visit_Import(self, node):
        """Transform import statements.
        
        Args:
            node: AST Import node
            
        Returns:
            Transformed node
        """
        for alias in node.names:
            root_name = alias.name.split('.')[0]
            
            if self.stdlib_checker.is_standard_library(root_name):
                continue
                
            alias.asname = root_name
            alias.name = f"packages.{root_name}"
            self.logger.info(f"Import {root_name} redirected to packages.{root_name}")
        return node
    
    def visit_ImportFrom(self, node):
        """Transform from import statements.
        
        Args:
            node: AST ImportFrom node
            
        Returns:
            Transformed node
        """
        if not node.module:
            return node
            
        root_module = node.module.split('.')[0]
        
        if self.stdlib_checker.is_standard_library(root_module):
            return node
        
        node.module = f"packages.{root_module}"
        self.logger.info(f"Import from {root_module} redirected to packages.{root_module}")
        return node
