"""Unit tests for XML parser module."""
import pytest
from core.xml_parser import XMLCompiler


class TestXMLCompiler:
    """Test cases for XMLCompiler class."""
    
    def test_initialization(self):
        """Test XML compiler initialization."""
        compiler = XMLCompiler()
        assert compiler.ttk_imported is False
        assert len(compiler.widget_counts) == 0
        assert len(compiler.user_files) == 0
    
    def test_compile_simple_window(self):
        """Test compilation of simple window."""
        xml_code = '<Window title="Test" size="400x300" />'
        compiler = XMLCompiler()
        result = compiler.compile(xml_code)
        
        assert "tk.Tk()" in result
        assert 'title("Test")' in result
        assert 'geometry("400x300")' in result
        assert "mainloop()" in result
    
    def test_compile_with_button(self):
        """Test compilation with button widget."""
        xml_code = '''<Application>
            <Window title="Test" size="400x300" />
            <Button text="Click Me" pack="pady=10" />
        </Application>'''
        compiler = XMLCompiler()
        result = compiler.compile(xml_code)
        
        assert "Button" in result
        assert "Click Me" in result
        assert "pack" in result
    
    def test_compile_with_import(self):
        """Test compilation with import statement."""
        xml_code = '''<Application>
            <Window title="Test" size="400x300" />
            <Import module="logic" />
        </Application>'''
        compiler = XMLCompiler()
        result = compiler.compile(xml_code)
        
        assert "import logic" in result
        assert "logic" in compiler.user_files
    
    def test_compile_with_require(self):
        """Test compilation with require statement."""
        xml_code = '''<Application>
            <Window title="Test" size="400x300" />
            <Require module="json" />
        </Application>'''
        compiler = XMLCompiler()
        result = compiler.compile(xml_code)
        
        assert "import json" in result
    
    def test_compile_with_ttk_widget(self):
        """Test compilation with ttk widget."""
        xml_code = '''<Application>
            <Window title="Test" size="400x300" />
            <TtkButton text="Styled" pack="pady=10" />
        </Application>'''
        compiler = XMLCompiler()
        result = compiler.compile(xml_code)
        
        assert "import tkinter.ttk as ttk" in result
        assert "ttk.Button" in result
        assert compiler.ttk_imported is True
    
    def test_compile_invalid_element(self):
        """Test compilation with invalid element."""
        xml_code = '<InvalidElement />'
        compiler = XMLCompiler()
        
        with pytest.raises(ValueError, match="Неизвестный XML-элемент"):
            compiler.compile(xml_code)
    
    def test_widget_name_generation(self):
        """Test unique widget name generation."""
        compiler = XMLCompiler()
        
        name1 = compiler._generate_widget_name("btn")
        name2 = compiler._generate_widget_name("btn")
        name3 = compiler._generate_widget_name("lbl")
        
        assert name1 == "btn_1"
        assert name2 == "btn_2"
        assert name3 == "lbl_1"
    
    def test_parse_attributes(self):
        """Test attribute parsing."""
        compiler = XMLCompiler()
        attrs = 'pady=10, fill=x, expand=true'
        result = compiler._parse_attributes(attrs)
        
        assert result["pady"] == "10"
        assert result["fill"] == "x"
        assert result["expand"] == "true"
    
    def test_value_node_boolean(self):
        """Test boolean value conversion."""
        compiler = XMLCompiler()
        
        true_node = compiler._value_node("true")
        false_node = compiler._value_node("false")
        
        assert true_node.value is True
        assert false_node.value is False
    
    def test_value_node_number(self):
        """Test numeric value conversion."""
        compiler = XMLCompiler()
        
        int_node = compiler._value_node("42")
        float_node = compiler._value_node("3.14")
        str_node = compiler._value_node("hello")
        
        assert int_node.value == 42
        assert float_node.value == 3.14
        assert str_node.value == "hello"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
