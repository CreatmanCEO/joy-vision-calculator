@echo off
REM Joy Vision Calculator - Запуск приложения

title Joy Vision Calculator

echo ====================================
echo Joy Vision Calculator
echo ====================================
echo.

REM Проверка виртуального окружения
if not exist venv (
    echo ОШИБКА: Виртуальное окружение не найдено!
    echo Запустите install.bat для установки
    pause
    exit /b 1
)

REM Активация окружения
echo Активация виртуального окружения...
call venv\Scripts\activate.bat

REM Проверка .env
if not exist .env (
    echo ОШИБКА: Файл .env не найден!
    echo Скопируйте .env.example в .env и настройте
    pause
    exit /b 1
)

echo.
echo Запуск Joy Vision Calculator...
echo Приложение будет доступно по адресу: http://localhost:5000
echo.
echo Для остановки нажмите Ctrl+C
echo ====================================
echo.

REM Запуск приложения
python app.py

pause
