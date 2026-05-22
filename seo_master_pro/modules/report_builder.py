"""
SEO Master PRO - Drag-and-Drop конструктор White-Label отчетов
Позволяет создавать кастомные отчеты с перетаскиванием блоков
"""

import json
from typing import Dict, List, Optional
from dataclasses import dataclass, field, asdict
from enum import Enum
from datetime import datetime


class ReportBlockType(Enum):
    """Типы блоков отчета"""
    HEADER = "header"
    SUMMARY = "summary"
    SCORE_CARD = "score_card"
    META_TAGS = "meta_tags"
    SNIPPET_PREVIEW = "snippet_preview"
    HEADINGS = "headings"
    COMMERCIAL_FACTORS = "commercial_factors"
    JS_RENDERING = "js_rendering"
    TECHNICAL_ISSUES = "technical_issues"
    RECOMMENDATIONS = "recommendations"
    CHART = "chart"
    TABLE = "table"
    TEXT = "text"
    IMAGE = "image"
    FOOTER = "footer"


@dataclass
class ReportBlock:
    """Блок отчета"""
    block_id: str
    block_type: ReportBlockType
    title: str
    content: Dict
    position: int
    enabled: bool = True
    settings: Dict = field(default_factory=dict)


@dataclass
class ReportTemplate:
    """Шаблон отчета"""
    template_id: str
    name: str
    description: str
    blocks: List[ReportBlock]
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    is_default: bool = False


