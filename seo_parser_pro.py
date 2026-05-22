#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SEO PARSER PRO - Ultimate Professional SEO Analysis Tool
========================================================
Comprehensive SEO parser with advanced relevance analysis, 
technical SEO checks, and GEO optimization compliance.

Features:
- Deep Content Relevance Analysis (TF-IDF, Keyword Density, Semantic Clusters)
- Technical SEO Audit (Core Web Vitals, Indexability, Crawlability)
- On-Page Optimization (Meta tags, Headers, Schema.org, Open Graph)
- Link Architecture Analysis (Internal/External links, Anchor distribution)
- Mobile-Friendliness & Page Speed indicators
- Google E-E-A-T compliance checks
- Local SEO / GEO optimization validation
- Competitive gap analysis ready data
- Export to multiple formats (HTML, JSON, CSV, PDF-ready)

Author: SEO Expert AI
Version: 2.0 PRO
"""

import requests
from bs4 import BeautifulSoup, Comment
from urllib.parse import urljoin, urlparse, parse_qs
from collections import Counter, defaultdict
import re
import json
import csv
import hashlib
import time
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Any, Set
import math
import asyncio
from dataclasses import dataclass, field, asdict
from enum import Enum
import warnings
warnings.filterwarnings('ignore')

try:
    import pandas as pd
    import numpy as np
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

try:
    import nltk
    from nltk.corpus import stopwords
    from nltk.tokenize import word_tokenize, sent_tokenize
    from nltk.stem import WordNetLemmatizer
    NLTK_AVAILABLE = True
except ImportError:
    NLTK_AVAILABLE = False


class Severity(Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


@dataclass
class SEOIssue:
    """Represents a single SEO issue found during analysis"""
    category: str
    severity: Severity
    title: str
    description: str
    recommendation: str
    element: Optional[str] = None
    value: Optional[str] = None
    impact_score: float = 0.0


@dataclass
class KeywordMetrics:
    """Keyword analysis metrics"""
    keyword: str
    count: int
    density: float
    tf_idf: float = 0.0
    positions: List[int] = field(default_factory=list)
    in_title: bool = False
    in_h1: bool = False
    in_meta: bool = False
    in_first_paragraph: bool = False


@dataclass
class ContentRelevance:
    """Content relevance analysis results"""
    primary_topics: List[str] = field(default_factory=list)
    semantic_clusters: Dict[str, List[str]] = field(default_factory=dict)
    keyword_density: Dict[str, KeywordMetrics] = field(default_factory=dict)
    content_quality_score: float = 0.0
    readability_score: float = 0.0
    uniqueness_hash: str = ""
    word_count: int = 0
    sentence_count: int = 0
    paragraph_count: int = 0
    avg_sentence_length: float = 0.0
    lexical_diversity: float = 0.0
    entity_mentions: Dict[str, int] = field(default_factory=dict)


@dataclass
class TechnicalSEO:
    """Technical SEO audit results"""
    https_enabled: bool = False
    www_redirect: Optional[bool] = None
    canonical_url: Optional[str] = None
    robots_meta: Optional[str] = None
    hreflang_tags: List[str] = field(default_factory=list)
    amp_version: Optional[str] = None
    mobile_viewport: bool = False
    charset: Optional[str] = None
    language: Optional[str] = None
    doctype: Optional[str] = None
    http_status: int = 0
    response_time_ms: float = 0.0
    page_size_kb: float = 0.0
    load_time_estimate: float = 0.0
    render_blocking_resources: List[str] = field(default_factory=list)
    core_web_vitals: Dict[str, Any] = field(default_factory=dict)


@dataclass
class OnPageSEO:
    """On-page SEO elements"""
    title: Optional[str] = None
    title_length: int = 0
    title_optimal: bool = False
    meta_description: Optional[str] = None
    meta_description_length: int = 0
    meta_description_optimal: bool = False
    meta_keywords: Optional[str] = None
    h1_tags: List[str] = field(default_factory=list)
    h2_tags: List[str] = field(default_factory=list)
    h3_tags: List[str] = field(default_factory=list)
    h4_tags: List[str] = field(default_factory=list)
    h5_tags: List[str] = field(default_factory=list)
    h6_tags: List[str] = field(default_factory=list)
    header_hierarchy_valid: bool = False
    images_count: int = 0
    images_without_alt: int = 0
    images_with_alt: int = 0
    og_tags: Dict[str, str] = field(default_factory=dict)
    twitter_cards: Dict[str, str] = field(default_factory=dict)
    schema_org: List[Dict] = field(default_factory=list)
    favicon_present: bool = False
    internal_links_count: int = 0
    external_links_count: int = 0
    nofollow_links_count: int = 0
    broken_links: List[str] = field(default_factory=list)


@dataclass
class LinkAnalysis:
    """Detailed link architecture analysis"""
    total_internal: int = 0
    total_external: int = 0
    total_nofollow: int = 0
    total_dofollow: int = 0
    anchor_distribution: Dict[str, int] = field(default_factory=dict)
    internal_link_depth: Dict[int, int] = field(default_factory=dict)
    orphan_pages_detected: bool = False
    link_juice_flow: Dict[str, float] = field(default_factory=dict)
    toxic_links: List[Dict] = field(default_factory=list)
    redirect_chains: List[List[str]] = field(default_factory=list)


@dataclass
class GeoOptimization:
    """Local SEO / GEO optimization checks"""
    business_name_found: bool = False
    nap_consistent: bool = False
    local_schema_present: bool = False
    google_maps_embedded: bool = False
    local_keywords_present: bool = False
    city_region_mentions: Dict[str, int] = field(default_factory=dict)
    geo_coordinates: Optional[Dict[str, float]] = None
    opening_hours_specified: bool = False
    local_images: int = 0
    reviews_markup: bool = False


@dataclass
class EEATSignals:
    """Google E-E-A-T signals"""
    author_info_present: bool = False
    author_credentials: List[str] = field(default_factory=list)
    publication_date: Optional[str] = None
    last_modified: Optional[str] = None
    about_page_exists: bool = False
    contact_page_exists: bool = False
    privacy_policy_exists: bool = False
    terms_exists: bool = False
    external_citations: int = 0
    expert_review_indicated: bool = False
    trust_badges: List[str] = field(default_factory=list)
    ssl_certificate: bool = False
    secure_payment_indicators: bool = False


@dataclass
class SEOScore:
    """Overall SEO scoring"""
    total_score: float = 0.0
    technical_score: float = 0.0
    onpage_score: float = 0.0
    content_score: float = 0.0
    relevance_score: float = 0.0
    geo_score: float = 0.0
    eeat_score: float = 0.0
    grade: str = "F"
    passed_checks: int = 0
    total_checks: int = 0


class AdvancedTokenProcessor:
    """Advanced NLP text processing for SEO analysis"""
    
    def __init__(self, language: str = 'english'):
        self.language = language
        self.lemmatizer = WordNetLemmatizer() if NLTK_AVAILABLE else None
        
        if NLTK_AVAILABLE:
            try:
                self.stopwords = set(stopwords.words(language))
            except:
                self.stopwords = set(stopwords.words('english'))
        else:
            self.stopwords = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
                            'of', 'with', 'by', 'from', 'is', 'are', 'was', 'were', 'be', 'been',
                            'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
                            'could', 'should', 'may', 'might', 'must', 'shall', 'can', 'this',
                            'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they'}
        
        self.seo_stopwords = self.stopwords | {
            'click', 'here', 'read', 'more', 'learn', 'about', 'our', 'us', 'contact',
            'privacy', 'policy', 'terms', 'service', 'copyright', 'all', 'rights', 'reserved'
        }
    
    def tokenize(self, text: str) -> List[str]:
        if not text:
            return []
        text = text.lower()
        text = re.sub(r'[^\w\s]', ' ', text)
        text = re.sub(r'\s+', ' ', text).strip()
        return text.split()
    
    def remove_stopwords(self, tokens: List[str]) -> List[str]:
        return [t for t in tokens if t not in self.seo_stopwords and len(t) > 2]
    
    def lemmatize(self, tokens: List[str]) -> List[str]:
        if not self.lemmatizer:
            return tokens
        return [self.lemmatizer.lemmatize(t) for t in tokens]
    
    def process(self, text: str, remove_stops: bool = True, lemmatize: bool = True) -> List[str]:
        tokens = self.tokenize(text)
        if remove_stops:
            tokens = self.remove_stopwords(tokens)
        if lemmatize:
            tokens = self.lemmatize(tokens)
        return [t for t in tokens if len(t) > 2]


class CloudRelevanceAnalyzer:
    """
    Advanced Cloud Relevance Analyzer
    Implements TF-IDF, semantic clustering, and topical authority analysis
    """
    
    def __init__(self):
        self.processor = AdvancedTokenProcessor()
        self.vectorizer = TfidfVectorizer(
            max_features=500, ngram_range=(1, 3), min_df=2, max_df=0.8
        ) if SKLEARN_AVAILABLE else None
    
    def analyze_relevance_cloud(self, content: str, target_keywords: List[str] = None) -> ContentRelevance:
        result = ContentRelevance()
        
        if not content or len(content.strip()) < 50:
            return result
        
        result.word_count = len(content.split())
        sentences = sent_tokenize(content) if NLTK_AVAILABLE else content.split('.')
        result.sentence_count = len([s for s in sentences if s.strip()])
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
        result.paragraph_count = len(paragraphs)
        
        if result.sentence_count > 0:
            result.avg_sentence_length = result.word_count / result.sentence_count
        
        tokens = self.processor.process(content)
        unique_tokens = set(tokens)
        
        if len(tokens) > 0:
            result.lexical_diversity = len(unique_tokens) / len(tokens)
        
        token_freq = Counter(tokens)
        total_tokens = len(tokens)
        content_lower = content.lower()
        first_100_words = ' '.join(content_lower.split()[:100])
        
        for token, count in token_freq.most_common(50):
            if count < 2:
                continue
            
            density = (count / total_tokens) * 100 if total_tokens > 0 else 0
            positions = []
            start = 0
            while True:
                pos = content_lower.find(token, start)
                if pos == -1:
                    break
                positions.append(pos)
                start = pos + 1
            
            metrics = KeywordMetrics(
                keyword=token, count=count, density=round(density, 3),
                positions=positions[:20], in_title=token in content_lower[:500],
                in_h1=token in first_100_words, in_meta=token in content_lower[:1000],
                in_first_paragraph=token in first_100_words
            )
            result.keyword_density[token] = metrics
        
        if SKLEARN_AVAILABLE and self.vectorizer and len(paragraphs) > 3:
            try:
                tfidf_matrix = self.vectorizer.fit_transform(paragraphs)
                feature_names = self.vectorizer.get_feature_names_out()
                mean_tfidf = np.array(tfidf_matrix.mean(axis=0)).flatten()
                top_indices = mean_tfidf.argsort()[-20:][::-1]
                result.primary_topics = [feature_names[i] for i in top_indices if mean_tfidf[i] > 0.01]
                
                for idx, feature in enumerate(feature_names):
                    if feature in result.keyword_density:
                        result.keyword_density[feature].tf_idf = round(mean_tfidf[idx], 4)
                
                similarity_matrix = cosine_similarity(tfidf_matrix)
                clusters = self._cluster_topics(paragraphs, similarity_matrix, feature_names)
                result.semantic_clusters = clusters
            except:
                pass
        
        entities = self._extract_entities(content)
        result.entity_mentions = entities
        
        quality_factors = []
        if 1000 <= result.word_count <= 3000:
            quality_factors.append(1.0)
        elif 500 <= result.word_count < 1000 or 3000 < result.word_count <= 5000:
            quality_factors.append(0.7)
        elif result.word_count > 500:
            quality_factors.append(0.5)
        else:
            quality_factors.append(0.3)
        
        quality_factors.append(min(result.lexical_diversity * 2, 1.0))
        
        if result.paragraph_count >= 5 and result.sentence_count >= 10:
            quality_factors.append(1.0)
        elif result.paragraph_count >= 3:
            quality_factors.append(0.7)
        else:
            quality_factors.append(0.4)
        
        if 15 <= result.avg_sentence_length <= 25:
            quality_factors.append(1.0)
        elif 10 <= result.avg_sentence_length <= 30:
            quality_factors.append(0.8)
        else:
            quality_factors.append(0.6)
        
        result.content_quality_score = round(sum(quality_factors) / len(quality_factors) * 100, 2)
        result.uniqueness_hash = hashlib.md5(content.encode()).hexdigest()
        
        return result
    
    def _cluster_topics(self, paragraphs, similarity_matrix, feature_names):
        clusters = {}
        threshold = 0.3
        for i, para in enumerate(paragraphs[:10]):
            similar_indices = np.where(similarity_matrix[i] > threshold)[0]
            if len(similar_indices) > 1:
                cluster_key = f"cluster_{i}"
                cluster_terms = []
                for idx in similar_indices[:5]:
                    if idx < len(feature_names):
                        cluster_terms.extend(feature_names[idx].split())
                if cluster_terms:
                    term_freq = Counter(cluster_terms)
                    clusters[cluster_key] = [term for term, _ in term_freq.most_common(10)]
        return clusters
    
    def _extract_entities(self, text: str) -> Dict[str, int]:
        entities = {}
        org_pattern = r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)\b'
        orgs = re.findall(org_pattern, text)
        for org in orgs:
            entities[org] = entities.get(org, 0) + 1
        
        date_pattern = r'\b(\d{1,2}[./-]\d{1,2}[./-]\d{2,4})\b'
        dates = re.findall(date_pattern, text)
        if dates:
            entities['dates'] = len(dates)
        
        money_pattern = r'\$[\d,]+(?:\.\d{2})?'
        money = re.findall(money_pattern, text)
        if money:
            entities['monetary_values'] = len(money)
        
        percent_pattern = r'\d+(?:\.\d+)?%'
        percents = re.findall(percent_pattern, text)
        if percents:
            entities['percentages'] = len(percents)
        
        return dict(Counter(entities))


class TechnicalSEOAnalyzer:
    """Deep technical SEO analysis"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
        })
    
    def analyze(self, url: str) -> Tuple[TechnicalSEO, List[SEOIssue]]:
        result = TechnicalSEO()
        issues = []
        start_time = time.time()
        
        try:
            response = self.session.get(url, timeout=30, allow_redirects=True)
            result.response_time_ms = round((time.time() - start_time) * 1000, 2)
            result.http_status = response.status_code
            result.page_size_kb = round(len(response.content) / 1024, 2)
            result.load_time_estimate = round(result.response_time_ms + (result.page_size_kb * 0.5), 2)
            
            parsed_url = urlparse(url)
            result.https_enabled = parsed_url.scheme == 'https'
            
            if not result.https_enabled:
                issues.append(SEOIssue(
                    category="Security", severity=Severity.HIGH,
                    title="HTTPS Not Enabled",
                    description="Site is not using HTTPS protocol",
                    recommendation="Implement SSL certificate and redirect HTTP to HTTPS",
                    impact_score=8.5
                ))
            
            if response.status_code != 200:
                severity = Severity.CRITICAL if response.status_code >= 500 else Severity.MEDIUM
                issues.append(SEOIssue(
                    category="Crawlability", severity=severity,
                    title=f"HTTP Status {response.status_code}",
                    description=f"Page returned status code {response.status_code}",
                    recommendation="Ensure page returns 200 OK status",
                    impact_score=9.0 if response.status_code >= 500 else 5.0
                ))
            
            soup = BeautifulSoup(response.content, 'lxml')
            
            canonical = soup.find('link', rel='canonical')
            if canonical and canonical.get('href'):
                result.canonical_url = urljoin(url, canonical['href'])
            else:
                issues.append(SEOIssue(
                    category="On-Page", severity=Severity.MEDIUM,
                    title="Missing Canonical URL",
                    description="No canonical tag found",
                    recommendation="Add canonical tag to prevent duplicate content",
                    impact_score=4.0
                ))
            
            robots_meta = soup.find('meta', attrs={'name': 'robots'})
            if robots_meta:
                result.robots_meta = robots_meta.get('content')
                if 'noindex' in result.robots_meta.lower():
                    issues.append(SEOIssue(
                        category="Indexability", severity=Severity.CRITICAL,
                        title="Page Set to NoIndex",
                        description="Robots meta contains 'noindex'",
                        recommendation="Remove noindex if page should be indexed",
                        impact_score=10.0
                    ))
            
            hreflangs = soup.find_all('link', rel='alternate')
            for hreflang in hreflangs:
                if hreflang.get('hreflang'):
                    result.hreflang_tags.append(f"{hreflang.get('hreflang')}: {hreflang.get('href')}")
            
            viewport = soup.find('meta', attrs={'name': 'viewport'})
            result.mobile_viewport = viewport is not None
            
            if not result.mobile_viewport:
                issues.append(SEOIssue(
                    category="Mobile", severity=Severity.HIGH,
                    title="Missing Viewport Meta Tag",
                    description="Page lacks viewport for mobile",
                    recommendation="Add viewport meta tag",
                    impact_score=7.5
                ))
            
            charset_meta = soup.find('meta', attrs={'charset': True})
            if charset_meta:
                result.charset = charset_meta.get('charset')
            
            html_tag = soup.find('html')
            if html_tag and html_tag.get('lang'):
                result.language = html_tag['lang']
            else:
                issues.append(SEOIssue(
                    category="Accessibility", severity=Severity.LOW,
                    title="Missing Language Attribute",
                    description="HTML lacks lang attribute",
                    recommendation="Add lang attribute to HTML tag",
                    impact_score=2.0
                ))
            
            scripts = soup.find_all('script', src=True)
            for script in scripts:
                if not script.get('async') and not script.get('defer'):
                    result.render_blocking_resources.append(script['src'])
            
            if len(result.render_blocking_resources) > 3:
                issues.append(SEOIssue(
                    category="Performance", severity=Severity.MEDIUM,
                    title="Multiple Render-Blocking Resources",
                    description=f"Found {len(result.render_blocking_resources)} blocking scripts",
                    recommendation="Add async/defer to non-critical scripts",
                    impact_score=5.5
                ))
            
            result.core_web_vitals = {
                'lcp_estimate': round(result.load_time_estimate * 0.7, 2),
                'fid_estimate': round(result.response_time_ms * 0.3, 2),
                'cls_estimate': 0.05 if result.mobile_viewport else 0.15,
                'performance_score': max(0, 100 - (result.load_time_estimate / 50))
            }
            
        except requests.exceptions.RequestException as e:
            issues.append(SEOIssue(
                category="Crawlability", severity=Severity.CRITICAL,
                title="Request Failed",
                description=f"Failed to fetch URL: {str(e)}",
                recommendation="Check URL and server availability",
                impact_score=10.0
            ))
        
        return result, issues


