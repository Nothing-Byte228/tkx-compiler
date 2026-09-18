"""Unit tests for configuration module."""
import pytest
import os
import tempfile
import json
from core.config import Config, ProjectTemplate


class TestConfig:
    """Test cases for Config class."""
    
    def test_default_config(self):
        """Test default configuration values."""
        config = Config()
        assert config.get("output_file") == "program.py"
        assert config.get("verbose") is False
        assert config.get("log_level") == "INFO"
    
    def test_config_get_set(self):
        """Test getting and setting configuration values."""
        config = Config()
        config.set("output_file", "custom.py")
        assert config.get("output_file") == "custom.py"
    
    def test_config_get_with_default(self):
        """Test getting configuration with default value."""
        config = Config()
        value = config.get("nonexistent_key", "default_value")
        assert value == "default_value"
    
    def test_config_load_from_file(self):
        """Test loading configuration from JSON file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({"output_file": "test.py", "verbose": True}, f)
            temp_path = f.name
        
        try:
            config = Config(temp_path)
            assert config.get("output_file") == "test.py"
            assert config.get("verbose") is True
        finally:
            os.unlink(temp_path)
    
    def test_config_save_to_file(self):
        """Test saving configuration to JSON file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_path = f.name
        
        try:
            config = Config()
            config.set("output_file", "saved.py")
            config.save_to_file(temp_path)
            
            # Load and verify
            with open(temp_path, 'r') as f:
                saved_config = json.load(f)
            
            assert saved_config["output_file"] == "saved.py"
        finally:
            os.unlink(temp_path)
    
    def test_config_env_variables(self):
        """Test loading configuration from environment variables."""
        os.environ["TKX_OUTPUT_FILE"] = "env_test.py"
        os.environ["TKX_VERBOSE"] = "true"
        
        try:
            config = Config()
            assert config.get("output_file") == "env_test.py"
            assert config.get("verbose") is True
        finally:
            del os.environ["TKX_OUTPUT_FILE"]
            del os.environ["TKX_VERBOSE"]
    
    def test_config_to_dict(self):
        """Test converting configuration to dictionary."""
        config = Config()
        config.set("custom_key", "custom_value")
        config_dict = config.to_dict()
        
        assert isinstance(config_dict, dict)
        assert config_dict["custom_key"] == "custom_value"


class TestProjectTemplate:
    """Test cases for ProjectTemplate class."""
    
    def test_create_basic_template(self):
        """Test creating basic project template."""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_path = os.path.join(temp_dir, "test_project")
            ProjectTemplate.create_basic_template(project_path, "TestProject")
            
            # Check if files were created
            assert os.path.exists(os.path.join(project_path, "main.xml"))
            assert os.path.exists(os.path.join(project_path, "logic.py"))
            assert os.path.exists(os.path.join(project_path, ".tkxrc.json"))
    
    def test_create_advanced_template(self):
        """Test creating advanced project template."""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_path = os.path.join(temp_dir, "advanced_project")
            ProjectTemplate.create_advanced_template(project_path, "AdvancedProject")
            
            # Check if files were created
            assert os.path.exists(os.path.join(project_path, "main.xml"))
            assert os.path.exists(os.path.join(project_path, "app_logic.py"))
            assert os.path.exists(os.path.join(project_path, "helpers.py"))
            assert os.path.exists(os.path.join(project_path, ".tkxrc.json"))
    
    def test_create_default_config(self):
        """Test creating default configuration file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Config.create_default_config(temp_dir)
            
            assert os.path.exists(config_path)
            assert config_path.endswith(".tkxrc.json")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
