#!/usr/bin/env python3
"""
SEO Master PRO - Веб-интерфейс
Запуск сервера для работы в браузере
"""

import os
import sys
from pathlib import Path

# Добавляем родительскую директорию в путь
sys.path.insert(0, str(Path(__file__).parent.parent))

from web.app import app
import uvicorn

if __name__ == "__main__":
    print("\n" + "="*70)
    print("🚀 SEO Master PRO - Веб-интерфейс")
    print("="*70)
    print("\n📊 Откройте в браузере: http://localhost:8000")
    print("\n⚙️  Доступный функционал:")
    print("   ✓ Полный SEO аудит сайта")
    print("   ✓ Анализ коммерческих факторов (16 элементов)")
    print("   ✓ Проверка JS рендеринга")
    print("   ✓ Анализ sitemap.xml и robots.txt")
    print("   ✓ Превью сниппетов Google")
    print("   ✓ Drag-and-Drop конструктор отчетов")
    print("   ✓ Интерактивный дашборд")
    print("\n📁 Отчеты сохраняются в: reports/")
    print("\n💡 Для остановки нажмите: Ctrl+C")
    print("="*70 + "\n")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)