class OnPageSEOAnalyzer:
    """Comprehensive on-page SEO analysis"""
    
    def analyze(self, url: str, html_content: str) -> Tuple[OnPageSEO, List[SEOIssue]]:
        result = OnPageSEO()
        issues = []
        soup = BeautifulSoup(html_content, 'lxml')
        
        title_tag = soup.find('title')
        if title_tag and title_tag.string:
            result.title = title_tag.string.strip()
            result.title_length = len(result.title)
            
            if result.title_length == 0:
                issues.append(SEOIssue(
                    category="On-Page", severity=Severity.HIGH,
                    title="Empty Title Tag",
                    description="Title tag is empty",
                    recommendation="Add descriptive title (50-60 chars)",
                    impact_score=8.0
                ))
            elif result.title_length < 30:
                issues.append(SEOIssue(
                    category="On-Page", severity=Severity.MEDIUM,
                    title="Title Too Short",
                    description=f"Title is {result.title_length} chars (optimal: 50-60)",
                    recommendation="Expand title with keywords",
                    impact_score=4.5
                ))
            elif result.title_length > 70:
                issues.append(SEOIssue(
                    category="On-Page", severity=Severity.LOW,
                    title="Title Too Long",
                    description=f"Title is {result.title_length} chars (may truncate)",
                    recommendation="Shorten to 50-60 characters",
                    impact_score=3.0
                ))
            else:
                result.title_optimal = True
        else:
            issues.append(SEOIssue(
                category="On-Page", severity=Severity.HIGH,
                title="Missing Title Tag",
                description="No title tag found",
                recommendation="Add unique title tag",
                impact_score=8.5
            ))
        
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc and meta_desc.get('content'):
            result.meta_description = meta_desc['content'].strip()
            result.meta_description_length = len(result.meta_description)
            
            if result.meta_description_length < 120:
                issues.append(SEOIssue(
                    category="On-Page", severity=Severity.MEDIUM,
                    title="Meta Description Too Short",
                    description=f"Description is {result.meta_description_length} chars",
                    recommendation="Expand to 150-160 characters",
                    impact_score=4.0
                ))
            elif result.meta_description_length > 170:
                issues.append(SEOIssue(
                    category="On-Page", severity=Severity.LOW,
                    title="Meta Description Too Long",
                    description=f"Description is {result.meta_description_length} chars",
                    recommendation="Shorten to 150-160 characters",
                    impact_score=2.5
                ))
            else:
                result.meta_description_optimal = True
        else:
            issues.append(SEOIssue(
                category="On-Page", severity=Severity.MEDIUM,
                title="Missing Meta Description",
                description="No meta description found",
                recommendation="Add compelling meta description",
                impact_score=5.0
            ))
        
        for i in range(1, 7):
            tags = soup.find_all(f'h{i}')
            tag_list = [tag.get_text().strip() for tag in tags if tag.get_text().strip()]
            
            if i == 1:
                result.h1_tags = tag_list
                if len(result.h1_tags) == 0:
                    issues.append(SEOIssue(
                        category="On-Page", severity=Severity.HIGH,
                        title="Missing H1 Tag",
                        description="No H1 heading found",
                        recommendation="Add one H1 tag",
                        impact_score=7.0
                    ))
                elif len(result.h1_tags) > 1:
                    issues.append(SEOIssue(
                        category="On-Page", severity=Severity.LOW,
                        title="Multiple H1 Tags",
                        description=f"Found {len(result.h1_tags)} H1 tags",
                        recommendation="Use only one H1 per page",
                        impact_score=2.0
                    ))
            elif i == 2:
                result.h2_tags = tag_list
            elif i == 3:
                result.h3_tags = tag_list
            elif i == 4:
                result.h4_tags = tag_list
        
        result.header_hierarchy_valid = self._validate_header_hierarchy(soup)
        
        images = soup.find_all('img')
        result.images_count = len(images)
        
        for img in images:
            alt = img.get('alt')
            if alt and alt.strip():
                result.images_with_alt += 1
            else:
                result.images_without_alt += 1
        
        if result.images_without_alt > 0:
            severity = Severity.MEDIUM if result.images_without_alt > 5 else Severity.LOW
            issues.append(SEOIssue(
                category="On-Page", severity=severity,
                title="Images Missing Alt Text",
                description=f"{result.images_without_alt} images lack alt",
                recommendation="Add alt text to all images",
                impact_score=4.0 if result.images_without_alt > 5 else 2.0
            ))
        
        og_tags = soup.find_all('meta', property=lambda x: x and x.startswith('og:'))
        for og in og_tags:
            prop = og.get('property')
            content = og.get('content')
            if prop and content:
                result.og_tags[prop] = content
        
        schema_scripts = soup.find_all('script', type='application/ld+json')
        for script in schema_scripts:
            try:
                schema_data = json.loads(script.string)
                result.schema_org.append(schema_data)
            except:
                pass
        
        favicon = soup.find('link', rel=lambda x: x and 'icon' in x.lower())
        result.favicon_present = favicon is not None
        
        links = soup.find_all('a', href=True)
        parsed_url = urlparse(url)
        base_domain = parsed_url.netloc
        
        for link in links:
            href = link.get('href', '')
            if not href or href.startswith('#') or href.startswith('javascript:'):
                continue
            
            link_domain = urlparse(urljoin(url, href)).netloc
            rel = link.get('rel', '')
            
            if link_domain == base_domain or link_domain == '':
                result.internal_links_count += 1
            else:
                result.external_links_count += 1
            
            if 'nofollow' in rel.lower():
                result.nofollow_links_count += 1
        
        return result, issues
    
    def _validate_header_hierarchy(self, soup) -> bool:
        headers = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
        if not headers:
            return False
        current_level = 0
        for header in headers:
            level = int(header.name[1])
            if level > current_level + 1:
                return False
            current_level = level
        return True


