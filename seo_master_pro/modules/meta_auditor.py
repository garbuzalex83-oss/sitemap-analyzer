"""
SEO Master PRO - Модуль анализа мета-тегов и заголовков
Профессиональный аудит Title, Description, H1-H6 с интеллектуальной оценкой
"""

import re
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum


class IssuePriority(Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class MetaIssue:
    """Проблема с мета-тегами"""
    url: str
    issue_type: str
    priority: IssuePriority
    message: str
    recommendation: str
    current_value: Optional[str] = None
    expected_value: Optional[str] = None


class MetaTagsAuditor:
    """
    Профессиональный аудитор мета-тегов
    Проверяет Title, Description, H1-H6 по всем правилам Google
    """
    
    # Оптимальные длины
    TITLE_MIN_LENGTH = 30
    TITLE_MAX_LENGTH = 60
    TITLE_MAX_PIXELS = 580
    
    DESCRIPTION_MIN_LENGTH = 70
    DESCRIPTION_MAX_LENGTH = 160
    DESCRIPTION_MAX_PIXELS = 920
    
    # Шаблоны для разных типов страниц
    TITLE_PATTERNS = {
        'product': r'{product_name} - купить в {city} | {brand}',
        'category': r'{category_name} в {city} - цены, отзывы | {brand}',
        'article': r'{title} | {brand}',
        'homepage': r'{brand} - {tagline}',
        'brand': r'{brand_name} - каталог товаров | {company}',
        'tag': r'Все материалы по тегу "{tag}" | {brand}',
    }
    
    def __init__(self):
        self.issues: List[MetaIssue] = []
        
    def analyze_page(self, url: str, html: str, page_type: str = 'unknown') -> Dict:
        """
        Полный анализ мета-тегов страницы
        
        Args:
            url: URL страницы
            html: HTML контент
            page_type: Тип страницы (product, category, article, etc.)
            
        Returns:
            Dict с результатами анализа и проблемами
        """
        self.issues = []
        
        # Извлечение мета-тегов
        title = self._extract_title(html)
        description = self._extract_description(html)
        headings = self._extract_headings(html)
        h1_count = len(headings.get('h1', []))
        
        result = {
            'url': url,
            'page_type': page_type,
            'title': {
                'value': title,
                'length': len(title) if title else 0,
                'status': self._check_title_length(title),
                'issues': []
            },
            'description': {
                'value': description,
                'length': len(description) if description else 0,
                'status': self._check_description_length(description),
                'issues': []
            },
            'headings': headings,
            'h1_status': self._check_h1(h1_count, title),
            'structure_score': self._calculate_structure_score(headings),
            'issues': []
        }
        
        # Проверка Title
        title_issues = self._validate_title(url, title, page_type)
        result['title']['issues'] = [i.__dict__ for i in title_issues]
        self.issues.extend(title_issues)
        
        # Проверка Description
        desc_issues = self._validate_description(url, description, title)
        result['description']['issues'] = [i.__dict__ for i in desc_issues]
        self.issues.extend(desc_issues)
        
        # Проверка заголовков
        heading_issues = self._validate_headings(url, headings, title)
        result['headings']['issues'] = [i.__dict__ for i in heading_issues]
        self.issues.extend(heading_issues)
        
        # Добавляем все проблемы в результат
        result['issues'] = [i.__dict__ for i in self.issues]
        result['total_issues'] = len(self.issues)
        result['critical_count'] = len([i for i in self.issues if i.priority == IssuePriority.CRITICAL])
        result['high_count'] = len([i for i in self.issues if i.priority == IssuePriority.HIGH])
        
        return result
    
    def _extract_title(self, html: str) -> str:
        """Извлекает Title из HTML"""
        match = re.search(r'<title[^>]*>(.*?)</title>', html, re.IGNORECASE | re.DOTALL)
        if match:
            return re.sub(r'\s+', ' ', match.group(1).strip())
        return ""
    
    def _extract_description(self, html: str) -> str:
        """Извлекает meta description из HTML"""
        match = re.search(r'<meta[^>]*name=["\']description["\'][^>]*content=["\']([^"\']*)["\']', html, re.IGNORECASE)
        if not match:
            match = re.search(r'<meta[^>]*content=["\']([^"\']*)["\'][^>]*name=["\']description["\']', html, re.IGNORECASE)
        if match:
            return match.group(1).strip()
        return ""
    
    def _extract_headings(self, html: str) -> Dict[str, List[str]]:
        """Извлекает все заголовки H1-H6"""
        headings = {f'h{i}': [] for i in range(1, 7)}
        
        for i in range(1, 7):
            pattern = f'<h{i}[^>]*>(.*?)</h{i}>'
            matches = re.findall(pattern, html, re.IGNORECASE | re.DOTALL)
            headings[f'h{i}'] = [re.sub(r'\s+', ' ', m.strip()) for m in matches]
        
        return headings
    
    def _check_title_length(self, title: Optional[str]) -> str:
        """Проверяет длину Title"""
        if not title:
            return "missing"
        
        length = len(title)
        
        if length < self.TITLE_MIN_LENGTH:
            return "too_short"
        elif length > self.TITLE_MAX_LENGTH:
            return "too_long"
        else:
            return "optimal"
    
    def _check_description_length(self, description: Optional[str]) -> str:
        """Проверяет длину Description"""
        if not description:
            return "missing"
        
        length = len(description)
        
        if length < self.DESCRIPTION_MIN_LENGTH:
            return "too_short"
        elif length > self.DESCRIPTION_MAX_LENGTH:
            return "too_long"
        else:
            return "optimal"
    
    def _check_h1(self, h1_count: int, title: Optional[str]) -> Dict:
        """Проверяет наличие и корректность H1"""
        result = {
            'count': h1_count,
            'status': 'optimal',
            'issues': []
        }
        
        if h1_count == 0:
            result['status'] = 'missing'
        elif h1_count > 1:
            result['status'] = 'multiple'
        
        # Проверка дублирования с Title
        if h1_count == 1 and title:
            # Упрощенная проверка (можно усложнить)
            pass
        
        return result
    
    def _calculate_structure_score(self, headings: Dict) -> int:
        """
        Рассчитывает оценку структуры заголовков (0-100)
        
        Критерии:
        - Наличие H1: +30
        - Один H1: +10 (если больше одного, то 0)
        - Логичная иерархия: +30
        - Наличие H2: +15
        - Нет пропусков уровней: +15
        """
        score = 0
        
        h1_count = len(headings.get('h1', []))
        if h1_count > 0:
            score += 30
            if h1_count == 1:
                score += 10
        
        # Проверка иерархии
        has_h2 = len(headings.get('h2', [])) > 0
        if has_h2:
            score += 15
        
        # Проверка пропусков уровней
        levels_present = [i for i in range(1, 7) if len(headings.get(f'h{i}', [])) > 0]
        if levels_present:
            max_level = max(levels_present)
            expected_levels = list(range(1, max_level + 1))
            
            if all(level in levels_present for level in expected_levels):
                score += 15
            else:
                # Штраф за пропуски
                score += 5
        
        # Дополнительный бонус за хорошую структуру
        if h1_count == 1 and has_h2 and len(headings.get('h3', [])) > 0:
            score += 15
        
        return min(score, 100)
    
    def _validate_title(self, url: str, title: Optional[str], page_type: str) -> List[MetaIssue]:
        """Валидация Title с генерацией проблем"""
        issues = []
        
        if not title:
            issues.append(MetaIssue(
                url=url,
                issue_type="missing_title",
                priority=IssuePriority.CRITICAL,
                message="Отсутствует Title tag",
                recommendation="Добавьте уникальный Title для каждой страницы. Это критически важно для SEO.",
                expected_value=f"Рекомендуемый формат для {page_type}: {self.TITLE_PATTERNS.get(page_type, '{keyword} | {brand}')}"
            ))
            return issues
        
        length = len(title)
        
        if length < self.TITLE_MIN_LENGTH:
            issues.append(MetaIssue(
                url=url,
                issue_type="short_title",
                priority=IssuePriority.MEDIUM,
                message=f"Title слишком короткий ({length} символов)",
                recommendation=f"Оптимальная длина Title: {self.TITLE_MIN_LENGTH}-{self.TITLE_MAX_LENGTH} символов. Добавьте ключевые слова и УТП.",
                current_value=title,
                expected_value=f"{self.TITLE_MIN_LENGTH}-{self.TITLE_MAX_LENGTH} символов"
            ))
        
        if length > self.TITLE_MAX_LENGTH:
            issues.append(MetaIssue(
                url=url,
                issue_type="long_title",
                priority=IssuePriority.MEDIUM,
                message=f"Title слишком длинный ({length} символов). В поиске он будет обрезан.",
                recommendation=f"Сократите Title до {self.TITLE_MAX_LENGTH} символов. Важную информацию разместите в начале.",
                current_value=title,
                expected_value=f"Максимум {self.TITLE_MAX_LENGTH} символов"
            ))
        
        # Проверка на дублирование слов (переспам)
        words = title.lower().split()
        word_counts = {}
        for word in words:
            if len(word) > 3:  # Игнорируем короткие слова
                word_counts[word] = word_counts.get(word, 0) + 1
        
        repeated_words = [w for w, c in word_counts.items() if c > 2]
        if repeated_words:
            issues.append(MetaIssue(
                url=url,
                issue_type="title_spam",
                priority=IssuePriority.HIGH,
                message=f"Обнаружен переспам в Title: слова '{', '.join(repeated_words)}' повторяются более 2 раз",
                recommendation="Уберите повторяющиеся ключевые слова. Title должен быть естественным и читаемым.",
                current_value=title
            ))
        
        # Проверка на наличие заглавных букв (все caps)
        if title.isupper() and len(title) > 10:
            issues.append(MetaIssue(
                url=url,
                issue_type="title_all_caps",
                priority=IssuePriority.LOW,
                message="Title написан полностью заглавными буквами",
                recommendation="Используйте нормальный регистр. Заглавные буквы могут восприниматься как спам.",
                current_value=title
            ))
        
        return issues
    
    def _validate_description(self, url: str, description: Optional[str], title: Optional[str]) -> List[MetaIssue]:
        """Валидация Description"""
        issues = []
        
        if not description:
            priority = IssuePriority.HIGH if title else IssuePriority.MEDIUM
            issues.append(MetaIssue(
                url=url,
                issue_type="missing_description",
                priority=priority,
                message="Отсутствует meta description",
                recommendation="Добавьте уникальное описание для каждой страницы. Это влияет на CTR в поисковой выдаче.",
                expected_value=f"{self.DESCRIPTION_MIN_LENGTH}-{self.DESCRIPTION_MAX_LENGTH} символов с призывом к действию"
            ))
            return issues
        
        length = len(description)
        
        if length < self.DESCRIPTION_MIN_LENGTH:
            issues.append(MetaIssue(
                url=url,
                issue_type="short_description",
                priority=IssuePriority.LOW,
                message=f"Description слишком короткий ({length} символов)",
                recommendation=f"Расширьте описание до {self.DESCRIPTION_MIN_LENGTH}-{self.DESCRIPTION_MAX_LENGTH} символов. Добавьте ключевые слова и преимущества.",
                current_value=description,
                expected_value=f"{self.DESCRIPTION_MIN_LENGTH}-{self.DESCRIPTION_MAX_LENGTH} символов"
            ))
        
        if length > self.DESCRIPTION_MAX_LENGTH:
            issues.append(MetaIssue(
                url=url,
                issue_type="long_description",
                priority=IssuePriority.LOW,
                message=f"Description слишком длинный ({length} символов). В поиске он будет обрезан.",
                recommendation=f"Сократите описание до {self.DESCRIPTION_MAX_LENGTH} символов. Важную информацию разместите в начале.",
                current_value=description,
                expected_value=f"Максимум {self.DESCRIPTION_MAX_LENGTH} символов"
            ))
        
        # Проверка на дублирование с Title
        if title and description.lower().startswith(title.lower()):
            issues.append(MetaIssue(
                url=url,
                issue_type="desc_duplicates_title",
                priority=IssuePriority.MEDIUM,
                message="Description начинается с точной копии Title",
                recommendation="Сделайте Description уникальным. Он должен дополнять Title, а не дублировать его.",
                current_value=description[:100] + "..."
            ))
        
        return issues
    
    def _validate_headings(self, url: str, headings: Dict, title: Optional[str]) -> List[MetaIssue]:
        """Валидация структуры заголовков"""
        issues = []
        
        h1_list = headings.get('h1', [])
        h1_count = len(h1_list)
        
        # Проверка наличия H1
        if h1_count == 0:
            issues.append(MetaIssue(
                url=url,
                issue_type="missing_h1",
                priority=IssuePriority.HIGH,
                message="Отсутствует заголовок H1",
                recommendation="Добавьте один уникальный H1 на страницу. Это основной заголовок, который помогает поисковым системам понять содержание.",
                expected_value="Один H1 с основным ключевым запросом"
            ))
        
        # Проверка множественных H1
        if h1_count > 1:
            issues.append(MetaIssue(
                url=url,
                issue_type="multiple_h1",
                priority=IssuePriority.MEDIUM,
                message=f"Найдено {h1_count} заголовков H1 (должен быть один)",
                recommendation="Оставьте только один H1 на странице. Остальные понизьте до H2 или H3.",
                current_value=f"Найдены H1: {', '.join(h1_list[:3])}{'...' if h1_count > 3 else ''}"
            ))
        
        # Проверка пустых заголовков
        for level in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            for idx, heading in enumerate(headings.get(level, [])):
                if not heading or heading.strip() == '':
                    issues.append(MetaIssue(
                        url=url,
                        issue_type=f"empty_{level}",
                        priority=IssuePriority.MEDIUM,
                        message=f"Пустой заголовок {level.upper()}",
                        recommendation="Заполните заголовок содержимым или удалите пустой тег.",
                        current_value=f"<{level}></{level}>"
                    ))
        
        # Проверка пропусков уровней иерархии
        levels_present = [i for i in range(1, 7) if len(headings.get(f'h{i}', [])) > 0]
        if levels_present:
            for i in range(len(levels_present) - 1):
                if levels_present[i+1] - levels_present[i] > 1:
                    missing_level = levels_present[i] + 1
                    issues.append(MetaIssue(
                        url=url,
                        issue_type="heading_skip",
                        priority=IssuePriority.LOW,
                        message=f"Пропущен уровень заголовка H{missing_level} (переход с H{levels_present[i]} на H{levels_present[i+1]})",
                        recommendation="Соблюдайте иерархию заголовков. Не пропускайте уровни (H1 → H2 → H3).",
                        current_value=f"Уровни: {levels_present}"
                    ))
        
        # Проверка слишком длинных заголовков
        for level in ['h1', 'h2', 'h3']:
            max_length = 70 if level == 'h1' else 60
            for heading in headings.get(level, []):
                if len(heading) > max_length:
                    issues.append(MetaIssue(
                        url=url,
                        issue_type=f"long_{level}",
                        priority=IssuePriority.LOW,
                        message=f"Заголовок {level.upper()} слишком длинный ({len(heading)} символов)",
                        recommendation=f"Сократите заголовок до {max_length} символов для лучшей читаемости.",
                        current_value=heading[:50] + "..."
                    ))
        
        return issues
    
    def generate_snippet_preview(self, title: Optional[str], description: Optional[str], url: str) -> Dict:
        """
        Генерирует превью сниппета в Google
        
        Returns:
            Dict с параметрами для отображения сниппета
        """
        # Обрезка по пикселям (приблизительно)
        def truncate_by_pixels(text: str, max_pixels: int) -> str:
            # Средняя ширина символа ~10px для десктопа
            max_chars = int(max_pixels / 10)
            if len(text) <= max_chars:
                return text
            return text[:max_chars-3] + "..."
        
        display_title = truncate_by_pixels(title or "", self.TITLE_MAX_PIXELS) if title else "Нет Title"
        display_desc = truncate_by_pixels(description or "", self.DESCRIPTION_MAX_PIXELS) if description else "Нет описания. Поисковая система сгенерирует его автоматически из контента страницы."
        
        # Извлечение домена из URL
        domain = url.split('/')[2] if '//' in url else url.split('/')[0]
        
        return {
            'title': display_title,
            'description': display_desc,
            'url': url,
            'domain': domain,
            'title_length': len(title) if title else 0,
            'description_length': len(description) if description else 0,
            'title_truncated': len(display_title) < len(title) if title else False,
            'description_truncated': len(display_desc) < len(description) if description else False
        }


class HeadingsStructureAnalyzer:
    """
    Глубокий анализ структуры заголовков
    Оценивает логичность, полноту и SEO-оптимизацию
    """
    
    def analyze_structure(self, headings: Dict[str, List[str]]) -> Dict:
        """
        Анализирует структуру заголовков
        
        Returns:
            Dict с оценкой и рекомендациями
        """
        result = {
            'score': 0,
            'grade': 'F',
            'issues': [],
            'recommendations': [],
            'structure_map': self._build_structure_map(headings)
        }
        
        # Базовая оценка
        h1_count = len(headings.get('h1', []))
        h2_count = len(headings.get('h2', []))
        h3_count = len(headings.get('h3', []))
        
        # Наличие H1
        if h1_count == 1:
            result['score'] += 30
        elif h1_count == 0:
            result['issues'].append("Отсутствует H1")
            result['recommendations'].append("Добавьте один H1 с основным ключевым словом")
        else:
            result['issues'].append(f"Множественные H1 ({h1_count})")
            result['recommendations'].append("Оставьте только один H1")
        
        # Наличие H2
        if h2_count > 0:
            result['score'] += 20
        else:
            result['recommendations'].append("Добавьте H2 для разделения контента на секции")
        
        # Глубина структуры
        total_headings = sum(len(headings.get(f'h{i}', [])) for i in range(1, 7))
        if total_headings >= 5:
            result['score'] += 15
        
        # Проверка иерархии
        hierarchy_score = self._check_hierarchy(headings)
        result['score'] += hierarchy_score
        
        # Определение оценки
        if result['score'] >= 90:
            result['grade'] = 'A'
        elif result['score'] >= 75:
            result['grade'] = 'B'
        elif result['score'] >= 60:
            result['grade'] = 'C'
        elif result['score'] >= 40:
            result['grade'] = 'D'
        else:
            result['grade'] = 'F'
        
        return result
    
    def _build_structure_map(self, headings: Dict) -> List[Dict]:
        """Строит карту структуры заголовков"""
        structure = []
        
        for level_num in range(1, 7):
            level_key = f'h{level_num}'
            for idx, text in enumerate(headings.get(level_key, [])):
                structure.append({
                    'level': level_num,
                    'order': idx + 1,
                    'text': text,
                    'length': len(text)
                })
        
        return structure
    
    def _check_hierarchy(self, headings: Dict) -> int:
        """Проверяет правильность иерархии заголовков"""
        score = 0
        levels_present = [i for i in range(1, 7) if len(headings.get(f'h{i}', [])) > 0]
        
        if not levels_present:
            return 0
        
        # Проверка последовательности
        is_sequential = all(
            levels_present[i+1] - levels_present[i] == 1 
            for i in range(len(levels_present) - 1)
        )
        
        if is_sequential:
            score = 35
        else:
            # Штраф за пропуски
            score = 15
        
        return score


# Пример использования
if __name__ == "__main__":
    # Тестовый HTML
    test_html = """
    <html>
    <head>
        <title>Купить кроссовки Nike в Москве - лучшие цены | SportMaster</title>
        <meta name="description" content="Широкий выбор кроссовок Nike в Москве. Оригинальная продукция, гарантия качества, быстрая доставка. Закажите онлайн!">
    </head>
    <body>
        <h1>Кроссовки Nike</h1>
        <h2>Популярные модели</h2>
        <h3>Nike Air Max</h3>
        <h3>Nike Air Force</h3>
        <h2>Как выбрать размер</h2>
        <h3>Таблица размеров</h3>
        <h2>Отзывы покупателей</h2>
    </body>
    </html>
    """
    
    auditor = MetaTagsAuditor()
    result = auditor.analyze_page("https://example.com/nike", test_html, "category")
    
    print("=" * 80)
    print("РЕЗУЛЬТАТЫ АНАЛИЗА МЕТА-ТЕГОВ")
    print("=" * 80)
    print(f"URL: {result['url']}")
    print(f"Тип страницы: {result['page_type']}")
    print(f"\nTitle: {result['title']['value']}")
    print(f"Длина: {result['title']['length']} символов ({result['title']['status']})")
    print(f"\nDescription: {result['description']['value']}")
    print(f"Длина: {result['description']['length']} символов ({result['description']['status']})")
    print(f"\nСтруктура заголовков:")
    for level in ['h1', 'h2', 'h3']:
        count = len(result['headings'].get(level, []))
        if count > 0:
            print(f"  {level.upper()}: {count}")
    
    print(f"\nОценка структуры: {result['structure_score']}/100")
    print(f"\nВсего проблем: {result['total_issues']}")
    print(f"  Critical: {result['critical_count']}")
    print(f"  High: {result['high_count']}")
    
    if result['issues']:
        print("\n" + "=" * 80)
        print("ПРОБЛЕМЫ:")
        print("=" * 80)
        for issue in result['issues']:
            print(f"\n[{issue['priority'].value.upper()}] {issue['issue_type']}")
            print(f"  Проблема: {issue['message']}")
            print(f"  Решение: {issue['recommendation']}")
    
    # Генерация превью сниппета
    print("\n" + "=" * 80)
    print("ПРЕВЬЮ СНИППЕТА В GOOGLE")
    print("=" * 80)
    snippet = auditor.generate_snippet_preview(
        result['title']['value'],
        result['description']['value'],
        result['url']
    )
    
    print(f"\n🔗 {snippet['domain']}")
    print(f"📄 {snippet['title']}")
    print(f"💬 {snippet['description']}")
    print(f"\nДлина Title: {snippet['title_length']} (обрезан: {snippet['title_truncated']})")
    print(f"Длина Description: {snippet['description_length']} (обрезан: {snippet['description_truncated']})")
