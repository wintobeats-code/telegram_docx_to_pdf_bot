"""Конвертация и удаление файлов"""
import os
from subprocess import run, TimeoutExpired
from logging import error

def docx2pdf(input_path: str, output_path: str) -> bool:
    """Конвертация файла с помощью LibreOffice="""
    try:
        result = run([
            "soffice", "--headless", "--convert-to", "pdf", "--outdir", 
            os.path.dirname(output_path),
            input_path
        ], timeout=30, capture_output=True, text=True, check=True)

        if result.returncode == 0:
            return os.path.exists(output_path)
        error("Ошибка LibreOffice: %s", result.stderr)
        return False

    except TimeoutExpired as te:
        error("Конвертация файла %s заняла слишком много времени: %s", input_path, te)
        return False
    except (FileNotFoundError, PermissionError, OSError, UnicodeDecodeError) as e:
        error("Ошибка конвертации файла %s: %s", input_path, e)
        return False

def remove_file(path: str):
    '''Функция удаляет файл'''
    try:
        os.remove(path)
    except OSError as oe:
        error('Не удалось удалить файл %path: %s', oe)