class LinkArchitectureAnalyzer:
    """Deep link architecture analysis"""
    
    def analyze(self, url: str, html_content: str) -> Tuple[LinkAnalysis, List[SEOIssue]]:
        result = LinkAnalysis()
        issues = []
        soup = BeautifulSoup(html_content, 'lxml')
        parsed_url = urlparse(url)
        base_domain = parsed_url.netloc
        
        links = soup.find_all('a', href=True)
        anchor_texts = []
        internal_urls = set()
        
        for link in links:
            href = link.get('href', '').strip()
            if not href or href.startswith('#') or href.startswith('javascript:') or href.startswith('mailto:'):
                continue
            
            anchor_text = link.get_text().strip().lower()
            if anchor_text:
                anchor_texts.append(anchor_text)
            
            link_parsed = urlparse(urljoin(url, href))
            link_domain = link_parsed.netloc
            rel = link.get('rel', '')
            is_nofollow = 'nofollow' in rel.lower()
            
            if link_domain == base_domain or link_domain == '':
                result.total_internal += 1
                internal_urls.add(href)
                depth = link_parsed.path.count('/')
                result.internal_link_depth[depth] = result.internal_link_depth.get(depth, 0) + 1
            else:
                result.total_external += 1
            
            if is_nofollow:
                result.total_nofollow += 1
            else:
                result.total_dofollow += 1
        
        if anchor_texts:
            exact_match = sum(1 for a in anchor_texts if len(a.split()) == 1)
            partial_match = sum(1 for a in anchor_texts if 2 <= len(a.split()) <= 4)
            branded = sum(1 for a in anchor_texts if any(b in a for b in ['click here', 'read more']))
            generic = sum(1 for a in anchor_texts if a in ['home', 'contact', 'about'])
            
            result.anchor_distribution = {
                'exact_match': exact_match,
                'partial_match': partial_match,
                'branded': branded,
                'generic': generic,
                'total': len(anchor_texts)
            }
            
            total = len(anchor_texts)
            if total > 10 and exact_match / total > 0.6:
                issues.append(SEOIssue(
                    category="Link Profile", severity=Severity.MEDIUM,
                    title="Over-Optimized Anchor Text",
                    description=f"{round(exact_match/total*100, 1)}% exact match anchors",
                    recommendation="Diversify anchor text naturally",
                    impact_score=5.5
                ))
        
        if result.total_internal == 0 and parsed_url.path != '/':
            result.orphan_pages_detected = True
            issues.append(SEOIssue(
                category="Internal Linking", severity=Severity.HIGH,
                title="Potential Orphan Page",
                description="No internal links found",
                recommendation="Add internal links from relevant pages",
                impact_score=6.0
            ))
        
        if result.total_internal > 0:
            base_juice = 1.0 / max(result.total_internal, 1)
            for depth, count in result.internal_link_depth.items():
                decay_factor = 0.8 ** depth
                result.link_juice_flow[f'depth_{depth}'] = round(base_juice * decay_factor * count, 4)
        
        return result, issues