class ReportBuilder:
    """
    Конструктор отчетов с поддержкой Drag-and-Drop
    Позволяет создавать white-label отчеты
    """
    
    DEFAULT_TEMPLATES = {
        'technical_audit': {
            'name': 'Технический аудит',
            'description': 'Полный технический SEO аудит сайта',
            'blocks': ['header', 'summary', 'score_card', 'technical_issues', 'recommendations', 'footer']
        },
        'onpage_seo': {
            'name': 'On-Page SEO анализ',
            'description': 'Аudit мета-тегов, заголовков и контента',
            'blocks': ['header', 'meta_tags', 'snippet_preview', 'headings', 'recommendations', 'footer']
        },
        'ecommerce': {
            'name': 'E-commerce аудит',
            'description': 'Анализ коммерческих факторов интернет-магазина',
            'blocks': ['header', 'summary', 'commercial_factors', 'score_card', 'recommendations', 'footer']
        },
        'js_seo': {
            'name': 'JavaScript SEO аудит',
            'description': 'Проверка рендеринга и индексации JS-контента',
            'blocks': ['header', 'js_rendering', 'technical_issues', 'recommendations', 'footer']
        },
        'full_report': {
            'name': 'Полный SEO отчет',
            'description': 'Комплексный анализ всех аспектов SEO',
            'blocks': ['header', 'summary', 'score_card', 'meta_tags', 'snippet_preview', 'headings', 
                      'commercial_factors', 'js_rendering', 'technical_issues', 'recommendations', 'footer']
        }
    }
    
    def __init__(self):
        self.templates: Dict[str, ReportTemplate] = {}
        self.custom_templates: List[ReportTemplate] = []
        self._load_default_templates()
    
    def _load_default_templates(self):
        """Загружает шаблоны по умолчанию"""
        for template_id, config in self.DEFAULT_TEMPLATES.items():
            blocks = []
            for idx, block_type in enumerate(config['blocks']):
                block = ReportBlock(
                    block_id=f"{block_type}_{idx}",
                    block_type=ReportBlockType(block_type),
                    title=self._get_block_title(block_type),
                    content={},
                    position=idx,
                    enabled=True
                )
                blocks.append(block)
            
            template = ReportTemplate(
                template_id=template_id,
                name=config['name'],
                description=config['description'],
                blocks=blocks,
                is_default=True
            )
            self.templates[template_id] = template
    
    def _get_block_title(self, block_type: str) -> str:
        """Возвращает заголовок для типа блока"""
        titles = {
            'header': 'Заголовок отчета',
            'summary': 'Краткое резюме',
            'score_card': 'Оценки и метрики',
            'meta_tags': 'Анализ мета-тегов',
            'snippet_preview': 'Превью сниппета в Google',
            'headings': 'Структура заголовков',
            'commercial_factors': 'Коммерческие факторы',
            'js_rendering': 'JavaScript рендеринг',
            'technical_issues': 'Технические проблемы',
            'recommendations': 'Рекомендации',
            'chart': 'График',
            'table': 'Таблица',
            'text': 'Текстовый блок',
            'image': 'Изображение',
            'footer': 'Подвал отчета'
        }
        return titles.get(block_type, block_type)
    
    def create_custom_template(self, 
                               name: str, 
                               description: str,
                               block_types: List[str]) -> ReportTemplate:
        """
        Создает пользовательский шаблон отчета
        
        Args:
            name: Название шаблона
            description: Описание
            block_types: Список типов блоков в нужном порядке
            
        Returns:
            ReportTemplate
        """
        blocks = []
        for idx, block_type in enumerate(block_types):
            if block_type in [bt.value for bt in ReportBlockType]:
                block = ReportBlock(
                    block_id=f"custom_{block_type}_{idx}",
                    block_type=ReportBlockType(block_type),
                    title=self._get_block_title(block_type),
                    content={},
                    position=idx,
                    enabled=True
                )
                blocks.append(block)
        
        template = ReportTemplate(
            template_id=f"custom_{len(self.custom_templates) + 1}",
            name=name,
            description=description,
            blocks=blocks
        )
        
        self.custom_templates.append(template)
        return template
    
    def reorder_blocks(self, template_id: str, new_order: List[str]) -> bool:
        """
        Меняет порядок блоков (Drag-and-Drop)
        
        Args:
            template_id: ID шаблона
            new_order: Новый порядок блоков по block_id
            
        Returns:
            bool: Успешность операции
        """
        template = self.get_template(template_id)
        if not template:
            return False
        
        # Создаем карту block_id -> block
        block_map = {b.block_id: b for b in template.blocks}
        
        # Пересортировываем
        new_blocks = []
        for idx, block_id in enumerate(new_order):
            if block_id in block_map:
                block = block_map[block_id]
                block.position = idx
                new_blocks.append(block)
        
        template.blocks = sorted(new_blocks, key=lambda b: b.position)
        return True
    
    def toggle_block(self, template_id: str, block_id: str, enabled: bool) -> bool:
        """Включает/выключает блок в шаблоне"""
        template = self.get_template(template_id)
        if not template:
            return False
        
        for block in template.blocks:
            if block.block_id == block_id:
                block.enabled = enabled
                return True
        
        return False
    
    def update_block_settings(self, 
                             template_id: str, 
                             block_id: str, 
                             settings: Dict) -> bool:
        """Обновляет настройки блока"""
        template = self.get_template(template_id)
        if not template:
            return False
        
        for block in template.blocks:
            if block.block_id == block_id:
                block.settings.update(settings)
                return True
        
        return False
    
    def get_template(self, template_id: str) -> Optional[ReportTemplate]:
        """Получает шаблон по ID"""
        if template_id in self.templates:
            return self.templates[template_id]
        
        for template in self.custom_templates:
            if template.template_id == template_id:
                return template
        
        return None
    
    def list_templates(self) -> List[Dict]:
        """Возвращает список всех шаблонов"""
        all_templates = list(self.templates.values()) + self.custom_templates
        
        return [
            {
                'template_id': t.template_id,
                'name': t.name,
                'description': t.description,
                'blocks_count': len(t.blocks),
                'is_default': t.is_default,
                'created_at': t.created_at
            }
            for t in all_templates
        ]
    
    def generate_report(self, 
                       template_id: str,
                       audit_data: Dict,
                       branding: Optional[Dict] = None) -> Dict:
        """
        Генерирует отчет на основе шаблона и данных аудита
        
        Args:
            template_id: ID шаблона
            audit_data: Данные из модулей аудита
            branding: Брендирование (logo, colors, company_name)
            
        Returns:
            Dict с готовым отчетом
        """
        template = self.get_template(template_id)
        if not template:
            return {'error': 'Шаблон не найден'}
        
        report = {
            'report_id': f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            'generated_at': datetime.now().isoformat(),
            'template': {
                'id': template.template_id,
                'name': template.name
            },
            'branding': branding or {},
            'sections': [],
            'summary': self._generate_summary(audit_data),
            'overall_score': self._calculate_overall_score(audit_data)
        }
        
        # Генерируем секции на основе блоков
        for block in template.blocks:
            if not block.enabled:
                continue
            
            section = self._render_block(block, audit_data, branding)
            if section:
                report['sections'].append(section)
        
        return report
    
    def _render_block(self, 
                     block: ReportBlock, 
                     audit_data: Dict, 
                     branding: Optional[Dict]) -> Optional[Dict]:
        """Рендерит блок отчета"""
        
        if block.block_type == ReportBlockType.HEADER:
            return {
                'type': 'header',
                'title': audit_data.get('url', 'SEO Отчет'),
                'subtitle': f"Дата аудита: {datetime.now().strftime('%d.%m.%Y')}",
                'branding': branding,
                'settings': block.settings
            }
        
        elif block.block_type == ReportBlockType.SUMMARY:
            return {
                'type': 'summary',
                'title': 'Краткое резюме',
                'content': self._generate_summary(audit_data),
                'settings': block.settings
            }
        
        elif block.block_type == ReportBlockType.SCORE_CARD:
            scores = self._extract_scores(audit_data)
            return {
                'type': 'score_card',
                'title': 'Оценки и метрики',
                'scores': scores,
                'overall': self._calculate_overall_score(audit_data),
                'settings': block.settings
            }
        
        elif block.block_type == ReportBlockType.META_TAGS:
            meta_data = audit_data.get('meta_tags', {})
            return {
                'type': 'meta_tags',
                'title': 'Анализ мета-тегов',
                'data': meta_data,
                'issues': meta_data.get('issues', []),
                'settings': block.settings
            }
        
        elif block.block_type == ReportBlockType.SNIPPET_PREVIEW:
            meta_data = audit_data.get('meta_tags', {})
            if 'snippet' in audit_data:
                snippet = audit_data['snippet']
            else:
                # Генерируем превью
                from modules.meta_auditor import MetaTagsAuditor
                auditor = MetaTagsAuditor()
                snippet = auditor.generate_snippet_preview(
                    meta_data.get('title', {}).get('value'),
                    meta_data.get('description', {}).get('value'),
                    audit_data.get('url', '')
                )
            
            return {
                'type': 'snippet_preview',
                'title': 'Превью сниппета в Google',
                'snippet': snippet,
                'settings': block.settings
            }
        
        elif block.block_type == ReportBlockType.HEADINGS:
            headings = audit_data.get('meta_tags', {}).get('headings', {})
            structure_score = audit_data.get('meta_tags', {}).get('structure_score', 0)
            return {
                'type': 'headings',
                'title': 'Структура заголовков',
                'headings': headings,
                'structure_score': structure_score,
                'settings': block.settings
            }
        
        elif block.block_type == ReportBlockType.COMMERCIAL_FACTORS:
            commercial = audit_data.get('commercial', {})
            return {
                'type': 'commercial_factors',
                'title': 'Коммерческие факторы',
                'commercial_score': commercial.get('commercial_score', 0),
                'trust_score': commercial.get('trust_score', 0),
                'elements_found': commercial.get('elements_found', []),
                'elements_missing': commercial.get('elements_missing', []),
                'conversion_readiness': commercial.get('conversion_readiness', 'unknown'),
                'settings': block.settings
            }
        
        elif block.block_type == ReportBlockType.JS_RENDERING:
            js_data = audit_data.get('javascript', {})
            return {
                'type': 'js_rendering',
                'title': 'JavaScript рендеринг',
                'render_score': js_data.get('render_seo_score', 0),
                'googlebot_compatibility': js_data.get('googlebot_compatibility', {}),
                'differences': js_data.get('differences', []),
                'issues': js_data.get('issues', []),
                'settings': block.settings
            }
        
        elif block.block_type == ReportBlockType.TECHNICAL_ISSUES:
            # Собираем все проблемы из разных модулей
            all_issues = []
            
            if 'meta_tags' in audit_data:
                all_issues.extend(audit_data['meta_tags'].get('issues', []))
            
            if 'commercial' in audit_data:
                all_issues.extend(audit_data['commercial'].get('issues', []))
            
            if 'javascript' in audit_data:
                all_issues.extend(audit_data['javascript'].get('issues', []))
            
            if 'crawl' in audit_data:
                all_issues.extend(audit_data['crawl'].get('issues', []))
            
            # Группируем по приоритету
            issues_by_priority = {
                'critical': [],
                'high': [],
                'medium': [],
                'low': []
            }
            
            for issue in all_issues:
                priority = issue.get('priority', 'low')
                if isinstance(priority, dict):
                    priority = priority.get('value', 'low')
                
                if priority in issues_by_priority:
                    issues_by_priority[priority].append(issue)
            
            return {
                'type': 'technical_issues',
                'title': 'Технические проблемы',
                'total_issues': len(all_issues),
                'by_priority': issues_by_priority,
                'critical_count': len(issues_by_priority['critical']),
                'high_count': len(issues_by_priority['high']),
                'settings': block.settings
            }
        
        elif block.block_type == ReportBlockType.RECOMMENDATIONS:
            recommendations = self._generate_recommendations(audit_data)
            return {
                'type': 'recommendations',
                'title': 'Рекомендации',
                'recommendations': recommendations,
                'settings': block.settings
            }
        
        elif block.block_type == ReportBlockType.FOOTER:
            return {
                'type': 'footer',
                'company_name': branding.get('company_name', 'SEO Master PRO'),
                'contact_info': branding.get('contact_info', ''),
                'disclaimer': block.settings.get('disclaimer', 'Отчет сгенерирован автоматически'),
                'settings': block.settings
            }
        
        return None
    
    def _generate_summary(self, audit_data: Dict) -> Dict:
        """Генерирует краткое резюме"""
        overall_score = self._calculate_overall_score(audit_data)
        
        # Определяем статус
        if overall_score >= 80:
            status = 'excellent'
            status_text = 'Отличное состояние'
            color = '#22c55e'
        elif overall_score >= 60:
            status = 'good'
            status_text = 'Хорошее состояние'
            color = '#3b82f6'
        elif overall_score >= 40:
            status = 'needs_improvement'
            status_text = 'Требует улучшений'
            color = '#f59e0b'
        else:
            status = 'critical'
            status_text = 'Критическое состояние'
            color = '#ef4444'
        
        # Подсчет проблем
        total_issues = 0
        critical_issues = 0
        
        for module in ['meta_tags', 'commercial', 'javascript', 'crawl']:
            if module in audit_data:
                total_issues += audit_data[module].get('total_issues', 0)
                critical_issues += audit_data[module].get('critical_count', 0)
        
        return {
            'overall_score': overall_score,
            'status': status,
            'status_text': status_text,
            'color': color,
            'total_issues': total_issues,
            'critical_issues': critical_issues,
            'url': audit_data.get('url', 'Unknown'),
            'audit_date': datetime.now().strftime('%d.%m.%Y %H:%M')
        }
    
    def _calculate_overall_score(self, audit_data: Dict) -> int:
        """Рассчитывает общую оценку SEO"""
        scores = []
        weights = []
        
        # Meta Tags (вес 25%)
        if 'meta_tags' in audit_data:
            structure_score = audit_data['meta_tags'].get('structure_score', 0)
            scores.append(structure_score)
            weights.append(25)
        
        # Commercial Factors (вес 25%)
        if 'commercial' in audit_data:
            comm_score = audit_data['commercial'].get('commercial_score', 0)
            scores.append(comm_score)
            weights.append(25)
        
        # JavaScript Rendering (вес 20%)
        if 'javascript' in audit_data:
            js_score = audit_data['javascript'].get('render_seo_score', 0)
            scores.append(js_score)
            weights.append(20)
        
        # Crawl (вес 30%)
        if 'crawl' in audit_data:
            crawl_score = audit_data['crawl'].get('seo_score', 70)
            scores.append(crawl_score)
            weights.append(30)
        
        if not scores:
            return 50  # Оценка по умолчанию
        
        # Взвешенное среднее
        total_weight = sum(weights)
        weighted_sum = sum(s * w for s, w in zip(scores, weights))
        
        return int(weighted_sum / total_weight)
    
    def _extract_scores(self, audit_data: Dict) -> List[Dict]:
        """Извлекает все оценки из данных аудита"""
        scores = []
        
        if 'meta_tags' in audit_data:
            scores.append({
                'name': 'Мета-теги',
                'score': audit_data['meta_tags'].get('structure_score', 0),
                'max_score': 100
            })
        
        if 'commercial' in audit_data:
            scores.append({
                'name': 'Коммерческие факторы',
                'score': audit_data['commercial'].get('commercial_score', 0),
                'max_score': 100
            })
            scores.append({
                'name': 'Доверие',
                'score': audit_data['commercial'].get('trust_score', 0),
                'max_score': 100
            })
        
        if 'javascript' in audit_data:
            scores.append({
                'name': 'JS Рендеринг',
                'score': audit_data['javascript'].get('render_seo_score', 0),
                'max_score': 100
            })
        
        return scores
    
    def _generate_recommendations(self, audit_data: Dict) -> List[Dict]:
        """Генерирует сводные рекомендации"""
        recommendations = []
        
        # Из meta_tags
        if 'meta_tags' in audit_data:
            for issue in audit_data['meta_tags'].get('issues', [])[:3]:
                if issue.get('priority') in ['critical', 'high']:
                    recommendations.append({
                        'priority': issue.get('priority', 'medium'),
                        'category': 'Мета-теги',
                        'action': issue.get('recommendation', ''),
                        'impact': 'Высокое'
                    })
        
        # Из commercial
        if 'commercial' in audit_data:
            for rec in audit_data['commercial'].get('recommendations', [])[:3]:
                recommendations.append({
                    'priority': rec.get('priority', 'medium'),
                    'category': 'E-commerce',
                    'action': rec.get('action', ''),
                    'impact': rec.get('impact', '')
                })
        
        # Из javascript
        if 'javascript' in audit_data:
            for rec in audit_data['javascript'].get('recommendations', [])[:3]:
                recommendations.append({
                    'priority': rec.get('priority', 'medium'),
                    'category': 'JavaScript',
                    'action': rec.get('description', ''),
                    'impact': rec.get('impact', '')
                })
        
        # Сортируем по приоритету
        priority_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
        recommendations.sort(key=lambda x: priority_order.get(x.get('priority', 'low'), 3))
        
        return recommendations[:10]  # Топ 10 рекомендаций
    
    def export_to_html(self, report: Dict) -> str:
        """Экспортирует отчет в HTML формат"""
        html = f"""
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SEO Отчет - {report.get('summary', {}).get('url', 'Unknown')}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 40px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .header {{ text-align: center; padding-bottom: 30px; border-bottom: 2px solid #eee; margin-bottom: 30px; }}
        .score-card {{ display: flex; gap: 20px; margin: 20px 0; }}
        .score-item {{ flex: 1; padding: 20px; border-radius: 8px; text-align: center; background: #f8f9fa; }}
        .score-value {{ font-size: 48px; font-weight: bold; color: #3b82f6; }}
        .section {{ margin: 30px 0; padding: 20px; border: 1px solid #e5e7eb; border-radius: 8px; }}
        .section-title {{ font-size: 24px; margin-bottom: 15px; color: #1f2937; }}
        .issue {{ padding: 15px; margin: 10px 0; border-left: 4px solid #ef4444; background: #fef2f2; }}
        .issue.critical {{ border-color: #dc2626; }}
        .issue.high {{ border-color: #ea580c; }}
        .issue.medium {{ border-color: #ca8a04; }}
        .issue.low {{ border-color: #2563eb; }}
        .snippet-preview {{ border: 1px solid #ddd; padding: 15px; border-radius: 8px; max-width: 600px; }}
        .snippet-url {{ color: #202124; font-size: 14px; margin-bottom: 5px; }}
        .snippet-title {{ color: #1a0dab; font-size: 20px; margin-bottom: 5px; }}
        .snippet-desc {{ color: #545454; font-size: 14px; line-height: 1.58; }}
        .recommendation {{ padding: 15px; margin: 10px 0; background: #f0f9ff; border-radius: 8px; }}
        .footer {{ text-align: center; padding-top: 30px; border-top: 2px solid #eee; margin-top: 40px; color: #6b7280; }}
    </style>
</head>
<body>
    <div class="container">
"""
        
        # Рендерим секции
        for section in report.get('sections', []):
            html += self._render_section_html(section)
        
        html += """
    </div>
</body>
</html>
"""
        return html
    
    def _render_section_html(self, section: Dict) -> str:
        """Рендерит секцию в HTML"""
        section_type = section.get('type', '')
        
        if section_type == 'header':
            branding = section.get('branding', {})
            logo_html = f'<img src="{branding.get("logo", "")}" alt="Logo" style="height: 50px; margin-bottom: 20px;">' if branding.get('logo') else ''
            return f"""
        <div class="header">
            {logo_html}
            <h1>{section.get('title', 'SEO Отчет')}</h1>
            <p>{section.get('subtitle', '')}</p>
        </div>
"""
        
        elif section_type == 'summary':
            summary = section.get('content', {})
            return f"""
        <div class="section">
            <h2 class="section-title">Краткое резюме</h2>
            <div class="score-card">
                <div class="score-item" style="background: {summary.get('color', '#3b82f6')}20;">
                    <div class="score-value" style="color: {summary.get('color', '#3b82f6')}">{summary.get('overall_score', 0)}</div>
                    <div>Общая оценка</div>
                </div>
                <div class="score-item">
                    <div class="score-value">{summary.get('total_issues', 0)}</div>
                    <div>Всего проблем</div>
                </div>
                <div class="score-item">
                    <div class="score-value" style="color: #ef4444">{summary.get('critical_issues', 0)}</div>
                    <div>Критических</div>
                </div>
            </div>
            <p><strong>Статус:</strong> {summary.get('status_text', '')}</p>
            <p><strong>URL:</strong> {summary.get('url', '')}</p>
        </div>
"""
        
        elif section_type == 'snippet_preview':
            snippet = section.get('snippet', {})
            return f"""
        <div class="section">
            <h2 class="section-title">Как страница видится в Google</h2>
            <div class="snippet-preview">
                <div class="snippet-url">{snippet.get('domain', '')}</div>
                <div class="snippet-title">{snippet.get('title', '')}</div>
                <div class="snippet-desc">{snippet.get('description', '')}</div>
            </div>
        </div>
"""
        
        elif section_type == 'technical_issues':
            by_priority = section.get('by_priority', {})
            issues_html = ''
            
            for priority in ['critical', 'high', 'medium', 'low']:
                issues = by_priority.get(priority, [])
                for issue in issues[:5]:  # Показываем топ 5 каждой категории
                    issues_html += f"""
                <div class="issue {priority}">
                    <strong>[{priority.upper()}]</strong> {issue.get('message', '')}<br>
                    <em>Решение:</em> {issue.get('recommendation', '')}
                </div>
"""
            
            return f"""
        <div class="section">
            <h2 class="section-title">Технические проблемы ({section.get('total_issues', 0)})</h2>
            {issues_html}
        </div>
"""
        
        elif section_type == 'recommendations':
            recs = section.get('recommendations', [])
            recs_html = ''
            
            for rec in recs:
                recs_html += f"""
                <div class="recommendation">
                    <strong>[{rec.get('priority', '').upper()}] {rec.get('category', '')}</strong><br>
                    {rec.get('action', '')}<br>
                    <em>Влияние:</em> {rec.get('impact', '')}
                </div>
"""
            
            return f"""
        <div class="section">
            <h2 class="section-title">Рекомендации</h2>
            {recs_html}
        </div>
"""
        
        elif section_type == 'footer':
            return f"""
        <div class="footer">
            <p>{section.get('company_name', 'SEO Master PRO')}</p>
            <p>{section.get('disclaimer', 'Отчет сгенерирован автоматически')}</p>
        </div>
"""
        
        return ''
    
    def export_to_json(self, report: Dict) -> str:
        """Экспортирует отчет в JSON формат"""
        # Кастомный encoder для обработки Enum
        class ReportEncoder(json.JSONEncoder):
            def default(self, obj):
                if isinstance(obj, Enum):
                    return obj.value
                return super().default(obj)
        
        return json.dumps(report, ensure_ascii=False, indent=2, cls=ReportEncoder)


