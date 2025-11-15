#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Профессиональный анализатор Sitemap
Автор: SEO специалист
Версия: 2.0
"""

import requests
import xml.etree.ElementTree as ET
from urllib.parse import urlparse, urljoin
from datetime import datetime
import time
from collections import defaultdict
import re
from typing import List, Dict, Set, Tuple
import sys

class SitemapAnalyzer:
    def __init__(self, sitemap_url: str, timeout: int = 10):
        """
        Инициализация анализатора sitemap
        
        Args:
            sitemap_url: URL sitemap для анализа
            timeout: Таймаут для HTTP запросов
        """
        self.sitemap_url = sitemap_url
        self.timeout = timeout
        self.domain = urlparse(sitemap_url).netloc
        self.protocol = urlparse(sitemap_url).scheme
        
        # Результаты анализа
        self.urls = []
        self.errors = []
        self.warnings = []
        self.statistics = defaultdict(int)
        self.url_details = []
        
        # Настройки
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (compatible; SitemapAnalyzer/2.0; +http://example.com/bot)'
        }
        
    def fetch_sitemap(self, url: str) -> str:
        """Загрузка содержимого sitemap"""
        try:
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            return response.text
        except requests.exceptions.RequestException as e:
            self.errors.append(f"❌ Ошибка загрузки sitemap: {e}")
            return None
    
    def parse_sitemap(self, content: str, sitemap_url: str) -> List[Dict]:
        """Парсинг XML sitemap"""
        urls_data = []
        
        try:
            root = ET.fromstring(content)
            
            # Определение namespace
            namespace = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
            
            # Проверка на sitemap index
            sitemaps = root.findall('.//ns:sitemap', namespace)
            if sitemaps:
                self.statistics['sitemap_index'] = True
                print(f"\n📑 Обнаружен Sitemap Index с {len(sitemaps)} подкартами")
                
                for sitemap in sitemaps:
                    loc = sitemap.find('ns:loc', namespace)
                    if loc is not None and loc.text:
                        print(f"  ↳ Обработка: {loc.text}")
                        sub_content = self.fetch_sitemap(loc.text)
                        if sub_content:
                            urls_data.extend(self.parse_sitemap(sub_content, loc.text))
                return urls_data
            
            # Парсинг обычного sitemap
            urlset = root.findall('.//ns:url', namespace)
            
            for url_element in urlset:
                url_data = {}
                
                # Извлечение loc
                loc = url_element.find('ns:loc', namespace)
                if loc is not None and loc.text:
                    url_data['loc'] = loc.text.strip()
                else:
                    self.errors.append(f"❌ Пустой тег <loc> в {sitemap_url}")
                    continue
                
                # Извлечение lastmod
                lastmod = url_element.find('ns:lastmod', namespace)
                url_data['lastmod'] = lastmod.text.strip() if lastmod is not None and lastmod.text else None
                
                # Извлечение changefreq
                changefreq = url_element.find('ns:changefreq', namespace)
                url_data['changefreq'] = changefreq.text.strip() if changefreq is not None and changefreq.text else None
                
                # Извлечение priority
                priority = url_element.find('ns:priority', namespace)
                url_data['priority'] = priority.text.strip() if priority is not None and priority.text else None
                
                url_data['source_sitemap'] = sitemap_url
                urls_data.append(url_data)
            
            self.statistics['total_urls'] += len(urlset)
            
        except ET.ParseError as e:
            self.errors.append(f"❌ Ошибка парсинга XML: {e}")
        except Exception as e:
            self.errors.append(f"❌ Неожиданная ошибка при парсинге: {e}")
        
        return urls_data
    
    def validate_url_format(self, url: str) -> List[str]:
        """Валидация формата URL"""
        issues = []
        
        # Проверка протокола
        if not url.startswith(('http://', 'https://')):
            issues.append("Отсутствует протокол (http/https)")
        
        # Проверка длины URL
        if len(url) > 2048:
            issues.append(f"URL слишком длинный ({len(url)} символов, рекомендуется до 2048)")
        
        # Проверка на пробелы
        if ' ' in url:
            issues.append("URL содержит пробелы")
        
        # Проверка на кириллицу (не закодированную)
        if re.search(r'[а-яА-ЯёЁ]', url):
            issues.append("URL содержит незакодированные кириллические символы")
        
        # Проверка на спецсимволы
        forbidden_chars = ['<', '>', '"', '{', '}', '|', '\\', '^', '`', '[', ']']
        for char in forbidden_chars:
            if char in url:
                issues.append(f"URL содержит запрещенный символ: {char}")
        
        return issues
    
    def validate_lastmod(self, lastmod: str) -> List[str]:
        """Валидация даты lastmod"""
        issues = []
        
        if not lastmod:
            return issues
        
        # Допустимые форматы даты
        date_formats = [
            '%Y-%m-%d',
            '%Y-%m-%dT%H:%M:%S%z',
            '%Y-%m-%dT%H:%M:%S.%f%z',
            '%Y-%m-%dT%H:%M:%SZ',
            '%Y-%m-%d %H:%M:%S'
        ]
        
        valid = False
        for fmt in date_formats:
            try:
                datetime.strptime(lastmod.replace('+00:00', 'Z'), fmt.replace('%z', 'Z'))
                valid = True
                break
            except ValueError:
                continue
        
        if not valid:
            issues.append(f"Неверный формат даты lastmod: {lastmod}")
        
        # Проверка на будущую дату
        try:
            date = datetime.fromisoformat(lastmod.replace('Z', '+00:00'))
            if date > datetime.now(date.tzinfo or None):
                issues.append("Дата lastmod в будущем")
        except:
            pass
        
        return issues
    
    def validate_changefreq(self, changefreq: str) -> List[str]:
        """Валидация changefreq"""
        issues = []
        
        if not changefreq:
            return issues
        
        valid_values = ['always', 'hourly', 'daily', 'weekly', 'monthly', 'yearly', 'never']
        
        if changefreq.lower() not in valid_values:
            issues.append(f"Неверное значение changefreq: {changefreq}")
        
        return issues
    
    def validate_priority(self, priority: str) -> List[str]:
        """Валидация priority"""
        issues = []
        
        if not priority:
            return issues
        
        try:
            p = float(priority)
            if p < 0.0 or p > 1.0:
                issues.append(f"Priority вне диапазона 0.0-1.0: {priority}")
        except ValueError:
            issues.append(f"Неверное значение priority: {priority}")
        
        return issues
    
    def check_url_status(self, url: str) -> Tuple[int, str]:
        """Проверка HTTP статуса URL"""
        try:
            response = requests.head(url, headers=self.headers, timeout=5, allow_redirects=False)
            return response.status_code, response.headers.get('Location', '')
        except requests.exceptions.RequestException:
            try:
                response = requests.get(url, headers=self.headers, timeout=5, allow_redirects=False)
                return response.status_code, response.headers.get('Location', '')
            except:
                return 0, ''
    
    def analyze_urls(self, check_status: bool = False):
        """Комплексный анализ URL из sitemap"""
        print(f"\n🔍 Анализ {len(self.urls)} URL...")
        
        url_set = set()
        domain_urls = 0
        external_urls = 0
        protocol_issues = 0
        
        for idx, url_data in enumerate(self.urls, 1):
            url = url_data['loc']
            issues = []
            
            # Прогресс
            if idx % 100 == 0:
                print(f"  Обработано: {idx}/{len(self.urls)}")
            
            # Проверка дубликатов
            if url in url_set:
                issues.append("⚠️ Дубликат URL")
                self.statistics['duplicates'] += 1
            else:
                url_set.add(url)
            
            # Проверка домена
            url_domain = urlparse(url).netloc
            if url_domain != self.domain:
                issues.append(f"⚠️ Внешний домен: {url_domain}")
                external_urls += 1
            else:
                domain_urls += 1
            
            # Проверка протокола
            url_protocol = urlparse(url).scheme
            if url_protocol != self.protocol:
                issues.append(f"⚠️ Несоответствие протокола: {url_protocol} (ожидался {self.protocol})")
                protocol_issues += 1
            
            # Валидация формата URL
            format_issues = self.validate_url_format(url)
            issues.extend(format_issues)
            
            # Валидация lastmod
            if url_data.get('lastmod'):
                lastmod_issues = self.validate_lastmod(url_data['lastmod'])
                issues.extend(lastmod_issues)
            
            # Валидация changefreq
            if url_data.get('changefreq'):
                changefreq_issues = self.validate_changefreq(url_data['changefreq'])
                issues.extend(changefreq_issues)
            
            # Валидация priority
            if url_data.get('priority'):
                priority_issues = self.validate_priority(url_data['priority'])
                issues.extend(priority_issues)
            
            # Проверка HTTP статуса (опционально)
            status_code = None
            redirect_to = None
            if check_status:
                status_code, redirect_to = self.check_url_status(url)
                
                if status_code == 0:
                    issues.append("❌ URL недоступен")
                elif status_code >= 400:
                    issues.append(f"❌ Ошибка {status_code}")
                    self.statistics['error_urls'] += 1
                elif status_code in [301, 302, 307, 308]:
                    issues.append(f"⚠️ Редирект {status_code} → {redirect_to}")
                    self.statistics['redirects'] += 1
                elif status_code == 200:
                    self.statistics['ok_urls'] += 1
                
                time.sleep(0.1)  # Задержка между запросами
            
            # Сохранение деталей
            self.url_details.append({
                'url': url,
                'lastmod': url_data.get('lastmod'),
                'changefreq': url_data.get('changefreq'),
                'priority': url_data.get('priority'),
                'status_code': status_code,
                'redirect_to': redirect_to,
                'issues': issues
            })
            
            if issues:
                self.warnings.append(f"{url}: {', '.join(issues)}")
        
        self.statistics['domain_urls'] = domain_urls
        self.statistics['external_urls'] = external_urls
        self.statistics['protocol_issues'] = protocol_issues
    
    def generate_report(self):
        """Генерация детального отчета"""
        print("\n" + "="*80)
        print("📊 ОТЧЕТ ПО АНАЛИЗУ SITEMAP")
        print("="*80)
        
        print(f"\n📍 Анализируемый sitemap: {self.sitemap_url}")
        print(f"🌐 Домен: {self.domain}")
        print(f"🔒 Протокол: {self.protocol}")
        
        # Основная статистика
        print(f"\n📈 ОСНОВНАЯ СТАТИСТИКА:")
        print(f"  • Всего URL в sitemap: {self.statistics['total_urls']}")
        print(f"  • URL своего домена: {self.statistics['domain_urls']}")
        print(f"  • Внешних URL: {self.statistics['external_urls']}")
        print(f"  • Дубликатов: {self.statistics['duplicates']}")
        print(f"  • Проблем с протоколом: {self.statistics['protocol_issues']}")
        
        if self.statistics.get('ok_urls'):
            print(f"\n🌐 ПРОВЕРКА ДОСТУПНОСТИ:")
            print(f"  • Доступных (200): {self.statistics['ok_urls']}")
            print(f"  • С редиректами: {self.statistics['redirects']}")
            print(f"  • С ошибками: {self.statistics['error_urls']}")
        
        # Критические ошибки
        if self.errors:
            print(f"\n❌ КРИТИЧЕСКИЕ ОШИБКИ ({len(self.errors)}):")
            for error in self.errors[:10]:
                print(f"  {error}")
            if len(self.errors) > 10:
                print(f"  ... и еще {len(self.errors) - 10} ошибок")
        
        # Предупреждения
        if self.warnings:
            print(f"\n⚠️  ПРЕДУПРЕЖДЕНИЯ ({len(self.warnings)}):")
            for warning in self.warnings[:20]:
                print(f"  {warning}")
            if len(self.warnings) > 20:
                print(f"  ... и еще {len(self.warnings) - 20} предупреждений")
        
        # Рекомендации
        print(f"\n💡 РЕКОМЕНДАЦИИ:")
        
        if self.statistics['duplicates'] > 0:
            print(f"  ⚠️ Удалите {self.statistics['duplicates']} дубликатов URL")
        
        if self.statistics['external_urls'] > 0:
            print(f"  ⚠️ Удалите {self.statistics['external_urls']} внешних URL")
        
        if self.statistics['protocol_issues'] > 0:
            print(f"  ⚠️ Исправьте {self.statistics['protocol_issues']} несоответствий протокола")
        
        if self.statistics.get('redirects', 0) > 0:
            print(f"  ⚠️ Замените {self.statistics['redirects']} URL с редиректами на финальные")
        
        if self.statistics.get('error_urls', 0) > 0:
            print(f"  ❌ Удалите или исправьте {self.statistics['error_urls']} недоступных URL")
        
        if self.statistics['total_urls'] > 50000:
            print(f"  ⚠️ Sitemap содержит {self.statistics['total_urls']} URL (лимит 50,000)")
            print(f"     Разбейте на несколько sitemap и используйте sitemap index")
        
        # Итоговая оценка
        print(f"\n{'='*80}")
        total_issues = len(self.errors) + len(self.warnings)
        if total_issues == 0:
            print("✅ ОТЛИЧНО! Sitemap не содержит ошибок")
        elif total_issues < 10:
            print(f"⚠️  ХОРОШО: Обнаружено {total_issues} незначительных проблем")
        elif total_issues < 50:
            print(f"⚠️  СРЕДНЕ: Обнаружено {total_issues} проблем, требуется оптимизация")
        else:
            print(f"❌ КРИТИЧНО: Обнаружено {total_issues} проблем, требуется срочная доработка")
        print(f"{'='*80}\n")
    
    def save_detailed_report(self, filename: str = 'sitemap_report.txt'):
        """Сохранение детального отчета в файл"""
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("ДЕТАЛЬНЫЙ ОТЧЕТ ПО SITEMAP\n")
            f.write("="*80 + "\n\n")
            
            for detail in self.url_details:
                f.write(f"URL: {detail['url']}\n")
                if detail['lastmod']:
                    f.write(f"  Last Modified: {detail['lastmod']}\n")
                if detail['changefreq']:
                    f.write(f"  Change Frequency: {detail['changefreq']}\n")
                if detail['priority']:
                    f.write(f"  Priority: {detail['priority']}\n")
                if detail['status_code']:
                    f.write(f"  HTTP Status: {detail['status_code']}\n")
                if detail['redirect_to']:
                    f.write(f"  Redirect To: {detail['redirect_to']}\n")
                if detail['issues']:
                    f.write(f"  Проблемы:\n")
                    for issue in detail['issues']:
                        f.write(f"    - {issue}\n")
                f.write("\n")
        
        print(f"💾 Детальный отчет сохранен в: {filename}")
    
    def run(self, check_status: bool = False, save_report: bool = False):
        """Запуск полного анализа"""
        print("🚀 Запуск анализа sitemap...")
        print(f"🔗 URL: {self.sitemap_url}\n")
        
        # Загрузка sitemap
        content = self.fetch_sitemap(self.sitemap_url)
        if not content:
            print("\n❌ Не удалось загрузить sitemap")
            return
        
        # Парсинг
        self.urls = self.parse_sitemap(content, self.sitemap_url)
        
        if not self.urls:
            print("\n❌ Не найдено ни одного URL в sitemap")
            return
        
        # Анализ
        self.analyze_urls(check_status=check_status)
        
        # Генерация отчета
        self.generate_report()
        
        # Сохранение детального отчета
        if save_report:
            self.save_detailed_report()


def main():
    """Основная функция"""
    print("""
╔═══════════════════════════════════════════════════════════════╗
║         🔍 ПРОФЕССИОНАЛЬНЫЙ АНАЛИЗАТОР SITEMAP 2.0           ║
║                   SEO & Web Development Tool                  ║
╚═══════════════════════════════════════════════════════════════╝
    """)
    
    # Пример использования
    if len(sys.argv) > 1:
        sitemap_url = sys.argv[1]
    else:
        sitemap_url = input("Введите URL sitemap: ").strip()
    
    if not sitemap_url:
        print("❌ URL не указан")
        return
    
    # Опции
    check_status = input("\nПроверять HTTP статус каждого URL? (медленно) [y/N]: ").lower() == 'y'
    save_report = input("Сохранить детальный отчет в файл? [y/N]: ").lower() == 'y'
    
    # Запуск анализатора
    analyzer = SitemapAnalyzer(sitemap_url)
    analyzer.run(check_status=check_status, save_report=save_report)


if __name__ == "__main__":
    main()
