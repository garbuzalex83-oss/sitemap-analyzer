"""
SEO Master PRO - Профессиональная система SEO-аудита уровня Enterprise
© 2024 - Все права защищены

Модуль ядра системы: Site Crawler, Sitemap Analyzer, Robots.txt Analyzer
"""

import requests
from urllib.parse import urlparse, urljoin, urldefrag
from urllib.robotparser import RobotFileParser
from bs4 import BeautifulSoup
from typing import Dict, List, Set, Tuple, Optional, Any
from dataclasses import dataclass, field, asdict
from datetime import datetime
import xml.etree.ElementTree as ET
import re
import json
import hashlib
from collections import defaultdict
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


@dataclass
class URLData:
    """Данные о URL после краулинга"""
    url: str
    status_code: int
    content_type: str = ""
    title: str = ""
    meta_description: str = ""
    h1: List[str] = field(default_factory=list)
    h2: List[str] = field(default_factory=list)
    h3: List[str] = field(default_factory=list)
    canonical: str = ""
    meta_robots: str = ""
    hreflang: Dict[str, str] = field(default_factory=dict)
    internal_links: List[Dict] = field(default_factory=list)
    external_links: List[Dict] = field(default_factory=list)
    images: List[Dict] = field(default_factory=list)
    word_count: int = 0
    html_size: int = 0
    load_time: float = 0.0
    schema_data: List[Dict] = field(default_factory=list)
    breadcrumbs: List[Dict] = field(default_factory=list)
    page_type: str = "unknown"
    depth: int = 0
    issues: List[Dict] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class CrawlResult:
    """Результаты полного краулинга сайта"""
    base_url: str
    crawl_date: str
    total_urls: int = 0
    urls_by_status: Dict[int, int] = field(default_factory=dict)
    urls_by_depth: Dict[int, int] = field(default_factory=dict)
    urls_data: Dict[str, URLData] = field(default_factory=dict)
    sitemap_urls: List[str] = field(default_factory=list)
    robots_rules: Dict[str, List[str]] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        result = asdict(self)
        result['urls_data'] = {k: v.to_dict() for k, v in self.urls_data.items()}
        return result


