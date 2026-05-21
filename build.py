# build.py
import os
import subprocess
import sys

def build_exe():
    print("Начинаю сборку exe файла...")
    
    # Проверяем установку pyinstaller
    try:
        import PyInstaller
    except ImportError:
        print("Устанавливаю PyInstaller...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
    
    # Команда для сборки
    cmd = [
        "pyinstaller",
        "--onefile",           # Один файл
        "--windowed",          # Без консоли (для GUI)
        "--name", "AIS_Shareholders",
        "--hidden-import", "PyQt6",
        "--hidden-import", "psycopg2",
        "--hidden-import", "psycopg2._psycopg",
        "--hidden-import", "psycopg2.extras",
        "--hidden-import", "psycopg2.extensions",
        "--hidden-import", "reportlab",
        "--hidden-import", "reportlab.pdfbase",
        "--hidden-import", "reportlab.pdfbase.ttfonts",
        "--hidden-import", "reportlab.graphics",
        "--hidden-import", "reportlab.graphics.charts",
        "--hidden-import", "reportlab.lib",
        "--hidden-import", "reportlab.platypus",
        "--collect-all", "PyQt6",
        "main.py"
    ]
    
    # Запуск сборки
    subprocess.run(cmd)
    
    print("\nСборка завершена!")
    print("exe файл находится в папке dist/")

if __name__ == "__main__":
    build_exe()