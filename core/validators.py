"""Validation and error handling modules for tkx-compiler."""
import os
import ast
import xml.etree.ElementTree as ElementTree
from typing import Tuple, Optional, List


class ValidationError(Exception):
    """Custom exception for validation errors."""
    
    def __init__(self, message: str, details: Optional[str] = None):
        """Initialize validation error.
        
        Args:
            message: Error message
            details: Additional error details
        """
        self.message = message
        self.details = details
        super().__init__(self.message)


class XMLValidator:
    """Validates XML structure and content."""
    
    @staticmethod
    def validate_xml_file(xml_path: str) -> Tuple[bool, Optional[str]]:
        """Validate XML file structure.
        
        Args:
            xml_path: Path to XML file
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not os.path.exists(xml_path):
            return False, f"XML file not found: {xml_path}"
        
        if not os.path.isfile(xml_path):
            return False, f"Path is not a file: {xml_path}"
        
        try:
            with open(xml_path, "r", encoding="utf-8") as f:
                content = f.read()
                
            if not content.strip():
                return False, "XML file is empty"
                
            ElementTree.fromstring(content)
            return True, None
            
        except ElementTree.ParseError as e:
            return False, f"XML parsing error: {e}"
        except UnicodeDecodeError as e:
            return False, f"Encoding error: {e}"
        except Exception as e:
            return False, f"Unexpected error reading XML: {e}"
    
    @staticmethod
    def validate_xml_structure(xml_content: str) -> Tuple[bool, Optional[str]]:
        """Validate XML structure and required elements.
        
        Args:
            xml_content: XML content as string
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            root = ElementTree.fromstring(xml_content)
            
            # Check if root is Application or has valid widget elements
            valid_root_tags = {"Application", "Window", "Button", "Label", "Entry", 
                             "Text", "Checkbutton", "Frame", "Canvas", "Listbox",
                             "Menu", "Toplevel", "Require", "Import"}
            
            if root.tag not in valid_root_tags and not any(
                child.tag in valid_root_tags for child in root
            ):
                return False, f"Invalid root element: {root.tag}"
            
            return True, None
            
        except ElementTree.ParseError as e:
            return False, f"XML structure error: {e}"
        except Exception as e:
            return False, f"Unexpected validation error: {e}"


class PythonValidator:
    """Validates Python file structure and syntax."""
    
    @staticmethod
    def validate_python_file(py_path: str) -> Tuple[bool, Optional[str]]:
        """Validate Python file structure.
        
        Args:
            py_path: Path to Python file
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not os.path.exists(py_path):
            return False, f"Python file not found: {py_path}"
        
        if not os.path.isfile(py_path):
            return False, f"Path is not a file: {py_path}"
        
        try:
            with open(py_path, "r", encoding="utf-8") as f:
                content = f.read()
                
            if not content.strip():
                return False, "Python file is empty"
                
            ast.parse(content)
            return True, None
            
        except SyntaxError as e:
            return False, f"Syntax error at line {e.lineno}: {e.msg}"
        except UnicodeDecodeError as e:
            return False, f"Encoding error: {e}"
        except Exception as e:
            return False, f"Unexpected error reading Python file: {e}"
    
    @staticmethod
    def validate_python_syntax(code: str, filename: str = "<string>") -> Tuple[bool, Optional[str]]:
        """Validate Python code syntax.
        
        Args:
            code: Python code string
            filename: Filename for error reporting
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            ast.parse(code, filename=filename)
            return True, None
        except SyntaxError as e:
            return False, f"Syntax error at line {e.lineno}: {e.msg}"


class ProjectValidator:
    """Validates project structure and dependencies."""
    
    @staticmethod
    def validate_project_structure(project_path: str) -> Tuple[bool, List[str]]:
        """Validate project directory structure.
        
        Args:
            project_path: Path to project directory
            
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        
        if not os.path.exists(project_path):
            errors.append(f"Project directory not found: {project_path}")
            return False, errors
        
        if not os.path.isdir(project_path):
            errors.append(f"Project path is not a directory: {project_path}")
            return False, errors
        
        main_xml = os.path.join(project_path, "main.xml")
        if not os.path.exists(main_xml):
            errors.append(f"Required file main.xml not found in: {project_path}")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def validate_dependencies(import_names: List[str]) -> Tuple[bool, List[str]]:
        """Validate that required dependencies can be found.
        
        Args:
            import_names: List of module names to check
            
        Returns:
            Tuple of (all_found, list_of_missing)
        """
        import importlib.util
        
        missing = []
        for module_name in import_names:
            base_name = module_name.split('.')[0]
            try:
                spec = importlib.util.find_spec(base_name)
                if spec is None:
                    missing.append(module_name)
            except Exception:
                missing.append(module_name)
        
        return len(missing) == 0, missing


class PathValidator:
    """Validates and sanitizes file paths."""
    
    @staticmethod
    def is_safe_path(base_path: str, target_path: str) -> bool:
        """Check if target path is safe (no path traversal).
        
        Args:
            base_path: Base directory path
            target_path: Target path to check
            
        Returns:
            True if path is safe, False otherwise
        """
        try:
            base_abs = os.path.abspath(base_path)
            target_abs = os.path.abspath(target_path)
            
            # Check if target is within base directory
            return os.path.commonpath([base_abs, target_abs]) == base_abs
        except Exception:
            return False
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """Sanitize filename to prevent path traversal.
        
        Args:
            filename: Original filename
            
        Returns:
            Sanitized filename
        """
        # Remove path separators and parent directory references
        sanitized = filename.replace("..", "").replace("/", "").replace("\\", "")
        # Remove null bytes
        sanitized = sanitized.replace("\x00", "")
        # Limit length
        return sanitized[:255]
