# Гайд по использованию tkx-compiler

## 📋 Содержание
1. [Установка](#установка)
2. [Быстрый старт](#быстрый-старт)
3. [Команды CLI](#команды-cli)
4. [Создание проектов](#создание-проектов)
5. [Сборка проектов](#сборка-проектов)
6. [Упаковка в EXE](#упаковка-in-exe)
7. [Конфигурация](#конфигурация)
8. [XML разметка](#xml-разметка)
9. [Python логика](#python-логика)
10. [Продвинутые функции](#продвинутые-функции)

## 🚀 Установка

### Требования
- Python 3.8 или выше
- pip (устанавливается с Python)

### Установка из исходников
```bash
git clone https://github.com/yourusername/tkx-compiler.git
cd tkx-compiler
pip install -e .
```

### Установка с дополнительными зависимостями
```bash
# Для разработки
pip install -e ".[dev]"

# Для улучшенного UI (цветной вывод, прогресс-бары)
pip install -e ".[ui]"
```

## ⚡ Быстрый старт

### 1. Создайте простой проект
```bash
python main.py init my_first_app --name "Моё приложение"
```

### 2. Отредактируйте файлы
Откройте созданную папку `my_first_app` и отредактируйте:
- `main.xml` — разметка интерфейса
- `logic.py` — логика приложения

### 3. Соберите проект
```bash
python main.py build my_first_app
```

### 4. Запустите приложение
```bash
python my_first_app/dist/program.py
```

## 🎮 Команды CLI

### Общий синтаксис
```bash
python main.py <команда> [аргументы] [опции]
```

### Доступные команды
- `build` — собрать проект
- `init` — создать новый проект
- `package` — упаковать в EXE

### Получение помощи
```bash
# Общая справка
python main.py --help

# Справка по конкретной команде
python main.py build --help
python main.py init --help
python main.py package --help
```

## 📁 Создание проектов

### Команда init
```bash
python main.py init <путь> [опции]
```

### Опции init
- `-n, --name` — название проекта (по умолчанию: tkx_project)
- `-t, --template` — шаблон проекта (basic/advanced, по умолчанию: basic)

### Примеры
```bash
# Базовый проект
python main.py init ./my_app

# Проект с названием
python main.py init ./my_app --name "Моё приложение"

# Расширенный шаблон
python main.py init ./my_app --template advanced
```

### Что создаётся

#### Basic шаблон
```
my_app/
├── main.xml          # Разметка интерфейса
├── logic.py          # Файл логики
└── .tkxrc.json       # Конфигурация проекта
```

#### Advanced шаблон
```
my_app/
├── main.xml          # Разметка интерфейса
├── app_logic.py      # Основная логика
├── helpers.py        # Вспомогательные функции
└── .tkxrc.json       # Конфигурация проекта
```

## 🔨 Сборка проектов

### Команда build
```bash
python main.py build <путь_к_проекту> [опции]
```

### Опции build
- `-o, --output` — имя выходного файла (по умолчанию: program.py)
- `-v, --verbose` — подробное логирование
- `-c, --config` — путь к файлу конфигурации
- `--no-color` — отключить цветной вывод
- `--no-progress` — отключить прогресс-бары

### Примеры
```bash
# Базовая сборка
python main.py build ./my_app

# С указанием выходного файла
python main.py build ./my_app -o app.py

# С подробным логированием
python main.py build ./my_app -v

# С файлом конфигурации
python main.py build ./my_app -c custom_config.json
```

### Обратная совместимость
Старый формат команд также поддерживается:
```bash
python main.py ./my_app -o app.py -v
```

## 📦 Упаковка в EXE

### Команда package
```bash
python main.py package <путь_к_проекту> [опции]
```

### Опции package
- `-s, --script` — путь к Python скрипту (по умолчанию: dist/program.py)
- `-o, --output` — имя EXE файла (по умолчанию: app)
- `--icon` — путь к иконке (.ico)
- `--windowed` — создать GUI приложение без консоли
- `--no-onefile` — создать папку вместо одного файла

### Примеры
```bash
# Базовая упаковка
python main.py package ./my_app

# Упаковка конкретного скрипта
python main.py package ./my_app --script dist/app.py

# С названием и иконкой
python main.py package ./my_app --output myapp --icon icon.ico

# GUI приложение без консоли
python main.py package ./my_app --windowed

# Папка вместо одного файла
python main.py package ./my_app --no-onefile
```

### Требования для упаковки
- PyInstaller (устанавливается автоматически при необходимости)
- Для GUI приложений автоматически определяется режим без консоли

## ⚙️ Конфигурация

### Файл конфигурации .tkxrc.json
Создаётся автоматически в папке проекта при использовании `init`.

```json
{
  "output_file": "program.py",
  "dist_dir": "dist",
  "packages_dir": "packages",
  "verbose": false,
  "validate_xml": true,
  "validate_python": true,
  "check_dependencies": true,
  "recursive_dependencies": true,
  "safe_paths": true,
  "log_level": "INFO",
  "encoding": "utf-8",
  "max_file_size": 10485760
}
```

### Переменные окружения
```bash
# Windows
set TKX_OUTPUT_FILE=app.py
set TKX_VERBOSE=true
set TKX_LOG_LEVEL=DEBUG

# Linux/Mac
export TKX_OUTPUT_FILE=app.py
export TKX_VERBOSE=true
export TKX_LOG_LEVEL=DEBUG
```

### Приоритет настроек
1. Аргументы командной строки (высший приоритет)
2. Файл конфигурации .tkxrc.json
3. Переменные окружения
4. Значения по умолчанию

## 🏗️ XML разметка

### Базовая структура
```xml
<?xml version="1.0" encoding="UTF-8"?>
<Application>
    <Window title="Заголовок" size="400x300" />
    <!-- Ваши виджеты -->
</Application>
```

### Основные элементы

#### Window — главное окно
```xml
<Window title="Моё приложение" size="600x400" />
```

#### Toplevel — дополнительное окно
```xml
<Toplevel title="Дополнительное окно" size="300x200" />
```

#### Import — импорт пользовательского модуля
```xml
<Import module="logic" />
```

#### Require — импорт внешнего модуля
```xml
<Require module="json" />
```

### Виджеты

#### Кнопка
```xml
<Button text="Нажми меня" command="logic.handle_click" pack="pady=10" />
```

#### Текстовая метка
```xml
<Label text="Привет, мир!" pack="pady=20" />
```

#### Поле ввода
```xml
<Entry pack="pady=5" />
```

#### Текстовое поле
```xml
<Text height="10" pack="fill=both, expand=true" />
```

#### Чекбокс
```xml
<Checkbutton text="Согласен" pack="pady=5" />
```

### TTK виджеты (стилизованные)
```xml
<TtkButton text="Стильная кнопка" pack="pady=10" />
<TtkLabel text="Стильная метка" pack="pady=5" />
<TtkEntry pack="pady=5" />
```

### Менеджеры компоновки

#### Pack (по умолчанию)
```xml
<Button pack="pady=10, padx=5, fill=x, expand=true" />
```

#### Grid
```xml
<Button grid="row=0, column=0, padx=5, pady=5" />
<Label grid="row=0, column=1, padx=5" />
```

#### Place
```xml
<Button place="x=100, y=50, width=100, height=30" />
```

### Полный пример
```xml
<?xml version="1.0" encoding="UTF-8"?>
<Application>
    <Window title="Калькулятор" size="300x400" />
    <Import module="calculator" />
    
    <Frame pack="fill=both, expand=true, padx=10, pady=10">
        <Entry pack="fill=x, pady=5" />
        
        <Frame pack="fill=x">
            <Button text="7" grid="row=0, column=0" command="calculator.press_7" />
            <Button text="8" grid="row=0, column=1" command="calculator.press_8" />
            <Button text="9" grid="row=0, column=2" command="calculator.press_9" />
            <Button text="/" grid="row=0, column=3" command="calculator.press_divide" />
        </Frame>
    </Frame>
</Application>
```

## 🐍 Python логика

### Структура файла логики
```python
# logic.py
def handle_click():
    """Обработчик нажатия кнопки."""
    print("Кнопка была нажата!")

def calculate_result():
    """Вычисление результата."""
    return 42
```

### Подключение функций в XML
```xml
<Button text="Вычислить" command="logic.calculate_result" />
```

### Использование нескольких файлов
```xml
<Import module="main_logic" />
<Import module="helpers" />

<Button text="Сохранить" command="main_logic.save" />
<Button text="Загрузить" command="helpers.load" />
```

### Доступ к виджетам
Для доступа к виджетам из Python логики, используйте их имена:

```python
# В XML виджет получает имя автоматически: btn_1, lbl_1 и т.д.
# Или можно указать своё имя через атрибут name (если поддерживается)

def handle_button():
    # Получить текст из Entry
    # (требует дополнительной реализации)
    pass
```

## 🔧 Продвинутые функции

### Валидация
Компилятор автоматически проверяет:
- Структуру XML
- Синтаксис Python файлов
- Безопасность путей
- Наличие зависимостей

### Логирование
Уровни логирования:
- `DEBUG` — детальная информация
- `INFO` — обычная информация (по умолчанию)
- `WARNING` — предупреждения
- `ERROR` — ошибки
- `CRITICAL` — критические ошибки

### Цветной вывод
Для включения цветного вывода убедитесь, что ваш терминал поддерживает ANSI коды.

### Обработка ошибок
При ошибках компилятор показывает:
- Тип ошибки
- Контекст (файл, строка)
- Детальное описание
- Suggestions по исправлению

### Кэширование зависимостей
Зависимости кэшируются для ускорения повторных сборок.

## 🐛 Устранение проблем

### Ошибка: main.xml не найден
Убедитесь, что в папке проекта есть файл `main.xml`.

### Ошибка: Python синтаксис
Проверьте файлы логики на наличие синтаксических ошибок.

### Ошибка: Модуль не найден
Убедитесь, что все необходимые модули установлены:
```bash
pip install <module_name>
```

### Проблемы с упаковкой в EXE
- Убедитесь, что PyInstaller установлен
- Проверьте путь к скрипту
- Для GUI приложений используйте `--windowed`

## 📚 Дополнительные ресурсы

- [README.md](README.md) — основная документация
- [CONTRIBUTING.md](CONTRIBUTING.md) — руководство для контрибьюторов
- [CHANGELOG.md](CHANGELOG.md) — список изменений
- [Тесты](tests/) — примеры использования

## 💡 Советы

1. **Начните с basic шаблона** — для простых приложений
2. **Используйте verbose режим** — для отладки
3. **Проверяйте XML** — перед сборкой
4. **Тестируйте логику** — отдельно от интерфейса
5. **Используйте конфигурацию** — для повторяемых сборок
6. **Создавайте EXE** — для распространения

## 🎯 Пример полного рабочего процесса

```bash
# 1. Создаём проект
python main.py init ./todo_app --name "Список дел"

# 2. Редактируем main.xml
# (открываем файл и добавляем виджеты)

# 3. Редактируем logic.py
# (открываем файл и добавляем функции)

# 4. Тестируем сборку
python main.py build ./todo_app -v

# 5. Запускаем для проверки
python ./todo_app/dist/program.py

# 6. Упаковываем в EXE
python main.py package ./todo_app --output todo_app --windowed

# 7. Распространяем готовый EXE файл
```

---

**Удачи в создании приложений с tkx-compiler!** 🚀
