import os
import sys
import ast
import shutil
import sysconfig
import importlib.util

# Get absolute paths to the Python Standard Library
STDLIB_PATH = os.path.normpath(sysconfig.get_path("stdlib")).lower()
PLATSTDLIB_PATH = os.path.normpath(sysconfig.get_path("platstdlib")).lower()

class PyParser:
    def __init__(self, source_code):
        self.tree = ast.parse(source=source_code)

    def get_syntax_tree(self) -> str:
        return ast.dump(self.tree, indent=4)

    def get_code(self) -> str:
        return ast.unparse(self.tree)

    def get_imports(self) -> list:
        """Extracts names of imported modules."""
        imports = []
        for node in ast.walk(self.tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imports.append(node.module)
        return imports

    def is_standard_library(self, import_name: str) -> bool:
        """Checks if a module is part of the Python Standard Library."""
        base_name = import_name.split('.')[0]
        
        if base_name in sys.builtin_module_names:
            return True
            
        try:
            spec = importlib.util.find_spec(base_name)
            if spec is not None and spec.origin:
                origin_path = os.path.normpath(spec.origin).lower()
                if origin_path.startswith(STDLIB_PATH) or origin_path.startswith(PLATSTDLIB_PATH):
                    if "site-packages" not in origin_path:
                        return True
        except Exception:
            return False
            
        return False

    def add_import(self, import_name: str, dist_path: str = "packages", verbose: bool = False) -> str | None:
        """Copies a third-party module to the destination directory."""
        base_name = import_name.split('.')[0]

        if self.is_standard_library(import_name):
            if verbose: print(f"[SKIP] '{import_name}' is a standard library module.")
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
            print(f"Package '{base_name}' -> {destination}")
            return os.path.join(destination, "__init__.py")
        else:
            destination = os.path.join(dist_path, os.path.basename(origin_path))
            if os.path.exists(destination):
                return destination
                
            shutil.copy2(origin_path, destination)
            print(f"Module file '{base_name}' -> {destination}")
            return destination

    def add_import_recursive(self, import_name: str, dist_path: str = "packages", processed_modules: set = None, verbose: bool = False):
        """Recursively extracts a module and ALL its external dependencies."""
        if processed_modules is None:
            processed_modules = set()

        base_module_name = import_name.split('.')[0]

        if self.is_standard_library(base_module_name):
            return

        if base_module_name in processed_modules:
            return
        
        processed_modules.add(base_module_name)

        # 1. Copy the module itself
        copied_file_path = self.add_import(base_module_name, dist_path, verbose=verbose)

        if copied_file_path:
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

            # 2. Scan found files for sub-dependencies
            for file_path in files_to_scan:
                try:
                    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                        sub_code = f.read()

                    sub_parser = PyParser(sub_code)
                    sub_imports = sub_parser.get_imports()

                    for sub_imp in sub_imports:
                        sub_base = sub_imp.split('.')[0]
                        if sub_base == base_module_name or sub_base == '':
                            continue
                            
                        self.add_import_recursive(sub_imp, dist_path, processed_modules, verbose=verbose)
                except Exception:
                    continue

    def get_functions(self) -> dict:
        functions = {}
        for node in ast.walk(self.tree):
            if isinstance(node, ast.FunctionDef):
                functions[node.name] = ast.unparse(node)
        return functions

    def modify_imports(self):
        """
        Transforms third-party imports using AST matching:
        - import requests -> import packages.requests as requests
        - import requests.auth -> import packages.requests as requests
        - from flask import Flask -> from packages.flask import Flask
        """
        print("Rewriting import nodes to direct 'packages.' paths...")

        class ImportPathRewriter(ast.NodeTransformer):
            def visit_Import(self, node):
                for alias in node.names:
                    # Извлекаем корневое имя (из 'requests.auth' -> 'requests')
                    root_name = alias.name.split('.')[0]
                    
                    # Игнорируем встроенные системные модули (math, sys, os)
                    if hasattr(self, 'outer_parser') and self.outer_parser.is_standard_library(root_name):
                        continue
                        
                    # КРИТИЧЕСКИЙ ФИКС: asname должен быть строго корневым (без точек!)
                    # Чтобы вместо 'as requests.auth' (ошибка) было 'as requests'
                    alias.asname = root_name
                    
                    # Переписываем путь импорта на корневую папку packages
                    alias.name = f"packages.{root_name}"
                    print(f"import {root_name} -> import packages.{root_name} as {root_name}")
                return node

            def visit_ImportFrom(self, node):
                if not node.module:
                    return node
                    
                # Извлекаем корневое имя модуля (из 'urllib3.exceptions' -> 'urllib3')
                root_module = node.module.split('.')[0]
                
                # Игнорируем стандартную библиотеку
                if hasattr(self, 'outer_parser') and self.outer_parser.is_standard_library(root_module):
                    return node

                # Переписываем модуль, указывая на корень в packages
                node.module = f"packages.{root_module}"
                print(f"from {root_module} import ... -> from packages.{root_module} import ...")
                return node

        # Инициализируем трансформер и связываем его с внешним парсером
        rewriter = ImportPathRewriter()
        rewriter.outer_parser = self
        
        # Запускаем модификацию дерева
        self.tree = rewriter.visit(self.tree)
        
        # Фиксируем координаты измененных узлов
        ast.fix_missing_locations(self.tree)
        print("Import paths have been successfully hardcoded to the 'packages' directory.")
