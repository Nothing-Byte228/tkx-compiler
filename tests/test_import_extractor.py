"""Unit tests for import extractor module."""
import pytest
from core.parsers.import_extractor import ImportExtractor


class TestImportExtractor:
    """Test cases for ImportExtractor class."""
    
    def test_extract_simple_import(self):
        """Test extraction of simple import statement."""
        code = "import os"
        extractor = ImportExtractor(code)
        imports = extractor.get_imports()
        assert "os" in imports
    
    def test_extract_multiple_imports(self):
        """Test extraction of multiple import statements."""
        code = "import os\nimport sys\nimport json"
        extractor = ImportExtractor(code)
        imports = extractor.get_imports()
        assert "os" in imports
        assert "sys" in imports
        assert "json" in imports
    
    def test_extract_from_import(self):
        """Test extraction of from import statement."""
        code = "from tkinter import Button"
        extractor = ImportExtractor(code)
        imports = extractor.get_imports()
        assert "tkinter" in imports
    
    def test_extract_mixed_imports(self):
        """Test extraction of mixed import statements."""
        code = "import os\nfrom sys import path\nimport json"
        extractor = ImportExtractor(code)
        imports = extractor.get_imports()
        assert "os" in imports
        assert "sys" in imports
        assert "json" in imports
    
    def test_extract_no_imports(self):
        """Test extraction when no imports exist."""
        code = "def test():\n    return 'hello'"
        extractor = ImportExtractor(code)
        imports = extractor.get_imports()
        assert len(imports) == 0
    
    def test_get_syntax_tree(self):
        """Test getting syntax tree."""
        code = "import os"
        extractor = ImportExtractor(code)
        syntax_tree = extractor.get_syntax_tree()
        assert isinstance(syntax_tree, str)
        assert "Module" in syntax_tree


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
