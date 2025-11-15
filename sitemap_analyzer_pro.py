#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Расширенный SEO анализатор Sitemap Pro
Включает проверку контента страниц, мета-тегов, скорости загрузки
"""

import requests
import xml.etree.ElementTree as ET
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
from datetime import datetime
import time
import re
from collections import defaultdict
from typing import List, Dict, Set, Tuple
import hashlib

class AdvancedSitemapAnalyzer:
    def __init__(self, sitemap_url: str, deep_check: bool = False):
        """
        Расширенный анализатор с проверкой контента
        
        Args:
            sitemap_url: URL sitemap
            deep_check: Проверять контент страниц (медленно!)
        """
        self.sitemap_url = sitemap_url
        self.deep_check = deep_check
        self.domain = urlparse(sitemap_url).netloc
        self.protocol = urlparse(sitemap_url).scheme
        
        self.urls = []
        self.errors = []
        self.warnings = []
        self.seo_issues = []
        self.statistics = defaultdict(int)
        self.page_data = []
        
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    def fetch_sitemap(self, url: str) -> str:
        """Загрузка sitemap"""
        try:
            response = requests.get(url, headers=self.headers, timeout=15)
            response.raise_for_status()
            
            # Проверка размера
            size_mb = len(response.content) / (1024 * 1024)
            if size_mb > 50:
                self.warnings.append(f"⚠️ Размер sitemap {size_mb:.2f} МБ (рекомендуется до 50 МБ)")
            
            return response.text
        except Exception as e:
            self.errors.append(f"❌ Ошибка загрузки sitemap: {e}")
            return None
    
    def parse_sitemap(self, content: str, sitemap_url: str) -> List[Dict]:
        """Парсинг XML sitemap"""
        urls_data = []
        
        try:
            root = ET.fromstring(content)
            namespace = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
            
            # Sitemap index
            sitemaps = root.findall('.//ns:sitemap', namespace)
            if sitemaps:
                self.statistics['has_sitemap_index'] = True
                print(f"\n📑 Sitemap Index: найдено {len(sitemaps)} подкарт")
                
                for sitemap in sitemaps:
                    loc = sitemap.find('ns:loc', namespace)
                    lastmod = sitemap.find('ns:lastmod', namespace)
                    
                    if loc is not None and loc.text:
                        print(f"  ↳ {loc.text}")
                        if lastmod is not None and lastmod.text:
                            print(f"     Обновлен: {lastmod.text}")
                        
                        sub_content = self.fetch_sitemap(loc.text)
                        if sub_content:
                            urls_data.extend(self.parse_sitemap(sub_content, loc.text))
                
                return urls_data
            
            # Обычный sitemap
            urlset = root.findall('.//ns:url', namespace)
            
            for url_element in urlset:
                url_data = {}
                
                loc = url_element.find('ns:loc', namespace)
                if loc is not None and loc.text:
                    url_data['loc'] = loc.text.strip()
                else:
                    self.errors.append(f"❌ Пустой <loc> в {sitemap_url}")
                    continue
                
                lastmod = url_element.find('ns:lastmod', namespace)
                url_data['lastmod'] = lastmod.text.strip() if lastmod is not None and lastmod.text else None
                
                changefreq = url_element.find('ns:changefreq', namespace)
                url_data['changefreq'] = changefreq.text.strip() if changefreq is not None and changefreq.text else None
                
                priority = url_element.find('ns:priority', namespace)
                url_data['priority'] = priority.text.strip() if priority is not None and priority.text else None
                
                # Дополнительные атрибуты
                url_data['source_sitemap'] = sitemap_url
                
                urls_data.append(url_data)
            
            self.statistics['total_urls'] += len(urlset)
            
        except ET.ParseError as e:
            self.errors.append(f"❌ XML parse error: {e}")
        
        return urls_data
    
    def check_page_content(self, url: str) -> Dict:
        """
        Глубокая проверка контента страницы
        """
        page_info = {
            'url': url,
            'status': None,
            'title': None,
            'title_length': 0,
            'meta_description': None,
            'meta_description_length': 0,
            'h1_count': 0,
            'h1_text': [],
            'canonical': None,
            'robots': None,
            'response_time': 0,
            'content_length': 0,
            'images_without_alt': 0,
            'links_count': 0,
            'issues': []
        }
        
        try:
            start_time = time.time()
            response = requests.get(url, headers=self.headers, timeout=10)
            page_info['response_time'] = round(time.time() - start_time, 2)
            page_info['status'] = response.status_code
            page_info['content_length'] = len(response.content)
            
            if response.status_code != 200:
                page_info['issues'].append(f"HTTP {response.status_code}")
                return page_info
            
            # Парсинг HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Title
            title_tag = soup.find('title')
            if title_tag:
                page_info['title'] = title_tag.text.strip()
                page_info['title_length'] = len(page_info['title'])
                
                if page_info['title_length'] < 30:
                    page_info['issues'].append(f"Title слишком короткий ({page_info['title_length']} символов)")
                elif page_info['title_length'] > 60:
                    page_info['issues'].append(f"Title слишком длинный ({page_info['title_length']} символов)")
            else:
                page_info['issues'].append("Отсутствует Title")
            
            # Meta Description
            meta_desc = soup.find('meta', attrs={'name': 'description'})
            if meta_desc and meta_desc.get('content'):
                page_info['meta_description'] = meta_desc['content'].strip()
                page_info['meta_description_length'] = len(page_info['meta_description'])
                
                if page_info['meta_description_length'] < 70:
                    page_info['issues'].append(f"Description короткий ({page_info['meta_description_length']} символов)")
                elif page_info['meta_description_length'] > 160:
                    page_info['issues'].append(f"Description длинный ({page_info['meta_description_length']} символов)")
            else:
                page_info['issues'].append("Отсутствует Meta Description")
            
            # H1
            h1_tags = soup.find_all('h1')
            page_info['h1_count'] = len(h1_tags)
            page_info['h1_text'] = [h1.text.strip() for h1 in h1_tags]
            
            if page_info['h1_count'] == 0:
                page_info['issues'].append("Отсутствует H1")
            elif page_info['h1_count'] > 1:
                page_info['issues'].append(f"Множественные H1 ({page_info['h1_count']})")
            
            # Canonical
            canonical = soup.find('link', attrs={'rel': 'canonical'})
            if canonical and canonical.get('href'):
                page_info['canonical'] = canonical['href']
                
                # Проверка соответствия
                canonical_url = urljoin(url, page_info['canonical'])
                if canonical_url != url:
                    page_info['issues'].append(f"Canonical указывает на другой URL: {canonical_url}")
            
            # Robots meta
            robots_meta = soup.find('meta', attrs={'name': 'robots'})
            if robots_meta and robots_meta.get('content'):
                page_info['robots'] = robots_meta['content'].lower()
                
                if 'noindex' in page_info['robots']:
                    page_info['issues'].append("⚠️ NOINDEX - страница не должна быть в sitemap")
                if 'nofollow' in page_info['robots']:
                    page_info['issues'].append("NOFOLLOW в meta robots")
            
            # Изображения без ALT
            images = soup.find_all('img')
            for img in images:
                if not img.get('alt'):
                    page_info['images_without_alt'] += 1
            
            if page_info['images_without_alt'] > 0:
                page_info['issues'].append(f"{page_info['images_without_alt']} изображений без ALT")
            
            # Ссылки
            links = soup.find_all('a', href=True)
            page_info['links_count'] = len(links)
            
            # Скорость загрузки
            if page_info['response_time'] > 3:
                page_info['issues'].append(f"⚠️ Медленная загрузка ({page_info['response_time']}с)")
            
            # Размер страницы
            if page_info['content_length'] > 2 * 1024 * 1024:  # 2MB
                size_mb = page_info['content_length'] / (1024 * 1024)
                page_info['issues'].append(f"⚠️ Большой размер страницы ({size_mb:.2f} MB)")
            
        except Exception as e:
            page_info['issues'].append(f"Ошибка проверки: {str(e)}")
        
        return page_info
    
    def analyze_with_deep_check(self):
        """Анализ с проверкой контента"""
        print(f"\n🔍 Глубокий анализ {len(self.urls)} страниц...")
        print("⚠️  Это займет время (примерно 10-15 сек на 100 URL)")
        
        url_set = set()
        content_hashes = set()
        
        for idx, url_data in enumerate(self.urls, 1):
            url = url_data['loc']
            
            # Прогресс
            if idx % 10 == 0:
                print(f"  📊 Обработано: {idx}/{len(self.urls)}")
            
            # Базовые проверки
            if url in url_set:
                self.warnings.append(f"{url}: Дубликат URL")
                self.statistics['duplicates'] += 1
            else:
                url_set.add(url)
            
            # Проверка домена
            url_domain = urlparse(url).netloc
            if url_domain == self.domain:
                self.statistics['domain_urls'] += 1
                
                # Глубокая проверка контента
                if self.deep_check:
                    page_info = self.check_page_content(url)
                    self.page_data.append(page_info)
                    
                    # Проверка дублированного контента (по title)
                    if page_info['title']:
                        title_hash = hashlib.md5(page_info['title'].encode()).hexdigest()
                        if title_hash in content_hashes:
                            self.seo_issues.append(f"{url}: Дублированный Title")
                            self.statistics['duplicate_titles'] += 1
                        else:
                            content_hashes.add(title_hash)
                    
                    # SEO проблемы
                    if page_info['issues']:
                        for issue in page_info['issues']:
                            self.seo_issues.append(f"{url}: {issue}")
                    
                    # Статистика по статусам
                    if page_info['status'] == 200:
                        self.statistics['ok_urls'] += 1
                    elif page_info['status'] in [301, 302, 307, 308]:
                        self.statistics['redirects'] += 1
                    elif page_info['status'] >= 400:
                        self.statistics['error_urls'] += 1
                    
                    time.sleep(0.2)  # Задержка между запросами
            else:
                self.statistics['external_urls'] += 1
    
    def generate_advanced_report(self):
        """Расширенный отчет"""
        print("\n" + "="*100)
        print("📊 РАСШИРЕННЫЙ SEO ОТЧЕТ ПО SITEMAP")
        print("="*100)
        
        print(f"\n📍 Sitemap: {self.sitemap_url}")
        print(f"🌐 Домен: {self.domain}")
        
        # Основная статистика
        print(f"\n📈 СТАТИСТИКА:")
        print(f"  • Всего URL: {self.statistics['total_urls']}")
        print(f"  • URL домена: {self.statistics['domain_urls']}")
        print(f"  • Внешних URL: {self.statistics['external_urls']}")
        print(f"  • Дубликатов: {self.statistics['duplicates']}")
        
        if self.deep_check:
            print(f"\n🌐 ПРОВЕРКА ДОСТУПНОСТИ:")
            print(f"  • Доступных (200): {self.statistics['ok_urls']}")
            print(f"  • Редиректов: {self.statistics['redirects']}")
            print(f"  • Ошибок: {self.statistics['error_urls']}")
            
            print(f"\n🎯 SEO МЕТРИКИ:")
            print(f"  • Дублированных Title: {self.statistics.get('duplicate_titles', 0)}")
            print(f"  • Страниц с проблемами: {len(self.seo_issues)}")
            
            # Средние показатели
            if self.page_data:
                avg_response = sum(p['response_time'] for p in self.page_data) / len(self.page_data)
                avg_size = sum(p['content_length'] for p in self.page_data) / len(self.page_data) / 1024
                
                print(f"\n⚡ ПРОИЗВОДИТЕЛЬНОСТЬ:")
                print(f"  • Средняя скорость загрузки: {avg_response:.2f}с")
                print(f"  • Средний размер страницы: {avg_size:.2f} KB")
        
        # Критические ошибки
        if self.errors:
            print(f"\n❌ КРИТИЧЕСКИЕ ОШИБКИ ({len(self.errors)}):")
            for error in self.errors[:10]:
                print(f"  {error}")
        
        # SEO проблемы
        if self.seo_issues:
            print(f"\n⚠️  SEO ПРОБЛЕМЫ ({len(self.seo_issues)}):")
            
            # Группировка по типам
            issue_types = defaultdict(int)
            for issue in self.seo_issues:
                if 'Title' in issue:
                    issue_types['Title'] += 1
                elif 'Description' in issue:
                    issue_types['Description'] += 1
                elif 'H1' in issue:
                    issue_types['H1'] += 1
                elif 'NOINDEX' in issue:
                    issue_types['NOINDEX'] += 1
                elif 'ALT' in issue:
                    issue_types['Images'] += 1
                else:
                    issue_types['Другое'] += 1
            
            for issue_type, count in sorted(issue_types.items(), key=lambda x: x[1], reverse=True):
                print(f"  • {issue_type}: {count} проблем")
            
            print(f"\n  Первые 20 проблем:")
            for issue in self.seo_issues[:20]:
                print(f"    - {issue}")
            
            if len(self.seo_issues) > 20:
                print(f"    ... и еще {len(self.seo_issues) - 20} проблем")
        
        # Рекомендации
        print(f"\n💡 SEO РЕКОМЕНДАЦИИ:")
        
        recommendations = []
        
        if self.statistics['duplicates'] > 0:
            recommendations.append(f"🔴 Удалите {self.statistics['duplicates']} дубликатов URL")
        
        if self.statistics.get('duplicate_titles', 0) > 0:
            recommendations.append(f"🔴 Исправьте {self.statistics['duplicate_titles']} дублированных Title")
        
        if self.statistics.get('redirects', 0) > 0:
            recommendations.append(f"⚠️ Замените {self.statistics['redirects']} URL с редиректами")
        
        if self.statistics.get('error_urls', 0) > 0:
            recommendations.append(f"🔴 Удалите {self.statistics['error_urls']} недоступных URL")
        
        # Анализ типов проблем
        noindex_count = sum(1 for issue in self.seo_issues if 'NOINDEX' in issue)
        if noindex_count > 0:
            recommendations.append(f"🔴 Удалите {noindex_count} страниц с NOINDEX из sitemap")
        
        missing_meta = sum(1 for issue in self.seo_issues if 'Отсутствует' in issue)
        if missing_meta > 10:
            recommendations.append(f"⚠️ Добавьте мета-теги на {missing_meta} страниц")
        
        if not recommendations:
            recommendations.append("✅ Отлично! Серьезных проблем не обнаружено")
        
        for rec in recommendations:
            print(f"  {rec}")
        
        # Оценка
        print(f"\n{'='*100}")
        total_issues = len(self.errors) + len(self.warnings) + len(self.seo_issues)
        
        if total_issues == 0:
            score = 100
            rating = "ОТЛИЧНО"
        elif total_issues < 20:
            score = 90
            rating = "ХОРОШО"
        elif total_issues < 50:
            score = 70
            rating = "СРЕДНЕ"
        else:
            score = 40
            rating = "ТРЕБУЕТСЯ ДОРАБОТКА"
        
        print(f"📊 ИТОГОВАЯ ОЦЕНКА: {score}/100 - {rating}")
        print(f"Найдено проблем: {total_issues}")
        print("="*100 + "\n")
    
    def run(self):
        """Запуск анализа"""
        print("🚀 Запуск расширенного SEO анализа...")
        
        content = self.fetch_sitemap(self.sitemap_url)
        if not content:
            return
        
        self.urls = self.parse_sitemap(content, self.sitemap_url)
        
        if not self.urls:
            print("\n❌ URL не найдены")
            return
        
        self.analyze_with_deep_check()
        self.generate_advanced_report()


def main():
    print("""
╔═══════════════════════════════════════════════════════════════════╗
║     🔍 РАСШИРЕННЫЙ SEO АНАЛИЗАТОР SITEMAP PRO 3.0                ║
║         Глубокая проверка контента и SEO метрик                   ║
╚═══════════════════════════════════════════════════════════════════╝
    """)
    
    sitemap_url = input("Введите URL sitemap: ").strip()
    if not sitemap_url:
        print("❌ URL не указан")
        return
    
    deep_check = input("\n🔬 Выполнить глубокую проверку контента? (медленно) [y/N]: ").lower() == 'y'
    
    print("\n" + "="*70)
    print("ВАЖНО: Глубокая проверка анализирует:")
    print("  • Title и Meta Description")
    print("  • Заголовки H1")
    print("  • Canonical и Robots")
    print("  • Изображения без ALT")
    print("  • Скорость загрузки")
    print("  • Дублированный контент")
    print("="*70 + "\n")
    
    analyzer = AdvancedSitemapAnalyzer(sitemap_url, deep_check=deep_check)
    analyzer.run()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ Анализ прерван пользователем")
