"""Integration tests for compiler builder."""
import pytest
import os
import tempfile
import shutil
from core.builders.compiler_builder import CompilerBuilder


class TestCompilerBuilderIntegration:
    """Integration tests for the complete build process."""
    
    def test_full_build_process(self):
        """Test complete build process with simple project."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create project structure
            project_path = os.path.join(temp_dir, "test_project")
            os.makedirs(project_path)
            
            # Create main.xml
            xml_content = '''<?xml version="1.0" encoding="UTF-8"?>
<Application>
    <Window title="Integration Test" size="400x300" />
    <Label text="Test Label" pack="pady=10" />
    <Button text="Test Button" pack="pady=10" />
</Application>'''
            
            with open(os.path.join(project_path, "main.xml"), 'w') as f:
                f.write(xml_content)
            
            # Build project
            builder = CompilerBuilder(project_path, "test_output.py", verbose=False)
            result = builder.build()
            
            # Verify build succeeded
            assert result is not None
            assert os.path.exists(result)
            
            # Verify output content
            with open(result, 'r') as f:
                output = f.read()
            
            assert "tk.Tk()" in output
            assert "Integration Test" in output
            assert "Test Label" in output
            assert "Test Button" in output
            assert "mainloop()" in output
    
    def test_build_with_user_module(self):
        """Test build process with user-defined module."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create project structure
            project_path = os.path.join(temp_dir, "test_project")
            os.makedirs(project_path)
            
            # Create main.xml
            xml_content = '''<?xml version="1.0" encoding="UTF-8"?>
<Application>
    <Window title="Module Test" size="400x300" />
    <Import module="user_logic" />
    <Button text="Click Me" pack="pady=10" command="user_logic.handle_click" />
</Application>'''
            
            with open(os.path.join(project_path, "main.xml"), 'w') as f:
                f.write(xml_content)
            
            # Create user_logic.py
            logic_content = '''def handle_click():
    print("Button clicked!")
'''
            
            with open(os.path.join(project_path, "user_logic.py"), 'w') as f:
                f.write(logic_content)
            
            # Build project
            builder = CompilerBuilder(project_path, "module_test.py", verbose=False)
            result = builder.build()
            
            # Verify build succeeded
            assert result is not None
            assert os.path.exists(result)
            
            # Verify user module was copied
            packages_dir = os.path.join(project_path, "dist", "packages")
            assert os.path.exists(os.path.join(packages_dir, "user_logic.py"))
    
    def test_build_invalid_project_structure(self):
        """Test build with invalid project structure."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create empty directory without main.xml
            project_path = os.path.join(temp_dir, "empty_project")
            os.makedirs(project_path)
            
            # Build should fail
            builder = CompilerBuilder(project_path, "test.py", verbose=False)
            result = builder.build()
            
            assert result is None
    
    def test_build_invalid_xml(self):
        """Test build with invalid XML."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create project with invalid XML
            project_path = os.path.join(temp_dir, "invalid_project")
            os.makedirs(project_path)
            
            with open(os.path.join(project_path, "main.xml"), 'w') as f:
                f.write('<Invalid><XML>')
            
            # Build should fail
            builder = CompilerBuilder(project_path, "test.py", verbose=False)
            result = builder.build()
            
            assert result is None
    
    def test_build_with_invalid_user_module(self):
        """Test build with invalid user module syntax."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create project structure
            project_path = os.path.join(temp_dir, "test_project")
            os.makedirs(project_path)
            
            # Create main.xml
            xml_content = '''<?xml version="1.0" encoding="UTF-8"?>
<Application>
    <Window title="Test" size="400x300" />
    <Import module="invalid_logic" />
</Application>'''
            
            with open(os.path.join(project_path, "main.xml"), 'w') as f:
                f.write(xml_content)
            
            # Create invalid user_logic.py
            with open(os.path.join(project_path, "invalid_logic.py"), 'w') as f:
                f.write('def invalid(:\n    return "bad syntax"')
            
            # Build should succeed but skip invalid module
            builder = CompilerBuilder(project_path, "test.py", verbose=False)
            result = builder.build()
            
            # Build should still succeed (module is skipped)
            assert result is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