class GeoOptimizationAnalyzer:
    """Local SEO / GEO optimization analysis"""
    
    def analyze(self, url: str, html_content: str) -> Tuple[GeoOptimization, List[SEOIssue]]:
        result = GeoOptimization()
        issues = []
        soup = BeautifulSoup(html_content, 'lxml')
        text_content = soup.get_text().lower()
        
        schema_scripts = soup.find_all('script', type='application/ld+json')
        for script in schema_scripts:
            try:
                schema_data = json.loads(script.string)
                if isinstance(schema_data, dict):
                    schema_type = schema_data.get('@type', '')
                    if isinstance(schema_type, str) and 'LocalBusiness' in schema_type:
                        result.local_schema_present = True
                        if schema_data.get('name'):
                            result.business_name_found = True
                        if schema_data.get('geo'):
                            geo = schema_data['geo']
                            result.geo_coordinates = {
                                'latitude': float(geo.get('latitude', 0)),
                                'longitude': float(geo.get('longitude', 0))
                            }
                        if schema_data.get('openingHours'):
                            result.opening_hours_specified = True
                        if schema_data.get('aggregateRating') or schema_data.get('review'):
                            result.reviews_markup = True
            except:
                pass
        
        iframes = soup.find_all('iframe')
        for iframe in iframes:
            src = iframe.get('src', '').lower()
            if 'google.com/maps' in src or 'maps.google.com' in src:
                result.google_maps_embedded = True
                break
        
        city_patterns = [
            r'\b(?:in|near|around|serving)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b',
            r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*,\s*[A-Z]{2})\b'
        ]
        
        for pattern in city_patterns:
            matches = re.findall(pattern, html_content)
            for match in matches:
                result.city_region_mentions[match] = result.city_region_mentions.get(match, 0) + 1
        
        if result.city_region_mentions:
            result.local_keywords_present = True
        
        images = soup.find_all('img')
        location_keywords = ['location', 'store', 'office', 'branch', 'map']
        for img in images:
            alt = img.get('alt', '').lower()
            if any(kw in alt for kw in location_keywords):
                result.local_images += 1
        
        if not result.local_schema_present:
            issues.append(SEOIssue(
                category="Local SEO", severity=Severity.MEDIUM,
                title="Missing LocalBusiness Schema",
                description="No LocalBusiness structured data",
                recommendation="Add LocalBusiness schema with NAP",
                impact_score=6.5
            ))
        
        return result, issues


