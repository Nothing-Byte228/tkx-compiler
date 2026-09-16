import ast
from lupa import LuaRuntime

class Lua(LuaRuntime):
    def __init__(self):
        print("Инициализирую среду выполнения Lua...")
        super().__init__()
        
        # Корневое дерево Python AST
        self.final_body = [
            ast.Import(names=[ast.alias(name='tkinter', asname='tk')])
        ]
        
        # Инициализируем счётчики для каждого типа виджета
        self.widget_counts = {}
        # Список для пользовательских файлов Python (логики)
        self.user_files = []
        
        self._setup_lua_environment()

    def _generate_widget_name(self, prefix: str) -> str:
        """Generates a unique variable name for a widget (e.g., btn_1, entry_2)."""
        self.widget_counts[prefix] = self.widget_counts.get(prefix, 0) + 1
        return f"{prefix}_{self.widget_counts[prefix]}"

    def _parse_pack_args(self, pack_str: str) -> list:
        """Helper to convert a string like 'pady=20, fill=x' into AST keyword nodes."""
        keywords = []
        if not pack_str or not isinstance(pack_str, str):
            return keywords
            
        # Разделяем аргументы по запятой
        pairs = pack_str.split(",")
        for pair in pairs:
            if "=" in pair:
                key, val = pair.split("=")
                key = key.strip()
                val = val.strip().strip("'").strip('"') # Очищаем от кавычек
                
                # Пробуем понять, число это или строка
                if val.isdigit():
                    ast_val = ast.Constant(value=int(val))
                else:
                    ast_val = ast.Constant(value=val)
                    
                keywords.append(ast.keyword(arg=key, value=ast_val))
        return keywords

    def _setup_lua_environment(self):
        print("Подключаю элементы графического интерфейса к Lua...")
        lua_globals = self.globals()

        # 1. СИСТЕМНЫЕ ФУНКЦИИ
        def lua_window(title, size):
            print(f"Создаю окно «{title}» размером {size}")
            window_nodes = [
                ast.Assign(targets=[ast.Name(id='root', ctx=ast.Store())], 
                           value=ast.Call(func=ast.Attribute(value=ast.Name(id='tk', ctx=ast.Load()), attr='Tk', ctx=ast.Load()), args=[], keywords=[])),
                ast.Expr(value=ast.Call(func=ast.Attribute(value=ast.Name(id='root', ctx=ast.Load()), attr='title', ctx=ast.Load()), args=[ast.Constant(value=title)], keywords=[])),
                ast.Expr(value=ast.Call(func=ast.Attribute(value=ast.Name(id='root', ctx=ast.Load()), attr='geometry', ctx=ast.Load()), args=[ast.Constant(value=size)], keywords=[]))
            ]
            self.final_body.extend(window_nodes)

        def lua_require(module_name):
            print(f"Подключаю модуль: {module_name}")
            self.final_body.append(ast.Import(names=[ast.alias(name=module_name, asname=None)]))

        def lua_import_python(module_name):
            print(f"Подключаю файл логики: {module_name}.py")
            self.final_body.append(ast.Import(names=[ast.alias(name=module_name, asname=None)]))
            self.user_files.append(module_name)

        # 2. ПРОКАЧАННЫЕ ВИДЖЕТЫ ИНТЕРФЕЙСА
        
        # Кнопка (Button) с поддержкой колбэков событий (третий аргумент)
        def lua_button(text, pack_args="", command_func=""):
            w_name = self._generate_widget_name("btn")
            print(f"Создаю кнопку: «{text}»")
            
            # Собираем параметры кнопки
            btn_keywords = [ast.keyword(arg='text', value=ast.Constant(value=text))]
            if command_func:
                if "." in command_func:
                    mod, func = command_func.split(".")
                    func_node = ast.Attribute(value=ast.Name(id=mod, ctx=ast.Load()), attr=func, ctx=ast.Load())
                else:
                    func_node = ast.Name(id=command_func, ctx=ast.Load())
                btn_keywords.append(ast.keyword(arg='command', value=func_node))

            # Создание и упаковка виджета в AST
            self.final_body.append(ast.Assign(
                targets=[ast.Name(id=w_name, ctx=ast.Store())],
                value=ast.Call(func=ast.Attribute(value=ast.Name(id='tk', ctx=ast.Load()), attr='Button', ctx=ast.Load()), args=[ast.Name(id='root', ctx=ast.Load())], keywords=btn_keywords)
            ))
            self.final_body.append(ast.Expr(
                value=ast.Call(func=ast.Attribute(value=ast.Name(id=w_name, ctx=ast.Load()), attr='pack', ctx=ast.Load()), args=[], keywords=self._parse_pack_args(pack_args))
            ))

        # Текстовая метка (Label)
        def lua_label(text, pack_args=""):
            w_name = self._generate_widget_name("lbl")
            print(f"Создаю текстовую метку: «{text}»")
            self.final_body.append(ast.Assign(
                targets=[ast.Name(id=w_name, ctx=ast.Store())],
                value=ast.Call(func=ast.Attribute(value=ast.Name(id='tk', ctx=ast.Load()), attr='Label', ctx=ast.Load()), args=[ast.Name(id='root', ctx=ast.Load())], keywords=[ast.keyword(arg='text', value=ast.Constant(value=text))])
            ))
            self.final_body.append(ast.Expr(
                value=ast.Call(func=ast.Attribute(value=ast.Name(id=w_name, ctx=ast.Load()), attr='pack', ctx=ast.Load()), args=[], keywords=self._parse_pack_args(pack_args))
            ))

        # Однострочное поле ввода (Entry)
        def lua_entry(pack_args=""):
            w_name = self._generate_widget_name("entry")
            print("Создаю поле ввода")
            self.final_body.append(ast.Assign(
                targets=[ast.Name(id=w_name, ctx=ast.Store())],
                value=ast.Call(func=ast.Attribute(value=ast.Name(id='tk', ctx=ast.Load()), attr='Entry', ctx=ast.Load()), args=[ast.Name(id='root', ctx=ast.Load())], keywords=[])
            ))
            self.final_body.append(ast.Expr(
                value=ast.Call(func=ast.Attribute(value=ast.Name(id=w_name, ctx=ast.Load()), attr='pack', ctx=ast.Load()), args=[], keywords=self._parse_pack_args(pack_args))
            ))

        # Многострочный текстовый блок (Text)
        def lua_text(height=10, pack_args=""):
            w_name = self._generate_widget_name("text")
            print(f"Создаю многострочное поле высотой {height}")
            self.final_body.append(ast.Assign(
                targets=[ast.Name(id=w_name, ctx=ast.Store())],
                value=ast.Call(func=ast.Attribute(value=ast.Name(id='tk', ctx=ast.Load()), attr='Text', ctx=ast.Load()), args=[ast.Name(id='root', ctx=ast.Load())], keywords=[ast.keyword(arg='height', value=ast.Constant(value=int(height)))])
            ))
            self.final_body.append(ast.Expr(
                value=ast.Call(func=ast.Attribute(value=ast.Name(id=w_name, ctx=ast.Load()), attr='pack', ctx=ast.Load()), args=[], keywords=self._parse_pack_args(pack_args))
            ))

        # Чекбокс (Checkbutton)
        def lua_checkbox(text, pack_args=""):
            w_name = self._generate_widget_name("check")
            print(f"Создаю флажок: «{text}»")
            self.final_body.append(ast.Assign(
                targets=[ast.Name(id=w_name, ctx=ast.Store())],
                value=ast.Call(func=ast.Attribute(value=ast.Name(id='tk', ctx=ast.Load()), attr='Checkbutton', ctx=ast.Load()), args=[ast.Name(id='root', ctx=ast.Load())], keywords=[ast.keyword(arg='text', value=ast.Constant(value=text))])
            ))
            self.final_body.append(ast.Expr(
                value=ast.Call(func=ast.Attribute(value=ast.Name(id=w_name, ctx=ast.Load()), attr='pack', ctx=ast.Load()), args=[], keywords=self._parse_pack_args(pack_args))
            ))

        # Привязываем функции к глобальной среде Lua
        lua_globals.Window = lua_window
        lua_globals.Require = lua_require
        lua_globals.ImportPython = lua_import_python
        lua_globals.Button = lua_button
        lua_globals.Label = lua_label
        lua_globals.Entry = lua_entry
        lua_globals.Text = lua_text
        lua_globals.Checkbox = lua_checkbox

    def compile(self, lua_code: str) -> str:
        print("Компилирую Lua-код...")
        self.execute(lua_code)
        
        mainloop_node = ast.Expr(value=ast.Call(
            func=ast.Attribute(value=ast.Name(id='root', ctx=ast.Load()), attr='mainloop', ctx=ast.Load()),
            args=[], keywords=[]
        ))
        self.final_body.append(mainloop_node)
        
        full_tree = ast.Module(body=self.final_body, type_ignores=[])
        ast.fix_missing_locations(full_tree)
        return ast.unparse(full_tree)
