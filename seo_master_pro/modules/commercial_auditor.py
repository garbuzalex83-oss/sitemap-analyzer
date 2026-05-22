"""
SEO Master PRO - Модуль анализа коммерческих факторов для E-commerce
Профессиональная проверка наличия элементов доверия и конверсии
"""

import re
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum


class CommercialFactorType(Enum):
    """Типы коммерческих факторов"""
    PRICE = "price"
    BUY_BUTTON = "buy_button"
    CART = "cart"
    CONTACTS = "contacts"
    DELIVERY = "delivery"
    PAYMENT = "payment"
    WARRANTY = "warranty"
    RETURNS = "returns"
    REVIEWS = "reviews"
    TRUST_BADGES = "trust_badges"
    AVAILABILITY = "availability"
    SKU = "sku"
    BRAND = "brand"
    SPECIFICATIONS = "specifications"
    CTA = "cta"
    SOCIAL_PROOF = "social_proof"


@dataclass
class CommercialElement:
    """Найденный коммерческий элемент"""
    element_type: CommercialFactorType
    found: bool
    confidence: float  # 0.0 - 1.0
    content: Optional[str] = None
    location: Optional[str] = None  # CSS селектор или XPath
    issues: List[str] = field(default_factory=list)


@dataclass
class CommercialIssue:
    """Проблема с коммерческими факторами"""
    url: str
    factor_type: CommercialFactorType
    severity: str  # critical, high, medium, low
    message: str
    recommendation: str
    impact_on_conversion: str  # high, medium, low
    impact_on_seo: str  # high, medium, low