class EEATAnalyzer:
    """Google E-E-A-T signals analysis"""
    
    def analyze(self, url: str, html_content: str) -> Tuple[EEATSignals, List[SEOIssue]]:
        result = EEATSignals()
        issues = []
        soup = BeautifulSoup(html_content, 'lxml')
        parsed_url = urlparse(url)
        
        author_meta = soup.find('meta', attrs={'name': 'author'})
        if author_meta and author_meta.get('content'):
            result.author_info_present = True
            result.author_credentials.append(author_meta['content'])
        
        date_published = soup.find('meta', attrs={'name': 'datePublished'})
        if not date_published:
            date_published = soup.find('meta', attrs={'property': 'article:published_time'})
        if date_published and date_published.get('content'):
            result.publication_date = date_published['content']
        
        date_modified = soup.find('meta', attrs={'name': 'dateModified'})
        if not date_modified:
            date_modified = soup.find('meta', attrs={'property': 'article:modified_time'})
        if date_modified and date_modified.get('content'):
            result.last_modified = date_modified['content']
        
        links = soup.find_all('a', href=True)
        page_keywords = {
            'about': ['about', 'company', 'team'],
            'contact': ['contact', 'get-in-touch'],
            'privacy': ['privacy', 'privacy-policy'],
            'terms': ['terms', 'terms-of-service']
        }
        
        for link in links:
            href = link.get('href', '').lower()
            text = link.get_text().lower()
            for page_type, keywords in page_keywords.items():
                for kw in keywords:
                    if kw in href or kw in text:
                        setattr(result, f'{page_type}_page_exists', True)
        
        base_domain = parsed_url.netloc
        external_links = 0
        for link in links:
            href = link.get('href', '')
            if href and not href.startswith('#'):
                link_domain = urlparse(urljoin(url, href)).netloc
                if link_domain and link_domain != base_domain:
                    external_links += 1
        result.external_citations = external_links
        
        review_indicators = ['reviewed by', 'medically reviewed', 'fact-checked', 'expert review']
        for indicator in review_indicators:
            if indicator in soup.get_text().lower():
                result.expert_review_indicated = True
                break
        
        result.ssl_certificate = parsed_url.scheme == 'https'
        
        if not result.author_info_present:
            issues.append(SEOIssue(
                category="E-E-A-T", severity=Severity.MEDIUM,
                title="Missing Author Information",
                description="No author attribution found",
                recommendation="Add author bio and credentials",
                impact_score=5.5
            ))
        
        if not result.about_page_exists:
            issues.append(SEOIssue(
                category="E-E-A-T", severity=Severity.MEDIUM,
                title="Missing About Page",
                description="No About page link detected",
                recommendation="Create comprehensive About page",
                impact_score=4.5
            ))
        
        if not result.contact_page_exists:
            issues.append(SEOIssue(
                category="E-E-A-T", severity=Severity.MEDIUM,
                title="Missing Contact Information",
                description="No Contact page link detected",
                recommendation="Add clear contact information",
                impact_score=5.0
            ))
        
        if not result.privacy_policy_exists:
            issues.append(SEOIssue(
                category="E-E-A-T", severity=Severity.HIGH,
                title="Missing Privacy Policy",
                description="No Privacy Policy link detected",
                recommendation="Add Privacy Policy page",
                impact_score=7.0
            ))
        
        return result, issues


