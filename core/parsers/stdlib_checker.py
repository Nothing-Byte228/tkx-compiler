"""Module for checking if imports are from Python standard library."""
import sys
import sysconfig
import os


class StdlibChecker:
    """Checks if a module is from Python standard library."""
    
    def __init__(self):
        """Initialize with standard library paths."""
        self.stdlib_path = os.path.normpath(sysconfig.get_path("stdlib")).lower()
        self.platstdlib_path = os.path.normpath(sysconfig.get_path("platstdlib")).lower()
    
    def is_standard_library(self, import_name: str) -> bool:
        """Check if import is from standard library.
        
        Args:
            import_name: Name of the module to check
            
        Returns:
            True if module is from standard library, False otherwise
        """
        base_name = import_name.split(".", 1)[0]
        
        if base_name in sys.builtin_module_names:
            return True
        
        if base_name in sys.stdlib_module_names:
            return True
        
        return False
