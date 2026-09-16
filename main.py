import os
import shutil
import argparse
from core.pyparser import PyParser
from core.xml_parser import XMLCompiler

def main():
    # 1. Настраиваем argparse для консоли сборщика
    cli_parser = argparse.ArgumentParser(
        description="tkx-compiler: Build zero-dependency Python GUI apps from XML markup."
    )
    
    # Позиционный аргумент: путь к папке проекта (обязательный)
    cli_parser.add_argument(
        "project_path", 
        help="Path to the directory containing your main.xml file"
    )
    
    # Именованный аргумент: имя выходного файла (по умолчанию program.py)
    cli_parser.add_argument(
        "-o", "--output", 
        default="program.py", 
        help="Name of the compiled output Python file (default: program.py)"
    )
    
    # Флаг: включать ли подробные логи рекурсивного сборщика пакетов
    cli_parser.add_argument(
        "-v", "--verbose", 
        action="store_true", 
        help="Show detailed logs during recursive dependency extraction"
    )

    # Разбираем переданные в терминале аргументы
    args = cli_parser.parse_args()

    PROJ_PATH = args.project_path
    DIST_PATH = f"{PROJ_PATH}/dist"
    PACKAGES_PATH = f"{DIST_PATH}/packages"
    MAIN_XML_PATH = f"{PROJ_PATH}/main.xml"

    # Проверяем, существует ли папка проекта и главный файл
    if not os.path.exists(MAIN_XML_PATH):
        print(f"Ошибка: файл main.xml не найден по пути: {MAIN_XML_PATH}")
        return

    print(f"Начинаю сборку проекта: {PROJ_PATH}")
    
    # 2. Создаем структуру папок на диске
    os.makedirs(PACKAGES_PATH, exist_ok=True)

    # 3. Читаем XML-разметку
    with open(MAIN_XML_PATH, "r", encoding="utf-8") as f:
        code = f.read()

    # 4. Транслируем Lua в Python AST
    compiler = XMLCompiler()
    done_code = compiler.compile(code)

    # 5. Копируем локальные файлы логики пользователя прямо в папку packages
    local_modules = set()
    if hasattr(compiler, 'user_files'):
        for module_name in compiler.user_files:
            src_file = f"{PROJ_PATH}/{module_name}.py"
            dist_file = f"{PACKAGES_PATH}/{module_name}.py"
            
            if os.path.exists(src_file):
                shutil.copy2(src_file, dist_file)
                local_modules.add(module_name)
                print(f"Скопирован файл логики: {module_name}.py")
            else:
                print(f"Предупреждение: файл логики не найден: {src_file}")

    # 6. Собираем внешние библиотеки и генерируем финальный код
    output_filepath = f"{DIST_PATH}/{args.output}"
    
    with open(output_filepath, "w", encoding="utf-8") as py:
        parser = PyParser(done_code)
        imports = parser.get_imports()
        
        for module in imports:
            if module in local_modules:
                print(f"Проверяю зависимости файла логики: {module}.py")
                try:
                    user_module_path = f"{PROJ_PATH}/{module}.py"
                    with open(user_module_path, "r", encoding="utf-8") as mf:
                        mcode = mf.read()
                    
                    mparser = PyParser(mcode)
                    sub_imports = mparser.get_imports()
                    
                    for sub_mod in sub_imports:
                        # Передаем флаг verbose из аргументов консоли!
                        parser.add_import_recursive(sub_mod, PACKAGES_PATH, verbose=args.verbose)
                except Exception as e:
                    print(f"Ошибка при проверке зависимостей файла {module}.py: {e}")
                continue
                
            # Передаем флаг verbose из аргументов консоли!
            parser.add_import_recursive(module, PACKAGES_PATH, verbose=args.verbose)
            
        # Переписываем импорты
        parser.modify_imports()

        # Записываем готовый скрипт
        py.write(parser.get_code())

    print(f"Сборка завершена. Результат сохранён в: {output_filepath}")

if __name__ == "__main__":
    main()
