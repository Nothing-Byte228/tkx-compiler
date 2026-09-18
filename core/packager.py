"""Module for packaging applications into executables."""
import os
import sys
import subprocess
from typing import Optional, List
from pathlib import Path
from core.logger import get_logger


class AppPackager:
    """Package compiled Python applications into executables."""
    
    def __init__(self, project_path: str, dist_path: Optional[str] = None):
        """Initialize app packager.
        
        Args:
            project_path: Path to project directory
            dist_path: Path to distribution directory
        """
        self.project_path = project_path
        self.dist_path = dist_path or os.path.join(project_path, "dist")
        self.logger = get_logger()
    
    def check_pyinstaller(self) -> bool:
        """Check if PyInstaller is available.
        
        Returns:
            True if PyInstaller is available, False otherwise
        """
        try:
            import PyInstaller
            self.logger.info("PyInstaller is available")
            return True
        except ImportError:
            self.logger.warning("PyInstaller is not installed")
            return False
    
    def install_pyinstaller(self) -> bool:
        """Install PyInstaller.
        
        Returns:
            True if installation succeeded, False otherwise
        """
        try:
            self.logger.info("Installing PyInstaller...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
            self.logger.info("PyInstaller installed successfully")
            return True
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to install PyInstaller: {e}")
            return False
    
    def create_spec_file(self, script_path: str, output_name: str, 
                        icon_path: Optional[str] = None,
                        hidden_imports: Optional[List[str]] = None) -> str:
        """Create PyInstaller spec file.
        
        Args:
            script_path: Path to Python script
            output_name: Name of output executable
            icon_path: Optional path to icon file
            hidden_imports: Optional list of hidden imports
            
        Returns:
            Path to created spec file
        """
        spec_content = f'''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['{script_path}'],
    pathex=['{self.project_path}'],
    binaries=[],
    datas=[],
    hiddenimports={hidden_imports or []},
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='{output_name}',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    {f'icon=["{icon_path}"]' if icon_path else ''}
)
'''
        
        spec_path = os.path.join(self.dist_path, f"{output_name}.spec")
        with open(spec_path, 'w', encoding='utf-8') as f:
            f.write(spec_content)
        
        self.logger.info(f"Created spec file: {spec_path}")
        return spec_path
    
    def package_to_exe(self, script_path: str, output_name: str = "app",
                      icon_path: Optional[str] = None,
                      one_file: bool = True,
                      windowed: bool = False,
                      hidden_imports: Optional[List[str]] = None) -> Optional[str]:
        """Package Python script to executable.
        
        Args:
            script_path: Path to Python script
            output_name: Name of output executable
            icon_path: Optional path to icon file
            one_file: Create single file executable
            windowed: Create windowed (no console) executable
            hidden_imports: Optional list of hidden imports
            
        Returns:
            Path to created executable or None if failed
        """
        if not self.check_pyinstaller():
            if not self.install_pyinstaller():
                self.logger.error("Cannot package without PyInstaller")
                return None
        
        try:
            # Create spec file
            spec_path = self.create_spec_file(script_path, output_name, icon_path, hidden_imports)
            
            # Build PyInstaller command
            cmd = [sys.executable, "-m", "PyInstaller"]
            
            if one_file:
                cmd.append("--onefile")
            else:
                cmd.append("--onedir")
            
            if windowed:
                cmd.append("--noconsole")
            
            if icon_path and os.path.exists(icon_path):
                cmd.extend(["--icon", icon_path])
            
            cmd.extend(["--distpath", self.dist_path])
            cmd.extend(["--workpath", os.path.join(self.dist_path, "build")])
            cmd.append(spec_path)
            
            self.logger.info(f"Running PyInstaller: {' '.join(cmd)}")
            
            # Run PyInstaller
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                self.logger.error(f"PyInstaller failed: {result.stderr}")
                return None
            
            # Determine output path
            if one_file:
                exe_path = os.path.join(self.dist_path, f"{output_name}.exe")
            else:
                exe_path = os.path.join(self.dist_path, output_name, f"{output_name}.exe")
            
            if os.path.exists(exe_path):
                self.logger.info(f"Successfully created executable: {exe_path}")
                return exe_path
            else:
                self.logger.error("Executable not found after packaging")
                return None
                
        except Exception as e:
            self.logger.error(f"Error during packaging: {e}", exc_info=True)
            return None
    
    def package_with_auto_detect(self, script_path: str, output_name: str = "app") -> Optional[str]:
        """Package with automatic detection of settings.
        
        Args:
            script_path: Path to Python script
            output_name: Name of output executable
            
        Returns:
            Path to created executable or None if failed
        """
        # Detect if it's a GUI application (has tkinter import)
        with open(script_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        is_gui = 'tkinter' in content.lower()
        
        # Auto-detect hidden imports from packages directory
        packages_dir = os.path.join(self.dist_path, "packages")
        hidden_imports = []
        
        if os.path.exists(packages_dir):
            for item in os.listdir(packages_dir):
                if os.path.isdir(os.path.join(packages_dir, item)):
                    hidden_imports.append(item)
        
        return self.package_to_exe(
            script_path=script_path,
            output_name=output_name,
            one_file=True,
            windowed=is_gui,
            hidden_imports=hidden_imports
        )
    
    def clean_build_artifacts(self) -> None:
        """Clean build artifacts."""
        build_dir = os.path.join(self.dist_path, "build")
        spec_files = [f for f in os.listdir(self.dist_path) if f.endswith(".spec")]
        
        if os.path.exists(build_dir):
            import shutil
            shutil.rmtree(build_dir)
            self.logger.info(f"Removed build directory: {build_dir}")
        
        for spec_file in spec_files:
            os.remove(os.path.join(self.dist_path, spec_file))
            self.logger.info(f"Removed spec file: {spec_file}")