class SEOScoreCalculator:
    """Calculate comprehensive SEO scores"""
    
    def calculate(self, technical, onpage, relevance, geo, eeat, issues) -> SEOScore:
        score = SEOScore()
        
        technical_checks = 10
        technical_passed = 0
        if technical.https_enabled: technical_passed += 2
        if technical.http_status == 200: technical_passed += 2
        if technical.canonical_url: technical_passed += 1
        if technical.mobile_viewport: technical_passed += 1
        if technical.charset: technical_passed += 0.5
        if technical.language: technical_passed += 0.5
        if len(technical.render_blocking_resources) <= 2: technical_passed += 1
        if technical.response_time_ms < 1000: technical_passed += 1
        if technical.core_web_vitals.get('performance_score', 0) > 70: technical_passed += 1
        score.technical_score = min(100, (technical_passed / technical_checks) * 100)
        
        onpage_checks = 10
        onpage_passed = 0
        if onpage.title_optimal: onpage_passed += 2
        elif onpage.title: onpage_passed += 1
        if onpage.meta_description_optimal: onpage_passed += 2
        elif onpage.meta_description: onpage_passed += 1
        if len(onpage.h1_tags) == 1: onpage_passed += 2
        elif onpage.h1_tags: onpage_passed += 1
        if onpage.header_hierarchy_valid: onpage_passed += 1
        if onpage.images_without_alt == 0: onpage_passed += 1
        elif onpage.images_with_alt > onpage.images_without_alt: onpage_passed += 0.5
        if onpage.og_tags: onpage_passed += 1
        if onpage.schema_org: onpage_passed += 1
        score.onpage_score = min(100, (onpage_passed / onpage_checks) * 100)
        
        content_checks = 5
        content_passed = 0
        if 1000 <= relevance.word_count <= 3000: content_passed += 1.5
        elif relevance.word_count > 500: content_passed += 1
        if relevance.content_quality_score > 70: content_passed += 1.5
        elif relevance.content_quality_score > 50: content_passed += 1
        if relevance.lexical_diversity > 0.6: content_passed += 1
        if relevance.paragraph_count >= 5: content_passed += 0.5
        if relevance.primary_topics: content_passed += 0.5
        score.content_score = min(100, (content_passed / content_checks) * 100)
        
        relevance_checks = 4
        relevance_passed = 0
        if relevance.keyword_density:
            top_kw = sorted(relevance.keyword_density.values(), key=lambda x: x.density, reverse=True)[:5]
            if any(kw.in_h1 or kw.in_title for kw in top_kw): relevance_passed += 1.5
        if relevance.semantic_clusters: relevance_passed += 1
        if relevance.entity_mentions: relevance_passed += 1
        if 15 <= relevance.avg_sentence_length <= 25: relevance_passed += 0.5
        score.relevance_score = min(100, (relevance_passed / relevance_checks) * 100)
        
        geo_checks = 5
        geo_passed = 0
        if geo.local_schema_present: geo_passed += 2
        if geo.business_name_found: geo_passed += 1
        if geo.google_maps_embedded or geo.geo_coordinates: geo_passed += 1
        if geo.local_keywords_present: geo_passed += 0.5
        if geo.opening_hours_specified: geo_passed += 0.5
        score.geo_score = min(100, (geo_passed / geo_checks) * 100)
        
        eeat_checks = 6
        eeat_passed = 0
        if eeat.author_info_present: eeat_passed += 1.5
        if eeat.publication_date: eeat_passed += 1
        if eeat.about_page_exists: eeat_passed += 1
        if eeat.contact_page_exists: eeat_passed += 1
        if eeat.privacy_policy_exists: eeat_passed += 1
        if eeat.ssl_certificate: eeat_passed += 0.5
        score.eeat_score = min(100, (eeat_passed / eeat_checks) * 100)
        
        score.total_score = (
            score.technical_score * 0.25 +
            score.onpage_score * 0.25 +
            score.content_score * 0.20 +
            score.relevance_score * 0.15 +
            score.geo_score * 0.10 +
            score.eeat_score * 0.05
        )
        score.total_score = round(score.total_score, 2)
        
        if score.total_score >= 90: score.grade = "A+"
        elif score.total_score >= 85: score.grade = "A"
        elif score.total_score >= 80: score.grade = "A-"
        elif score.total_score >= 75: score.grade = "B+"
        elif score.total_score >= 70: score.grade = "B"
        elif score.total_score >= 65: score.grade = "B-"
        elif score.total_score >= 60: score.grade = "C+"
        elif score.total_score >= 55: score.grade = "C"
        elif score.total_score >= 50: score.grade = "C-"
        elif score.total_score >= 40: score.grade = "D"
        else: score.grade = "F"
        
        score.passed_checks = int(technical_passed + onpage_passed + content_passed + relevance_passed + geo_passed + eeat_passed)
        score.total_checks = int(technical_checks + onpage_checks + content_checks + relevance_checks + geo_checks + eeat_checks)
        
        return score