class CommercialFactorsAuditor:
    """
    Профессиональный аудитор коммерческих факторов
    Проверяет наличие всех необходимых элементов для доверия и конверсии
    """
    
    # Паттерны для поиска элементов
    PATTERNS = {
        'price': [
            r'цена[:\s]*([\d\s,]+)',
            r'(\d[\d\s,]*)\s*(руб|usd|eur|грн|lei|€|\$|₽)',
            r'cost[:\s]*([\d\s,]+)',
            r'стоимость[:\s]*([\d\s,]+)',
            r'<span[^>]*class="[^"]*price[^"]*"[^>]*>(.*?)</span>',
            r'<meta[^>]*property="product:price[^"]*"[^>]*content="([^"]*)"',
            r'data-price=["\']([\d\s,]+)["\']',
        ],
        'buy_button': [
            r'<button[^>]*>[^<]*(купить|add\s*to\s*cart|в\s*корзину|заказать)[^<]*</button>',
            r'<a[^>]*class="[^"]*(buy|cart|order)[^"]*"[^>]*>',
            r'<input[^>]*type=["\']submit["\'][^>]*value=["\']([^"\']*(купить|заказать)[^"\']*)["\']',
            r'data-action=["\'](buy|add-to-cart|order)["\']',
            r'class=["\'][^"\']*(btn-buy|buy-btn|add-to-cart)[^"\']*["\']',
        ],
        'cart': [
            r'<a[^>]*href=["\'][^"\']*cart[^"\']*["\']',
            r'<div[^>]*class=["\'][^"\']*(cart|корзина)[^"\']*["\']',
            r'корзина\s*\((\d+)\)',
            r'<span[^>]*class=["\'][^"\']*cart[^"\']*["\']',
        ],
        'contacts': [
            r'tel:[+\d()\- ]+',
            r'<a[^>]*href=["\']tel:[^"\']*["\']',
            r'[\+]?[\d][\d\s()\-]{8,}\d',
            r'<span[^>]*class=["\'][^"\']*(phone|contact|телефон)[^"\']*["\']',
            r'email[:\s]*([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})',
            r'<a[^>]*href=["\']mailto:[^"\']*["\']',
        ],
        'delivery': [
            r'(доставка|shipping|delivery)[:\s]',
            r'(бесплатная\s*доставка|free\s*shipping)',
            r'(доставка\s*по|shipping\s*to)\s*[\w\s,]+',
            r'<a[^>]*href=["\'][^"\']*(delivery|shipping|доставка)[^"\']*["\']',
            r'class=["\'][^"\']*(delivery|shipping-info)[^"\']*["\']',
        ],
        'payment': [
            r'(оплата|payment)[:\s]',
            r'(наличные|card|картой|visa|mastercard|paypal)',
            r'<a[^>]*href=["\'][^"\']*(payment|оплата)[^"\']*["\']',
            r'class=["\'][^"\']*(payment|payment-methods)[^"\']*["\']',
        ],
        'warranty': [
            r'(гарантия|warranty)[:\s]*(\d+)?\s*(мес|год|month|year)',
            r'(гарантийный\s*срок|warranty\s*period)',
            r'<a[^>]*href=["\'][^"\']*(warranty|гарантия)[^"\']*["\']',
        ],
        'returns': [
            r'(возврат|return|exchange)[:\s]',
            r'(возврат\s*товара|return\s*policy)',
            r'(обмен\s*товара|exchange\s*policy)',
            r'<a[^>]*href=["\'][^"\']*(return|returns|возврат)[^"\']*["\']',
        ],
        'reviews': [
            r'<div[^>]*class=["\'][^"\']*(review|отзыв|rating)[^"\']*["\']',
            r'отзывы?\s*\((\d+)\)',
            r'reviews?\s*\((\d+)\)',
            r'<span[^>]*class=["\'][^"\']*(rating|stars)[^"\']*["\']',
            r'data-rating=["\']([\d.]+)["\']',
        ],
        'trust_badges': [
            r'(безопасная\s*оплата|secure\s*payment)',
            r'(SSL|HTTPS|защищено|protected)',
            r'<img[^>]*alt=["\'][^"\']*(secure|trust|badge)[^"\']*["\']',
            r'class=["\'][^"\']*(trust-badge|security-badge)[^"\']*["\']',
        ],
        'availability': [
            r'(в\s*наличии|in\s*stock|available)',
            r'(нет\s*в\s*наличии|out\s*of\s*stock|unavailable)',
            r'(осталось\s*\d+|only\s*\d+\s*left)',
            r'<span[^>]*class=["\'][^"\']*(availability|stock|наличие)[^"\']*["\']',
            r'data-availability=["\'](in-stock|out-of-stock)["\']',
        ],
        'sku': [
            r'(арт\.?|SKU|код\s*товара|артикул)[:\s]*([\w\-]+)',
            r'<meta[^>]*property="product:product_id[^"]*"[^>]*content="([^"]*)"',
            r'data-sku=["\']([\w\-]+)["\']',
        ],
        'brand': [
            r'<meta[^>]*property="product:brand[^"]*"[^>]*content="([^"]*)"',
            r'data-brand=["\']([^"\']+)["\']',
            r'<a[^>]*href=["\'][^"\']*(brand|бренд)[^"\']*["\'][^>]*>([^<]+)</a>',
        ],
        'specifications': [
            r'<table[^>]*class=["\'][^"\']*(specs|specifications|характеристики)[^"\']*["\']',
            r'<div[^>]*class=["\'][^"\']*(specs|specifications|характеристики)[^"\']*["\']',
            r'(характеристики|specifications|specs)[:\s]',
            r'<th[^>]*>[\s]*(материал|цвет|размер|вес|dimensions|material|color)[\s]*</th>',
        ],
        'cta': [
            r'<button[^>]*>[^<]*(заказать|купить|оформить|subscribe)[^<]*</button>',
            r'<a[^>]*class=["\'][^"\']*(cta|call-to-action)[^"\']*["\']',
            r'(свяжитесь\s*с\s*нами|contact\s*us|закажите\s*сейчас|order\s*now)',
        ],
        'social_proof': [
            r'<div[^>]*class=["\'][^"\']*(testimonials|social-proof)[^"\']*["\']',
            r'(нам\s*доверяют|trusted\s*by|клиентов|customers)',
            r'<div[^>]*class=["\'][^"\']*(partners|clients|логотипы)[^"\']*["\']',
        ],
    }
    
    # Обязательные элементы для разных типов страниц
    REQUIRED_ELEMENTS = {
        'product': [
            CommercialFactorType.PRICE,
            CommercialFactorType.BUY_BUTTON,
            CommercialFactorType.AVAILABILITY,
            CommercialFactorType.CONTACTS,
            CommercialFactorType.DELIVERY,
            CommercialFactorType.SKU,
        ],
        'category': [
            CommercialFactorType.CONTACTS,
            CommercialFactorType.DELIVERY,
            CommercialFactorType.CART,
        ],
        'homepage': [
            CommercialFactorType.CONTACTS,
            CommercialFactorType.DELIVERY,
            CommercialFactorType.PAYMENT,
            CommercialFactorType.TRUST_BADGES,
        ],
    }
    
    def __init__(self):
        self.issues: List[CommercialIssue] = []
        self.elements: List[CommercialElement] = []
    
    def analyze_page(self, url: str, html: str, page_type: str = 'product') -> Dict:
        """
        Полный анализ коммерческих факторов страницы
        
        Args:
            url: URL страницы
            html: HTML контент
            page_type: Тип страницы (product, category, homepage)
            
        Returns:
            Dict с результатами анализа
        """
        self.issues = []
        self.elements = []
        
        # Анализ всех факторов
        for factor_type in CommercialFactorType:
            element = self._check_factor(html, factor_type)
            self.elements.append(element)
        
        # Проверка обязательных элементов
        required = self.REQUIRED_ELEMENTS.get(page_type, [])
        for factor_type in required:
            element = next((e for e in self.elements if e.element_type == factor_type), None)
            if element and not element.found:
                self._add_critical_issue(url, factor_type, page_type)
        
        # Расчет scores
        result = {
            'url': url,
            'page_type': page_type,
            'elements_found': [e.__dict__ for e in self.elements if e.found],
            'elements_missing': [e.__dict__ for e in self.elements if not e.found],
            'total_elements': len([e for e in self.elements if e.found]),
            'commercial_score': self._calculate_commercial_score(),
            'trust_score': self._calculate_trust_score(),
            'conversion_readiness': self._calculate_conversion_readiness(page_type),
            'issues': [i.__dict__ for i in self.issues],
            'critical_issues': len([i for i in self.issues if i.severity == 'critical']),
            'recommendations': self._generate_recommendations(page_type),
        }
        
        return result
    
    def _check_factor(self, html: str, factor_type: CommercialFactorType) -> CommercialElement:
        """Проверяет наличие конкретного фактора"""
        patterns = self.PATTERNS.get(factor_type.value, [])
        
        best_match = None
        best_confidence = 0.0
        best_content = None
        
        for pattern in patterns:
            matches = re.findall(pattern, html, re.IGNORECASE | re.MULTILINE)
            if matches:
                # Оценка уверенности по типу паттерна
                confidence = self._calculate_confidence(pattern, matches)
                if confidence > best_confidence:
                    best_confidence = confidence
                    best_match = pattern
                    best_content = matches[0] if isinstance(matches[0], str) else str(matches[0])
        
        found = best_confidence > 0.3  # Порог обнаружения
        
        return CommercialElement(
            element_type=factor_type,
            found=found,
            confidence=best_confidence,
            content=self._clean_content(best_content) if best_content else None,
            issues=self._check_element_issues(factor_type, best_content)
        )
    
    def _calculate_confidence(self, pattern: str, matches: List) -> float:
        """Рассчитывает уверенность обнаружения"""
        confidence = 0.5  # Базовая уверенность
        
        # Повышаем уверенность для структурных паттернов
        if '<meta' in pattern or 'data-' in pattern:
            confidence += 0.3
        elif '<span' in pattern or '<div' in pattern:
            confidence += 0.2
        elif 'class=' in pattern:
            confidence += 0.15
        
        # Повышаем уверенность за количество совпадений
        if len(matches) > 1:
            confidence += min(0.2, len(matches) * 0.05)
        
        return min(confidence, 1.0)
    
    def _clean_content(self, content: str) -> str:
        """Очищает контент от HTML тегов"""
        if not content:
            return content
        
        # Удаляем HTML теги
        cleaned = re.sub(r'<[^>]+>', '', content)
        # Очищаем пробелы
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        
        return cleaned[:200]  # Ограничиваем длину
    
    def _check_element_issues(self, factor_type: CommercialFactorType, content: Optional[str]) -> List[str]:
        """Проверяет конкретные проблемы элемента"""
        issues = []
        
        if not content:
            return issues
        
        # Проверка цены
        if factor_type == CommercialFactorType.PRICE:
            if '0' in content or 'бесплатно' in content.lower():
                issues.append("Цена равна 0 или указана как бесплатная")
            
            # Проверка на отсутствие валюты
            if not re.search(r'(руб|usd|eur|грн|lei|€|\$|₽)', content, re.IGNORECASE):
                issues.append("В цене не указана валюта")
        
        # Проверка доступности
        if factor_type == CommercialFactorType.AVAILABILITY:
            if re.search(r'(нет\s*в\s*наличии|out\s*of\s*stock)', content, re.IGNORECASE):
                issues.append("Товар отсутствует в наличии")
        
        return issues
    
    def _add_critical_issue(self, url: str, factor_type: CommercialFactorType, page_type: str):
        """Добавляет критическую проблему отсутствия обязательного элемента"""
        severity_map = {
            CommercialFactorType.PRICE: ('critical', 'Высокое', 'Высокое'),
            CommercialFactorType.BUY_BUTTON: ('critical', 'Критическое', 'Среднее'),
            CommercialFactorType.AVAILABILITY: ('high', 'Среднее', 'Высокое'),
            CommercialFactorType.CONTACTS: ('critical', 'Высокое', 'Высокое'),
            CommercialFactorType.DELIVERY: ('high', 'Среднее', 'Среднее'),
            CommercialFactorType.SKU: ('medium', 'Низкое', 'Среднее'),
        }
        
        severity, conv_impact, seo_impact = severity_map.get(
            factor_type, ('medium', 'Среднее', 'Среднее')
        )
        
        self.issues.append(CommercialIssue(
            url=url,
            factor_type=factor_type,
            severity=severity,
            message=f"Отсутствует обязательный элемент '{factor_type.value}' на странице типа '{page_type}'",
            recommendation=self._get_recommendation(factor_type),
            impact_on_conversion=conv_impact,
            impact_on_seo=seo_impact
        ))
    
    def _get_recommendation(self, factor_type: CommercialFactorType) -> str:
        """Возвращает рекомендацию для фактора"""
        recommendations = {
            CommercialFactorType.PRICE: "Добавьте четкую цену товара с указанием валюты. Используйте schema.org Product разметку.",
            CommercialFactorType.BUY_BUTTON: "Добавьте заметную кнопку 'Купить' или 'В корзину'. Разместите её над сгибом страницы.",
            CommercialFactorType.AVAILABILITY: "Добавьте информацию о наличии товара. Используйте индикаторы 'В наличии' / 'Нет в наличии'.",
            CommercialFactorType.CONTACTS: "Разместите контактный телефон в шапке сайта. Добавьте кликабельную ссылку tel:.",
            CommercialFactorType.DELIVERY: "Добавьте блок с информацией о доставке: сроки, стоимость, условия бесплатной доставки.",
            CommercialFactorType.SKU: "Укажите артикул товара (SKU). Это важно для сравнения цен и идентификации товара.",
            CommercialFactorType.CART: "Добавьте видимую иконку корзины с счетчиком товаров.",
            CommercialFactorType.PAYMENT: "Разместите информацию о способах оплаты и логотипы платежных систем.",
            CommercialFactorType.WARRANTY: "Добавьте информацию о гарантии на товар.",
            CommercialFactorType.RETURNS: "Добавьте ссылку на политику возврата товаров.",
            CommercialFactorType.TRUST_BADGES: "Добавьте значки доверия: безопасная оплата, SSL сертификат, гарантии.",
        }
        
        return recommendations.get(factor_type, "Доработайте этот элемент для улучшения пользовательского опыта.")
    
    def _calculate_commercial_score(self) -> int:
        """Рассчитывает общую оценку коммерческих факторов (0-100)"""
        if not self.elements:
            return 0
        
        weights = {
            CommercialFactorType.PRICE: 15,
            CommercialFactorType.BUY_BUTTON: 15,
            CommercialFactorType.AVAILABILITY: 10,
            CommercialFactorType.CONTACTS: 15,
            CommercialFactorType.DELIVERY: 10,
            CommercialFactorType.PAYMENT: 8,
            CommercialFactorType.SKU: 5,
            CommercialFactorType.BRAND: 5,
            CommercialFactorType.SPECIFICATIONS: 7,
            CommercialFactorType.REVIEWS: 5,
            CommercialFactorType.TRUST_BADGES: 5,
        }
        
        total_score = 0
        max_score = sum(weights.values())
        
        for element in self.elements:
            weight = weights.get(element.element_type, 3)
            if element.found:
                total_score += weight * element.confidence
        
        return int((total_score / max_score) * 100) if max_score > 0 else 0
    
    def _calculate_trust_score(self) -> int:
        """Рассчитывает оценку доверия (0-100)"""
        trust_elements = [
            CommercialFactorType.CONTACTS,
            CommercialFactorType.DELIVERY,
            CommercialFactorType.PAYMENT,
            CommercialFactorType.WARRANTY,
            CommercialFactorType.RETURNS,
            CommercialFactorType.TRUST_BADGES,
            CommercialFactorType.REVIEWS,
        ]
        
        found_count = sum(
            1 for e in self.elements 
            if e.element_type in trust_elements and e.found
        )
        
        return int((found_count / len(trust_elements)) * 100)
    
    def _calculate_conversion_readiness(self, page_type: str) -> str:
        """Оценивает готовность страницы к конверсии"""
        score = self._calculate_commercial_score()
        
        required = self.REQUIRED_ELEMENTS.get(page_type, [])
        missing_required = sum(
            1 for f in required 
            if not any(e.element_type == f and e.found for e in self.elements)
        )
        
        if score >= 80 and missing_required == 0:
            return "excellent"
        elif score >= 60 and missing_required <= 1:
            return "good"
        elif score >= 40 and missing_required <= 2:
            return "needs_improvement"
        else:
            return "critical"
    
    def _generate_recommendations(self, page_type: str) -> List[Dict]:
        """Генерирует список рекомендаций по приоритету"""
        recommendations = []
        
        # Критические рекомендации
        for issue in self.issues:
            if issue.severity == 'critical':
                recommendations.append({
                    'priority': 'critical',
                    'action': issue.recommendation,
                    'impact': 'Высокое влияние на конверсию и SEO',
                    'factor': issue.factor_type.value
                })
        
        # Рекомендации по отсутствующим важным элементам
        important_factors = [
            CommercialFactorType.PRICE,
            CommercialFactorType.BUY_BUTTON,
            CommercialFactorType.REVIEWS,
            CommercialFactorType.TRUST_BADGES,
        ]
        
        for factor in important_factors:
            element = next((e for e in self.elements if e.element_type == factor), None)
            if element and not element.found:
                if not any(r['factor'] == factor.value for r in recommendations):
                    recommendations.append({
                        'priority': 'high',
                        'action': self._get_recommendation(factor),
                        'impact': 'Среднее/Высокое влияние на конверсию',
                        'factor': factor.value
                    })
        
        return recommendations
    
    def compare_with_competitors(self, own_result: Dict, competitors: List[Dict]) -> Dict:
        """
        Сравнивает коммерческие факторы с конкурентами
        
        Args:
            own_result: Результаты анализа своей страницы
            competitors: Список результатов анализа страниц конкурентов
            
        Returns:
            Dict с сравнительным анализом
        """
        if not competitors:
            return {'error': 'Нет данных конкурентов'}
        
        # Средние показатели конкурентов
        avg_commercial_score = sum(c.get('commercial_score', 0) for c in competitors) / len(competitors)
        avg_trust_score = sum(c.get('trust_score', 0) for c in competitors) / len(competitors)
        
        # Какие элементы есть у конкурентов, но нет у нас
        own_elements = set(e['element_type'].value for e in own_result.get('elements_found', []))
        
        competitor_elements = set()
        for comp in competitors:
            for e in comp.get('elements_found', []):
                competitor_elements.add(e['element_type'].value)
        
        missing_vs_competitors = competitor_elements - own_elements
        
        # Преимущества перед конкурентами
        advantages = own_elements - competitor_elements
        
        return {
            'own_commercial_score': own_result.get('commercial_score', 0),
            'avg_competitor_score': round(avg_commercial_score, 1),
            'score_difference': round(own_result.get('commercial_score', 0) - avg_commercial_score, 1),
            'own_trust_score': own_result.get('trust_score', 0),
            'avg_competitor_trust_score': round(avg_trust_score, 1),
            'missing_vs_competitors': list(missing_vs_competitors),
            'advantages_vs_competitors': list(advantages),
            'recommendations': [
                f"Добавьте следующие элементы, которые есть у конкурентов: {', '.join(missing_vs_competitors)}"
            ] if missing_vs_competitors else ["Вы не уступаете конкурентам по коммерческим факторам"]
        }


