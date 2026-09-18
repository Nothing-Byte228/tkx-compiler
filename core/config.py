"""Configuration management for tkx-compiler."""
import os
import json
from typing import Dict, Any, Optional
from pathlib import Path


class Config:
    """Configuration manager for tkx-compiler."""
    
    DEFAULT_CONFIG = {
        "output_file": "program.py",
        "dist_dir": "dist",
        "packages_dir": "packages",
        "verbose": False,
        "validate_xml": True,
        "validate_python": True,
        "check_dependencies": True,
        "recursive_dependencies": True,
        "safe_paths": True,
        "log_level": "INFO",
        "encoding": "utf-8",
        "max_file_size": 10485760,  # 10MB
    }
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize configuration.
        
        Args:
            config_path: Path to configuration file (optional)
        """
        self.config = self.DEFAULT_CONFIG.copy()
        self.config_path = config_path
        
        if config_path and os.path.exists(config_path):
            self.load_from_file(config_path)
        
        self.load_from_env()
    
    def load_from_file(self, config_path: str) -> None:
        """Load configuration from JSON file.
        
        Args:
            config_path: Path to configuration file
        """
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                user_config = json.load(f)
                self.config.update(user_config)
        except Exception as e:
            print(f"Warning: Failed to load config from {config_path}: {e}")
    
    def load_from_env(self) -> None:
        """Load configuration from environment variables."""
        env_mapping = {
            "TKX_OUTPUT_FILE": "output_file",
            "TKX_DIST_DIR": "dist_dir",
            "TKX_PACKAGES_DIR": "packages_dir",
            "TKX_VERBOSE": "verbose",
            "TKX_LOG_LEVEL": "log_level",
            "TKX_ENCODING": "encoding",
        }
        
        for env_var, config_key in env_mapping.items():
            value = os.getenv(env_var)
            if value is not None:
                # Convert string to appropriate type
                if config_key == "verbose":
                    self.config[config_key] = value.lower() in ("true", "1", "yes")
                else:
                    self.config[config_key] = value
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value.
        
        Args:
            key: Configuration key
            default: Default value if key not found
            
        Returns:
            Configuration value
        """
        return self.config.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """Set configuration value.
        
        Args:
            key: Configuration key
            value: Value to set
        """
        self.config[key] = value
    
    def save_to_file(self, config_path: Optional[str] = None) -> None:
        """Save configuration to JSON file.
        
        Args:
            config_path: Path to save configuration (uses self.config_path if not provided)
        """
        path = config_path or self.config_path
        if not path:
            raise ValueError("No config path specified")
        
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.config, f, indent=2)
    
    def to_dict(self) -> Dict[str, Any]:
        """Get configuration as dictionary.
        
        Returns:
            Configuration dictionary
        """
        return self.config.copy()
    
    @classmethod
    def create_default_config(cls, project_path: str) -> str:
        """Create default configuration file in project directory.
        
        Args:
            project_path: Path to project directory
            
        Returns:
            Path to created config file
        """
        config_path = os.path.join(project_path, ".tkxrc.json")
        config = cls()
        config.save_to_file(config_path)
        return config_path


class ProjectTemplate:
    """Project template generator."""
    
    @staticmethod
    def create_basic_template(project_path: str, project_name: str = "tkx_project") -> None:
        """Create basic project template.
        
        Args:
            project_path: Path where to create project
            project_name: Name of the project
        """
        os.makedirs(project_path, exist_ok=True)
        
        # Create main.xml
        main_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Application>
    <Window title="{project_name}" size="400x300" />
    <Label text="Welcome to tkx-compiler!" pack="pady=20" />
    <Button text="Click Me" pack="pady=10" />
</Application>
"""
        with open(os.path.join(project_path, "main.xml"), "w", encoding="utf-8") as f:
            f.write(main_xml)
        
        # Create logic.py
        logic_py = """def button_click():
    print("Button clicked!")
"""
        with open(os.path.join(project_path, "logic.py"), "w", encoding="utf-8") as f:
            f.write(logic_py)
        
        # Create .tkxrc.json
        Config.create_default_config(project_path)
        
        print(f"Project template created at: {project_path}")
    
    @staticmethod
    def create_advanced_template(project_path: str, project_name: str = "advanced_tkx") -> None:
        """Create advanced project template with multiple files.
        
        Args:
            project_path: Path where to create project
            project_name: Name of the project
        """
        os.makedirs(project_path, exist_ok=True)
        
        # Create main.xml
        main_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Application>
    <Window title="{project_name}" size="600x400" />
    <Import module="app_logic" />
    <Import module="helpers" />
    
    <Frame pack="fill=x, padx=10, pady=10">
        <Label text="Advanced tkx Project" pack="pady=10" />
        <Entry pack="pady=5" />
        <Button text="Process" pack="pady=10" command="app_logic.process_input" />
        <Checkbutton text="Enable Feature" pack="pady=5" />
    </Frame>
</Application>
"""
        with open(os.path.join(project_path, "main.xml"), "w", encoding="utf-8") as f:
            f.write(main_xml)
        
        # Create app_logic.py
        app_logic = """def process_input():
    print("Processing input...")
    # Add your logic here
"""
        with open(os.path.join(project_path, "app_logic.py"), "w", encoding="utf-8") as f:
            f.write(app_logic)
        
        # Create helpers.py
        helpers = """def helper_function():
    print("Helper function called")
    return True
"""
        with open(os.path.join(project_path, "helpers.py"), "w", encoding="utf-8") as f:
            f.write(helpers)
        
        # Create .tkxrc.json
        Config.create_default_config(project_path)
        
        print(f"Advanced project template created at: {project_path}")
