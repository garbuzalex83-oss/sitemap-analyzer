# 🚀 SEO Master PRO - Веб-интерфейс

## ⚠️ ВАЖНО: GitHub Pages не поддерживает Python/FastAPI!

GitHub Pages работает **только со статическими файлами** (HTML, CSS, JS).  
Наш инструмент использует **Python + FastAPI сервер**, который требует:
- Установки Python
- Запуска веб-сервера
- Обработки запросов на бэкенде

## ✅ Как запустить инструмент:

### Вариант 1: Локальный запуск (рекомендуется)

```bash
# 1. Клонируйте репозиторий
git clone https://github.com/garbuzalex83-oss/sitemap-analyzer.git
cd sitemap-analyzer

# 2. Установите зависимости
pip install -r requirements.txt

# 3. Установите Playwright для JS рендеринга
playwright install --with-deps chromium

# 4. Запустите веб-сервер
python run_web.py

# 5. Откройте в браузере
http://localhost:8000
```

### Вариант 2: Развертывание на хостинге с поддержкой Python

#### **Render.com** (Бесплатно)
1. Зарегистрируйтесь на https://render.com
2. Создайте новый **Web Service**
3. Подключите ваш GitHub репозиторий
4. Выберите файл `render.yaml` для конфигурации
5. Deploy автоматически запустится

#### **Railway.app** (Бесплатно с лимитами)
1. Зарегистрируйтесь на https://railway.app
2. Нажмите "New Project" → "Deploy from GitHub repo"
3. Выберите ваш репозиторий
4. Railway автоматически обнаружит Python и запустит приложение

#### **Heroku** (Платно)
1. Установите Heroku CLI
2. `heroku create seo-master-pro`
3. `git push heroku main`
4. `heroku open`

#### **PythonAnywhere** (Есть бесплатный тариф)
1. Зарегистрируйтесь на https://www.pythonanywhere.com
2. Загрузите файлы через файловый менеджер
3. Настройте Web App с FastAPI

### Вариант 3: Docker (для любого VPS)

Создайте файл `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN playwright install --with-deps chromium

COPY . .

EXPOSE 8000

CMD ["uvicorn", "web.app:app", "--host", "0.0.0.0", "--port", "8000"]
```

Запуск:
```bash
docker build -t seo-master-pro .
docker run -p 8000:8000 seo-master-pro
```

### Вариант 4: VPS (DigitalOcean, Hetzner, Contabo)

```bash
# На Ubuntu/Debian
sudo apt update
sudo apt install python3-pip python3-venv git

git clone https://github.com/garbuzalex83-oss/sitemap-analyzer.git
cd sitemap-analyzer

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
playwright install --with-deps chromium

# Запуск через systemd или supervisor
uvicorn web.app:app --host 0.0.0.0 --port 8000
```

## 📁 Структура проекта

```
seo_master_pro/
├── core/                    # Ядро системы
│   └── core_crawler.py     # SiteCrawler, Sitemap, Robots.txt
├── modules/                 # Модули аудита
│   ├── meta_auditor.py     # Мета-теги + сниппеты Google
│   ├── commercial_auditor.py  # Коммерческие факторы
│   ├── js_renderer_analyzer.py  # JS рендеринг
│   └── report_builder.py   # Конструктор отчетов
├── web/                     # Веб-интерфейс
│   ├── app.py              # FastAPI сервер
│   ├── templates/          # HTML шаблоны
│   │   ├── index.html      # Главная страница
│   │   └── dashboard.html  # Дашборд результатов
│   └── static/             # CSS/JS файлы
│       ├── css/
│       └── js/
├── reports/                # Сгенерированные отчеты
├── requirements.txt        # Зависимости Python
├── Procfile               # Конфигурация для Heroku/Render
├── render.yaml            # Конфигурация для Render.com
├── run_web.py             # Точка входа
└── README_DEPLOY.md       # Эта инструкция
```

## 🔧 Требования к серверу

- **Python**: 3.9+
- **ОЗУ**: минимум 512 MB (рекомендуется 1 GB+)
- **Место**: 200 MB
- **Порты**: 8000 (HTTP)

## 🎯 Что делать с GitHub Pages?

GitHub Pages можно использовать только для:
1. **Статической документации** (README, инструкции)
2. **Демо-страницы** с редиректом на работающий сервер

Пример `index.html` для GitHub Pages:

```html
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <title>SEO Master PRO</title>
    <style>
        body { font-family: Arial; text-align: center; padding: 50px; }
        .btn { background: #4CAF50; color: white; padding: 15px 30px; 
               text-decoration: none; border-radius: 5px; }
    </style>
</head>
<body>
    <h1>🚀 SEO Master PRO</h1>
    <p>Профессиональный инструмент SEO-аудита</p>
    <p style="color: red;"><strong>Внимание:</strong> Требуется сервер с Python</p>
    <p>Выберите способ запуска:</p>
    <ul>
        <li><a href="#local">Локально на компьютере</a></li>
        <li><a href="#render">Render.com (бесплатно)</a></li>
        <li><a href="#railway">Railway.app</a></li>
    </ul>
    <br>
    <a href="https://github.com/garbuzalex83-oss/sitemap-analyzer#readme" class="btn">
        📖 Инструкция по установке
    </a>
</body>
</html>
```

## 📞 Поддержка

Если возникли проблемы с развертыванием:
1. Проверьте логи сервера
2. Убедитесь, что все зависимости установлены
3. Проверьте, что порт 8000 открыт
4. Убедитесь, что Playwright установлен: `playwright install --with-deps chromium`

## 🎉 Готово!

После успешного развертывания вы получите URL вида:
- `https://seo-master-pro.onrender.com`
- `https://seo-master-production.up.railway.app`
- `http://your-vps-ip:8000`

Откройте этот URL в браузере и пользуйтесь инструментом! 🚀