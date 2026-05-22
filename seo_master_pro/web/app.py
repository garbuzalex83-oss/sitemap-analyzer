"""
SEO Master PRO - Web Interface
Современный веб-интерфейс для профессионального SEO-аудита
"""

import os
import sys
import json
import asyncio
from datetime import datetime
from typing import Optional, Dict, Any
from pathlib import Path

from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn

# Добавляем родительскую директорию в путь
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.core_crawler import SiteCrawler, SitemapAnalyzer, RobotsTxtAnalyzer
from modules.meta_auditor import MetaTagsAuditor
from modules.commercial_auditor import CommercialFactorsAuditor
from modules.js_renderer_analyzer import JavaScriptSEOAnalyzer as JSRendererAnalyzer
from modules.report_builder import ReportBuilder

app = FastAPI(
    title="SEO Master PRO",
    description="Профессиональная система SEO-аудита уровня Enterprise",
    version="2.0.0"
)

# Пути
BASE_DIR = Path(__file__).parent
TEMPLATES_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"
REPORTS_DIR = BASE_DIR.parent / "reports"

# Создаем директории если не существуют
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

# Подключаем шаблоны и статику
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# Глобальное хранилище результатов (в памяти)
audit_results: Dict[str, Dict[str, Any]] = {}


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Главная страница"""
    return templates.TemplateResponse("index.html", {
        "request": request,
        "title": "SEO Master PRO - Профессиональный SEO Аудит"
    })


@app.post("/api/audit/start")
async def start_audit(
    url: str = Form(...),
    max_pages: int = Form(default=50),
    max_depth: int = Form(default=3),
    check_commercial: bool = Form(default=True),
    check_js: bool = Form(default=True),
    check_sitemap: bool = Form(default=True),
    check_robots: bool = Form(default=True)
):
    """Запуск полного аудита сайта"""
    
    # Валидация URL
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    audit_id = f"audit_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    try:
        results = {
            "audit_id": audit_id,
            "url": url,
            "started_at": datetime.now().isoformat(),
            "status": "running",
            "progress": 0,
            "crawler": {},
            "sitemap": {},
            "robots": {},
            "meta": {},
            "commercial": {},
            "js": {},
            "scores": {}
        }
        
        # 1. Краулер
        crawler = SiteCrawler(max_pages=max_pages, max_depth=max_depth)
        crawl_data = await asyncio.to_thread(crawler.crawl, url)
        results["crawler"] = crawl_data
        results["progress"] = 20
        
        # 2. Sitemap Analyzer
        if check_sitemap:
            sitemap_analyzer = SitemapAnalyzer()
            sitemap_data = await asyncio.to_thread(sitemap_analyzer.analyze, url)
            results["sitemap"] = sitemap_data
            results["progress"] = 40
        
        # 3. Robots.txt Analyzer
        if check_robots:
            robots_analyzer = RobotsTxtAnalyzer()
            robots_data = await asyncio.to_thread(robots_analyzer.analyze, url)
            results["robots"] = robots_data
            results["progress"] = 50
        
        # 4. Meta Tags Auditor (на первой странице)
        if crawl_data.get("pages"):
            first_page = crawl_data["pages"][0]
            meta_auditor = MetaTagsAuditor()
            meta_data = await asyncio.to_thread(meta_auditor.audit_page, first_page["url"])
            results["meta"] = meta_data
            results["progress"] = 70
        
        # 5. Commercial Factors Auditor
        if check_commercial and crawl_data.get("pages"):
            first_page = crawl_data["pages"][0]
            commercial_auditor = CommercialFactorsAuditor()
            commercial_data = await asyncio.to_thread(commercial_auditor.audit, first_page["html"], first_page["url"])
            results["commercial"] = commercial_data
            results["progress"] = 85
        
        # 6. JS Renderer Analyzer
        if check_js and crawl_data.get("pages"):
            first_page = crawl_data["pages"][0]
            js_analyzer = JSRendererAnalyzer()
            js_data = await asyncio.to_thread(js_analyzer.analyze_url, first_page["url"])
            results["js"] = js_data
            results["progress"] = 95
        
        # Расчет общих оценок
        scores = calculate_scores(results)
        results["scores"] = scores
        results["completed_at"] = datetime.now().isoformat()
        results["status"] = "completed"
        results["progress"] = 100
        
        # Сохраняем результаты
        audit_results[audit_id] = results
        
        # Генерируем отчет
        report_builder = ReportBuilder()
        report_path = await asyncio.to_thread(
            report_builder.generate_html_report,
            results,
            output_dir=str(REPORTS_DIR)
        )
        results["report_path"] = str(report_path)
        
        return JSONResponse({
            "success": True,
            "audit_id": audit_id,
            "message": "Аудит успешно завершен",
            "scores": scores
        })
        
    except Exception as e:
        return JSONResponse({
            "success": False,
            "error": str(e),
            "audit_id": audit_id
        }, status_code=500)


def calculate_scores(results: Dict) -> Dict:
    """Расчет комплексных оценок SEO"""
    
    scores = {
        "technical": 0,
        "onpage": 0,
        "commercial": 0,
        "js": 0,
        "overall": 0
    }
    
    # Technical Score (краулер + sitemap + robots)
    tech_points = 0
    tech_max = 0
    
    if results.get("crawler"):
        crawler = results["crawler"]
        tech_max += 100
        
        # Штрафы за ошибки
        error_404 = crawler.get("summary", {}).get("errors_404", 0)
        error_500 = crawler.get("summary", {}).get("errors_500", 0)
        redirects = crawler.get("summary", {}).get("redirects", 0)
        
        tech_points += max(0, 100 - (error_404 * 5) - (error_500 * 10) - (redirects * 2))
    
    if results.get("robots"):
        robots = results["robots"]
        tech_max += 100
        issues = len(robots.get("issues", []))
        tech_points += max(0, 100 - (issues * 10))
    
    if tech_max > 0:
        scores["technical"] = round(tech_points / tech_max * 100)
    
    # On-Page Score (meta tags)
    if results.get("meta"):
        meta = results["meta"]
        scores["onpage"] = meta.get("score", 0)
    
    # Commercial Score
    if results.get("commercial"):
        commercial = results["commercial"]
        scores["commercial"] = commercial.get("commercial_score", 0)
    
    # JS Score
    if results.get("js"):
        js = results["js"]
        scores["js"] = js.get("compatibility_score", 100)
    
    # Overall Score (средневзвешенное)
    total = (
        scores["technical"] * 0.35 +
        scores["onpage"] * 0.25 +
        scores["commercial"] * 0.25 +
        scores["js"] * 0.15
    )
    scores["overall"] = round(total)
    
    return scores


@app.get("/api/audit/{audit_id}")
async def get_audit_results(audit_id: str):
    """Получение результатов аудита"""
    if audit_id not in audit_results:
        raise HTTPException(status_code=404, detail="Аудит не найден")
    
    return JSONResponse(audit_results[audit_id])


@app.get("/dashboard/{audit_id}", response_class=HTMLResponse)
async def dashboard(request: Request, audit_id: str):
    """Дашборд с результатами аудита"""
    if audit_id not in audit_results:
        raise HTTPException(status_code=404, detail="Аудит не найден")
    
    results = audit_results[audit_id]
    
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "title": f"Дашборд - {results['url']}",
        "results": results,
        "audit_id": audit_id
    })


@app.get("/reports/{filename}")
async def get_report(filename: str):
    """Получение сгенерированного отчета"""
    report_path = REPORTS_DIR / filename
    if not report_path.exists():
        raise HTTPException(status_code=404, detail="Отчет не найден")
    
    return FileResponse(report_path, media_type="text/html")


@app.get("/api/projects")
async def get_projects():
    """Список всех проектов/аудитов"""
    projects = []
    for audit_id, data in audit_results.items():
        projects.append({
            "audit_id": audit_id,
            "url": data.get("url"),
            "completed_at": data.get("completed_at"),
            "overall_score": data.get("scores", {}).get("overall", 0)
        })
    
    return JSONResponse({"projects": projects})


if __name__ == "__main__":
    print("\n" + "="*60)
    print("🚀 SEO Master PRO - Веб-интерфейс запускается...")
    print("="*60)
    print("\n📊 Откройте в браузере: http://localhost:8000")
    print("\n⚙️  Функционал:")
    print("   ✓ Полный SEO аудит сайта")
    print("   ✓ Анализ коммерческих факторов")
    print("   ✓ Проверка JS рендеринга")
    print("   ✓ Анализ sitemap.xml и robots.txt")
    print("   ✓ Drag-and-Drop конструктор отчетов")
    print("   ✓ Превью сниппетов Google")
    print("\n" + "="*60 + "\n")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)