class SiteCrawler:
    """
    Профессиональный краулер сайтов уровня Screaming Frog
    
    Функционал:
    - Сканирование всех URL с проверкой статус-кодов
    - Сбор мета-тегов, заголовков, canonical, hreflang
    - Анализ внутренней и внешней перелинковки
    - Определение глубины клика
    - Проверка изображений и Schema.org разметки
    - Определение типа страницы
    - Выявление технических проблем
    """
    
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }
    
    def __init__(self, base_url: str, max_depth: int = 5, max_pages: int = 1000, 
                 threads: int = 5, respect_robots: bool = True):
        self.base_url = self._normalize_url(base_url)
        self.base_domain = urlparse(self.base_url).netloc
        self.max_depth = max_depth
        self.max_pages = max_pages
        self.threads = threads
        self.respect_robots = respect_robots
        
        self.visited: Set[str] = set()
        self.to_visit: List[Tuple[str, int]] = [(self.base_url, 0)]
        self.results: Dict[str, URLData] = {}
        
        self.robots_parser = RobotFileParser()
        self._load_robots_txt()
        
        logger.info(f"Инициализирован краулер для: {self.base_url}")
        logger.info(f"Макс. глубина: {max_depth}, Макс. страниц: {max_pages}, Потоков: {threads}")
    
    def _normalize_url(self, url: str) -> str:
        """Нормализация URL"""
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        parsed = urlparse(url)
        # Удаляем фрагменты
        url = urldefrag(parsed.geturl())[0]
        # Приводим к нижнему регистру домен
        return f"{parsed.scheme}://{parsed.netloc.lower()}{parsed.path}"
    
    def _load_robots_txt(self):
        """Загрузка и парсинг robots.txt"""
        try:
            robots_url = f"{urlparse(self.base_url).scheme}://{self.base_domain}/robots.txt"
            response = requests.get(robots_url, headers=self.HEADERS, timeout=10)
            if response.status_code == 200:
                self.robots_parser.parse(response.text.splitlines())
                logger.info(f"robots.txt загружен с {robots_url}")
            else:
                logger.warning(f"robots.txt не найден (статус {response.status_code})")
        except Exception as e:
            logger.warning(f"Ошибка загрузки robots.txt: {e}")
    
    def _is_allowed(self, url: str) -> bool:
        """Проверка разрешения на сканирование в robots.txt"""
        if not self.respect_robots:
            return True
        try:
            return self.robots_parser.can_fetch("*", url)
        except:
            return True
    
    def _is_internal_url(self, url: str) -> bool:
        """Проверка, является ли URL внутренним"""
        try:
            domain = urlparse(url).netloc
            return domain == self.base_domain or domain.endswith('.' + self.base_domain)
        except:
            return False
    
    def _extract_links(self, soup: BeautifulSoup, base_url: str) -> Tuple[List[str], List[str]]:
        """Извлечение внутренних и внешних ссылок"""
        internal = []
        external = []
        
        for link in soup.find_all('a', href=True):
            href = link['href'].strip()
            if not href or href.startswith(('#', 'javascript:', 'mailto:', 'tel:')):
                continue
            
            full_url = urljoin(base_url, href)
            full_url = urldefrag(full_url)[0]  # Удаляем фрагменты
            
            link_data = {
                'url': full_url,
                'anchor': link.get_text(strip=True)[:100],
                'title': link.get('title', ''),
                'rel': link.get('rel', []),
                'is_nofollow': 'nofollow' in link.get('rel', [])
            }
            
            if self._is_internal_url(full_url):
                internal.append(link_data)
            else:
                external.append(link_data)
        
        return internal, external
    
    def _extract_images(self, soup: BeautifulSoup, base_url: str) -> List[Dict]:
        """Извлечение данных об изображениях"""
        images = []
        for img in soup.find_all('img'):
            src = img.get('src', '').strip()
            if not src:
                continue
            
            full_src = urljoin(base_url, src)
            images.append({
                'src': full_src,
                'alt': img.get('alt', '').strip(),
                'width': img.get('width', ''),
                'height': img.get('height', ''),
                'loading': img.get('loading', ''),
                'has_alt': bool(img.get('alt', '').strip()),
                'is_lazy': img.get('loading') == 'lazy'
            })
        
        return images
    
    def _extract_schema(self, soup: BeautifulSoup) -> List[Dict]:
        """Извлечение Schema.org разметки"""
        schemas = []
        
        # JSON-LD
        for script in soup.find_all('script', type='application/ld+json'):
            try:
                schema_data = json.loads(script.string)
                schemas.append({
                    'type': 'JSON-LD',
                    'data': schema_data
                })
            except json.JSONDecodeError:
                pass
        
        # Microdata
        for item in soup.find_all(itemscope=True):
            itemtype = item.get('itemtype', '')
            if itemtype:
                schemas.append({
                    'type': 'Microdata',
                    'itemtype': itemtype,
                    'properties': {}
                })
        
        return schemas
    
    def _extract_breadcrumbs(self, soup: BeautifulSoup) -> List[Dict]:
        """Извлечение хлебных крошек"""
        breadcrumbs = []
        
        # Поиск через Schema.org
        for script in soup.find_all('script', type='application/ld+json'):
            try:
                data = json.loads(script.string)
                if isinstance(data, dict):
                    if '@type' in data and data['@type'] == 'BreadcrumbList':
                        for item in data.get('itemListElement', []):
                            breadcrumbs.append({
                                'position': item.get('position'),
                                'name': item.get('item', {}).get('name', ''),
                                'url': item.get('item', {}).get('@id', '')
                            })
                    elif 'breadcrumb' in data:
                        bc_data = data['breadcrumb']
                        if 'itemListElement' in bc_data:
                            for item in bc_data['itemListElement']:
                                breadcrumbs.append({
                                    'position': item.get('position'),
                                    'name': item.get('item', {}).get('name', ''),
                                    'url': item.get('item', {}).get('@id', '')
                                })
            except:
                pass
        
        # Поиск через HTML структуру
        if not breadcrumbs:
            bc_containers = soup.find_all(['nav', 'div'], class_=re.compile(r'breadcrumb|breadcrumbs', re.I))
            for container in bc_containers:
                for i, link in enumerate(container.find_all('a')):
                    breadcrumbs.append({
                        'position': i + 1,
                        'name': link.get_text(strip=True),
                        'url': link.get('href', '')
                    })
                if breadcrumbs:
                    break
        
        return breadcrumbs
    
    def _detect_page_type(self, url: str, soup: BeautifulSoup) -> str:
        """Определение типа страницы"""
        url_lower = url.lower()
        path = urlparse(url).path.lower()
        
        # Проверка через URL паттерны
        if any(x in path for x in ['/product/', '/tovar/', '/item/', '/p/']):
            return 'product'
        if any(x in path for x in ['/category/', '/kategorija/', '/cat/', '/c/']):
            return 'category'
        if any(x in path for x in ['/blog/', '/article/', '/statya/', '/news/', '/novost/']):
            return 'article'
        if any(x in path for x in ['/tag/', '/tags/', '/metka/']):
            return 'tag'
        if any(x in path for x in ['/brand/', '/brend/', '/manufacturer/']):
            return 'brand'
        if any(x in path for x in ['?page=', '&page=', '/page/']):
            return 'pagination'
        if any(x in path for x in ['?filter=', '&filter=', '/filter/']):
            return 'filter'
        if any(x in path for x in ['/cart/', '/korzina/', '/basket/']):
            return 'cart'
        if any(x in path for x in ['/checkout/', '/order/']):
            return 'checkout'
        if path in ['/', '/ru/', '/ro/', '/en/']:
            return 'homepage'
        
        # Проверка через Schema.org
        schemas = self._extract_schema(soup)
        for schema in schemas:
            if schema['type'] == 'JSON-LD':
                data = schema['data']
                if isinstance(data, dict):
                    schema_type = data.get('@type', '')
                    if schema_type == 'Product':
                        return 'product'
                    if schema_type in ['CategoryCode', 'CollectionPage']:
                        return 'category'
                    if schema_type in ['Article', 'NewsArticle', 'BlogPosting']:
                        return 'article'
        
        # Проверка через контент
        h1_text = ' '.join([h.get_text(strip=True).lower() for h in soup.find_all('h1')])
        if any(x in h1_text for x in ['купить', 'цена', 'заказать', 'товар', 'product']):
            return 'product'
        if any(x in h1_text for x in ['категория', 'category', 'раздел']):
            return 'category'
        
        return 'other'
    
    def _count_words(self, soup: BeautifulSoup) -> int:
        """Подсчет количества слов"""
        # Удаляем скрипты и стили
        for tag in soup(['script', 'style', 'noscript']):
            tag.decompose()
        
        text = soup.get_text(separator=' ')
        words = re.findall(r'\b\w+\b', text, re.UNICODE)
        return len(words)
    
    def _crawl_single_url(self, url: str, depth: int) -> Optional[URLData]:
        """Краулинг одного URL"""
        if not self._is_allowed(url):
            logger.debug(f"URL закрыт в robots.txt: {url}")
            return None
        
        start_time = time.time()
        
        try:
            response = requests.get(
                url, 
                headers=self.HEADERS, 
                timeout=30,
                allow_redirects=True,
                stream=False
            )
            load_time = time.time() - start_time
            
            url_data = URLData(
                url=url,
                status_code=response.status_code,
                content_type=response.headers.get('Content-Type', ''),
                html_size=len(response.content),
                load_time=round(load_time, 3),
                depth=depth
            )
            
            # Парсим только HTML страницы
            if 'text/html' in response.headers.get('Content-Type', ''):
                soup = BeautifulSoup(response.text, 'lxml')
                
                # Извлекаем мета-теги
                title_tag = soup.find('title')
                url_data.title = title_tag.get_text(strip=True)[:500] if title_tag else ''
                
                meta_desc = soup.find('meta', attrs={'name': 'description'})
                url_data.meta_description = meta_desc.get('content', '').strip()[:1000] if meta_desc else ''
                
                meta_robots = soup.find('meta', attrs={'name': 'robots'})
                url_data.meta_robots = meta_robots.get('content', '').strip() if meta_robots else ''
                
                # Canonical
                canonical = soup.find('link', rel='canonical')
                url_data.canonical = canonical.get('href', '') if canonical else ''
                
                # Hreflang
                for link in soup.find_all('link', rel='alternate'):
                    hreflang = link.get('hreflang', '')
                    href = link.get('href', '')
                    if hreflang and href:
                        url_data.hreflang[hreflang] = href
                
                # Заголовки
                url_data.h1 = [h.get_text(strip=True) for h in soup.find_all('h1')]
                url_data.h2 = [h.get_text(strip=True) for h in soup.find_all('h2')]
                url_data.h3 = [h.get_text(strip=True) for h in soup.find_all('h3')]
                
                # Ссылки
                internal, external = self._extract_links(soup, url)
                url_data.internal_links = internal
                url_data.external_links = external
                
                # Изображения
                url_data.images = self._extract_images(soup, url)
                
                # Schema.org
                url_data.schema_data = self._extract_schema(soup)
                
                # Хлебные крошки
                url_data.breadcrumbs = self._extract_breadcrumbs(soup)
                
                # Тип страницы
                url_data.page_type = self._detect_page_type(url, soup)
                
                # Количество слов
                url_data.word_count = self._count_words(soup)
                
                # Проверка проблем
                self._check_issues(url_data)
            
            return url_data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Ошибка при запросе {url}: {e}")
            return URLData(
                url=url,
                status_code=0,
                depth=depth,
                issues=[{'type': 'error', 'message': str(e), 'priority': 'critical'}]
            )
    
    def _check_issues(self, url_data: URLData):
        """Проверка на наличие проблем"""
        issues = []
        
        # Статус коды
        if url_data.status_code == 404:
            issues.append({'type': '404', 'message': 'Страница не найдена', 'priority': 'critical'})
        elif url_data.status_code >= 500:
            issues.append({'type': 'server_error', 'message': f'Ошибка сервера: {url_data.status_code}', 'priority': 'critical'})
        elif url_data.status_code in [301, 302]:
            issues.append({'type': 'redirect', 'message': f'Редирект: {url_data.status_code}', 'priority': 'medium'})
        
        # Meta tags
        if not url_data.title and url_data.status_code == 200:
            issues.append({'type': 'missing_title', 'message': 'Отсутствует Title', 'priority': 'high'})
        elif len(url_data.title) < 30:
            issues.append({'type': 'short_title', 'message': f'Title слишком короткий ({len(url_data.title)} симв.)', 'priority': 'medium'})
        elif len(url_data.title) > 70:
            issues.append({'type': 'long_title', 'message': f'Title слишком длинный ({len(url_data.title)} симв.)', 'priority': 'medium'})
        
        if not url_data.meta_description and url_data.status_code == 200:
            issues.append({'type': 'missing_description', 'message': 'Отсутствует Description', 'priority': 'medium'})
        elif len(url_data.meta_description) < 120:
            issues.append({'type': 'short_description', 'message': f'Description слишком короткий ({len(url_data.meta_description)} симв.)', 'priority': 'low'})
        elif len(url_data.meta_description) > 160:
            issues.append({'type': 'long_description', 'message': f'Description слишком длинный ({len(url_data.meta_description)} симв.)', 'priority': 'low'})
        
        # H1
        if not url_data.h1 and url_data.status_code == 200 and url_data.page_type not in ['cart', 'checkout']:
            issues.append({'type': 'missing_h1', 'message': 'Отсутствует H1', 'priority': 'high'})
        elif len(url_data.h1) > 1:
            issues.append({'type': 'multiple_h1', 'message': f'Несколько H1 ({len(url_data.h1)})', 'priority': 'medium'})
        
        # Canonical
        if not url_data.canonical and url_data.status_code == 200:
            issues.append({'type': 'missing_canonical', 'message': 'Отсутствует canonical', 'priority': 'medium'})
        
        # Images
        images_without_alt = [img for img in url_data.images if not img['has_alt']]
        if images_without_alt:
            issues.append({'type': 'missing_alt', 'message': f'{len(images_without_alt)} изображений без alt', 'priority': 'low'})
        
        # Internal links
        broken_internal = [link for link in url_data.internal_links if link.get('is_broken', False)]
        if broken_internal:
            issues.append({'type': 'broken_internal_links', 'message': f'{len(broken_internal)} битых внутренних ссылок', 'priority': 'high'})
        
        url_data.issues = issues
    
    def crawl(self) -> CrawlResult:
        """Основной метод краулинга"""
        logger.info("Начало краулинга...")
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=self.threads) as executor:
            while self.to_visit and len(self.visited) < self.max_pages:
                # Берем пакет URL для обработки
                batch = []
                while self.to_visit and len(batch) < self.threads * 2:
                    url, depth = self.to_visit.pop(0)
                    if url not in self.visited and self._is_internal_url(url):
                        batch.append((url, depth))
                
                if not batch:
                    break
                
                # Обрабатываем пакет
                futures = {executor.submit(self._crawl_single_url, url, depth): (url, depth) 
                          for url, depth in batch}
                
                for future in as_completed(futures):
                    url, depth = futures[future]
                    try:
                        result = future.result()
                        if result:
                            self.visited.add(url)
                            self.results[url] = result
                            
                            # Добавляем новые URL в очередь
                            if depth < self.max_depth and result.status_code == 200:
                                for link in result.internal_links:
                                    link_url = link['url']
                                    if link_url not in self.visited and self._is_internal_url(link_url):
                                        # Проверяем, нет ли уже в очереди
                                        if not any(u == link_url for u, _ in self.to_visit):
                                            self.to_visit.append((link_url, depth + 1))
                    
                    except Exception as e:
                        logger.error(f"Ошибка обработки {url}: {e}")
        
        # Формируем результат
        crawl_result = CrawlResult(
            base_url=self.base_url,
            crawl_date=datetime.now().isoformat(),
            total_urls=len(self.results),
            urls_data=self.results
        )
        
        # Статистика по статусам
        for url_data in self.results.values():
            status = url_data.status_code
            crawl_result.urls_by_status[status] = crawl_result.urls_by_status.get(status, 0) + 1
            
            depth = url_data.depth
            crawl_result.urls_by_depth[depth] = crawl_result.urls_by_depth.get(depth, 0) + 1
        
        elapsed = time.time() - start_time
        logger.info(f"Краулинг завершен: {len(self.results)} URL за {elapsed:.2f} сек.")
        
        return crawl_result


