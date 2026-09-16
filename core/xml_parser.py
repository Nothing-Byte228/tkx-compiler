import ast
import xml.etree.ElementTree as ElementTree


class XMLCompiler:
    WIDGETS = {
        "Button": ("Button", "button"),
        "Canvas": ("Canvas", "canvas"),
        "Checkbutton": ("Checkbutton", "checkbutton"),
        "Checkbox": ("Checkbutton", "check"),
        "Combobox": ("ttk.Combobox", "combobox"),
        "Entry": ("Entry", "entry"),
        "Frame": ("Frame", "frame"),
        "Label": ("Label", "label"),
        "LabelFrame": ("LabelFrame", "labelframe"),
        "Listbox": ("Listbox", "listbox"),
        "Message": ("Message", "message"),
        "PanedWindow": ("PanedWindow", "panedwindow"),
        "Radiobutton": ("Radiobutton", "radiobutton"),
        "Scale": ("Scale", "scale"),
        "Scrollbar": ("Scrollbar", "scrollbar"),
        "Spinbox": ("Spinbox", "spinbox"),
        "Text": ("Text", "text"),
        "Menubutton": ("Menubutton", "menubutton"),
        "Menu": ("Menu", "menu"),
        "TtkButton": ("ttk.Button", "ttk_button"),
        "TtkCheckbutton": ("ttk.Checkbutton", "ttk_checkbutton"),
        "TtkCombobox": ("ttk.Combobox", "ttk_combobox"),
        "TtkEntry": ("ttk.Entry", "ttk_entry"),
        "TtkFrame": ("ttk.Frame", "ttk_frame"),
        "TtkLabel": ("ttk.Label", "ttk_label"),
        "TtkLabelFrame": ("ttk.LabelFrame", "ttk_labelframe"),
        "TtkNotebook": ("ttk.Notebook", "ttk_notebook"),
        "TtkPanedWindow": ("ttk.Panedwindow", "ttk_panedwindow"),
        "TtkProgressbar": ("ttk.Progressbar", "ttk_progressbar"),
        "TtkRadiobutton": ("ttk.Radiobutton", "ttk_radiobutton"),
        "TtkScale": ("ttk.Scale", "ttk_scale"),
        "TtkScrollbar": ("ttk.Scrollbar", "ttk_scrollbar"),
        "TtkSeparator": ("ttk.Separator", "ttk_separator"),
        "TtkSizegrip": ("ttk.Sizegrip", "ttk_sizegrip"),
        "TtkSpinbox": ("ttk.Spinbox", "ttk_spinbox"),
        "TtkTreeview": ("ttk.Treeview", "ttk_treeview"),
    }

    def __init__(self):
        print("Инициализирую XML-компилятор...")
        self.final_body = [
            ast.Import(names=[ast.alias(name="tkinter", asname="tk")])
        ]
        self.ttk_imported = False
        self.widget_counts = {}
        self.user_files = []

    def _generate_widget_name(self, prefix: str) -> str:
        self.widget_counts[prefix] = self.widget_counts.get(prefix, 0) + 1
        return f"{prefix}_{self.widget_counts[prefix]}"

    def _parse_pack_args(self, pack_args: str) -> list:
        keywords = []
        for key, value in self._parse_attributes(pack_args).items():
            if value.isdigit():
                ast_value = ast.Constant(value=int(value))
            else:
                ast_value = ast.Constant(value=value)
            keywords.append(ast.keyword(arg=key, value=ast_value))
        return keywords

    def _parse_attributes(self, attributes: str) -> dict:
        if not attributes:
            return {}
        parsed_attributes = {}
        for item in attributes.split(","):
            if "=" in item:
                key, value = item.split("=", 1)
                parsed_attributes[key.strip()] = value.strip()
        return parsed_attributes

    def _pack_keywords(self, element: ElementTree.Element) -> list:
        pack_args = element.attrib.get("pack", "")
        return self._parse_pack_args(pack_args)

    def _value_node(self, value: str) -> ast.Constant:
        if value.lower() == "true":
            return ast.Constant(value=True)
        if value.lower() == "false":
            return ast.Constant(value=False)
        if value.isdigit():
            return ast.Constant(value=int(value))
        try:
            return ast.Constant(value=float(value))
        except ValueError:
            return ast.Constant(value=value)

    def _widget_keywords(self, element: ElementTree.Element) -> list:
        keywords = []
        for key, value in element.attrib.items():
            if key in {"pack", "name", "id", "command"}:
                continue
            keywords.append(ast.keyword(arg=key, value=self._value_node(value)))

        command = element.attrib.get("command", "")
        if command:
            if "." in command:
                module_name, function_name = command.split(".", 1)
                function_node = ast.Attribute(
                    value=ast.Name(id=module_name, ctx=ast.Load()),
                    attr=function_name,
                    ctx=ast.Load(),
                )
            else:
                function_node = ast.Name(id=command, ctx=ast.Load())
            keywords.append(ast.keyword(arg="command", value=function_node))
        return keywords

    def _widget_call(self, element: ElementTree.Element, widget_type: str, prefix: str, keywords: list) -> None:
        module_name = "tk"
        if widget_type.startswith("ttk."):
            module_name = "ttk"
            widget_type = widget_type.removeprefix("ttk.")
            if not self.ttk_imported:
                self.final_body.insert(
                    1,
                    ast.Import(names=[ast.alias(name="tkinter.ttk", asname="ttk")]),
                )
                self.ttk_imported = True
        widget_name = self._generate_widget_name(prefix)
        print(f"Создаю элемент {element.tag.lower()}: {element.attrib.get('text', '')}".rstrip())
        self.final_body.append(ast.Assign(
            targets=[ast.Name(id=widget_name, ctx=ast.Store())],
            value=ast.Call(
                func=ast.Attribute(
                    value=ast.Name(id=module_name, ctx=ast.Load()),
                    attr=widget_type,
                    ctx=ast.Load(),
                ),
                args=[ast.Name(id="root", ctx=ast.Load())],
                keywords=keywords,
            ),
        ))
        self.final_body.append(ast.Expr(
            value=ast.Call(
                func=ast.Attribute(
                    value=ast.Name(id=widget_name, ctx=ast.Load()),
                    attr="pack",
                    ctx=ast.Load(),
                ),
                args=[],
                keywords=self._pack_keywords(element),
            )
        ))

    def _compile_element(self, element: ElementTree.Element) -> None:
        tag = element.tag

        if tag == "Toplevel":
            print("Создаю дополнительное окно")
            window_name = self._generate_widget_name("window")
            self.final_body.append(ast.Assign(
                targets=[ast.Name(id=window_name, ctx=ast.Store())],
                value=ast.Call(
                    func=ast.Attribute(
                        value=ast.Name(id="tk", ctx=ast.Load()),
                        attr="Toplevel",
                        ctx=ast.Load(),
                    ),
                    args=[ast.Name(id="root", ctx=ast.Load())],
                    keywords=[],
                ),
            ))
            return

        if tag == "Window":
            title = element.attrib.get("title", "")
            size = element.attrib.get("size", "")
            print(f"Создаю окно «{title}» размером {size}")
            self.final_body.extend([
                ast.Assign(
                    targets=[ast.Name(id="root", ctx=ast.Store())],
                    value=ast.Call(
                        func=ast.Attribute(
                            value=ast.Name(id="tk", ctx=ast.Load()),
                            attr="Tk",
                            ctx=ast.Load(),
                        ),
                        args=[],
                        keywords=[],
                    ),
                ),
                ast.Expr(value=ast.Call(
                    func=ast.Attribute(
                        value=ast.Name(id="root", ctx=ast.Load()),
                        attr="title",
                        ctx=ast.Load(),
                    ),
                    args=[ast.Constant(value=title)],
                    keywords=[],
                )),
                ast.Expr(value=ast.Call(
                    func=ast.Attribute(
                        value=ast.Name(id="root", ctx=ast.Load()),
                        attr="geometry",
                        ctx=ast.Load(),
                    ),
                    args=[ast.Constant(value=size)],
                    keywords=[],
                )),
            ])
            return

        if tag == "Require":
            module_name = element.attrib.get("module", "")
            print(f"Подключаю модуль: {module_name}")
            self.final_body.append(ast.Import(names=[ast.alias(name=module_name, asname=None)]))
            return

        if tag == "Import":
            module_name = element.attrib.get("module", "")
            print(f"Подключаю файл логики: {module_name}.py")
            self.final_body.append(ast.Import(names=[ast.alias(name=module_name, asname=None)]))
            self.user_files.append(module_name)
            return

        if tag in self.WIDGETS:
            widget_type, prefix = self.WIDGETS[tag]
            self._widget_call(
                element,
                widget_type,
                prefix,
                self._widget_keywords(element),
            )
            return

        raise ValueError(f"Неизвестный XML-элемент: {tag}")

    def compile(self, xml_code: str) -> str:
        print("Компилирую XML-разметку...")
        root = ElementTree.fromstring(xml_code)
        elements = list(root) if root.tag == "Application" else [root]
        for element in elements:
            self._compile_element(element)

        self.final_body.append(ast.Expr(value=ast.Call(
            func=ast.Attribute(
                value=ast.Name(id="root", ctx=ast.Load()),
                attr="mainloop",
                ctx=ast.Load(),
            ),
            args=[],
            keywords=[],
        )))
        full_tree = ast.Module(body=self.final_body, type_ignores=[])
        ast.fix_missing_locations(full_tree)
        return ast.unparse(full_tree)
