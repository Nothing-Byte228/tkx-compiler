"""Builder class for orchestrating the compilation process."""
import os
import shutil
from typing import Optional
from core.xml_parser import XMLCompiler
from core.pyparser_refactored import PyParser
from core.validators import (
    XMLValidator, 
    PythonValidator, 
    ProjectValidator, 
    PathValidator,
    ValidationError
)
from core.logger import get_logger


class CompilerBuilder:
    """Orchestrates the compilation process from XML to standalone Python."""
    
    def __init__(self, project_path: str, output_file: str = "program.py", 
                 verbose: bool = False):
        """Initialize compiler builder.
        
        Args:
            project_path: Path to project directory
            output_file: Name of output file
            verbose: Enable detailed logging
        """
        self.project_path = project_path
        self.output_file = output_file
        self.verbose = verbose
        self.dist_path = f"{project_path}/dist"
        self.packages_path = f"{self.dist_path}/packages"
        self.main_xml_path = f"{project_path}/main.xml"
        self.logger = get_logger()
        
        if verbose:
            self.logger.configure("DEBUG")
    
    def validate_project_structure(self) -> bool:
        """Validate that project structure is correct.
        
        Returns:
            True if structure is valid, False otherwise
        """
        is_valid, errors = ProjectValidator.validate_project_structure(self.project_path)
        if not is_valid:
            for error in errors:
                self.logger.error(f"Validation error: {error}")
            return False
        return True
    
    def create_output_structure(self) -> None:
        """Create output directory structure."""
        os.makedirs(self.packages_path, exist_ok=True)
    
    def read_xml_source(self) -> str:
        """Read and validate XML source code.
        
        Returns:
            XML source code as string
            
        Raises:
            ValidationError: If XML validation fails
            FileNotFoundError: If XML file doesn't exist
            IOError: If file cannot be read
        """
        # Validate XML file
        is_valid, error_msg = XMLValidator.validate_xml_file(self.main_xml_path)
        if not is_valid:
            raise ValidationError(f"XML file validation failed: {error_msg}")
        
        with open(self.main_xml_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Validate XML structure
        is_valid, error_msg = XMLValidator.validate_xml_structure(content)
        if not is_valid:
            raise ValidationError(f"XML structure validation failed: {error_msg}")
        
        return content
    
    def compile_xml_to_python(self, xml_code: str) -> str:
        """Compile XML markup to Python code.
        
        Args:
            xml_code: XML source code
            
        Returns:
            Compiled Python code
        """
        compiler = XMLCompiler()
        return compiler.compile(xml_code)
    
    def copy_user_modules(self, compiler: XMLCompiler) -> set:
        """Copy user-defined Python modules to packages directory with validation.
        
        Args:
            compiler: XMLCompiler instance that may have user_files attribute
            
        Returns:
            Set of copied module names
        """
        local_modules = set()
        if hasattr(compiler, 'user_files'):
            for module_name in compiler.user_files:
                # Sanitize module name for security
                safe_module_name = PathValidator.sanitize_filename(module_name)
                src_file = os.path.join(self.project_path, f"{safe_module_name}.py")
                dist_file = os.path.join(self.packages_path, f"{safe_module_name}.py")
                
                # Validate path safety
                if not PathValidator.is_safe_path(self.project_path, src_file):
                    self.logger.warning(f"Unsafe path detected for module: {module_name}")
                    continue
                
                if os.path.exists(src_file):
                    # Validate Python file syntax
                    is_valid, error_msg = PythonValidator.validate_python_file(src_file)
                    if not is_valid:
                        self.logger.warning(f"Skipping invalid Python file {module_name}.py: {error_msg}")
                        continue
                    
                    try:
                        shutil.copy2(src_file, dist_file)
                        local_modules.add(safe_module_name)
                        self.logger.info(f"Copied logic file: {safe_module_name}.py")
                    except Exception as e:
                        self.logger.warning(f"Failed to copy {module_name}.py: {e}")
                else:
                    self.logger.warning(f"Logic file not found: {src_file}")
        
        return local_modules
    
    def process_dependencies(self, python_code: str, local_modules: set) -> str:
        """Process and copy all dependencies to packages directory with error handling.
        
        Args:
            python_code: Python source code with imports
            local_modules: Set of local module names to skip
            
        Returns:
            Python code with modified imports
            
        Raises:
            ValidationError: If dependency processing fails
        """
        try:
            parser = PyParser(python_code)
            imports = parser.get_imports()
            
            for module in imports:
                if module in local_modules:
                    self.logger.info(f"Checking dependencies for logic file: {module}.py")
                    try:
                        safe_module_name = PathValidator.sanitize_filename(module)
                        user_module_path = os.path.join(self.project_path, f"{safe_module_name}.py")
                        
                        # Validate path safety
                        if not PathValidator.is_safe_path(self.project_path, user_module_path):
                            self.logger.warning(f"Unsafe path detected for module: {module}")
                            continue
                        
                        # Validate Python file
                        is_valid, error_msg = PythonValidator.validate_python_file(user_module_path)
                        if not is_valid:
                            self.logger.warning(f"Skipping invalid Python file {module}.py: {error_msg}")
                            continue
                        
                        with open(user_module_path, "r", encoding="utf-8") as mf:
                            mcode = mf.read()
                        
                        mparser = PyParser(mcode)
                        sub_imports = mparser.get_imports()
                        
                        for sub_mod in sub_imports:
                            parser.add_import_recursive(sub_mod, self.packages_path, verbose=self.verbose)
                    except Exception as e:
                        self.logger.error(f"Error checking dependencies for file {module}.py: {e}")
                    continue
                    
                parser.add_import_recursive(module, self.packages_path, verbose=self.verbose)
            
            parser.modify_imports()
            return parser.get_code()
            
        except Exception as e:
            raise ValidationError(f"Dependency processing failed: {e}")
    
    def write_output(self, final_code: str) -> str:
        """Write final compiled code to output file.
        
        Args:
            final_code: Final Python code to write
            
        Returns:
            Path to output file
        """
        output_filepath = f"{self.dist_path}/{self.output_file}"
        with open(output_filepath, "w", encoding="utf-8") as py:
            py.write(final_code)
        return output_filepath
    
    def build(self) -> Optional[str]:
        """Execute the complete build process with comprehensive error handling.
        
        Returns:
            Path to output file if successful, None otherwise
        """
        self.logger.info(f"Starting build for project: {self.project_path}")
        
        # Validate project structure
        if not self.validate_project_structure():
            return None
        
        # Create output structure
        try:
            self.create_output_structure()
        except Exception as e:
            self.logger.error(f"Error creating output structure: {e}")
            return None
        
        try:
            # Read and compile XML
            xml_code = self.read_xml_source()
            python_code = self.compile_xml_to_python(xml_code)
            
            # Re-instantiate compiler to get user files
            compiler = XMLCompiler()
            compiler.compile(xml_code)
            local_modules = self.copy_user_modules(compiler)
            
            # Process dependencies
            final_code = self.process_dependencies(python_code, local_modules)
            
            # Write output
            output_path = self.write_output(final_code)
            self.logger.info(f"Build completed. Result saved to: {output_path}")
            return output_path
            
        except ValidationError as e:
            self.logger.error(f"Validation error: {e.message}")
            if e.details:
                self.logger.error(f"Details: {e.details}")
            return None
        except FileNotFoundError as e:
            self.logger.error(f"File not found error: {e}")
            return None
        except PermissionError as e:
            self.logger.error(f"Permission error: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Unexpected build error: {e}", exc_info=True)
            return None