# Пример использования
if __name__ == "__main__":
    builder = ReportBuilder()
    
    print("=" * 80)
    print("DRAG-AND-DROP КОНСТРУКТОР ОТЧЕТОВ")
    print("=" * 80)
    
    # Список шаблонов
    print("\nДоступные шаблоны:")
    for template in builder.list_templates():
        print(f"  - {template['name']} ({template['blocks_count']} блоков)")
    
    # Создание пользовательского шаблона
    custom = builder.create_custom_template(
        name="Быстрый аудит",
        description="Минимальный отчет для быстрой проверки",
        block_types=['header', 'summary', 'score_card', 'technical_issues', 'footer']
    )
    print(f"\n✓ Создан шаблон: {custom.name}")
    
    # Тестовые данные аудита
    test_audit_data = {
        'url': 'https://example.com/product/nike-air-max',
        'meta_tags': {
            'structure_score': 75,
            'title': {'value': 'Купить кроссовки Nike', 'length': 25},
            'description': {'value': 'Лучшие кроссовки Nike', 'length': 20},
            'headings': {'h1': ['Nike Air Max'], 'h2': ['Характеристики', 'Отзывы']},
            'issues': [
                {'priority': 'medium', 'message': 'Title слишком короткий', 'recommendation': 'Увеличьте Title'}
            ],
            'total_issues': 1,
            'critical_count': 0
        },
        'commercial': {
            'commercial_score': 85,
            'trust_score': 70,
            'elements_found': [{'element_type': 'PRICE'}, {'element_type': 'BUY_BUTTON'}],
            'elements_missing': [],
            'conversion_readiness': 'good',
            'issues': [],
            'total_issues': 0,
            'critical_count': 0,
            'recommendations': []
        },
        'javascript': {
            'render_seo_score': 65,
            'googlebot_compatibility': {'level': 'fair', 'message': 'Есть проблемы'},
            'differences': [],
            'issues': [
                {'severity': 'high', 'message': 'Title изменился после рендеринга', 'recommendation': 'Добавьте Title в HTML'}
            ],
            'total_issues': 1,
            'critical_count': 0,
            'recommendations': [{'priority': 'high', 'description': 'Добавьте критический контент в HTML', 'impact': 'SEO'}]
        },
        'crawl': {
            'seo_score': 80,
            'issues': [],
            'total_issues': 0,
            'critical_count': 0
        }
    }
    
    # Генерация отчета
    print("\n" + "=" * 80)
    print("ГЕНЕРАЦИЯ ОТЧЕТА")
    print("=" * 80)
    
    report = builder.generate_report(
        template_id='full_report',
        audit_data=test_audit_data,
        branding={
            'company_name': 'My SEO Agency',
            'logo': 'https://example.com/logo.png',
            'contact_info': 'info@seoagency.com | +1 234 567 8900'
        }
    )
    
    print(f"\n✓ Отчет сгенерирован: {report['report_id']}")
    print(f"  Шаблон: {report['template']['name']}")
    print(f"  Секций: {len(report['sections'])}")
    print(f"  Общая оценка: {report['overall_score']}/100")
    print(f"  Статус: {report['summary']['status_text']}")
    
    # Экспорт в HTML
    html_report = builder.export_to_html(report)
    print(f"\n✓ HTML отчет создан ({len(html_report)} байт)")
    
    # Сохранение HTML
    with open('/workspace/seo_master_pro/reports/sample_report.html', 'w', encoding='utf-8') as f:
        f.write(html_report)
    print("✓ Отчет сохранен: /workspace/seo_master_pro/reports/sample_report.html")
    
    # Экспорт в JSON
    json_report = builder.export_to_json(report)
    print(f"\n✓ JSON отчет создан ({len(json_report)} байт)")