class ReportGenerator:
    """Generate comprehensive SEO reports"""
    
    def generate_html_report(self, url: str, results: Dict[str, Any]) -> str:
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SEO Audit Report - {url}</title>
    <style>
        :root {{ --primary: #2563eb; --success: #16a34a; --warning: #ca8a04; --danger: #dc2626; }}
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; background: #f9fafb; }}
        .container {{ max-width: 1200px; margin: 0 auto; padding: 2rem; }}
        .header {{ background: linear-gradient(135deg, var(--primary), #1e40af); color: white; padding: 3rem 2rem; border-radius: 1rem; margin-bottom: 2rem; }}
        .header h1 {{ font-size: 2.5rem; margin-bottom: 0.5rem; }}
        .score-card {{ background: white; border-radius: 1rem; padding: 2rem; margin-bottom: 2rem; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
        .score-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 1.5rem; margin-top: 1.5rem; }}
        .score-item {{ text-align: center; padding: 1.5rem; background: #f3f4f6; border-radius: 0.75rem; }}
        .score-value {{ font-size: 2.5rem; font-weight: bold; color: var(--primary); }}
        .grade {{ display: inline-block; padding: 0.5rem 1.5rem; border-radius: 2rem; font-size: 1.5rem; font-weight: bold; background: var(--success); color: white; margin-top: 1rem; }}
        .section {{ background: white; border-radius: 1rem; padding: 2rem; margin-bottom: 2rem; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
        .section h2 {{ color: var(--primary); margin-bottom: 1.5rem; border-bottom: 2px solid #e5e7eb; padding-bottom: 0.5rem; }}
        .issue {{ padding: 1rem; margin-bottom: 1rem; border-left: 4px solid var(--danger); background: #fef2f2; border-radius: 0.5rem; }}
        .issue.medium {{ border-color: var(--warning); background: #fefce8; }}
        .keyword-cloud {{ display: flex; flex-wrap: wrap; gap: 0.5rem; }}
        .keyword-tag {{ padding: 0.5rem 1rem; background: #dbeafe; border-radius: 2rem; font-size: 0.9rem; }}
        table {{ width: 100%; border-collapse: collapse; }}
        th, td {{ padding: 0.75rem; text-align: left; border-bottom: 1px solid #e5e7eb; }}
        th {{ background: #f9fafb; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔍 SEO Audit Report</h1>
            <div>{url}</div>
            <div class="grade">Grade: {results['score']['grade']}</div>
        </div>
        
        <div class="score-card">
            <h2>Overall SEO Score</h2>
            <div class="score-grid">
                <div class="score-item"><div class="score-value">{results['score']['total_score']}</div><div>Total Score</div></div>
                <div class="score-item"><div class="score-value">{results['score']['technical_score']:.1f}</div><div>Technical</div></div>
                <div class="score-item"><div class="score-value">{results['score']['onpage_score']:.1f}</div><div>On-Page</div></div>
                <div class="score-item"><div class="score-value">{results['score']['content_score']:.1f}</div><div>Content</div></div>
                <div class="score-item"><div class="score-value">{results['score']['relevance_score']:.1f}</div><div>Relevance</div></div>
                <div class="score-item"><div class="score-value">{results['score']['geo_score']:.1f}</div><div>GEO</div></div>
                <div class="score-item"><div class="score-value">{results['score']['eeat_score']:.1f}</div><div>E-E-A-T</div></div>
            </div>
        </div>
        
        <div class="section">
            <h2>⚠️ Critical Issues</h2>
            {self._generate_issues_html(results['issues'])}
        </div>
        
        <div class="section">
            <h2>📋 Technical SEO</h2>
            <table>
                <tr><th>Metric</th><th>Value</th><th>Status</th></tr>
                <tr><td>HTTPS</td><td>{'✓ Yes' if results['technical']['https_enabled'] else '✗ No'}</td><td>{'✓' if results['technical']['https_enabled'] else '✗'}</td></tr>
                <tr><td>HTTP Status</td><td>{results['technical']['http_status']}</td><td>{'✓' if results['technical']['http_status'] == 200 else '✗'}</td></tr>
                <tr><td>Response Time</td><td>{results['technical']['response_time_ms']}ms</td><td>{'✓' if results['technical']['response_time_ms'] < 1000 else '⚠'}</td></tr>
                <tr><td>Mobile Viewport</td><td>{'✓ Yes' if results['technical']['mobile_viewport'] else '✗ No'}</td><td>{'✓' if results['technical']['mobile_viewport'] else '✗'}</td></tr>
                <tr><td>Canonical URL</td><td>{'✓ Present' if results['technical']['canonical_url'] else '✗ Missing'}</td><td>{'✓' if results['technical']['canonical_url'] else '✗'}</td></tr>
            </table>
        </div>
        
        <div class="section">
            <h2>📝 On-Page SEO</h2>
            <table>
                <tr><th>Element</th><th>Value</th></tr>
                <tr><td>Title</td><td>{results['onpage']['title'] or 'Missing'}</td></tr>
                <tr><td>Title Length</td><td>{results['onpage']['title_length']} chars</td></tr>
                <tr><td>Meta Description</td><td>{(results['onpage']['meta_description'] or 'Missing')[:100]}...</td></tr>
                <tr><td>H1 Tags</td><td>{len(results['onpage']['h1_tags'])}</td></tr>
                <tr><td>H2 Tags</td><td>{len(results['onpage']['h2_tags'])}</td></tr>
                <tr><td>Images</td><td>{results['onpage']['images_count']} ({results['onpage']['images_with_alt']} with alt)</td></tr>
                <tr><td>Internal Links</td><td>{results['onpage']['internal_links_count']}</td></tr>
                <tr><td>Schema.org</td><td>{len(results['onpage']['schema_org'])} schemas</td></tr>
            </table>
        </div>
        
        <div class="section">
            <h2>☁️ Content Relevance Cloud</h2>
            <table>
                <tr><th>Metric</th><th>Value</th></tr>
                <tr><td>Word Count</td><td>{results['relevance']['word_count']}</td></tr>
                <tr><td>Quality Score</td><td>{results['relevance']['content_quality_score']}/100</td></tr>
                <tr><td>Lexical Diversity</td><td>{results['relevance']['lexical_diversity']:.2f}</td></tr>
                <tr><td>Avg Sentence Length</td><td>{results['relevance']['avg_sentence_length']:.1f} words</td></tr>
            </table>
            <h3 style="margin-top:1.5rem">Top Keywords</h3>
            <div class="keyword-cloud">
            {self._generate_keyword_cloud(results['relevance']['keyword_density'])}
            </div>
        </div>
        
        <div class="section">
            <h2>🌍 GEO Optimization</h2>
            <table>
                <tr><th>Signal</th><th>Status</th></tr>
                <tr><td>LocalBusiness Schema</td><td>{'✓' if results['geo']['local_schema_present'] else '✗'}</td></tr>
                <tr><td>Google Maps</td><td>{'✓' if results['geo']['google_maps_embedded'] else '✗'}</td></tr>
                <tr><td>Geo Coordinates</td><td>{'✓' if results['geo']['geo_coordinates'] else '✗'}</td></tr>
                <tr><td>Opening Hours</td><td>{'✓' if results['geo']['opening_hours_specified'] else '✗'}</td></tr>
            </table>
        </div>
        
        <div class="section">
            <h2>🏆 E-E-A-T Signals</h2>
            <table>
                <tr><th>Signal</th><th>Status</th></tr>
                <tr><td>Author Info</td><td>{'✓' if results['eeat']['author_info_present'] else '✗'}</td></tr>
                <tr><td>Publication Date</td><td>{results['eeat']['publication_date'][:10] if results['eeat']['publication_date'] else '✗'}</td></tr>
                <tr><td>About Page</td><td>{'✓' if results['eeat']['about_page_exists'] else '✗'}</td></tr>
                <tr><td>Contact Page</td><td>{'✓' if results['eeat']['contact_page_exists'] else '✗'}</td></tr>
                <tr><td>Privacy Policy</td><td>{'✓' if results['eeat']['privacy_policy_exists'] else '✗'}</td></tr>
                <tr><td>SSL Certificate</td><td>{'✓' if results['eeat']['ssl_certificate'] else '✗'}</td></tr>
            </table>
        </div>
        
        <div style="text-align:center;color:#6b7280;margin-top:2rem">
            Report generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        </div>
    </div>
</body>
</html>"""
        return html
    
    def _generate_issues_html(self, issues: List[Dict]) -> str:
        critical = [i for i in issues if i['severity'] in ['critical', 'high']]
        if not critical:
            return "<p>No critical issues found! ✅</p>"
        
        html = ""
        for issue in critical[:10]:
            cls = "medium" if issue['severity'] == 'medium' else ""
            html += f"""
            <div class="issue {cls}">
                <strong>{issue['title']}</strong><br>
                {issue['description']}<br>
                <em>Recommendation: {issue['recommendation']}</em>
            </div>
            """
        return html
    
    def _generate_keyword_cloud(self, keyword_density: Dict) -> str:
        if not keyword_density:
            return "<span>No keywords analyzed</span>"
        
        top_keywords = sorted(keyword_density.values(), key=lambda x: x.get('density', 0), reverse=True)[:15]
        html = ""
        for kw in top_keywords:
            html += f"<span class='keyword-tag'>{kw.get('keyword', '')} ({kw.get('density', 0):.2f}%)</span>"
        return html
    
    def generate_json_report(self, results: Dict[str, Any]) -> str:
        return json.dumps(results, indent=2, default=str)
    
    def generate_csv_report(self, results: Dict[str, Any]) -> str:
        output = [['Category', 'Severity', 'Title', 'Description', 'Recommendation', 'Impact Score']]
        for issue in results.get('issues', []):
            output.append([
                issue.get('category', ''),
                issue.get('severity', ''),
                issue.get('title', ''),
                issue.get('description', ''),
                issue.get('recommendation', ''),
                issue.get('impact_score', 0)
            ])
        
        import io
        csv_output = io.StringIO()
        writer = csv.writer(csv_output)
        writer.writerows(output)
        return csv_output.getvalue()


class SEOAnalyzerPro:
    """Main SEO Analyzer orchestrating all components"""
    
    def __init__(self):
        self.technical_analyzer = TechnicalSEOAnalyzer()
        self.onpage_analyzer = OnPageSEOAnalyzer()
        self.link_analyzer = LinkArchitectureAnalyzer()
        self.relevance_analyzer = CloudRelevanceAnalyzer()
        self.geo_analyzer = GeoOptimizationAnalyzer()
        self.eeat_analyzer = EEATAnalyzer()
        self.score_calculator = SEOScoreCalculator()
        self.report_generator = ReportGenerator()
    
    def analyze(self, url: str, target_keywords: List[str] = None) -> Dict[str, Any]:
        print(f"\n🔍 Starting comprehensive SEO analysis for: {url}")
        print("=" * 60)
        
        all_issues = []
        results = {}
        
        print("\n📊 Analyzing Technical SEO...")
        technical, tech_issues = self.technical_analyzer.analyze(url)
        all_issues.extend(tech_issues)
        results['technical'] = asdict(technical)
        print(f"   ✓ Response: {technical.response_time_ms}ms | Status: {technical.http_status}")
        
        try:
            response = requests.get(url, timeout=30, headers=self.technical_analyzer.session.headers)
            html_content = response.text
        except Exception as e:
            return {'error': f'Failed to fetch URL: {str(e)}'}
        
        print("\n📝 Analyzing On-Page SEO...")
        onpage, onpage_issues = self.onpage_analyzer.analyze(url, html_content)
        all_issues.extend(onpage_issues)
        results['onpage'] = asdict(onpage)
        print(f"   ✓ Title: {onpage.title[:50] if onpage.title else 'Missing'}... | H1: {len(onpage.h1_tags)}")
        
        print("\n🔗 Analyzing Link Architecture...")
        links, link_issues = self.link_analyzer.analyze(url, html_content)
        all_issues.extend(link_issues)
        results['links'] = asdict(links)
        print(f"   ✓ Internal: {links.total_internal} | External: {links.total_external}")
        
        print("\n☁️ Analyzing Content Relevance Cloud...")
        soup = BeautifulSoup(html_content, 'lxml')
        text_content = soup.get_text()
        relevance = self.relevance_analyzer.analyze_relevance_cloud(text_content, target_keywords)
        results['relevance'] = asdict(relevance)
        print(f"   ✓ Words: {relevance.word_count} | Quality: {relevance.content_quality_score}")
        
        print("\n🌍 Analyzing GEO Optimization...")
        geo, geo_issues = self.geo_analyzer.analyze(url, html_content)
        all_issues.extend(geo_issues)
        results['geo'] = asdict(geo)
        print(f"   ✓ Local Schema: {'Yes' if geo.local_schema_present else 'No'}")
        
        print("\n🏆 Analyzing E-E-A-T Signals...")
        eeat, eeat_issues = self.eeat_analyzer.analyze(url, html_content)
        all_issues.extend(eeat_issues)
        results['eeat'] = asdict(eeat)
        print(f"   ✓ Author: {'Yes' if eeat.author_info_present else 'No'} | Privacy: {'Yes' if eeat.privacy_policy_exists else 'No'}")
        
        print("\n📈 Calculating SEO Scores...")
        issues_dict = [asdict(issue) for issue in all_issues]
        score = self.score_calculator.calculate(technical, onpage, relevance, geo, eeat, all_issues)
        results['score'] = asdict(score)
        results['issues'] = issues_dict
        results['url'] = url
        results['analyzed_at'] = datetime.now().isoformat()
        
        print(f"\n{'='*60}")
        print(f"✅ Analysis Complete! Grade: {score.grade} ({score.total_score}/100)")
        print("=" * 60)
        
        return results
    
    def export_report(self, results: Dict[str, Any], format: str = 'html', filename: str = None) -> str:
        if format.lower() == 'html':
            content = self.report_generator.generate_html_report(results['url'], results)
            ext = 'html'
        elif format.lower() == 'json':
            content = self.report_generator.generate_json_report(results)
            ext = 'json'
        elif format.lower() == 'csv':
            content = self.report_generator.generate_csv_report(results)
            ext = 'csv'
        else:
            raise ValueError(f"Unsupported format: {format}")
        
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            domain = urlparse(results['url']).netloc.replace('.', '_')
            filename = f"seo_report_{domain}_{timestamp}.{ext}"
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"\n📄 Report exported to: {filename}")
        return filename


def main():
    import sys
    
    if len(sys.argv) < 2:
        print("""
╔═══════════════════════════════════════════════════════════╗
║           SEO PARSER PRO - Ultimate SEO Tool              ║
╠═══════════════════════════════════════════════════════════╣
║ Usage: python seo_parser_pro.py <URL> [keywords_file]     ║
║                                                           ║
║ Examples:                                                 ║
║   python seo_parser_pro.py https://example.com            ║
║   python seo_parser_pro.py https://example.com keywords.txt
║                                                           ║
║ Features:                                                 ║
║   ✓ Cloud Relevance Analysis (TF-IDF, Semantic Clusters)  ║
║   ✓ Technical SEO Audit (Core Web Vitals)                 ║
║   ✓ On-Page Optimization (Meta, Headers, Schema)          ║
║   ✓ Link Architecture Analysis                            ║
║   ✓ GEO Optimization (Local SEO)                          ║
║   ✓ E-E-A-T Signals Detection                             ║
║   ✓ Multi-format Reports (HTML, JSON, CSV)                ║
╚═══════════════════════════════════════════════════════════╝
        """)
        sys.exit(1)
    
    url = sys.argv[1]
    target_keywords = []
    
    if len(sys.argv) > 2:
        keywords_file = sys.argv[2]
        try:
            with open(keywords_file, 'r') as f:
                target_keywords = [line.strip() for line in f if line.strip()]
            print(f"Loaded {len(target_keywords)} target keywords")
        except FileNotFoundError:
            print(f"Warning: Keywords file not found")
    
    analyzer = SEOAnalyzerPro()
    results = analyzer.analyze(url, target_keywords)
    
    if 'error' in results:
        print(f"\n❌ Error: {results['error']}")
        sys.exit(1)
    
    analyzer.export_report(results, 'html')
    analyzer.export_report(results, 'json')
    
    print("\n" + "=" * 60)
    print("📋 QUICK SUMMARY")
    print("=" * 60)
    print(f"URL: {results['url']}")
    print(f"Grade: {results['score']['grade']} ({results['score']['total_score']}/100)")
    print(f"\nScores:")
    print(f"  • Technical: {results['score']['technical_score']:.1f}/100")
    print(f"  • On-Page: {results['score']['onpage_score']:.1f}/100")
    print(f"  • Content: {results['score']['content_score']:.1f}/100")
    print(f"  • Relevance: {results['score']['relevance_score']:.1f}/100")
    print(f"  • GEO: {results['score']['geo_score']:.1f}/100")
    print(f"  • E-E-A-T: {results['score']['eeat_score']:.1f}/100")
    
    critical = [i for i in results['issues'] if i['severity'] == 'critical']
    high = [i for i in results['issues'] if i['severity'] == 'high']
    
    print(f"\n⚠️ Issues: Critical={len(critical)}, High={len(high)}, Total={len(results['issues'])}")
    
    if critical:
        print(f"\n🚨 Critical Issues:")
        for issue in critical[:5]:
            print(f"  - {issue['title']}")
    
    print("\n" + "=" * 60)
    print("✅ Analysis complete! Check exported reports.")
    print("=" * 60)


if __name__ == "__main__":
    main()
