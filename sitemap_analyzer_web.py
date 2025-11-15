#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Профессиональный Web-интерфейс для анализатора Sitemap
С полным выводом результатов и скачиванием отчетов
"""

from flask import Flask, render_template_string, request, jsonify, send_file, session
import requests
import xml.etree.ElementTree as ET
from urllib.parse import urlparse
from datetime import datetime
from collections import defaultdict
import json
import io
import os

app = Flask(__name__)
app.secret_key = 'sitemap-analyzer-secret-key-2025'

# Глобальное хранилище для последнего анализа
last_analysis = {}

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sitemap Analyzer Pro - Professional SEO Tool</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }
        
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 50px 40px;
            text-align: center;
            position: relative;
        }
        
        .header::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: url('data:image/svg+xml,<svg width="100" height="100" xmlns="http://www.w3.org/2000/svg"><defs><pattern id="grid" width="20" height="20" patternUnits="userSpaceOnUse"><path d="M 20 0 L 0 0 0 20" fill="none" stroke="rgba(255,255,255,0.1)" stroke-width="1"/></pattern></defs><rect width="100" height="100" fill="url(%23grid)"/></svg>');
            opacity: 0.3;
        }
        
        .header-content {
            position: relative;
            z-index: 1;
        }
        
        .header h1 {
            font-size: 3em;
            margin-bottom: 15px;
            font-weight: 700;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
        }
        
        .header .subtitle {
            font-size: 1.3em;
            opacity: 0.95;
            font-weight: 300;
        }
        
        .header .badge {
            display: inline-block;
            background: rgba(255,255,255,0.2);
            padding: 8px 20px;
            border-radius: 20px;
            margin-top: 15px;
            font-size: 0.9em;
            backdrop-filter: blur(10px);
        }
        
        .content {
            padding: 40px;
        }
        
        .input-section {
            background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
            padding: 40px;
            border-radius: 15px;
            margin-bottom: 30px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        }
        
        .form-group {
            margin-bottom: 25px;
        }
        
        label {
            display: block;
            font-weight: 600;
            margin-bottom: 10px;
            color: #333;
            font-size: 1.1em;
        }
        
        input[type="text"] {
            width: 100%;
            padding: 18px;
            border: 2px solid #ddd;
            border-radius: 12px;
            font-size: 16px;
            transition: all 0.3s;
            font-family: 'Inter', sans-serif;
        }
        
        input[type="text"]:focus {
            outline: none;
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }
        
        .checkbox-group {
            display: flex;
            gap: 30px;
            align-items: center;
            flex-wrap: wrap;
        }
        
        .checkbox-group label {
            display: flex;
            align-items: center;
            gap: 10px;
            margin: 0;
            cursor: pointer;
            font-weight: 500;
        }
        
        input[type="checkbox"] {
            width: 22px;
            height: 22px;
            cursor: pointer;
            accent-color: #667eea;
        }
        
        .btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 18px 40px;
            font-size: 18px;
            font-weight: 600;
            border-radius: 12px;
            cursor: pointer;
            transition: all 0.3s;
            width: 100%;
            font-family: 'Inter', sans-serif;
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
        }
        
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
        }
        
        .btn:disabled {
            background: #ccc;
            cursor: not-allowed;
            transform: none;
            box-shadow: none;
        }
        
        .btn-download {
            background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
            padding: 12px 30px;
            font-size: 16px;
            width: auto;
            display: inline-flex;
            align-items: center;
            gap: 10px;
            margin-top: 20px;
        }
        
        .btn-download:hover {
            box-shadow: 0 6px 20px rgba(17, 153, 142, 0.6);
        }
        
        .loading {
            display: none;
            text-align: center;
            padding: 60px 40px;
            background: #f8f9fa;
            border-radius: 15px;
            margin-bottom: 30px;
        }
        
        .spinner {
            border: 5px solid #f3f3f3;
            border-top: 5px solid #667eea;
            border-radius: 50%;
            width: 60px;
            height: 60px;
            animation: spin 1s linear infinite;
            margin: 0 auto 20px;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        .loading-text {
            font-size: 1.2em;
            color: #666;
            margin-top: 15px;
        }
        
        .results {
            display: none;
        }
        
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 25px;
            margin-bottom: 40px;
        }
        
        .stat-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 15px;
            text-align: center;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            transition: transform 0.3s;
        }
        
        .stat-card:hover {
            transform: translateY(-5px);
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
        
        .stat-card.info {
            background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        }
        
        .stat-value {
            font-size: 3em;
            font-weight: 700;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
        }
        
        .stat-label {
            font-size: 1.1em;
            opacity: 0.95;
            font-weight: 500;
        }
        
        .section {
            background: #ffffff;
            border: 2px solid #e9ecef;
            padding: 30px;
            border-radius: 15px;
            margin-bottom: 30px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        }
        
        .section-title {
            font-size: 1.8em;
            margin-bottom: 20px;
            color: #333;
            border-bottom: 3px solid #667eea;
            padding-bottom: 15px;
            font-weight: 700;
            display: flex;
            align-items: center;
            gap: 15px;
        }
        
        .section-title .icon {
            font-size: 1.2em;
        }
        
        .issue-list {
            max-height: 500px;
            overflow-y: auto;
        }
        
        .issue-item {
            background: #f8f9fa;
            padding: 20px;
            margin-bottom: 15px;
            border-radius: 10px;
            border-left: 5px solid #667eea;
            transition: all 0.3s;
        }
        
        .issue-item:hover {
            background: #e9ecef;
            transform: translateX(5px);
        }
        
        .issue-item.error {
            border-left-color: #f5576c;
            background: #fff5f5;
        }
        
        .issue-item.warning {
            border-left-color: #feca57;
            background: #fffbf0;
        }
        
        .url-text {
            word-break: break-all;
            font-family: 'Courier New', monospace;
            color: #555;
            margin-bottom: 8px;
            font-size: 0.95em;
            font-weight: 600;
        }
        
        .issue-text {
            color: #666;
            font-size: 0.95em;
            line-height: 1.6;
        }
        
        .recommendation {
            background: linear-gradient(135deg, #fff3cd 0%, #ffe8a1 100%);
            border-left: 5px solid #ffc107;
            padding: 20px;
            margin-bottom: 15px;
            border-radius: 10px;
            font-size: 1.05em;
            line-height: 1.7;
        }
        
        .score {
            text-align: center;
            padding: 40px;
            background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
            border-radius: 15px;
            margin-bottom: 40px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }
        
        .score-circle {
            width: 180px;
            height: 180px;
            border-radius: 50%;
            margin: 0 auto 25px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 4em;
            font-weight: 700;
            color: white;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            position: relative;
        }
        
        .score-circle::before {
            content: '/100';
            font-size: 0.3em;
            position: absolute;
            bottom: 35px;
            right: 20px;
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
        
        .score h2 {
            font-size: 2em;
            margin-bottom: 10px;
            color: #333;
        }
        
        .score p {
            font-size: 1.2em;
            color: #666;
        }
        
        .download-section {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 30px;
            border-radius: 15px;
            margin-bottom: 30px;
            color: white;
            text-align: center;
        }
        
        .download-section h3 {
            font-size: 1.5em;
            margin-bottom: 15px;
        }
        
        .download-buttons {
            display: flex;
            gap: 15px;
            justify-content: center;
            flex-wrap: wrap;
        }
        
        .footer {
            background: #f8f9fa;
            padding: 30px;
            text-align: center;
            color: #666;
            border-top: 2px solid #e9ecef;
        }
        
        .footer a {
            color: #667eea;
            text-decoration: none;
            font-weight: 600;
        }
        
        .footer a:hover {
            text-decoration: underline;
        }
        
        @media (max-width: 768px) {
            .header h1 {
                font-size: 2em;
            }
            
            .stats-grid {
                grid-template-columns: 1fr;
            }
            
            .score-circle {
                width: 150px;
                height: 150px;
                font-size: 3em;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="header-content">
                <h1>🔍 Sitemap Analyzer Pro</h1>
                <p class="subtitle">Профессиональный SEO анализ вашего sitemap.xml</p>
                <div class="badge">✨ Бесплатный инструмент by GARBUZ.ONLINE</div>
            </div>
        </div>
        
        <div class="content">
            <div class="input-section">
                <form id="analyzeForm">
                    <div class="form-group">
                        <label for="sitemapUrl">🌐 URL вашего Sitemap:</label>
                        <input type="text" id="sitemapUrl" name="sitemap_url" 
                               placeholder="https://example.com/sitemap.xml" required>
                    </div>
                    
                    <div class="form-group">
                        <div class="checkbox-group">
                            <label>
                                <input type="checkbox" id="checkStatus" name="check_status">
                                🔍 Проверять HTTP статус каждого URL (медленнее, но подробнее)
                            </label>
                        </div>
                    </div>
                    
                    <button type="submit" class="btn" id="analyzeBtn">
                        🚀 Анализировать Sitemap
                    </button>
                </form>
            </div>
            
            <div class="loading" id="loading">
                <div class="spinner"></div>
                <p class="loading-text">⏳ Анализирую sitemap...</p>
                <p style="color: #999; margin-top: 10px; font-size: 0.9em;">Это может занять от 10 секунд до нескольких минут</p>
            </div>
            
            <div class="results" id="results">
                <div class="download-section">
                    <h3>📥 Скачать отчет</h3>
                    <div class="download-buttons">
                        <button class="btn btn-download" onclick="downloadReport('txt')">
                            📄 Скачать TXT отчет
                        </button>
                        <button class="btn btn-download" onclick="downloadReport('json')">
                            📊 Скачать JSON данные
                        </button>
                        <button class="btn btn-download" onclick="downloadReport('csv')">
                            📑 Скачать CSV таблицу
                        </button>
                    </div>
                </div>
                
                <div class="stats-grid" id="statsGrid"></div>
                
                <div id="scoreSection"></div>
                
                <div class="section" id="errorsSection" style="display:none;">
                    <h2 class="section-title"><span class="icon">❌</span> Критические ошибки</h2>
                    <div class="issue-list" id="errorsList"></div>
                </div>
                
                <div class="section" id="warningsSection" style="display:none;">
                    <h2 class="section-title"><span class="icon">⚠️</span> Предупреждения</h2>
                    <div class="issue-list" id="warningsList"></div>
                </div>
                
                <div class="section" id="recommendationsSection" style="display:none;">
                    <h2 class="section-title"><span class="icon">💡</span> Рекомендации</h2>
                    <div id="recommendationsList"></div>
                </div>
            </div>
        </div>
        
        <div class="footer">
            <p>Made with ❤️ by <a href="https://garbuz.online" target="_blank">GARBUZ.ONLINE</a></p>
            <p style="margin-top: 10px; font-size: 0.9em;">
                <a href="https://github.com/your-username/sitemap-analyzer" target="_blank">GitHub</a> | 
                SEO Specialist & Web Developer
            </p>
        </div>
    </div>
    
    <script>
        let analysisData = null;
        
        document.getElementById('analyzeForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const btn = document.getElementById('analyzeBtn');
            const loading = document.getElementById('loading');
            const results = document.getElementById('results');
            
            btn.disabled = true;
            btn.textContent = '⏳ Анализирую...';
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
                analysisData = result;
                displayResults(result);
                
            } catch (error) {
                alert('❌ Ошибка при анализе: ' + error.message);
            } finally {
                btn.disabled = false;
                btn.textContent = '🚀 Анализировать Sitemap';
                loading.style.display = 'none';
                results.style.display = 'block';
                
                // Плавная прокрутка к результатам
                results.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
        });
        
        function displayResults(data) {
            // Статистика
            const statsGrid = document.getElementById('statsGrid');
            statsGrid.innerHTML = `
                <div class="stat-card">
                    <div class="stat-value">${data.statistics.total_urls || 0}</div>
                    <div class="stat-label">Всего URL</div>
                </div>
                <div class="stat-card success">
                    <div class="stat-value">${data.statistics.domain_urls || 0}</div>
                    <div class="stat-label">URL домена</div>
                </div>
                <div class="stat-card warning">
                    <div class="stat-value">${data.statistics.duplicates || 0}</div>
                    <div class="stat-label">Дубликаты</div>
                </div>
                <div class="stat-card error">
                    <div class="stat-value">${data.errors.length || 0}</div>
                    <div class="stat-label">Критических ошибок</div>
                </div>
                ${data.statistics.ok_urls !== undefined ? `
                <div class="stat-card info">
                    <div class="stat-value">${data.statistics.ok_urls || 0}</div>
                    <div class="stat-label">Доступных (200)</div>
                </div>
                ` : ''}
            `;
            
            // Оценка
            const totalIssues = data.errors.length + data.warnings.length;
            let score = Math.max(0, 100 - totalIssues);
            let scoreClass = 'score-excellent';
            let scoreText = '🎉 Отлично!';
            
            if (totalIssues > 50) {
                scoreClass = 'score-poor';
                scoreText = '⚠️ Требуется доработка';
                score = Math.max(0, 40 - (totalIssues - 50));
            } else if (totalIssues > 20) {
                scoreClass = 'score-medium';
                scoreText = '😐 Средний уровень';
                score = Math.max(40, 70 - (totalIssues - 20));
            } else if (totalIssues > 5) {
                scoreClass = 'score-good';
                scoreText = '👍 Хорошо';
                score = Math.max(70, 90 - (totalIssues - 5));
            }
            
            document.getElementById('scoreSection').innerHTML = `
                <div class="score">
                    <div class="score-circle ${scoreClass}">${score}</div>
                    <h2>${scoreText}</h2>
                    <p>Найдено проблем: ${totalIssues}</p>
                </div>
            `;
            
            // Ошибки
            if (data.errors.length > 0) {
                document.getElementById('errorsSection').style.display = 'block';
                document.getElementById('errorsList').innerHTML = data.errors.map(error => 
                    `<div class="issue-item error">
                        <div class="issue-text">❌ ${escapeHtml(error)}</div>
                    </div>`
                ).join('');
            }
            
            // Предупреждения
            if (data.warnings.length > 0) {
                document.getElementById('warningsSection').style.display = 'block';
                const warningsList = document.getElementById('warningsList');
                warningsList.innerHTML = data.warnings.slice(0, 100).map(warning => {
                    const parts = warning.split(': ');
                    return `
                        <div class="issue-item warning">
                            <div class="url-text">${escapeHtml(parts[0])}</div>
                            ${parts[1] ? `<div class="issue-text">⚠️ ${escapeHtml(parts[1])}</div>` : ''}
                        </div>
                    `;
                }).join('');
                
                if (data.warnings.length > 100) {
                    warningsList.innerHTML += `<div class="issue-item">... и еще ${data.warnings.length - 100} предупреждений</div>`;
                }
            }
            
            // Рекомендации
            if (data.recommendations.length > 0) {
                document.getElementById('recommendationsSection').style.display = 'block';
                document.getElementById('recommendationsList').innerHTML = data.recommendations.map(rec => 
                    `<div class="recommendation">${escapeHtml(rec)}</div>`
                ).join('');
            }
        }
        
        function escapeHtml(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }
        
        async function downloadReport(format) {
            if (!analysisData) {
                alert('⚠️ Нет данных для скачивания. Сначала выполните анализ.');
                return;
            }
            
            try {
                const response = await fetch(`/download/${format}`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(analysisData)
                });
                
                if (response.ok) {
                    const blob = await response.blob();
                    const url = window.URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = `sitemap_analysis_${Date.now()}.${format}`;
                    document.body.appendChild(a);
                    a.click();
                    window.URL.revokeObjectURL(url);
                    document.body.removeChild(a);
                } else {
                    alert('❌ Ошибка при скачивании отчета');
                }
            } catch (error) {
                alert('❌ Ошибка: ' + error.message);
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
            self.errors.append(f"Ошибка загрузки sitemap: {str(e)}")
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
                    url_data = {
                        'loc': loc.text.strip(),
                        'lastmod': None,
                        'changefreq': None,
                        'priority': None
                    }
                    
                    lastmod = url_element.find('ns:lastmod', namespace)
                    if lastmod is not None and lastmod.text:
                        url_data['lastmod'] = lastmod.text.strip()
                    
                    changefreq = url_element.find('ns:changefreq', namespace)
                    if changefreq is not None and changefreq.text:
                        url_data['changefreq'] = changefreq.text.strip()
                    
                    priority = url_element.find('ns:priority', namespace)
                    if priority is not None and priority.text:
                        url_data['priority'] = priority.text.strip()
                    
                    urls_data.append(url_data)
            
            self.statistics['total_urls'] += len(urlset)
            
        except Exception as e:
            self.errors.append(f"Ошибка парсинга XML: {str(e)}")
        
        return urls_data
    
    def check_url_status(self, url):
        try:
            response = requests.head(url, headers=self.headers, timeout=5, allow_redirects=False)
            return response.status_code
        except:
            try:
                response = requests.get(url, headers=self.headers, timeout=5, allow_redirects=False, stream=True)
                return response.status_code
            except:
                return 0
    
    def analyze(self, check_status=False):
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
                self.warnings.append(f"{url}: Внешний домен ({url_domain})")
                self.statistics['external_urls'] = self.statistics.get('external_urls', 0) + 1
            else:
                self.statistics['domain_urls'] += 1
            
            # Проверка HTTP статуса
            if check_status and url_domain == self.domain:
                status = self.check_url_status(url)
                if status == 200:
                    self.statistics['ok_urls'] = self.statistics.get('ok_urls', 0) + 1
                elif status in [301, 302, 307, 308]:
                    self.warnings.append(f"{url}: Редирект ({status})")
                    self.statistics['redirects'] = self.statistics.get('redirects', 0) + 1
                elif status >= 400:
                    self.warnings.append(f"{url}: Ошибка HTTP {status}")
                    self.statistics['error_urls'] = self.statistics.get('error_urls', 0) + 1
                elif status == 0:
                    self.warnings.append(f"{url}: URL недоступен")
                    self.statistics['error_urls'] = self.statistics.get('error_urls', 0) + 1
        
        # Генерация рекомендаций
        if self.statistics['duplicates'] > 0:
            self.recommendations.append(f"⚠️ Удалите {self.statistics['duplicates']} дубликатов URL из sitemap")
        
        if self.statistics.get('external_urls', 0) > 0:
            self.recommendations.append(f"⚠️ Удалите {self.statistics['external_urls']} внешних URL из sitemap")
        
        if self.statistics.get('redirects', 0) > 0:
            self.recommendations.append(f"⚠️ Замените {self.statistics['redirects']} URL с редиректами на финальные адреса")
        
        if self.statistics.get('error_urls', 0) > 0:
            self.recommendations.append(f"❌ Удалите {self.statistics['error_urls']} недоступных URL из sitemap")
        
        if self.statistics['total_urls'] > 50000:
            self.recommendations.append(f"⚠️ Sitemap содержит {self.statistics['total_urls']} URL (лимит 50,000). Разбейте на несколько файлов и используйте Sitemap Index")
        
        if not self.errors and not self.warnings:
            self.recommendations.append("✅ Отлично! Sitemap не содержит критических ошибок")
    
    def get_results(self):
        return {
            'statistics': dict(self.statistics),
            'errors': self.errors,
            'warnings': self.warnings,
            'recommendations': self.recommendations,
            'urls': self.urls
        }

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.get_json()
    sitemap_url = data.get('sitemap_url')
    check_status = data.get('check_status', False)
    
    if not sitemap_url:
        return jsonify({'error': 'URL не указан'}), 400
    
    analyzer = WebSitemapAnalyzer(sitemap_url)
    analyzer.analyze(check_status=check_status)
    
    results = analyzer.get_results()
    
    # Сохраняем последний анализ
    global last_analysis
    last_analysis = results
    
    return jsonify(results)

@app.route('/download/<format>', methods=['POST'])
def download(format):
    data = request.get_json()
    
    if not data:
        return "No data", 400
    
    if format == 'txt':
        # Генерация TXT отчета
        output = io.StringIO()
        output.write("="*80 + "\n")
        output.write("ОТЧЕТ ПО АНАЛИЗУ SITEMAP\n")
        output.write("="*80 + "\n\n")
        output.write(f"Дата: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        output.write("СТАТИСТИКА:\n")
        for key, value in data['statistics'].items():
            output.write(f"  • {key}: {value}\n")
        
        output.write("\n" + "="*80 + "\n")
        output.write("КРИТИЧЕСКИЕ ОШИБКИ:\n")
        output.write("="*80 + "\n")
        for error in data['errors']:
            output.write(f"❌ {error}\n")
        
        output.write("\n" + "="*80 + "\n")
        output.write("ПРЕДУПРЕЖДЕНИЯ:\n")
        output.write("="*80 + "\n")
        for warning in data['warnings'][:200]:
            output.write(f"⚠️  {warning}\n")
        
        output.write("\n" + "="*80 + "\n")
        output.write("РЕКОМЕНДАЦИИ:\n")
        output.write("="*80 + "\n")
        for rec in data['recommendations']:
            output.write(f"💡 {rec}\n")
        
        bytes_io = io.BytesIO(output.getvalue().encode('utf-8'))
        bytes_io.seek(0)
        return send_file(bytes_io, mimetype='text/plain', as_attachment=True, 
                        download_name=f'sitemap_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt')
    
    elif format == 'json':
        # Генерация JSON
        bytes_io = io.BytesIO(json.dumps(data, indent=2, ensure_ascii=False).encode('utf-8'))
        bytes_io.seek(0)
        return send_file(bytes_io, mimetype='application/json', as_attachment=True,
                        download_name=f'sitemap_data_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json')
    
    elif format == 'csv':
        # Генерация CSV
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['URL', 'Last Modified', 'Change Frequency', 'Priority', 'Issues'])
        
        # Создаем словарь проблем для каждого URL
        url_issues = defaultdict(list)
        for warning in data['warnings']:
            if ': ' in warning:
                url, issue = warning.split(': ', 1)
                url_issues[url].append(issue)
        
        for url_data in data.get('urls', [])[:1000]:
            url = url_data['loc']
            issues = ', '.join(url_issues.get(url, []))
            writer.writerow([
                url,
                url_data.get('lastmod', ''),
                url_data.get('changefreq', ''),
                url_data.get('priority', ''),
                issues
            ])
        
        bytes_io = io.BytesIO(output.getvalue().encode('utf-8-sig'))
        bytes_io.seek(0)
        return send_file(bytes_io, mimetype='text/csv', as_attachment=True,
                        download_name=f'sitemap_urls_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv')
    
    return "Invalid format", 400

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    print(f"""
╔═══════════════════════════════════════════════════════════════╗
║         🌐 SITEMAP ANALYZER PRO - WEB INTERFACE              ║
╚═══════════════════════════════════════════════════════════════╝

✨ Запуск веб-сервера...
🔗 Откройте браузер: http://localhost:{port}

Новые возможности:
✅ Полный вывод всех результатов
✅ Скачивание отчетов (TXT, JSON, CSV)
✅ Профессиональный дизайн
✅ Адаптивная верстка
    """)
    app.run(host='0.0.0.0', port=port, debug=False)
