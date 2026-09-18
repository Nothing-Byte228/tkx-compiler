"""Refactored Python parser with improved architecture."""
import ast
from core.parsers.import_extractor import ImportExtractor
from core.parsers.stdlib_checker import StdlibChecker
from core.compilers.module_copier import ModuleCopier
from core.compilers.import_rewriter import ImportRewriter


class PyParser:
    """Main Python parser that orchestrates import handling."""
    
    def __init__(self, source_code: str):
        """Initialize with source code.
        
        Args:
            source_code: Python source code to parse
        """
        self.tree = ast.parse(source=source_code)
        self.import_extractor = ImportExtractor(source_code)
        self.stdlib_checker = StdlibChecker()
        self.module_copier = ModuleCopier(self.stdlib_checker)
    
    def get_syntax_tree(self) -> str:
        """Get string representation of AST.
        
        Returns:
            String dump of the AST
        """
        return self.import_extractor.get_syntax_tree()
    
    def get_code(self) -> str:
        """Get uncompiled Python code from AST.
        
        Returns:
            Python source code
        """
        return ast.unparse(self.tree)
    
    def get_imports(self) -> list:
        """Extract names of imported modules.
        
        Returns:
            List of module names that are imported
        """
        return self.import_extractor.get_imports()
    
    def is_standard_library(self, import_name: str) -> bool:
        """Check if import is from standard library.
        
        Args:
            import_name: Name of the module to check
            
        Returns:
            True if module is from standard library, False otherwise
        """
        return self.stdlib_checker.is_standard_library(import_name)
    
    def add_import(self, import_name: str, dist_path: str = "packages", 
                   verbose: bool = False) -> str | None:
        """Copy a third-party module to the destination directory.
        
        Args:
            import_name: Name of the module to copy
            dist_path: Destination directory path
            verbose: Enable detailed logging
            
        Returns:
            Path to the copied file, or None if not copied
        """
        return self.module_copier.add_import(import_name, dist_path, verbose)
    
    def add_import_recursive(self, import_name: str, dist_path: str = "packages",
                            processed_modules: set = None, verbose: bool = False) -> None:
        """Recursively extract a module and ALL its external dependencies.
        
        Args:
            import_name: Name of the module to extract
            dist_path: Destination directory path
            processed_modules: Set of already processed modules
            verbose: Enable detailed logging
        """
        self.module_copier.add_import_recursive(import_name, dist_path, processed_modules, verbose)
    
    def get_functions(self) -> dict:
        """Extract function definitions from code.
        
        Returns:
            Dictionary mapping function names to their source code
        """
        functions = {}
        for node in ast.walk(self.tree):
            if isinstance(node, ast.FunctionDef):
                functions[node.name] = ast.unparse(node)
        return functions
    
    def modify_imports(self):
        """Transform third-party imports to use local packages directory."""
        print("Updating import paths for packages directory...")
        
        rewriter = ImportRewriter(self.stdlib_checker)
        self.tree = rewriter.visit(self.tree)
        ast.fix_missing_locations(self.tree)
        print("Import paths updated for packages directory.")