# Пример использования
if __name__ == "__main__":
    # Тестовый HTML интернет-магазина
    test_html = """
    <html>
    <head>
        <title>Кроссовки Nike Air Max - купить в Москве</title>
    </head>
    <body>
        <header>
            <a href="tel:+74951234567">+7 (495) 123-45-67</a>
            <a href="/cart">Корзина <span class="cart-count">(3)</span></a>
        </header>
        
        <main>
            <h1>Кроссовки Nike Air Max</h1>
            
            <div class="product-info">
                <span class="price">12 990 ₽</span>
                <span class="availability" data-availability="in-stock">В наличии</span>
                <span class="sku">Артикул: NK-AM-001</span>
                <span data-brand="Nike">Nike</span>
            </div>
            
            <button class="btn-buy" data-action="buy">Купить</button>
            <button class="btn-cart" data-action="add-to-cart">В корзину</button>
            
            <div class="specifications">
                <h2>Характеристики</h2>
                <table>
                    <tr><th>Материал</th><td>Текстиль</td></tr>
                    <tr><th>Цвет</th><td>Белый/Черный</td></tr>
                </table>
            </div>
            
            <div class="delivery-info">
                <h2>Доставка</h2>
                <p>Бесплатная доставка при заказе от 5000 ₽</p>
                <p>Доставка по Москве 1-2 дня</p>
            </div>
            
            <div class="payment-methods">
                <h2>Оплата</h2>
                <p>Наличные, картой, Visa, Mastercard</p>
            </div>
            
            <div class="reviews">
                <h2>Отзывы</h2>
                <span class="rating" data-rating="4.5">★★★★☆</span>
                <p>Отзывы (127)</p>
            </div>
            
            <div class="trust-badges">
                <span>🔒 Безопасная оплата</span>
                <span>✓ Гарантия качества</span>
            </div>
        </main>
    </body>
    </html>
    """
    
    auditor = CommercialFactorsAuditor()
    result = auditor.analyze_page("https://example.com/product/nike-air-max", test_html, "product")
    
    print("=" * 80)
    print("АНАЛИЗ КОММЕРЧЕСКИХ ФАКТОРОВ")
    print("=" * 80)
    print(f"URL: {result['url']}")
    print(f"Тип страницы: {result['page_type']}")
    print(f"\nКоммерческая оценка: {result['commercial_score']}/100")
    print(f"Оценка доверия: {result['trust_score']}/100")
    print(f"Готовность к конверсии: {result['conversion_readiness']}")
    
    print(f"\nНайдено элементов: {result['total_elements']}")
    print(f"Критических проблем: {result['critical_issues']}")
    
    if result['elements_found']:
        print("\n" + "=" * 80)
        print("НАЙДЕННЫЕ ЭЛЕМЕНТЫ:")
        print("=" * 80)
        for elem in result['elements_found']:
            print(f"✓ {elem['element_type'].split('.')[-1].upper()}")
            if elem.get('content'):
                print(f"  Содержание: {elem['content'][:50]}...")
            if elem.get('confidence'):
                print(f"  Уверенность: {elem['confidence']:.0%}")
    
    if result['elements_missing']:
        print("\n" + "=" * 80)
        print("ОТСУТСТВУЮЩИЕ ЭЛЕМЕНТЫ:")
        print("=" * 80)
        for elem in result['elements_missing']:
            print(f"✗ {elem['element_type'].split('.')[-1].upper()}")
    
    if result['issues']:
        print("\n" + "=" * 80)
        print("ПРОБЛЕМЫ:")
        print("=" * 80)
        for issue in result['issues']:
            print(f"\n[{issue['severity'].upper()}] {issue['factor_type'].split('.')[-1]}")
            print(f"  Проблема: {issue['message']}")
            print(f"  Решение: {issue['recommendation']}")
            print(f"  Влияние на конверсию: {issue['impact_on_conversion']}")
    
    if result['recommendations']:
        print("\n" + "=" * 80)
        print("РЕКОМЕНДАЦИИ:")
        print("=" * 80)
        for rec in result['recommendations']:
            print(f"\n[{rec['priority'].upper()}] {rec['factor']}")
            print(f"  Действие: {rec['action']}")
            print(f"  Влияние: {rec['impact']}")
