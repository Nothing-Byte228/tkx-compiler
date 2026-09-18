# TkinterX Compiler

## Что это такое
Перед вами компилятор проектов для обычной библиотеки `tkinter` на Python. Разметка приложения хранится в XML-файле `main.xml`, а логика подключается из файлов `*.py`.

> [!NOTE]
> Данная программа компилирует код вашего проекта в код на языке Python, а также ищет модули, установленные в Python глобально, так что, для корректной работы компилятора, вам потребуется установить интерпретатор Python `3.8.x` и выше. Скачать интерпретатор можно [здесь](https://www.python.org)

> [!WARNING]
> За ошибки в вашем проекте и/или скомпилированном коде, вызванные неправильным написанием синтаксиса, мы ответственности НЕ НЕСЁМ! Если вы всё же обнаружили ошибки в работе самого компилятора, то пишите в раздел `Issues`.

## Особенности
- ✅ **Чистая архитектура** — разделение на модули для парсинга, компиляции и валидации
- ✅ **Безопасность** — валидация путей, защита от path traversal атак
- ✅ **Обработка ошибок** — детальные сообщения об ошибках с контекстом
- ✅ **Type hints** — полная типизация для лучшей IDE поддержки
- ✅ **Валидация** — проверка XML структуры и Python синтаксиса
- ✅ **Рекурсивные зависимости** — автоматический сбор всех зависимостей
- ✅ **Zero-dependency** — готовые приложения без необходимости установки пакетов
- ✅ **Геометрия** — поддержка pack, grid и place менеджеров компоновки
- ✅ **Конфигурация** — поддержка .tkxrc.json и переменных окружения
- ✅ **Шаблоны** — генерация шаблонов проектов через `tkx init`
- ✅ **CLI** — улучшенный интерфейс с подкомандами и цветным выводом
- ✅ **Логирование** — структурированное логирование с разными уровнями

## Как использовать компилятор
Компилятор является консольным. Это значит, что имеется поддержка ввода команд через консоль, но отсутствует графический интерфейс.

> [!WARNING]
> Важное напоминание: данный компилятор НЕ поддерживает запуск программ, он только производит их сборку.

Вот некоторые агрументы компилятора:

- `project_path` - тут вам нужно ввести путь к вашему проекту (к папке, не к файлу!), где находятся `main.xml` и остальные файлы;
- `-o, --output OUTPUT` - имя главного файла после компиляции (по умолчанию, это `program.py`);
- `-v, --verbose` - более подробное логирование всех действий.
- `-h --help` - показ всех аргументов

## Установка

### Из исходников
```bash
git clone https://github.com/yourusername/tkx-compiler.git
cd tkx-compiler
pip install -e .
```

### С дополнительными зависимостями
```bash
pip install -e ".[dev]"  # Для разработки
pip install -e ".[ui]"   # Для улучшенного UI (цветной вывод, прогресс-бары)
```

## Примеры кода
Вот наглядные примеры кода для сравнения:

### Без `TKX`
```python
import tkinter as tk

def say_hello():
    print("Привет из чистого Python!")

# Инициализация окна
root = tk.Tk()
root.title("Окно без TKX")
root.geometry("400x300")

# Создание виджетов
label = tk.Label(root, text="Добро пожаловать в обычный Tkinter")
label.pack(pady=10)

button = tk.Button(root, text="Нажми меня", command=say_hello)
button.pack(pady=20)

# Запуск
root.mainloop()
```

### Используя `TKX`

> [!NOTE]
> Главная разметка приложения пишется в `XML`, а логика на `Python`.

1. #### main.xml
```xml
<Application>
    <Window title="Окно с TKX" size="400x300" />
    <Import module="logic" />
    <Label text="Добро пожаловать в tkx Framework!" pack="pady=10" />
    <Button text="Нажми меня" pack="pady=20" command="logic.say_hello" />
</Application>
```

Доступные элементы интерфейса: `Window`, `Toplevel`, `Button`, `Canvas`, `Checkbutton`, `Entry`, `Frame`, `Label`, `LabelFrame`, `Listbox`, `Message`, `PanedWindow`, `Radiobutton`, `Scale`, `Scrollbar`, `Spinbox`, `Text`, `Menu` и `Menubutton`. Также доступны основные виджеты `ttk`: `TtkButton`, `TtkCheckbutton`, `TtkCombobox`, `TtkEntry`, `TtkFrame`, `TtkLabel`, `TtkLabelFrame`, `TtkNotebook`, `TtkPanedWindow`, `TtkProgressbar`, `TtkRadiobutton`, `TtkScale`, `TtkScrollbar`, `TtkSeparator`, `TtkSizegrip`, `TtkSpinbox` и `TtkTreeview`. Атрибуты XML передаются как параметры соответствующего класса Tkinter, а атрибут `pack` задаёт параметры упаковки виджета.

2. #### logic.py
```python
def say_hello():
    print("Привет из файла логики через TKX!")
```

3. #### Компиляция

### Базовое использование
```cmd
tkx project_path -o program.py
```

### Новые команды

#### Инициализация проекта
```cmd
tkx init my_project --name "My App" --template basic
```

#### Сборка проекта
```cmd
tkx build my_project -o app.py -v
```

#### Упаковка в EXE
```cmd
tkx package my_project --script dist/app.py --output myapp --windowed
```

### Конфигурация

#### Файл конфигурации (.tkxrc.json)
```json
{
  "output_file": "app.py",
  "dist_dir": "dist",
  "packages_dir": "packages",
  "verbose": false,
  "validate_xml": true,
  "validate_python": true,
  "log_level": "INFO"
}
```

#### Переменные окружения
```bash
export TKX_OUTPUT_FILE="app.py"
export TKX_VERBOSE="true"
export TKX_LOG_LEVEL="DEBUG"
```

### Дополнительные опции CLI

- `--no-color` - отключить цветной вывод
- `--no-progress` - отключить прогресс-бары
- `-c, --config` - путь к файлу конфигурации
- `-v, --verbose` - подробное логирование

### Поддержка геометрии

Теперь поддерживаются все три менеджера компоновки:

#### Pack (по умолчанию)
```xml
<Button text="Click" pack="pady=10, fill=x" />
```

#### Grid
```xml
<Button text="Click" grid="row=0, column=0, padx=5" />
```

#### Place
```xml
<Button text="Click" place="x=100, y=50" />
```

## Архитектура проекта

```
tkx-compiler/
├── core/
│   ├── __init__.py
│   ├── validators.py          # Валидация XML, Python, путей
│   ├── xml_parser.py          # Компиляция XML в Python AST
│   ├── pyparser_refactored.py # Главный Python парсер
│   ├── parsers/
│   │   ├── __init__.py
│   │   ├── import_extractor.py # Извлечение импортов
│   │   └── stdlib_checker.py   # Проверка стандартной библиотеки
│   ├── compilers/
│   │   ├── __init__.py
│   │   ├── module_copier.py    # Копирование модулей
│   │   └── import_rewriter.py  # Переписывание импортов
│   └── builders/
│       ├── __init__.py
│       └── compiler_builder.py # Орхестрация сборки
├── cli/
│   └── __init__.py
├── main.py                     # Точка входа CLI
├── pyproject.toml             # Конфигурация проекта
├── requirements.txt           # Зависимости
└── README.md
```

## Разработка

### Запуск тестов
```bash
pytest
```

### Форматирование кода
```bash
black .
```

### Проверка типов
```bash
mypy core/
```

### Линтер
```bash
flake8 core/
```

## Лицензия
Apache License 2.0
