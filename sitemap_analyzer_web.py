#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Web-интерфейс для анализатора Sitemap
Flask приложение с визуальными отчетами
"""

from flask import Flask, render_template_string, request, jsonify
import requests
import xml.etree.ElementTree as ET
from urllib.parse import urlparse
from datetime import datetime
from collections import defaultdict
import json

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sitemap Analyzer - SEO Tool</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }
        
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }
        
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        
        .header p {
            font-size: 1.2em;
            opacity: 0.9;
        }
        
        .content {
            padding: 40px;
        }
        
        .input-section {
            background: #f8f9fa;
            padding: 30px;
            border-radius: 15px;
            margin-bottom: 30px;
        }
        
        .form-group {
            margin-bottom: 20px;
        }
        
        label {
            display: block;
            font-weight: 600;
            margin-bottom: 10px;
            color: #333;
        }
        
        input[type="text"] {
            width: 100%;
            padding: 15px;
            border: 2px solid #ddd;
            border-radius: 10px;
            font-size: 16px;
            transition: border-color 0.3s;
        }
        
        input[type="text"]:focus {
            outline: none;
            border-color: #667eea;
        }
        
        .checkbox-group {
            display: flex;
            gap: 20px;
            align-items: center;
        }
        
        .checkbox-group label {
            display: flex;
            align-items: center;
            gap: 8px;
            margin: 0;
            cursor: pointer;
        }
        
        input[type="checkbox"] {
            width: 20px;
            height: 20px;
            cursor: pointer;
        }
        
        .btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 15px 40px;
            font-size: 18px;
            font-weight: 600;
            border-radius: 10px;
            cursor: pointer;
            transition: transform 0.2s;
            width: 100%;
        }
        
        .btn:hover {
            transform: translateY(-2px);
        }
        
        .btn:disabled {
            background: #ccc;
            cursor: not-allowed;
            transform: none;
        }
        
        .loading {
            display: none;
            text-align: center;
            padding: 40px;
        }
        
        .spinner {
            border: 4px solid #f3f3f3;
            border-top: 4px solid #667eea;
            border-radius: 50%;
            width: 50px;
            height: 50px;
            animation: spin 1s linear infinite;
            margin: 0 auto 20px;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        .results {
            display: none;
        }
        
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .stat-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 25px;
            border-radius: 15px;
            text-align: center;
        }
        
        .stat-card.success {
            background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        }
        
        .stat-card.warning {
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        }
        
        .stat-card.error {
            background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
        }
        
        .stat-value {
            font-size: 2.5em;
            font-weight: bold;
            margin-bottom: 10px;
        }
        
        .stat-label {
            font-size: 1em;
            opacity: 0.9;
        }
        
        .section {
            background: #f8f9fa;
            padding: 25px;
            border-radius: 15px;
            margin-bottom: 20px;
        }
        
        .section-title {
            font-size: 1.5em;
            margin-bottom: 15px;
            color: #333;
            border-bottom: 3px solid #667eea;
            padding-bottom: 10px;
        }
        
        .issue-list {
            max-height: 400px;
            overflow-y: auto;
        }
        
        .issue-item {
            background: white;
            padding: 15px;
            margin-bottom: 10px;
            border-radius: 10px;
            border-left: 4px solid #667eea;
        }
        
        .issue-item.error {
            border-left-color: #f5576c;
        }
        
        .issue-item.warning {
            border-left-color: #feca57;
        }
        
        .url-text {
            word-break: break-all;
            font-family: monospace;
            color: #555;
            margin-bottom: 5px;
        }
        
        .issue-text {
            color: #666;
            font-size: 0.9em;
        }
        
        .recommendation {
            background: #fff3cd;
            border-left: 4px solid #ffc107;
            padding: 15px;
            margin-bottom: 10px;
            border-radius: 5px;
        }
        
        .score {
            text-align: center;
            padding: 30px;
            background: white;
            border-radius: 15px;
            margin-top: 30px;
        }
        
        .score-circle {
            width: 150px;
            height: 150px;
            border-radius: 50%;
            margin: 0 auto 20px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 3em;
            font-weight: bold;
            color: white;
        }
        
        .score-excellent {
            background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        }
        
        .score-good {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }
        
        .score-medium {
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        }
        
        .score-poor {
            background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔍 Sitemap Analyzer</h1>
            <p>Профессиональный SEO анализ вашего sitemap</p>
        </div>
        
        <div class="content">
            <div class="input-section">
                <form id="analyzeForm">
                    <div class="form-group">
                        <label for="sitemapUrl">URL Sitemap:</label>
                        <input type="text" id="sitemapUrl" name="sitemap_url" 
                               placeholder="https://example.com/sitemap.xml" required>
                    </div>
                    
                    <div class="form-group">
                        <div class="checkbox-group">
                            <label>
                                <input type="checkbox" id="checkStatus" name="check_status">
                                Проверять HTTP статус (медленнее, но подробнее)
                            </label>
                        </div>
                    </div>
                    
                    <button type="submit" class="btn" id="analyzeBtn">
                        Анализировать Sitemap
                    </button>
                </form>
            </div>
            
            <div class="loading" id="loading">
                <div class="spinner"></div>
                <p>Анализирую sitemap... Это может занять некоторое время</p>
            </div>
            
            <div class="results" id="results">
                <div class="stats-grid" id="statsGrid"></div>
                
                <div id="scoreSection"></div>
                
                <div class="section" id="errorsSection" style="display:none;">
                    <h2 class="section-title">❌ Критические ошибки</h2>
                    <div class="issue-list" id="errorsList"></div>
                </div>
                
                <div class="section" id="warningsSection" style="display:none;">
                    <h2 class="section-title">⚠️ Предупреждения</h2>
                    <div class="issue-list" id="warningsList"></div>
                </div>
                
                <div class="section" id="recommendationsSection" style="display:none;">
                    <h2 class="section-title">💡 Рекомендации</h2>
                    <div id="recommendationsList"></div>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        document.getElementById('analyzeForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const btn = document.getElementById('analyzeBtn');
            const loading = document.getElementById('loading');
            const results = document.getElementById('results');
            
            btn.disabled = true;
            loading.style.display = 'block';
            results.style.display = 'none';
            
            const formData = new FormData(e.target);
            const data = {
                sitemap_url: formData.get('sitemap_url'),
                check_status: formData.get('check_status') === 'on'
            };
            
            try {
                const response = await fetch('/analyze', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(data)
                });
                
                const result = await response.json();
                displayResults(result);
                
            } catch (error) {
                alert('Ошибка при анализе: ' + error.message);
            } finally {
                btn.disabled = false;
                loading.style.display = 'none';
                results.style.display = 'block';
            }
        });
        
        function displayResults(data) {
            // Статистика
            const statsGrid = document.getElementById('statsGrid');
            statsGrid.innerHTML = `
                <div class="stat-card">
                    <div class="stat-value">${data.statistics.total_urls}</div>
                    <div class="stat-label">Всего URL</div>
                </div>
                <div class="stat-card success">
                    <div class="stat-value">${data.statistics.domain_urls}</div>
                    <div class="stat-label">URL домена</div>
                </div>
                <div class="stat-card warning">
                    <div class="stat-value">${data.statistics.duplicates}</div>
                    <div class="stat-label">Дубликаты</div>
                </div>
                <div class="stat-card error">
                    <div class="stat-value">${data.errors.length}</div>
                    <div class="stat-label">Критических ошибок</div>
                </div>
            `;
            
            // Оценка
            const totalIssues = data.errors.length + data.warnings.length;
            let score = 100 - totalIssues;
            let scoreClass = 'score-excellent';
            let scoreText = 'Отлично!';
            
            if (totalIssues > 50) {
                scoreClass = 'score-poor';
                scoreText = 'Требуется доработка';
                score = Math.max(0, score);
            } else if (totalIssues > 20) {
                scoreClass = 'score-medium';
                scoreText = 'Средний уровень';
            } else if (totalIssues > 5) {
                scoreClass = 'score-good';
                scoreText = 'Хорошо';
            }
            
            document.getElementById('scoreSection').innerHTML = `
                <div class="score">
                    <div class="score-circle ${scoreClass}">${Math.max(0, score)}</div>
                    <h2>${scoreText}</h2>
                    <p>Найдено проблем: ${totalIssues}</p>
                </div>
            `;
            
            // Ошибки
            if (data.errors.length > 0) {
                document.getElementById('errorsSection').style.display = 'block';
                document.getElementById('errorsList').innerHTML = data.errors.map(error => 
                    `<div class="issue-item error"><div class="issue-text">${error}</div></div>`
                ).join('');
            }
            
            // Предупреждения
            if (data.warnings.length > 0) {
                document.getElementById('warningsSection').style.display = 'block';
                const warningsList = document.getElementById('warningsList');
                warningsList.innerHTML = data.warnings.slice(0, 50).map(warning => {
                    const parts = warning.split(': ');
                    return `
                        <div class="issue-item warning">
                            <div class="url-text">${parts[0]}</div>
                            <div class="issue-text">${parts[1] || ''}</div>
                        </div>
                    `;
                }).join('');
                
                if (data.warnings.length > 50) {
                    warningsList.innerHTML += `<div class="issue-item">... и еще ${data.warnings.length - 50} предупреждений</div>`;
                }
            }
            
            // Рекомендации
            if (data.recommendations.length > 0) {
                document.getElementById('recommendationsSection').style.display = 'block';
                document.getElementById('recommendationsList').innerHTML = data.recommendations.map(rec => 
                    `<div class="recommendation">${rec}</div>`
                ).join('');
            }
        }
    </script>
</body>
</html>
"""

