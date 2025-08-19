#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
K站工具 - 违规站点检测与举报系统
功能：检测违规网站、批量举报、收录监控、降权分析
作者：软件仓库源
版本：1.0
"""

import requests
import time
import random
import json
import re
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
import threading
from queue import Queue
import sqlite3
from datetime import datetime, timedelta
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import pandas as pd
from fake_useragent import UserAgent
import hashlib
import base64
from concurrent.futures import ThreadPoolExecutor, as_completed
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from config import CONFIG, SECURITY_CONFIG

class KSiteTool:
    def __init__(self):
        # 配置高性能requests会话
        self.session = self._create_optimized_session()
        self.ua = UserAgent()
        self.db_path = 'k_site_data.db'
        self.init_database()
        
        # 线程控制
        self.max_workers = CONFIG['request']['max_workers']
        self.stop_flag = threading.Event()
        
        # 违规关键词库
        self.violation_keywords = [
            '博彩', '赌博', '色情', '黄色', '成人', '裸体', '性爱', '做爱',
            '六合彩', '时时彩', '北京赛车', '澳门赌场', '真人荷官',
            '代孕', '假证', '假币', '枪支', '毒品', '迷药', '催情',
            '发票', '刻章', '办证', '代开', '增值税', '普通发票'
        ]
        
        # 搜索引擎User-Agent
        self.search_engines_ua = {
            'baidu': 'Mozilla/5.0 (compatible; Baiduspider/2.0; +http://www.baidu.com/search/spider.html)',
            'google': 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)',
            'sogou': 'Sogou web spider/4.0(+http://www.sogou.com/docs/help/webmasters.htm#07)',
            '360': 'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; 360Spider)'
        }
    
    def _create_optimized_session(self):
        """创建优化的requests会话"""
        session = requests.Session()
        
        # 配置重试策略
        retry_strategy = Retry(
            total=CONFIG['request']['max_retries'],
            backoff_factor=0.3,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        
        # 配置HTTP适配器
        adapter = HTTPAdapter(
            pool_connections=SECURITY_CONFIG['pool_connections'],
            pool_maxsize=SECURITY_CONFIG['pool_maxsize'],
            max_retries=retry_strategy
        )
        
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        # 设置超时
        session.timeout = (SECURITY_CONFIG['connection_timeout'], SECURITY_CONFIG['read_timeout'])
        
        return session
    
    def set_max_workers(self, workers):
        """设置最大工作线程数（1-100）"""
        self.max_workers = max(1, min(100, workers))
        CONFIG['request']['max_workers'] = self.max_workers
    
    def stop_detection(self):
        """停止检测"""
        self.stop_flag.set()
        
    def init_database(self):
        """初始化数据库"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 创建网站监控表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sites (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                domain TEXT UNIQUE,
                keywords TEXT,
                status TEXT DEFAULT 'active',
                violation_type TEXT,
                first_detected DATETIME,
                last_checked DATETIME,
                baidu_indexed INTEGER DEFAULT 1,
                google_indexed INTEGER DEFAULT 1,
                report_count INTEGER DEFAULT 0
            )
        ''')
        
        # 创建举报记录表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                site_id INTEGER,
                platform TEXT,
                report_time DATETIME,
                report_reason TEXT,
                status TEXT DEFAULT 'pending',
                FOREIGN KEY (site_id) REFERENCES sites (id)
            )
        ''')
        
        # 创建检测日志表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS detection_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                site_id INTEGER,
                check_time DATETIME,
                violation_found BOOLEAN,
                violation_details TEXT,
                page_content_hash TEXT,
                FOREIGN KEY (site_id) REFERENCES sites (id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_site(self, domain, keywords):
        """添加监控网站"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO sites (domain, keywords, first_detected, last_checked)
                VALUES (?, ?, ?, ?)
            ''', (domain, keywords, datetime.now(), datetime.now()))
            conn.commit()
            return cursor.lastrowid
        except sqlite3.IntegrityError:
            return None
        finally:
            conn.close()
    
    def get_random_headers(self, engine=None):
        """获取随机请求头"""
        if engine and engine in self.search_engines_ua:
            user_agent = self.search_engines_ua[engine]
        else:
            user_agent = self.ua.random
            
        return {
            'User-Agent': user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
    
    def check_site_content(self, url, use_search_engine_ua=False):
        """检查网站内容是否违规"""
        if self.stop_flag.is_set():
            return {'url': url, 'status': 'stopped'}
            
        try:
            headers = self.get_random_headers('baidu' if use_search_engine_ua else None)
            
            # 使用配置的超时设置
            timeout = (SECURITY_CONFIG['connection_timeout'], SECURITY_CONFIG['read_timeout'])
            response = self.session.get(url, headers=headers, timeout=timeout, allow_redirects=True)
            
            # 快速检查响应状态
            if response.status_code >= 400:
                return {
                    'url': url,
                    'status_code': response.status_code,
                    'error': f'HTTP {response.status_code}',
                    'status': 'error'
                }
            
            response.encoding = response.apparent_encoding or 'utf-8'
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 检查页面内容
            page_text = soup.get_text().lower()
            title = soup.title.string if soup.title else ''
            meta_desc = ''
            meta_keywords = ''
            
            # 获取meta信息
            for meta in soup.find_all('meta'):
                if meta.get('name') == 'description':
                    meta_desc = meta.get('content', '')
                elif meta.get('name') == 'keywords':
                    meta_keywords = meta.get('content', '')
            
            # 检查违规内容
            violations = []
            for keyword in self.violation_keywords:
                if keyword in page_text or keyword in title or keyword in meta_desc or keyword in meta_keywords:
                    violations.append(keyword)
            
            # 检查隐藏链接和JS跳转
            hidden_links = self.check_hidden_content(soup)
            js_redirects = self.check_js_redirects(soup)
            
            # 检查TDK篡改
            tdk_issues = self.check_tdk_tampering(soup)
            
            return {
                'url': url,
                'status_code': response.status_code,
                'title': title,
                'meta_description': meta_desc,
                'meta_keywords': meta_keywords,
                'violations': violations,
                'hidden_links': hidden_links,
                'js_redirects': js_redirects,
                'tdk_issues': tdk_issues,
                'content_hash': hashlib.md5(response.text.encode()).hexdigest(),
                'final_url': response.url
            }
            
        except Exception as e:
            return {
                'url': url,
                'error': str(e),
                'status': 'error'
            }
    
    def check_hidden_content(self, soup):
        """检查隐藏内容和暗链"""
        hidden_elements = []
        
        # 检查display:none的元素
        for element in soup.find_all(style=re.compile(r'display\s*:\s*none')):
            if element.get_text().strip():
                hidden_elements.append({
                    'type': 'display_none',
                    'content': element.get_text()[:100],
                    'tag': element.name
                })
        
        # 检查visibility:hidden的元素
        for element in soup.find_all(style=re.compile(r'visibility\s*:\s*hidden')):
            if element.get_text().strip():
                hidden_elements.append({
                    'type': 'visibility_hidden',
                    'content': element.get_text()[:100],
                    'tag': element.name
                })
        
        # 检查iframe隐藏内容
        for iframe in soup.find_all('iframe'):
            if iframe.get('style') and ('display:none' in iframe.get('style') or 'visibility:hidden' in iframe.get('style')):
                hidden_elements.append({
                    'type': 'hidden_iframe',
                    'src': iframe.get('src', ''),
                    'tag': 'iframe'
                })
        
        return hidden_elements
    
    def check_js_redirects(self, soup):
        """检查JS跳转和劫持"""
        js_issues = []
        
        # 检查script标签中的跳转代码
        for script in soup.find_all('script'):
            if script.string:
                script_content = script.string.lower()
                
                # 检查常见的跳转模式
                redirect_patterns = [
                    r'window\.location',
                    r'document\.location',
                    r'location\.href',
                    r'location\.replace',
                    r'window\.open'
                ]
                
                for pattern in redirect_patterns:
                    if re.search(pattern, script_content):
                        js_issues.append({
                            'type': 'js_redirect',
                            'pattern': pattern,
                            'content': script.string[:200]
                        })
        
        return js_issues
    
    def check_tdk_tampering(self, soup):
        """检查TDK篡改"""
        issues = []
        
        title = soup.title.string if soup.title else ''
        
        # 检查标题中的违规内容
        for keyword in self.violation_keywords:
            if keyword in title:
                issues.append({
                    'type': 'title_violation',
                    'keyword': keyword,
                    'title': title
                })
        
        # 检查meta描述和关键词
        for meta in soup.find_all('meta'):
            content = meta.get('content', '').lower()
            name = meta.get('name', '').lower()
            
            if name in ['description', 'keywords']:
                for keyword in self.violation_keywords:
                    if keyword in content:
                        issues.append({
                            'type': f'meta_{name}_violation',
                            'keyword': keyword,
                            'content': content[:100]
                        })
        
        return issues
    
    def check_site_indexing(self, domain):
        """检查网站收录状态 - 优化版本"""
        if self.stop_flag.is_set():
            return {'status': 'stopped'}
            
        results = {}
        timeout = (SECURITY_CONFIG['connection_timeout'], SECURITY_CONFIG['read_timeout'])
        
        # 检查百度收录 - 进一步优化版
        try:
            if self.stop_flag.is_set():
                return results
                
            # 添加随机延迟以避免被识别为机器人
            time.sleep(random.uniform(1, 3))
                
            baidu_query = f"site:{domain}"
            # 优先使用移动端接口，降低被拦截的风险
            baidu_url = f"https://m.baidu.com/s?word={baidu_query}"
            
            # 使用移动端浏览器headers
            headers = {
                'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'zh-CN,zh;q=0.8',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive'
            }
            
            response = self.session.get(baidu_url, headers=headers, timeout=timeout)
            # 处理编码问题
            if response.encoding is None or response.encoding == 'ISO-8859-1':
                response.encoding = 'utf-8'
            response_text = response.text
            
            # 如果内容看起来是乱码，尝试不同的解码方式
            if len([c for c in response_text[:100] if ord(c) > 127]) > 50:
                try:
                    response_text = response.content.decode('utf-8', errors='ignore')
                except:
                    try:
                        response_text = response.content.decode('gbk', errors='ignore')
                    except:
                        response_text = response.content.decode('latin-1', errors='ignore')
            
            # 记录调试信息
            results['baidu_debug'] = {
                'url': baidu_url,
                'status_code': response.status_code,
                'content_length': len(response_text)
            }
            
            # 更全面的百度收录判断模式
            baidu_patterns = [
                r'找到相关结果约([\d,]+)个',
                r'百度为您找到相关结果约([\d,]+)个', 
                r'找到相关结果([\d,]+)个',
                r'相关结果约([\d,]+)个',
                r'为您找到相关结果约([\d,]+)个',
                r'共找到([\d,]+)个结果',
                r'搜索结果约([\d,]+)个'
            ]
            
            found_count = False
            for pattern in baidu_patterns:
                match = re.search(pattern, response_text)
                if match:
                    count_str = match.group(1).replace(',', '').replace('，', '')
                    try:
                        count = int(count_str)
                        results['baidu_count'] = count
                        results['baidu_indexed'] = count > 0
                        results['baidu_match_pattern'] = pattern
                        found_count = True
                        break
                    except ValueError:
                        continue
            
            # 如果没有找到数量，进行更详细的内容分析
            if not found_count:
                # 首先检查是否被反爬虫拦截
                if ('验证码' in response_text or 
                    'captcha' in response_text.lower() or
                    '请输入验证码' in response_text or
                    '百度安全验证' in response_text or
                    'security verification' in response_text.lower() or
                    response.status_code == 302):
                    results['baidu_indexed'] = None
                    results['baidu_count'] = 'blocked'
                    results['baidu_reason'] = 'anti_crawler_detected'
                else:
                    # 检查明确的"无结果"指示
                    no_result_indicators = [
                        '抱歉，没有找到与',
                        '很抱歉，没有找到与', 
                        '没有找到相关结果',
                        '没有找到和',
                        '搜索结果为空',
                        '未找到相关网页',
                        '没有找到符合查询条件'
                    ]
                    
                    has_no_results = any(indicator in response_text for indicator in no_result_indicators)
                    
                    if has_no_results:
                        results['baidu_indexed'] = False
                        results['baidu_count'] = 0
                        results['baidu_reason'] = 'no_results_found'
                    else:
                        # 移动端特殊检测：查找结果容器和链接
                        from bs4 import BeautifulSoup
                        try:
                            soup = BeautifulSoup(response_text, 'html.parser')
                            
                            # 查找包含域名的链接
                            domain_links = soup.find_all('a', href=True)
                            found_domain_links = 0
                            for link in domain_links:
                                href = link.get('href', '')
                                text = link.get_text().strip()
                                if (domain in href or domain in text) and len(text) > 10:
                                    found_domain_links += 1
                            
                            # 查找结果容器
                            result_containers = soup.find_all(['div', 'section', 'article'], 
                                                            class_=re.compile(r'result|item|card|content'))
                            
                            if found_domain_links > 0 or len(result_containers) > 10:
                                results['baidu_indexed'] = True
                                results['baidu_count'] = f'约{found_domain_links}+' if found_domain_links > 0 else 'unknown'
                                results['baidu_reason'] = f'mobile_results_found_{found_domain_links}_links_{len(result_containers)}_containers'
                            else:
                                # 简单的文本检查
                                domain_indicators = [
                                    domain,
                                    domain.replace('www.', ''),
                                    f'www.{domain}' if not domain.startswith('www.') else domain[4:]
                                ]
                                
                                has_domain_in_text = any(indicator in response_text for indicator in domain_indicators)
                                
                                if has_domain_in_text:
                                    results['baidu_indexed'] = True
                                    results['baidu_count'] = 'unknown'
                                    results['baidu_reason'] = 'domain_found_in_text'
                                else:
                                    results['baidu_indexed'] = False
                                    results['baidu_count'] = 0
                                    results['baidu_reason'] = 'no_domain_in_results'
                        
                        except Exception as e:
                            # 如果BeautifulSoup解析失败，回退到简单文本检查
                            domain_indicators = [
                                domain,
                                domain.replace('www.', ''),
                                f'www.{domain}' if not domain.startswith('www.') else domain[4:]
                            ]
                            
                            has_domain_in_text = any(indicator in response_text for indicator in domain_indicators)
                            
                            if has_domain_in_text:
                                results['baidu_indexed'] = True
                                results['baidu_count'] = 'unknown'
                                results['baidu_reason'] = 'domain_found_fallback'
                            else:
                                results['baidu_indexed'] = False
                                results['baidu_count'] = 0
                                results['baidu_reason'] = 'no_domain_in_results'
                
        except Exception as e:
            results['baidu_error'] = str(e)
            results['baidu_indexed'] = False
        
        # 检查Google收录 - 改进版
        try:
            if self.stop_flag.is_set():
                return results
                
            # 添加随机延迟以避免被识别为机器人
            time.sleep(random.uniform(1, 3))
                
            google_query = f"site:{domain}"
            google_url = f"https://www.google.com/search?q={google_query}&num=10"
            headers = self.get_random_headers()
            
            response = self.session.get(google_url, headers=headers, timeout=timeout)
            response_text = response.text.lower()
            
            # 更准确的Google收录判断
            no_results_indicators = [
                'did not match any documents',
                'your search - site:',
                'no results found',
                'try different keywords'
            ]
            
            has_results_indicators = [
                'about',
                'results',
                domain.lower()
            ]
            
            # 检查是否明确表示没有结果
            no_results = any(indicator in response_text for indicator in no_results_indicators)
            
            if no_results:
                results['google_indexed'] = False
                results['google_count'] = 0
            else:
                # 尝试提取结果数量
                count_match = re.search(r'about ([\d,]+) results', response_text)
                if count_match:
                    count_str = count_match.group(1).replace(',', '')
                    try:
                        count = int(count_str)
                        results['google_count'] = count
                        results['google_indexed'] = count > 0
                    except ValueError:
                        results['google_indexed'] = True
                        results['google_count'] = 'unknown'
                else:
                    # 检查是否有域名相关内容
                    if any(indicator in response_text for indicator in has_results_indicators):
                        results['google_indexed'] = True
                        results['google_count'] = 'unknown'
                    else:
                        results['google_indexed'] = False
                        results['google_count'] = 0
                
        except Exception as e:
            results['google_error'] = str(e)
            results['google_indexed'] = False
        
        return results
    
    def submit_report_to_baidu(self, url, reason):
        """向百度提交举报"""
        try:
            # 百度举报接口（模拟）
            report_data = {
                'url': url,
                'reason': reason,
                'type': 'violation',
                'timestamp': int(time.time())
            }
            
            # 这里应该是实际的百度举报API
            # 由于API限制，这里只是记录举报信息
            
            return {
                'status': 'submitted',
                'platform': 'baidu',
                'data': report_data
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }
    
    def submit_report_to_12377(self, url, reason):
        """向12377举报中心提交举报"""
        try:
            # 12377举报接口（模拟）
            report_data = {
                'url': url,
                'reason': reason,
                'category': 'illegal_content',
                'timestamp': int(time.time())
            }
            
            return {
                'status': 'submitted',
                'platform': '12377',
                'data': report_data
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }
    
    def batch_check_sites(self, sites_data, callback=None):
        """批量检查网站（多线程并发版本）"""
        results = []
        completed_count = 0
        total_count = len(sites_data)
        
        # 重置停止标志
        self.stop_flag.clear()
        
        def check_single_site(site_info):
            """检查单个网站"""
            domain, keywords = site_info
            
            if self.stop_flag.is_set():
                return None
                
            try:
                # 检查网站内容
                url = f"http://{domain}" if not domain.startswith('http') else domain
                
                # 普通用户访问检查
                normal_check = self.check_site_content(url, use_search_engine_ua=False)
                
                if self.stop_flag.is_set():
                    return None
                
                # 搜索引擎爬虫访问检查
                spider_check = self.check_site_content(url, use_search_engine_ua=True)
                
                if self.stop_flag.is_set():
                    return None
                
                # 检查收录状态
                indexing_status = self.check_site_indexing(domain)
                
                result = {
                    'domain': domain,
                    'keywords': keywords,
                    'normal_check': normal_check,
                    'spider_check': spider_check,
                    'indexing_status': indexing_status,
                    'check_time': datetime.now().isoformat()
                }
                
                # 保存到数据库
                try:
                    site_id = self.add_site(domain, keywords)
                    if site_id:
                        self.save_detection_log(site_id, result)
                except Exception as db_error:
                    result['db_error'] = str(db_error)
                
                return result
                
            except Exception as e:
                return {
                    'domain': domain,
                    'keywords': keywords,
                    'error': str(e),
                    'check_time': datetime.now().isoformat()
                }
        
        # 使用线程池并发执行
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # 提交所有任务
            future_to_site = {executor.submit(check_single_site, site): site for site in sites_data}
            
            # 处理完成的任务
            for future in as_completed(future_to_site):
                if self.stop_flag.is_set():
                    # 取消所有未完成的任务
                    for f in future_to_site:
                        f.cancel()
                    break
                
                try:
                    result = future.result()
                    if result is not None:
                        results.append(result)
                        completed_count += 1
                        
                        # 回调进度更新
                        if callback:
                            callback(completed_count, total_count, result)
                            
                except Exception as e:
                    site = future_to_site[future]
                    error_result = {
                        'domain': site[0],
                        'keywords': site[1],
                        'error': f"Future execution error: {str(e)}",
                        'check_time': datetime.now().isoformat()
                    }
                    results.append(error_result)
                    completed_count += 1
                    
                    if callback:
                        callback(completed_count, total_count, error_result)
        
        return results
    
    def save_detection_log(self, site_id, result):
        """保存检测日志"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        violation_found = bool(result.get('normal_check', {}).get('violations', []))
        violation_details = json.dumps(result, ensure_ascii=False)
        content_hash = result.get('normal_check', {}).get('content_hash', '')
        
        cursor.execute('''
            INSERT INTO detection_logs (site_id, check_time, violation_found, violation_details, page_content_hash)
            VALUES (?, ?, ?, ?, ?)
        ''', (site_id, datetime.now(), violation_found, violation_details, content_hash))
        
        conn.commit()
        conn.close()
    
    def generate_report(self, results):
        """生成检测报告"""
        report = {
            'total_sites': len(results),
            'violation_sites': 0,
            'indexed_sites': 0,
            'hidden_content_sites': 0,
            'js_redirect_sites': 0,
            'details': []
        }
        
        for result in results:
            if 'error' in result:
                continue
                
            normal_check = result.get('normal_check', {})
            violations = normal_check.get('violations', [])
            hidden_links = normal_check.get('hidden_links', [])
            js_redirects = normal_check.get('js_redirects', [])
            indexing = result.get('indexing_status', {})
            
            if violations:
                report['violation_sites'] += 1
            
            if indexing.get('baidu_indexed') or indexing.get('google_indexed'):
                report['indexed_sites'] += 1
            
            if hidden_links:
                report['hidden_content_sites'] += 1
            
            if js_redirects:
                report['js_redirect_sites'] += 1
            
            report['details'].append({
                'domain': result['domain'],
                'violations': violations,
                'hidden_content': len(hidden_links),
                'js_redirects': len(js_redirects),
                'baidu_indexed': indexing.get('baidu_indexed', False),
                'google_indexed': indexing.get('google_indexed', False)
            })
        
        return report

if __name__ == "__main__":
    # 测试代码
    tool = KSiteTool()
    
    # 测试单个网站检查
    test_url = "http://example.com"
    result = tool.check_site_content(test_url)

    print(json.dumps(result, ensure_ascii=False, indent=2))
