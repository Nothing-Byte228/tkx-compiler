"""Module for copying Python modules to destination directory."""
import os
import shutil
import importlib.util
from typing import Optional
from core.parsers.stdlib_checker import StdlibChecker
from core.logger import get_logger


class ModuleCopier:
    """Copies Python modules to a destination directory."""
    
    def __init__(self, stdlib_checker: Optional[StdlibChecker] = None):
        """Initialize with optional stdlib checker.
        
        Args:
            stdlib_checker: Optional StdlibChecker instance
        """
        self.stdlib_checker = stdlib_checker or StdlibChecker()
        self.logger = get_logger()
    
    def add_import(self, import_name: str, dist_path: str = "packages", 
                   verbose: bool = False) -> Optional[str]:
        """Copy a third-party module to the destination directory.
        
        Args:
            import_name: Name of the module to copy
            dist_path: Destination directory path
            verbose: Enable detailed logging
            
        Returns:
            Path to the copied file, or None if not copied
        """
        base_name = import_name.split('.')[0]
        
        if self.stdlib_checker.is_standard_library(import_name):
            if verbose:
                self.logger.debug(f"Skipping standard module: {import_name}")
            return None
        
        try:
            spec = importlib.util.find_spec(base_name)
        except Exception:
            return None
        
        if spec is None or not spec.origin:
            return None
        
        origin_path = os.path.normpath(spec.origin)
        os.makedirs(dist_path, exist_ok=True)
        
        if origin_path.endswith("__init__.py"):
            module_dir = os.path.dirname(origin_path)
            destination = os.path.join(dist_path, base_name)
            
            if os.path.exists(destination):
                return os.path.join(destination, "__init__.py")
                
            shutil.copytree(module_dir, destination)
            if verbose:
                self.logger.info(f"Copied package {base_name}: {destination}")
            return os.path.join(destination, "__init__.py")
        else:
            destination = os.path.join(dist_path, os.path.basename(origin_path))
            if os.path.exists(destination):
                return destination
                
            shutil.copy2(origin_path, destination)
            if verbose:
                self.logger.info(f"Copied module {base_name}: {destination}")
            return destination
    
    def add_import_recursive(self, import_name: str, dist_path: str = "packages",
                            processed_modules: Optional[set] = None, 
                            verbose: bool = False) -> None:
        """Recursively extract a module and ALL its external dependencies.
        
        Args:
            import_name: Name of the module to extract
            dist_path: Destination directory path
            processed_modules: Set of already processed modules
            verbose: Enable detailed logging
        """
        if processed_modules is None:
            processed_modules = set()
        
        base_module_name = import_name.split('.')[0]
        
        if self.stdlib_checker.is_standard_library(base_module_name):
            return
        
        if base_module_name in processed_modules:
            return
        
        processed_modules.add(base_module_name)
        
        # Copy the module itself
        copied_file_path = self.add_import(base_module_name, dist_path, verbose=verbose)
        
        if copied_file_path:
            from core.parsers.import_extractor import ImportExtractor
            
            abs_copied_path = os.path.abspath(copied_file_path)
            files_to_scan = []
            
            if abs_copied_path.endswith("__init__.py"):
                module_dir = os.path.dirname(abs_copied_path)
                for root, dirs, files in os.walk(module_dir):
                    for file in files:
                        if file.endswith(".py"):
                            files_to_scan.append(os.path.join(root, file))
            elif abs_copied_path.endswith(".py"):
                files_to_scan.append(abs_copied_path)
            
            # Scan found files for sub-dependencies
            from core.parsers.import_extractor import ImportExtractor
            
            for file_path in files_to_scan:
                try:
                    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                        sub_code = f.read()
                    
                    sub_parser = ImportExtractor(sub_code)
                    sub_imports = sub_parser.get_imports()
                    
                    for sub_imp in sub_imports:
                        sub_base = sub_imp.split('.')[0]
                        if sub_base == base_module_name or sub_base == '':
                            continue
                            
                        self.add_import_recursive(sub_imp, dist_path, processed_modules, verbose=verbose)
                except Exception:
                    continue
