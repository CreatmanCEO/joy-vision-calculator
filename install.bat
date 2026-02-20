@echo off
REM Joy Vision Calculator - Windows Installer
REM Автоматический установщик для Windows 10/11

echo ====================================
echo Joy Vision Calculator
echo Установщик для Windows
echo ====================================
echo.

REM Проверка Python
echo [1/7] Проверка Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ОШИБКА: Python не найден!
    echo.
    echo Пожалуйста, установите Python 3.10+ с https://www.python.org/downloads/
    echo При установке ОБЯЗАТЕЛЬНО отметьте "Add Python to PATH"
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version') do set PYTHON_VERSION=%%i
echo Python версия: %PYTHON_VERSION%
echo OK
echo.

REM Создание виртуального окружения
echo [2/7] Создание виртуального окружения...
if exist venv (
    echo Виртуальное окружение уже существует, пропуск...
) else (
    python -m venv venv
    if %errorlevel% neq 0 (
        echo ОШИБКА: Не удалось создать виртуальное окружение
        pause
        exit /b 1
    )
    echo OK
)
echo.

REM Активация окружения и установка зависимостей
echo [3/7] Установка зависимостей...
call venv\Scripts\activate.bat
python -m pip install --upgrade pip >nul 2>&1
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ОШИБКА: Не удалось установить зависимости
    pause
    exit /b 1
)
echo OK
echo.

REM Создание директорий
echo [4/7] Создание необходимых директорий...
if not exist data mkdir data
if not exist data\exports mkdir data\exports
if not exist static\fonts mkdir static\fonts
if not exist logs mkdir logs
echo OK
echo.

REM Копирование .env
echo [5/7] Настройка конфигурации...
if exist .env (
    echo Файл .env уже существует, пропуск...
) else (
    copy .env.example .env >nul
    echo Файл .env создан из .env.example
)
echo OK
echo.

REM Проверка установки
echo [6/7] Проверка установки...
python -c "from app import create_app; app = create_app(); print('Приложение импортировано успешно')"
if %errorlevel% neq 0 (
    echo ОШИБКА: Приложение не импортируется
    echo Проверьте логи выше
    pause
    exit /b 1
)
echo OK
echo.

REM Запуск тестов
echo [7/7] Запуск тестов...
pytest tests/ -v --tb=short
if %errorlevel% neq 0 (
    echo ВНИМАНИЕ: Некоторые тесты не прошли
    echo Приложение может работать, но проверьте логи
    echo.
) else (
    echo Все тесты пройдены!
)
echo.

REM Финальные инструкции
echo ====================================
echo Установка завершена успешно!
echo ====================================
echo.
echo Следующие шаги:
echo.
echo 1. Отредактируйте файл .env:
echo    - Измените SECRET_KEY (используйте команду ниже)
echo    - Настройте BITRIX24_WEBHOOK_URL
echo    - Настройте BITRIX24_FOLDER_ID
echo.
echo    Генерация SECRET_KEY:
echo    python -c "import secrets; print(secrets.token_hex(32))"
echo.
echo 2. Подробные инструкции по настройке Битрикс24:
echo    Откройте файл INSTALL_WINDOWS.md (раздел 7)
echo.
echo 3. Запустите приложение:
echo    Двойной клик по файлу start.bat
echo.
echo 4. Откройте в браузере:
echo    http://localhost:5000
echo.
echo Полная документация: README.md и INSTALL_WINDOWS.md
echo.
pause
