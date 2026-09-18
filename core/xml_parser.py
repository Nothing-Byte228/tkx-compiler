import ast
import keyword
import xml.etree.ElementTree as ElementTree
from typing import Dict, List, Tuple, Optional
from core.logger import get_logger


class XMLCompiler:
    """Compiles XML markup to Python AST for tkinter GUI applications."""
    
    WIDGETS: Dict[str, Tuple[str, str]] = {
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

    def __init__(self) -> None:
        """Initialize XML compiler."""
        self.logger = get_logger()
        self.logger.info("Инициализирую XML-компилятор...")
        self.final_body: List[ast.stmt] = [
            ast.Import(names=[ast.alias(name="tkinter", asname="tk")])
        ]
        self.ttk_imported: bool = False
        self.widget_counts: Dict[str, int] = {}
        self.user_files: List[str] = []

    def _generate_widget_name(self, prefix: str) -> str:
        """Generate a unique widget name.
        
        Args:
            prefix: Widget type prefix
            
        Returns:
            Unique widget name
        """
        self.widget_counts[prefix] = self.widget_counts.get(prefix, 0) + 1
        return f"{prefix}_{self.widget_counts[prefix]}"

    def _parse_pack_args(self, pack_args: str) -> List[ast.keyword]:
        """Parse pack arguments string into AST keyword nodes.
        
        Args:
            pack_args: Pack arguments string
            
        Returns:
            List of AST keyword nodes
        """
        keywords: List[ast.keyword] = []
        for key, value in self._parse_attributes(pack_args).items():
            if value.isdigit():
                ast_value = ast.Constant(value=int(value))
            else:
                ast_value = ast.Constant(value=value)
            keywords.append(ast.keyword(arg=key, value=ast_value))
        return keywords

    def _parse_attributes(self, attributes: str) -> Dict[str, str]:
        """Parse attributes string into dictionary.
        
        Args:
            attributes: Attributes string
            
        Returns:
            Dictionary of attribute key-value pairs
        """
        if not attributes:
            return {}
        parsed_attributes: Dict[str, str] = {}
        for item in attributes.split(","):
            if "=" in item:
                key, value = item.split("=", 1)
                parsed_attributes[key.strip()] = value.strip()
        return parsed_attributes

    def _pack_keywords(self, element: ElementTree.Element) -> List[ast.keyword]:
        """Extract pack keywords from XML element.
        
        Args:
            element: XML element
            
        Returns:
            List of AST keyword nodes for pack
        """
        pack_args = element.attrib.get("pack", "")
        return self._parse_pack_args(pack_args)
    
    def _grid_keywords(self, element: ElementTree.Element) -> List[ast.keyword]:
        """Extract grid keywords from XML element.
        
        Args:
            element: XML element
            
        Returns:
            List of AST keyword nodes for grid
        """
        grid_args = element.attrib.get("grid", "")
        return self._parse_pack_args(grid_args)
    
    def _place_keywords(self, element: ElementTree.Element) -> List[ast.keyword]:
        """Extract place keywords from XML element.
        
        Args:
            element: XML element
            
        Returns:
            List of AST keyword nodes for place
        """
        place_args = element.attrib.get("place", "")
        return self._parse_pack_args(place_args)

    def _value_node(self, value: str) -> ast.Constant:
        """Convert string value to appropriate AST constant.
        
        Args:
            value: String value to convert
            
        Returns:
            AST constant node
        """
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

    def _widget_keywords(self, element: ElementTree.Element) -> List[ast.keyword]:
        """Extract widget keywords from XML element.
        
        Args:
            element: XML element
            
        Returns:
            List of AST keyword nodes for widget
        """
        keywords: List[ast.keyword] = []
        for key, value in element.attrib.items():
            if key in {"pack", "grid", "place", "name", "id", "command"}:
                continue
            argument_name = f"{key}_" if keyword.iskeyword(key) else key
            keywords.append(ast.keyword(arg=argument_name, value=self._value_node(value)))

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

    def _widget_call(self, element: ElementTree.Element, widget_type: str, prefix: str, keywords: List[ast.keyword]) -> None:
        """Generate AST for widget creation and packing.
        
        Args:
            element: XML element
            widget_type: Type of widget
            prefix: Widget name prefix
            keywords: Widget keyword arguments
        """
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
        self.logger.info(f"Создаю элемент {element.tag.lower()}: {element.attrib.get('text', '')}".rstrip())
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
        if element.tag != "Menu":
            # Determine which geometry manager to use
            geometry_method = "pack"  # default
            geometry_keywords = self._pack_keywords(element)
            
            if "grid" in element.attrib:
                geometry_method = "grid"
                geometry_keywords = self._grid_keywords(element)
            elif "place" in element.attrib:
                geometry_method = "place"
                geometry_keywords = self._place_keywords(element)
            
            self.final_body.append(ast.Expr(
                value=ast.Call(
                    func=ast.Attribute(
                        value=ast.Name(id=widget_name, ctx=ast.Load()),
                        attr=geometry_method,
                        ctx=ast.Load(),
                    ),
                    args=[],
                    keywords=geometry_keywords,
                )
            ))

    def _compile_element(self, element: ElementTree.Element) -> None:
        """Compile a single XML element to AST.
        
        Args:
            element: XML element to compile
            
        Raises:
            ValueError: If element tag is not recognized
        """
        tag = element.tag

        if tag == "Toplevel":
            self.logger.info("Создаю дополнительное окно")
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
            if "title" in element.attrib:
                self.final_body.append(ast.Expr(value=ast.Call(
                    func=ast.Attribute(
                        value=ast.Name(id=window_name, ctx=ast.Load()),
                        attr="title",
                        ctx=ast.Load(),
                    ),
                    args=[ast.Constant(value=element.attrib["title"])],
                    keywords=[],
                )))
            if "size" in element.attrib:
                self.final_body.append(ast.Expr(value=ast.Call(
                    func=ast.Attribute(
                        value=ast.Name(id=window_name, ctx=ast.Load()),
                        attr="geometry",
                        ctx=ast.Load(),
                    ),
                    args=[ast.Constant(value=element.attrib["size"])],
                    keywords=[],
                )))
            return

        if tag == "Window":
            title = element.attrib.get("title", "")
            size = element.attrib.get("size", "")
            self.logger.info(f"Создаю окно «{title}» размером {size}")
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
            self.logger.info(f"Подключаю модуль: {module_name}")
            self.final_body.append(ast.Import(names=[ast.alias(name=module_name, asname=None)]))
            return

        if tag == "Import":
            module_name = element.attrib.get("module", "")
            self.logger.info(f"Подключаю файл логики: {module_name}.py")
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
        """Compile XML markup to Python code.
        
        Args:
            xml_code: XML markup string
            
        Returns:
            Generated Python code
            
        Raises:
            ValueError: If XML contains unknown elements
        """
        self.logger.info("Компилирую XML-разметку...")
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
