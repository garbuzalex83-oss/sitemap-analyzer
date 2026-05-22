#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SEO PARSER PRO - Web Interface
Modern, intuitive web UI for professional SEO analysis
"""

from flask import Flask, render_template_string, request, jsonify, send_file
import threading
import os
from seo_parser_pro import SEOAnalyzerPro, ReportGenerator
from datetime import datetime
import io

app = Flask(__name__)
analyzer = SEOAnalyzerPro()

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SEO Parser PRO - Professional SEO Analysis Tool</title>
    <style>
        :root {
            --primary: #3b82f6;
            --primary-dark: #1d4ed8;
            --success: #10b981;
            --warning: #f59e0b;
            --danger: #ef4444;
            --gray-50: #f9fafb;
            --gray-100: #f3f4f6;
            --gray-200: #e5e7eb;
            --gray-300: #d1d5db;
            --gray-700: #374151;
            --gray-900: #111827;
        }
        
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 2rem;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
        }
        
        .header {
            text-align: center;
            color: white;
            margin-bottom: 3rem;
        }
        
        .header h1 {
            font-size: 3rem;
            font-weight: 800;
            margin-bottom: 0.5rem;
            text-shadow: 0 2px 10px rgba(0,0,0,0.2);
        }
        
        .header p {
            font-size: 1.2rem;
            opacity: 0.9;
        }
        
        .main-card {
            background: white;
            border-radius: 1.5rem;
            padding: 3rem;
            box-shadow: 0 20px 50px rgba(0,0,0,0.3);
            margin-bottom: 2rem;
        }
        
        .form-group {
            margin-bottom: 2rem;
        }
        
        .form-label {
            display: block;
            font-weight: 600;
            color: var(--gray-700);
            margin-bottom: 0.5rem;
            font-size: 1.1rem;
        }
        
        .form-input {
            width: 100%;
            padding: 1rem 1.5rem;
            border: 2px solid var(--gray-200);
            border-radius: 0.75rem;
            font-size: 1.1rem;
            transition: all 0.3s;
        }
        
        .form-input:focus {
            outline: none;
            border-color: var(--primary);
            box-shadow: 0 0 0 4px rgba(59, 130, 246, 0.1);
        }
        
        .btn {
            display: inline-block;
            padding: 1rem 2.5rem;
            background: linear-gradient(135deg, var(--primary), var(--primary-dark));
            color: white;
            border: none;
            border-radius: 0.75rem;
            font-size: 1.1rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
            text-decoration: none;
        }
        
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(59, 130, 246, 0.3);
        }
        
        .btn:disabled {
            opacity: 0.6;
            cursor: not-allowed;
            transform: none;
        }
        
        .features-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 1.5rem;
            margin-top: 2rem;
        }
        
        .feature-card {
            background: var(--gray-50);
            padding: 1.5rem;
            border-radius: 1rem;
            border-left: 4px solid var(--primary);
        }
        
        .feature-card h3 {
            color: var(--gray-900);
            margin-bottom: 0.5rem;
            font-size: 1.1rem;
        }
        
        .feature-card p {
            color: var(--gray-700);
            font-size: 0.95rem;
            line-height: 1.5;
        }
        
        .results-section {
            display: none;
            background: white;
            border-radius: 1.5rem;
            padding: 3rem;
            box-shadow: 0 20px 50px rgba(0,0,0,0.3);
        }
        
        .results-section.active {
            display: block;
        }
        
        .score-display {
            text-align: center;
            padding: 2rem;
            background: linear-gradient(135deg, var(--primary), var(--primary-dark));
            border-radius: 1rem;
            color: white;
            margin-bottom: 2rem;
        }
        
        .score-value {
            font-size: 5rem;
            font-weight: 800;
            line-height: 1;
        }
        
        .score-grade {
            font-size: 2rem;
            font-weight: 700;
            margin-top: 0.5rem;
        }
        
        .scores-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 1rem;
            margin-bottom: 2rem;
        }
        
        .score-item {
            background: var(--gray-50);
            padding: 1.5rem;
            border-radius: 0.75rem;
            text-align: center;
        }
        
        .score-item-value {
            font-size: 2rem;
            font-weight: 700;
            color: var(--primary);
        }
        
        .score-item-label {
            color: var(--gray-700);
            font-size: 0.9rem;
            margin-top: 0.5rem;
        }
        
        .issues-list {
            margin-top: 2rem;
        }
        
        .issue-card {
            padding: 1.5rem;
            margin-bottom: 1rem;
            border-radius: 0.75rem;
            border-left: 4px solid var(--danger);
            background: #fef2f2;
        }
        
        .issue-card.medium {
            border-color: var(--warning);
            background: #fefce8;
        }
        
        .issue-card.low {
            border-color: var(--gray-300);
            background: var(--gray-50);
        }
        
        .issue-title {
            font-weight: 700;
            color: var(--gray-900);
            margin-bottom: 0.5rem;
        }
        
        .issue-desc {
            color: var(--gray-700);
            margin-bottom: 0.5rem;
        }
        
        .issue-recommendation {
            color: var(--primary-dark);
            font-weight: 600;
        }
        
        .loading {
            display: none;
            text-align: center;
            padding: 3rem;
        }
        
        .loading.active {
            display: block;
        }
        
        .spinner {
            border: 4px solid var(--gray-200);
            border-top: 4px solid var(--primary);
            border-radius: 50%;
            width: 50px;
            height: 50px;
            animation: spin 1s linear infinite;
            margin: 0 auto 1rem;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        .export-buttons {
            display: flex;
            gap: 1rem;
            margin-top: 2rem;
            flex-wrap: wrap;
        }
        
        .btn-outline {
            background: white;
            color: var(--primary);
            border: 2px solid var(--primary);
        }
        
        .btn-outline:hover {
            background: var(--primary);
            color: white;
        }
        
        .keyword-cloud {
            display: flex;
            flex-wrap: wrap;
            gap: 0.5rem;
            margin-top: 1rem;
        }
        
        .keyword-tag {
            padding: 0.5rem 1rem;
            background: #dbeafe;
            border-radius: 2rem;
            font-size: 0.9rem;
            color: var(--primary-dark);
            font-weight: 600;
        }
        
        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 1rem;
        }
        
        th, td {
            padding: 0.75rem;
            text-align: left;
            border-bottom: 1px solid var(--gray-200);
        }
        
        th {
            background: var(--gray-50);
            font-weight: 600;
            color: var(--gray-900);
        }
        
        .status-ok { color: var(--success); }
        .status-warning { color: var(--warning); }
        .status-error { color: var(--danger); }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔍 SEO Parser PRO</h1>
            <p>Professional SEO Analysis Tool with Advanced Relevance Cloud</p>
        </div>
        
        <div class="main-card">
            <div class="form-group">
                <label class="form-label">Website URL</label>
                <input type="url" id="urlInput" class="form-input" placeholder="https://example.com" value="https://example.com">
            </div>
            
            <button onclick="analyzeSEO()" class="btn" id="analyzeBtn">
                🚀 Start Comprehensive SEO Analysis
            </button>
            
            <div class="features-grid">
                <div class="feature-card">
                    <h3>☁️ Content Relevance Cloud</h3>
                    <p>TF-IDF analysis, semantic clustering, keyword density with position weighting</p>
                </div>
                <div class="feature-card">
                    <h3>⚡ Technical SEO Audit</h3>
                    <p>Core Web Vitals, HTTPS, mobile-friendliness, crawlability checks</p>
                </div>
                <div class="feature-card">
                    <h3>📝 On-Page Optimization</h3>
                    <p>Meta tags, headers hierarchy, Schema.org, Open Graph validation</p>
                </div>
                <div class="feature-card">
                    <h3>🔗 Link Architecture</h3>
                    <p>Internal/external links, anchor distribution, link juice flow</p>
                </div>
                <div class="feature-card">
                    <h3>🌍 GEO Optimization</h3>
                    <p>LocalBusiness schema, NAP consistency, Google Maps integration</p>
                </div>
                <div class="feature-card">
                    <h3>🏆 E-E-A-T Signals</h3>
                    <p>Author credentials, publication dates, trust signals detection</p>
                </div>
            </div>
        </div>
        
        <div class="loading" id="loading">
            <div class="spinner"></div>
            <h3 style="color: white; font-size: 1.5rem;">Analyzing your website...</h3>
            <p style="color: white; opacity: 0.9; margin-top: 0.5rem;">This may take up to 30 seconds</p>
        </div>
        
        <div class="results-section" id="results">
            <div class="score-display">
                <div class="score-value" id="totalScore">0</div>
                <div class="score-grade" id="gradeLabel">F</div>
                <div style="margin-top: 1rem; opacity: 0.9;">Overall SEO Score</div>
            </div>
            
            <h2 style="margin-bottom: 1rem; color: var(--gray-900);">Score Breakdown</h2>
            <div class="scores-grid" id="scoresGrid">
                <!-- Populated dynamically -->
            </div>
            
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 2rem; margin-top: 2rem;">
                <div>
                    <h2 style="margin-bottom: 1rem; color: var(--gray-900);">📋 Technical SEO</h2>
                    <table id="technicalTable">
                        <!-- Populated dynamically -->
                    </table>
                </div>
                <div>
                    <h2 style="margin-bottom: 1rem; color: var(--gray-900);">📝 On-Page Elements</h2>
                    <table id="onpageTable">
                        <!-- Populated dynamically -->
                    </table>
                </div>
            </div>
            
            <div style="margin-top: 2rem;">
                <h2 style="margin-bottom: 1rem; color: var(--gray-900);">☁️ Content Relevance Cloud</h2>
                <div id="relevanceMetrics"></div>
                <div class="keyword-cloud" id="keywordCloud"></div>
            </div>
            
            <div class="issues-list" id="issuesList">
                <h2 style="margin-bottom: 1rem; color: var(--gray-900);">⚠️ Issues Found</h2>
                <!-- Populated dynamically -->
            </div>
            
            <div class="export-buttons">
                <button onclick="exportReport('html')" class="btn">📄 Export HTML</button>
                <button onclick="exportReport('json')" class="btn btn-outline">📊 Export JSON</button>
                <button onclick="exportReport('csv')" class="btn btn-outline">📑 Export CSV</button>
            </div>
        </div>
    </div>
    
    <script>
        let currentResults = null;
        
        async function analyzeSEO() {
            const url = document.getElementById('urlInput').value.trim();
            if (!url) {
                alert('Please enter a valid URL');
                return;
            }
            
            document.getElementById('analyzeBtn').disabled = true;
            document.getElementById('loading').classList.add('active');
            document.getElementById('results').classList.remove('active');
            
            try {
                const response = await fetch('/api/analyze', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ url: url })
                });
                
                const data = await response.json();
                
                if (data.error) {
                    alert('Error: ' + data.error);
                    return;
                }
                
                currentResults = data;
                displayResults(data);
                
            } catch (error) {
                alert('Analysis failed: ' + error.message);
            } finally {
                document.getElementById('analyzeBtn').disabled = false;
                document.getElementById('loading').classList.remove('active');
            }
        }
        
        function displayResults(data) {
            document.getElementById('results').classList.add('active');
            
            // Total score
            document.getElementById('totalScore').textContent = data.score.total_score;
            document.getElementById('gradeLabel').textContent = 'Grade: ' + data.score.grade;
            
            // Scores grid
            const scoresGrid = document.getElementById('scoresGrid');
            scoresGrid.innerHTML = `
                <div class="score-item">
                    <div class="score-item-value">${data.score.technical_score.toFixed(1)}</div>
                    <div class="score-item-label">Technical</div>
                </div>
                <div class="score-item">
                    <div class="score-item-value">${data.score.onpage_score.toFixed(1)}</div>
                    <div class="score-item-label">On-Page</div>
                </div>
                <div class="score-item">
                    <div class="score-item-value">${data.score.content_score.toFixed(1)}</div>
                    <div class="score-item-label">Content</div>
                </div>
                <div class="score-item">
                    <div class="score-item-value">${data.score.relevance_score.toFixed(1)}</div>
                    <div class="score-item-label">Relevance</div>
                </div>
                <div class="score-item">
                    <div class="score-item-value">${data.score.geo_score.toFixed(1)}</div>
                    <div class="score-item-label">GEO</div>
                </div>
                <div class="score-item">
                    <div class="score-item-value">${data.score.eeat_score.toFixed(1)}</div>
                    <div class="score-item-label">E-E-A-T</div>
                </div>
            `;
            
            // Technical table
            const techTable = document.getElementById('technicalTable');
            techTable.innerHTML = `
                <tr><th>Metric</th><th>Value</th><th>Status</th></tr>
                <tr><td>HTTPS</td><td>${data.technical.https_enabled ? 'Yes' : 'No'}</td>
                    <td class="${data.technical.https_enabled ? 'status-ok' : 'status-error'}">${data.technical.https_enabled ? '✓' : '✗'}</td></tr>
                <tr><td>HTTP Status</td><td>${data.technical.http_status}</td>
                    <td class="${data.technical.http_status == 200 ? 'status-ok' : 'status-error'}">${data.technical.http_status == 200 ? '✓' : '✗'}</td></tr>
                <tr><td>Response Time</td><td>${data.technical.response_time_ms}ms</td>
                    <td class="${data.technical.response_time_ms < 1000 ? 'status-ok' : 'status-warning'}">${data.technical.response_time_ms < 1000 ? '✓' : '⚠'}</td></tr>
                <tr><td>Mobile Viewport</td><td>${data.technical.mobile_viewport ? 'Yes' : 'No'}</td>
                    <td class="${data.technical.mobile_viewport ? 'status-ok' : 'status-error'}">${data.technical.mobile_viewport ? '✓' : '✗'}</td></tr>
                <tr><td>Canonical URL</td><td>${data.technical.canonical_url ? 'Present' : 'Missing'}</td>
                    <td class="${data.technical.canonical_url ? 'status-ok' : 'status-warning'}">${data.technical.canonical_url ? '✓' : '⚠'}</td></tr>
            `;
            
            // On-page table
            const onpageTable = document.getElementById('onpageTable');
            onpageTable.innerHTML = `
                <tr><th>Element</th><th>Value</th></tr>
                <tr><td>Title</td><td>${data.onpage.title || 'Missing'}</td></tr>
                <tr><td>Title Length</td><td>${data.onpage.title_length} chars</td></tr>
                <tr><td>H1 Tags</td><td>${data.onpage.h1_tags.length}</td></tr>
                <tr><td>H2 Tags</td><td>${data.onpage.h2_tags.length}</td></tr>
                <tr><td>Images</td><td>${data.onpage.images_count} (${data.onpage.images_with_alt} with alt)</td></tr>
                <tr><td>Internal Links</td><td>${data.onpage.internal_links_count}</td></tr>
                <tr><td>Schema.org</td><td>${data.onpage.schema_org.length} schemas</td></tr>
            `;
            
            // Relevance metrics
            const relevanceDiv = document.getElementById('relevanceMetrics');
            relevanceDiv.innerHTML = `
                <table>
                    <tr><th>Metric</th><th>Value</th></tr>
                    <tr><td>Word Count</td><td>${data.relevance.word_count}</td></tr>
                    <tr><td>Quality Score</td><td>${data.relevance.content_quality_score}/100</td></tr>
                    <tr><td>Lexical Diversity</td><td>${data.relevance.lexical_diversity.toFixed(2)}</td></tr>
                    <tr><td>Avg Sentence Length</td><td>${data.relevance.avg_sentence_length.toFixed(1)} words</td></tr>
                </table>
            `;
            
            // Keyword cloud
            const keywordCloud = document.getElementById('keywordCloud');
            const keywords = Object.values(data.relevance.keyword_density || {})
                .sort((a, b) => b.density - a.density)
                .slice(0, 15);
            
            keywordCloud.innerHTML = keywords.map(kw => 
                `<span class="keyword-tag">${kw.keyword} (${kw.density}%)</span>`
            ).join('');
            
            // Issues list
            const issuesList = document.getElementById('issuesList');
            const criticalIssues = data.issues.filter(i => ['critical', 'high'].includes(i.severity));
            
            if (criticalIssues.length > 0) {
                issuesList.innerHTML = '<h2 style="margin-bottom: 1rem; color: var(--gray-900);">⚠️ Issues Found (' + criticalIssues.length + ')</h2>' +
                    criticalIssues.slice(0, 10).map(issue => `
                        <div class="issue-card ${issue.severity === 'medium' ? 'medium' : issue.severity === 'low' ? 'low' : ''}">
                            <div class="issue-title">${issue.title}</div>
                            <div class="issue-desc">${issue.description}</div>
                            <div class="issue-recommendation">💡 ${issue.recommendation}</div>
                        </div>
                    `).join('');
            } else {
                issuesList.innerHTML = '<h2 style="margin-bottom: 1rem; color: var(--gray-900);">✅ No Critical Issues Found!</h2>';
            }
            
            // Scroll to results
            document.getElementById('results').scrollIntoView({ behavior: 'smooth' });
        }
        
        async function exportReport(format) {
            if (!currentResults) return;
            
            try {
                const response = await fetch('/api/export', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ 
                        results: currentResults,
                        format: format
                    })
                });
                
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `seo_report_${new Date().getTime()}.${format}`;
                a.click();
                window.URL.revokeObjectURL(url);
            } catch (error) {
                alert('Export failed: ' + error.message);
            }
        }
        
        // Allow Enter key to trigger analysis
        document.getElementById('urlInput').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                analyzeSEO();
            }
        });
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/analyze', methods=['POST'])
def api_analyze():
    data = request.get_json()
    url = data.get('url')
    
    if not url:
        return jsonify({'error': 'URL is required'}), 400
    
    if not url.startswith('http'):
        url = 'https://' + url
    
    try:
        results = analyzer.analyze(url)
        
        if 'error' in results:
            return jsonify(results), 400
        
        return jsonify(results)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/export', methods=['POST'])
def api_export():
    data = request.get_json()
    results = data.get('results')
    format = data.get('format', 'html')
    
    if not results:
        return jsonify({'error': 'Results data required'}), 400
    
    try:
        generator = ReportGenerator()
        
        if format.lower() == 'html':
            content = generator.generate_html_report(results['url'], results)
            mimetype = 'text/html'
        elif format.lower() == 'json':
            content = generator.generate_json_report(results)
            mimetype = 'application/json'
        elif format.lower() == 'csv':
            content = generator.generate_csv_report(results)
            mimetype = 'text/csv'
        else:
            return jsonify({'error': 'Unsupported format'}), 400
        
        return send_file(
            io.BytesIO(content.encode()),
            mimetype=mimetype,
            as_attachment=True,
            download_name=f"seo_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{format}"
        )
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def run_server():
    print("\n" + "=" * 60)
    print("🚀 SEO Parser PRO - Web Interface")
    print("=" * 60)
    print("\n📱 Open your browser and navigate to:")
    print("   http://localhost:5000")
    print("\nPress Ctrl+C to stop the server\n")
    print("=" * 60)
    
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)

if __name__ == '__main__':
    run_server()