class WebSitemapAnalyzer:
    def __init__(self, sitemap_url, timeout=10):
        self.sitemap_url = sitemap_url
        self.timeout = timeout
        self.domain = urlparse(sitemap_url).netloc
        self.protocol = urlparse(sitemap_url).scheme
        
        self.urls = []
        self.errors = []
        self.warnings = []
        self.statistics = defaultdict(int)
        self.recommendations = []
        
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (compatible; SitemapAnalyzer/2.0)'
        }
    
    def fetch_sitemap(self, url):
        try:
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            return response.text
        except Exception as e:
            self.errors.append(f"Ошибка загрузки: {str(e)}")
            return None
    
    def parse_sitemap(self, content, sitemap_url):
        urls_data = []
        try:
            root = ET.fromstring(content)
            namespace = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
            
            # Проверка sitemap index
            sitemaps = root.findall('.//ns:sitemap', namespace)
            if sitemaps:
                for sitemap in sitemaps:
                    loc = sitemap.find('ns:loc', namespace)
                    if loc is not None and loc.text:
                        sub_content = self.fetch_sitemap(loc.text)
                        if sub_content:
                            urls_data.extend(self.parse_sitemap(sub_content, loc.text))
                return urls_data
            
            # Парсинг URL
            urlset = root.findall('.//ns:url', namespace)
            for url_element in urlset:
                loc = url_element.find('ns:loc', namespace)
                if loc is not None and loc.text:
                    urls_data.append({'loc': loc.text.strip()})
            
            self.statistics['total_urls'] += len(urlset)
            
        except Exception as e:
            self.errors.append(f"Ошибка парсинга XML: {str(e)}")
        
        return urls_data
    
    def analyze(self):
        content = self.fetch_sitemap(self.sitemap_url)
        if not content:
            return
        
        self.urls = self.parse_sitemap(content, self.sitemap_url)
        
        url_set = set()
        for url_data in self.urls:
            url = url_data['loc']
            
            # Дубликаты
            if url in url_set:
                self.warnings.append(f"{url}: Дубликат URL")
                self.statistics['duplicates'] += 1
            else:
                url_set.add(url)
            
            # Домен
            url_domain = urlparse(url).netloc
            if url_domain != self.domain:
                self.warnings.append(f"{url}: Внешний домен")
            else:
                self.statistics['domain_urls'] += 1
        
        # Генерация рекомендаций
        if self.statistics['duplicates'] > 0:
            self.recommendations.append(f"⚠️ Удалите {self.statistics['duplicates']} дубликатов URL")
        
        if self.statistics['total_urls'] > 50000:
            self.recommendations.append(f"⚠️ Sitemap содержит {self.statistics['total_urls']} URL (лимит 50,000). Разбейте на несколько файлов")
        
        if not self.errors and not self.warnings:
            self.recommendations.append("✅ Отлично! Sitemap не содержит критических ошибок")
    
    def get_results(self):
        return {
            'statistics': dict(self.statistics),
            'errors': self.errors,
            'warnings': self.warnings,
            'recommendations': self.recommendations
        }

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.get_json()
    sitemap_url = data.get('sitemap_url')
    
    if not sitemap_url:
        return jsonify({'error': 'URL не указан'}), 400
    
    analyzer = WebSitemapAnalyzer(sitemap_url)
    analyzer.analyze()
    
    return jsonify(analyzer.get_results())

if __name__ == '__main__':
    print("""
╔═══════════════════════════════════════════════════════════════╗
║         🌐 SITEMAP ANALYZER - WEB INTERFACE                  ║
╚═══════════════════════════════════════════════════════════════╝

Запуск веб-сервера...
Откройте браузер: http://localhost:5000
    """)
    app.run(debug=True, host='0.0.0.0', port=5000)