class SitemapAnalyzer:
    """
    Анализатор sitemap.xml
    
    Функционал:
    - Проверка наличия и валидности sitemap
    - Анализ вложенных sitemap
    - Проверка URL на ошибки
    - Выявление проблемных страниц
    """
    
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')
        self.base_domain = urlparse(base_url).netloc
        self.sitemaps: List[str] = []
        self.urls: List[Dict] = []
        self.errors: List[str] = []
        self.warnings: List[str] = []
    
    def find_sitemaps(self) -> List[str]:
        """Поиск всех sitemap.xml"""
        sitemaps = []
        
        # Стандартный путь
        standard_sitemap = f"{self.base_url}/sitemap.xml"
        try:
            response = requests.get(standard_sitemap, timeout=10)
            if response.status_code == 200:
                sitemaps.append(standard_sitemap)
                logger.info(f"Найден sitemap: {standard_sitemap}")
        except:
            pass
        
        # Поиск через robots.txt
        try:
            robots_url = f"{self.base_url}/robots.txt"
            response = requests.get(robots_url, timeout=10)
            if response.status_code == 200:
                for line in response.text.splitlines():
                    if line.lower().startswith('sitemap:'):
                        sitemap_url = line.split(':', 1)[1].strip()
                        if sitemap_url not in sitemaps:
                            sitemaps.append(sitemap_url)
                            logger.info(f"Найден sitemap из robots.txt: {sitemap_url}")
        except:
            pass
        
        self.sitemaps = sitemaps
        return sitemaps
    
    def parse_sitemap(self, sitemap_url: str) -> Tuple[List[Dict], List[str]]:
        """Парсинг sitemap.xml"""
        urls = []
        nested_sitemaps = []
        
        try:
            response = requests.get(sitemap_url, timeout=30)
            response.raise_for_status()
            
            root = ET.fromstring(response.content)
            ns = {'sitemap': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
            
            # Проверяем, это индекс sitemap или обычный
            is_index = root.tag.endswith('sitemapindex')
            
            if is_index:
                # Индекс sitemap - ищем вложенные
                for sitemap in root.findall('.//sitemap:sitemap', ns):
                    loc = sitemap.find('sitemap:loc', ns)
                    if loc is not None and loc.text:
                        nested_sitemaps.append(loc.text)
                logger.info(f"Найдено {len(nested_sitemaps)} вложенных sitemap в {sitemap_url}")
            else:
                # Обычный sitemap
                for url_elem in root.findall('.//sitemap:url', ns):
                    loc = url_elem.find('sitemap:loc', ns)
                    if loc is not None and loc.text:
                        url_data = {
                            'loc': loc.text,
                            'lastmod': '',
                            'changefreq': '',
                            'priority': ''
                        }
                        
                        lastmod = url_elem.find('sitemap:lastmod', ns)
                        if lastmod is not None and lastmod.text:
                            url_data['lastmod'] = lastmod.text
                        
                        changefreq = url_elem.find('sitemap:changefreq', ns)
                        if changefreq is not None and changefreq.text:
                            url_data['changefreq'] = changefreq.text
                        
                        priority = url_elem.find('sitemap:priority', ns)
                        if priority is not None and priority.text:
                            url_data['priority'] = priority.text
                        
                        urls.append(url_data)
                
                logger.info(f"Найдено {len(urls)} URL в {sitemap_url}")
        
        except Exception as e:
            self.errors.append(f"Ошибка парсинга {sitemap_url}: {e}")
            logger.error(f"Ошибка парсинга {sitemap_url}: {e}")
        
        return urls, nested_sitemaps
    
    def analyze(self) -> Dict:
        """Полный анализ sitemap"""
        logger.info("Начало анализа sitemap...")
        
        sitemaps = self.find_sitemaps()
        if not sitemaps:
            return {
                'found': False,
                'errors': ['Sitemap.xml не найден'],
                'urls': [],
                'nested_sitemaps': []
            }
        
        all_urls = []
        all_nested = []
        
        for sitemap in sitemaps:
            urls, nested = self.parse_sitemap(sitemap)
            all_urls.extend(urls)
            all_nested.extend(nested)
            
            # Рекурсивно обрабатываем вложенные sitemap
            for nested_sitemap in nested:
                nested_urls, deeper_nested = self.parse_sitemap(nested_sitemap)
                all_urls.extend(nested_urls)
                all_nested.extend(deeper_nested)
        
        self.urls = all_urls
        
        # Анализ проблем
        issues = []
        for url_data in all_urls:
            url = url_data['loc']
            
            # Проверка на битые URL
            if not url.startswith(('http://', 'https://')):
                issues.append({'url': url, 'issue': 'Некорректный URL', 'priority': 'high'})
            
            # Проверка lastmod
            if url_data.get('lastmod'):
                try:
                    lastmod_date = datetime.fromisoformat(url_data['lastmod'].replace('Z', '+00:00'))
                    days_old = (datetime.now(lastmod_date.tzinfo) - lastmod_date).days if lastmod_date.tzinfo else (datetime.now() - lastmod_date).days
                    if days_old > 365:
                        issues.append({'url': url, 'issue': f'Страница не обновлялась {days_old} дней', 'priority': 'low'})
                except:
                    pass
        
        result = {
            'found': True,
            'sitemaps_found': sitemaps,
            'total_urls': len(all_urls),
            'nested_sitemaps': all_nested,
            'urls_sample': all_urls[:100],  # Первые 100 для примера
            'issues': issues,
            'errors': self.errors
        }
        
        logger.info(f"Анализ завершен: {len(all_urls)} URL, {len(issues)} проблем")
        return result


class RobotsTxtAnalyzer:
    """
    Анализатор robots.txt
    
    Функционал:
    - Проверка наличия robots.txt
    - Анализ правил доступа
    - Выявление конфликтных правил
    - Проверка закрытия важных разделов
    """
    
    IMPORTANT_PATHS = [
        '/', '/sitemap.xml', '/products', '/category', '/blog', '/article',
        '/news', '/about', '/contact', '/search', '/api'
    ]
    
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')
        self.base_domain = urlparse(base_url).netloc
        self.rules: Dict[str, List[str]] = {}
        self.sitemaps: List[str] = []
        self.errors: List[str] = []
        self.warnings: List[str] = []
    
    def analyze(self) -> Dict:
        """Анализ robots.txt"""
        logger.info("Начало анализа robots.txt...")
        
        robots_url = f"{self.base_url}/robots.txt"
        
        try:
            response = requests.get(robots_url, timeout=10)
            
            if response.status_code != 200:
                return {
                    'exists': False,
                    'status_code': response.status_code,
                    'warning': 'robots.txt не найден',
                    'rules': {},
                    'sitemaps': [],
                    'issues': [{'type': 'missing', 'message': 'Файл robots.txt отсутствует', 'priority': 'medium'}]
                }
            
            content = response.text
            rules = {}
            current_agent = '*'
            sitemaps = []
            issues = []
            
            for line in content.splitlines():
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                if line.lower().startswith('user-agent:'):
                    current_agent = line.split(':', 1)[1].strip()
                    if current_agent not in rules:
                        rules[current_agent] = []
                
                elif line.lower().startswith('disallow:'):
                    path = line.split(':', 1)[1].strip()
                    if current_agent in rules:
                        rules[current_agent].append({'type': 'disallow', 'path': path})
                    
                    # Проверка на закрытие важных путей
                    if path in self.IMPORTANT_PATHS or any(path.startswith(p) for p in self.IMPORTANT_PATHS if p != '/'):
                        issues.append({
                            'type': 'important_path_blocked',
                            'message': f'Важный путь "{path}" закрыт для {current_agent}',
                            'priority': 'critical',
                            'path': path
                        })
                
                elif line.lower().startswith('allow:'):
                    path = line.split(':', 1)[1].strip()
                    if current_agent in rules:
                        rules[current_agent].append({'type': 'allow', 'path': path})
                
                elif line.lower().startswith('sitemap:'):
                    sitemap = line.split(':', 1)[1].strip()
                    sitemaps.append(sitemap)
                
                elif line.lower().startswith('crawl-delay:'):
                    delay = line.split(':', 1)[1].strip()
                    if current_agent in rules:
                        rules[current_agent].append({'type': 'crawl-delay', 'value': delay})
            
            # Проверка на конфликты
            for agent, agent_rules in rules.items():
                disallow_paths = [r['path'] for r in agent_rules if r['type'] == 'disallow']
                allow_paths = [r['path'] for r in agent_rules if r['type'] == 'allow']
                
                for disallow in disallow_paths:
                    for allow in allow_paths:
                        if allow.startswith(disallow) and disallow != '/':
                            issues.append({
                                'type': 'conflict',
                                'message': f'Конфликт правил: Disallow {disallow} и Allow {allow}',
                                'priority': 'medium'
                            })
            
            self.rules = rules
            self.sitemaps = sitemaps
            
            result = {
                'exists': True,
                'status_code': response.status_code,
                'url': robots_url,
                'rules': rules,
                'sitemaps': sitemaps,
                'issues': issues,
                'warnings': self.warnings,
                'errors': self.errors
            }
            
            logger.info(f"Анализ завершен: {len(rules)} user-agent'ов, {len(issues)} проблем")
            return result
        
        except Exception as e:
            logger.error(f"Ошибка анализа robots.txt: {e}")
            return {
                'exists': False,
                'error': str(e),
                'rules': {},
                'sitemaps': [],
                'issues': [{'type': 'error', 'message': str(e), 'priority': 'high'}]
            }
    
    def can_crawl(self, url: str, user_agent: str = '*') -> bool:
        """Симуляция: можно ли сканировать URL"""
        from urllib.robotparser import RobotFileParser
        
        rp = RobotFileParser()
        robots_url = f"{self.base_url}/robots.txt"
        
        try:
            response = requests.get(robots_url, timeout=10)
            if response.status_code == 200:
                rp.parse(response.text.splitlines())
                return rp.can_fetch(user_agent, url)
        except:
            pass
        
        return True


if __name__ == '__main__':
    # Пример использования
    import sys
    
    if len(sys.argv) < 2:
        print("Использование: python core_crawler.py <URL> [max_depth] [max_pages]")
        sys.exit(1)
    
    url = sys.argv[1]
    max_depth = int(sys.argv[2]) if len(sys.argv) > 2 else 3
    max_pages = int(sys.argv[3]) if len(sys.argv) > 3 else 100
    
    # Краулер
    crawler = SiteCrawler(url, max_depth=max_depth, max_pages=max_pages, threads=5)
    result = crawler.crawl()
    
    print(f"\n=== РЕЗУЛЬТАТЫ КРАУЛИНГА ===")
    print(f"Всего URL: {result.total_urls}")
    print(f"Статусы: {result.urls_by_status}")
    print(f"Глубина: {result.urls_by_depth}")
    
    # Анализ sitemap
    sitemap_analyzer = SitemapAnalyzer(url)
    sitemap_result = sitemap_analyzer.analyze()
    
    print(f"\n=== АНАЛИЗ SITEMAP ===")
    print(f"Найден: {sitemap_result.get('found', False)}")
    if sitemap_result.get('found'):
        print(f"Всего URL в sitemap: {sitemap_result.get('total_urls', 0)}")
        print(f"Проблем: {len(sitemap_result.get('issues', []))}")
    
    # Анализ robots.txt
    robots_analyzer = RobotsTxtAnalyzer(url)
    robots_result = robots_analyzer.analyze()
    
    print(f"\n=== АНАЛИЗ ROBOTS.TXT ===")
    print(f"Существует: {robots_result.get('exists', False)}")
    print(f"Проблем: {len(robots_result.get('issues', []))}")
    
    # Сохранение результатов
    output_file = f"crawl_results_{urlparse(url).netloc}.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result.to_dict(), f, ensure_ascii=False, indent=2)
    
    print(f"\nРезультаты сохранены в {output_file}")
