"""Unit tests for validator modules."""
import pytest
import os
import tempfile
from core.validators import (
    XMLValidator,
    PythonValidator,
    ProjectValidator,
    PathValidator,
    ValidationError
)


class TestXMLValidator:
    """Test cases for XMLValidator."""
    
    def test_validate_xml_file_not_found(self):
        """Test validation of non-existent XML file."""
        is_valid, error = XMLValidator.validate_xml_file("/nonexistent/file.xml")
        assert not is_valid
        assert "not found" in error.lower()
    
    def test_validate_xml_file_valid(self):
        """Test validation of valid XML file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False) as f:
            f.write('<?xml version="1.0"?><Application><Window title="Test"/></Application>')
            temp_path = f.name
        
        try:
            is_valid, error = XMLValidator.validate_xml_file(temp_path)
            assert is_valid
            assert error is None
        finally:
            os.unlink(temp_path)
    
    def test_validate_xml_structure_valid(self):
        """Test validation of valid XML structure."""
        xml_content = '<?xml version="1.0"?><Application><Window title="Test"/></Application>'
        is_valid, error = XMLValidator.validate_xml_structure(xml_content)
        assert is_valid
        assert error is None
    
    def test_validate_xml_structure_invalid(self):
        """Test validation of invalid XML structure."""
        xml_content = '<?xml version="1.0"?><InvalidElement></InvalidElement>'
        is_valid, error = XMLValidator.validate_xml_structure(xml_content)
        assert not is_valid
        assert error is not None


class TestPythonValidator:
    """Test cases for PythonValidator."""
    
    def test_validate_python_file_not_found(self):
        """Test validation of non-existent Python file."""
        is_valid, error = PythonValidator.validate_python_file("/nonexistent/file.py")
        assert not is_valid
        assert "not found" in error.lower()
    
    def test_validate_python_file_valid(self):
        """Test validation of valid Python file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write('def test():\n    return "hello"')
            temp_path = f.name
        
        try:
            is_valid, error = PythonValidator.validate_python_file(temp_path)
            assert is_valid
            assert error is None
        finally:
            os.unlink(temp_path)
    
    def test_validate_python_syntax_invalid(self):
        """Test validation of invalid Python syntax."""
        python_code = 'def test(:\n    return "hello"'
        is_valid, error = PythonValidator.validate_python_syntax(python_code)
        assert not is_valid
        assert "Syntax error" in error
    
    def test_validate_python_syntax_valid(self):
        """Test validation of valid Python syntax."""
        python_code = 'def test():\n    return "hello"'
        is_valid, error = PythonValidator.validate_python_syntax(python_code)
        assert is_valid
        assert error is None


class TestProjectValidator:
    """Test cases for ProjectValidator."""
    
    def test_validate_project_structure_not_found(self):
        """Test validation of non-existent project directory."""
        is_valid, errors = ProjectValidator.validate_project_structure("/nonexistent/project")
        assert not is_valid
        assert len(errors) > 0
    
    def test_validate_project_structure_valid(self):
        """Test validation of valid project structure."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create main.xml
            xml_path = os.path.join(temp_dir, "main.xml")
            with open(xml_path, 'w') as f:
                f.write('<?xml version="1.0"?><Application><Window title="Test"/></Application>')
            
            is_valid, errors = ProjectValidator.validate_project_structure(temp_dir)
            assert is_valid
            assert len(errors) == 0
    
    def test_validate_project_structure_missing_main_xml(self):
        """Test validation of project without main.xml."""
        with tempfile.TemporaryDirectory() as temp_dir:
            is_valid, errors = ProjectValidator.validate_project_structure(temp_dir)
            assert not is_valid
            assert any("main.xml" in error for error in errors)


class TestPathValidator:
    """Test cases for PathValidator."""
    
    def test_is_safe_path_valid(self):
        """Test path safety validation for safe path."""
        with tempfile.TemporaryDirectory() as temp_dir:
            target_path = os.path.join(temp_dir, "safe_file.txt")
            is_safe = PathValidator.is_safe_path(temp_dir, target_path)
            assert is_safe
    
    def test_is_safe_path_traversal(self):
        """Test path safety validation for path traversal."""
        base_path = "/safe/base"
        target_path = "/safe/base/../../../etc/passwd"
        is_safe = PathValidator.is_safe_path(base_path, target_path)
        assert not is_safe
    
    def test_sanitize_filename(self):
        """Test filename sanitization."""
        malicious = "../../../etc/passwd"
        sanitized = PathValidator.sanitize_filename(malicious)
        assert ".." not in sanitized
        assert "/" not in sanitized
        assert "\\" not in sanitized
    
    def test_sanitize_filename_length(self):
        """Test filename length limit."""
        long_name = "a" * 300
        sanitized = PathValidator.sanitize_filename(long_name)
        assert len(sanitized) <= 255


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
