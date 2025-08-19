#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
K站工具 GUI界面
提供图形化界面进行违规站点检测和举报
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import json
import pandas as pd
from datetime import datetime
import os
import time
from k_site_tool import KSiteTool

class KSiteGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("K站工具 - 违规站点检测与举报系统 v1.0")
        self.root.geometry("1200x800")
        self.root.resizable(True, True)
        
        # 初始化工具
        self.tool = KSiteTool()
        self.current_results = []
        
        # 创建界面
        self.create_widgets()
        
        # 设置样式
        self.setup_styles()
    
    def setup_styles(self):
        """设置界面样式"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # 配置颜色
        style.configure('Title.TLabel', font=('Arial', 12, 'bold'))
        style.configure('Header.TLabel', font=('Arial', 10, 'bold'))
        style.configure('Success.TLabel', foreground='green')
        style.configure('Error.TLabel', foreground='red')
        style.configure('Warning.TLabel', foreground='orange')
    
    def create_widgets(self):
        """创建界面组件"""
        # 创建主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置网格权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)  # 左侧列
        main_frame.columnconfigure(1, weight=2)  # 右侧列权重更大
        main_frame.rowconfigure(2, weight=1)     # 主内容区域可扩展
        
        # 顶部免责声明
        self.create_top_disclaimer(main_frame)
        
        # 标题
        title_label = ttk.Label(main_frame, text="K站工具 - 违规站点检测与举报系统", style='Title.TLabel')
        title_label.grid(row=1, column=0, columnspan=2, pady=(10, 20))
        
        # 创建左右分栏
        self.create_left_panel(main_frame)
        self.create_right_panel(main_frame)
        
        # 状态栏
        self.create_status_bar(main_frame)
        
        # 底部免责声明
        self.create_bottom_disclaimer(main_frame)
    
    def create_left_panel(self, parent):
        """创建左侧面板"""
        left_frame = ttk.Frame(parent)
        left_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        left_frame.columnconfigure(0, weight=1)
        left_frame.rowconfigure(2, weight=1)  # 让进度区域可扩展
        
        # 输入区域
        self.create_input_section(left_frame)
        
        # 控制按钮区域
        self.create_control_section(left_frame)
        
        # 进度显示区域
        self.create_progress_section(left_frame)
    
    def create_right_panel(self, parent):
        """创建右侧面板"""
        right_frame = ttk.Frame(parent)
        right_frame.grid(row=2, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(10, 0))
        right_frame.columnconfigure(0, weight=1)
        right_frame.rowconfigure(0, weight=1)
        
        # 结果显示区域
        self.create_results_section(right_frame)
    
    def create_top_disclaimer(self, parent):
        """创建顶部免责声明"""
        disclaimer_frame = ttk.Frame(parent, style='Warning.TFrame')
        disclaimer_frame.grid(row=0, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        disclaimer_frame.columnconfigure(0, weight=1)
        
        disclaimer_text = (
            "⚠️ 免责声明：本工具仅供学习研究使用，请遵守相关法律法规。"
            "使用本工具产生的任何后果由用户自行承担。"
        )
        
        disclaimer_label = ttk.Label(
            disclaimer_frame, 
            text=disclaimer_text,
            foreground='#d63031',
            font=('Arial', 9),
            wraplength=800
        )
        disclaimer_label.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=10, pady=5)
        
        # 官网链接
        website_frame = ttk.Frame(disclaimer_frame)
        website_frame.grid(row=1, column=0, sticky=tk.W, padx=10, pady=(0, 5))
        
        ttk.Label(website_frame, text="官网：", font=('Arial', 9)).grid(row=0, column=0, sticky=tk.W)
        
        website_label = ttk.Label(
            website_frame, 
            text="http://srzhxvjtmptuwlal.net/",
            foreground='#0984e3',
            font=('Arial', 9, 'underline'),
            cursor='hand2'
        )
        website_label.grid(row=0, column=1, sticky=tk.W)
        
        # 绑定点击事件
        website_label.bind('<Button-1>', lambda e: self.open_website('http://srzhxvjtmptuwlal.net/'))
    
    def create_bottom_disclaimer(self, parent):
        """创建底部免责声明"""
        disclaimer_frame = ttk.Frame(parent)
        disclaimer_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        disclaimer_frame.columnconfigure(0, weight=1)
        
        # 分隔线
        separator = ttk.Separator(disclaimer_frame, orient='horizontal')
        separator.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # 免责声明内容
        bottom_text = (
            "本软件仅供技术研究和学习使用，严禁用于非法用途。"
            "用户在使用过程中应遵守当地法律法规，"
            "因使用本软件而产生的一切法律责任由用户自行承担。"
            "软件开发者不承担任何直接或间接的法律责任。"
        )
        
        bottom_label = ttk.Label(
            disclaimer_frame,
            text=bottom_text,
            foreground='gray',
            font=('Arial', 8),
            wraplength=1000
        )
        bottom_label.grid(row=1, column=0, sticky=(tk.W, tk.E), padx=10, pady=5)
        
        # 版权和官网信息
        copyright_frame = ttk.Frame(disclaimer_frame)
        copyright_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), padx=10, pady=(5, 0))
        copyright_frame.columnconfigure(1, weight=1)
        
        ttk.Label(
            copyright_frame,
            text="© 2025 K站工具 | 官网：",
            foreground='gray',
            font=('Arial', 8)
        ).grid(row=0, column=0, sticky=tk.W)
        
        website_bottom_label = ttk.Label(
            copyright_frame,
            text="http://srzhxvjtmptuwlal.net/",
            foreground='#0984e3',
            font=('Arial', 8, 'underline'),
            cursor='hand2'
        )
        website_bottom_label.grid(row=0, column=1, sticky=tk.W, padx=(5, 0))
        
        # 绑定点击事件
        website_bottom_label.bind('<Button-1>', lambda e: self.open_website('http://srzhxvjtmptuwlal.net/'))
    
    def open_website(self, url):
        """打开网站链接"""
        import webbrowser
        try:
            webbrowser.open(url)
        except Exception as e:
            messagebox.showwarning("提示", f"无法打开链接：{url}\n错误：{str(e)}")
    
    def create_input_section(self, parent):
        """创建输入区域"""
        input_frame = ttk.LabelFrame(parent, text="输入设置", padding="10")
        input_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        input_frame.columnconfigure(1, weight=1)
        
        # 域名输入
        ttk.Label(input_frame, text="域名列表:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        
        domain_frame = ttk.Frame(input_frame)
        domain_frame.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        domain_frame.columnconfigure(0, weight=1)
        
        self.domain_text = scrolledtext.ScrolledText(domain_frame, height=6, width=50)
        self.domain_text.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        # 域名输入说明
        ttk.Label(input_frame, text="每行一个域名，格式：domain.com 或 关键词,domain.com", 
                 foreground='gray').grid(row=1, column=1, sticky=tk.W, pady=(5, 0))
        
        # 文件导入按钮
        file_frame = ttk.Frame(input_frame)
        file_frame.grid(row=0, column=2, sticky=tk.N, padx=(10, 0))
        
        ttk.Button(file_frame, text="导入Excel", command=self.import_excel).grid(row=0, column=0, pady=(0, 5))
        ttk.Button(file_frame, text="导入TXT", command=self.import_txt).grid(row=1, column=0, pady=(0, 5))
        ttk.Button(file_frame, text="清空", command=self.clear_domains).grid(row=2, column=0)
        
        # 检测选项
        options_frame = ttk.LabelFrame(input_frame, text="检测选项", padding="5")
        options_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))
        
        self.check_content = tk.BooleanVar(value=True)
        self.check_indexing = tk.BooleanVar(value=True)
        self.check_hidden = tk.BooleanVar(value=True)
        self.check_js = tk.BooleanVar(value=True)
        self.auto_report = tk.BooleanVar(value=False)
        
        ttk.Checkbutton(options_frame, text="检测违规内容", variable=self.check_content).grid(row=0, column=0, sticky=tk.W, padx=(0, 20))
        ttk.Checkbutton(options_frame, text="检测收录状态", variable=self.check_indexing).grid(row=0, column=1, sticky=tk.W, padx=(0, 20))
        ttk.Checkbutton(options_frame, text="检测隐藏内容", variable=self.check_hidden).grid(row=0, column=2, sticky=tk.W, padx=(0, 20))
        ttk.Checkbutton(options_frame, text="检测JS劫持", variable=self.check_js).grid(row=1, column=0, sticky=tk.W, padx=(0, 20))
        ttk.Checkbutton(options_frame, text="自动举报违规站点", variable=self.auto_report).grid(row=1, column=1, sticky=tk.W, padx=(0, 20))
        
        # 线程数设置
        thread_frame = ttk.Frame(options_frame)
        thread_frame.grid(row=1, column=2, sticky=tk.W, padx=(0, 20))
        
        ttk.Label(thread_frame, text="并发线程:").grid(row=0, column=0, sticky=tk.W)
        self.thread_count = tk.IntVar(value=20)
        thread_spinbox = ttk.Spinbox(thread_frame, from_=1, to=100, width=8, textvariable=self.thread_count)
        thread_spinbox.grid(row=0, column=1, sticky=tk.W, padx=(5, 0))
        
        # 线程数说明
        ttk.Label(options_frame, text="线程数范围: 1-100 (推荐: 10-50)", 
                 foreground='gray', font=('TkDefaultFont', 8)).grid(row=2, column=0, columnspan=3, sticky=tk.W, pady=(5, 0))
    
    def create_control_section(self, parent):
        """创建控制按钮区域"""
        control_frame = ttk.Frame(parent)
        control_frame.grid(row=1, column=0, pady=(0, 10))
        
        self.start_button = ttk.Button(control_frame, text="开始检测", command=self.start_detection)
        self.start_button.grid(row=0, column=0, padx=(0, 10))
        
        self.stop_button = ttk.Button(control_frame, text="停止检测", command=self.stop_detection, state='disabled')
        self.stop_button.grid(row=0, column=1, padx=(0, 10))
        
        ttk.Button(control_frame, text="导出结果", command=self.export_results).grid(row=0, column=2, padx=(0, 10))
        ttk.Button(control_frame, text="批量举报", command=self.batch_report).grid(row=0, column=3, padx=(0, 10))
        ttk.Button(control_frame, text="查看历史", command=self.view_history).grid(row=0, column=4, padx=(0, 10))
    
    def create_progress_section(self, parent):
        """创建进度显示区域"""
        progress_frame = ttk.LabelFrame(parent, text="检测进度", padding="10")
        progress_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        progress_frame.columnconfigure(0, weight=1)
        
        self.progress_var = tk.StringVar(value="就绪")
        self.progress_label = ttk.Label(progress_frame, textvariable=self.progress_var)
        self.progress_label.grid(row=0, column=0, sticky=tk.W)
        
        self.progress_bar = ttk.Progressbar(progress_frame, mode='determinate')
        self.progress_bar.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(5, 0))
    
    def create_results_section(self, parent):
        """创建结果显示区域"""
        results_frame = ttk.LabelFrame(parent, text="检测结果", padding="10")
        results_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(0, weight=1)
        
        # 创建Treeview
        columns = ('域名', '状态', '违规类型', '收录状态', '隐藏内容', 'JS劫持', '检测时间')
        self.results_tree = ttk.Treeview(results_frame, columns=columns, show='headings', height=15)
        
        # 设置列标题
        for col in columns:
            self.results_tree.heading(col, text=col)
            self.results_tree.column(col, width=120)
        
        # 添加滚动条
        scrollbar_y = ttk.Scrollbar(results_frame, orient=tk.VERTICAL, command=self.results_tree.yview)
        scrollbar_x = ttk.Scrollbar(results_frame, orient=tk.HORIZONTAL, command=self.results_tree.xview)
        self.results_tree.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)
        
        self.results_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar_y.grid(row=0, column=1, sticky=(tk.N, tk.S))
        scrollbar_x.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        # 绑定双击事件
        self.results_tree.bind('<Double-1>', self.show_detail)
    
    def create_status_bar(self, parent):
        """创建状态栏"""
        status_frame = ttk.Frame(parent)
        status_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        status_frame.columnconfigure(1, weight=1)
        
        self.status_var = tk.StringVar(value="就绪")
        ttk.Label(status_frame, textvariable=self.status_var).grid(row=0, column=0, sticky=tk.W)
        
        # 统计信息
        self.stats_var = tk.StringVar(value="")
        ttk.Label(status_frame, textvariable=self.stats_var).grid(row=0, column=2, sticky=tk.E)
    
    def import_excel(self):
        """导入Excel文件"""
        file_path = filedialog.askopenfilename(
            title="选择Excel文件",
            filetypes=[("Excel files", "*.xlsx *.xls"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                df = pd.read_excel(file_path)
                
                # 假设第一列是域名，第二列是关键词（可选）
                domains = []
                for index, row in df.iterrows():
                    domain = str(row.iloc[0]).strip()
                    keywords = str(row.iloc[1]).strip() if len(row) > 1 else ""
                    
                    if domain and domain != 'nan':
                        if keywords and keywords != 'nan':
                            domains.append(f"{keywords},{domain}")
                        else:
                            domains.append(domain)
                
                self.domain_text.delete(1.0, tk.END)
                self.domain_text.insert(1.0, "\n".join(domains))
                
                self.status_var.set(f"已导入 {len(domains)} 个域名")
                
            except Exception as e:
                messagebox.showerror("错误", f"导入Excel文件失败：{str(e)}")
    
    def import_txt(self):
        """导入TXT文件"""
        file_path = filedialog.askopenfilename(
            title="选择TXT文件",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                self.domain_text.delete(1.0, tk.END)
                self.domain_text.insert(1.0, content)
                
                lines = [line.strip() for line in content.split('\n') if line.strip()]
                self.status_var.set(f"已导入 {len(lines)} 行数据")
                
            except Exception as e:
                messagebox.showerror("错误", f"导入TXT文件失败：{str(e)}")
    
    def clear_domains(self):
        """清空域名列表"""
        self.domain_text.delete(1.0, tk.END)
        self.status_var.set("已清空域名列表")
    
    def parse_domains(self):
        """解析域名列表"""
        content = self.domain_text.get(1.0, tk.END).strip()
        if not content:
            return []
        
        domains = []
        for line in content.split('\n'):
            line = line.strip()
            if not line:
                continue
            
            if ',' in line:
                parts = line.split(',', 1)
                keywords = parts[0].strip()
                domain = parts[1].strip()
            else:
                keywords = ""
                domain = line.strip()
            
            domains.append((domain, keywords))
        
        return domains
    
    def start_detection(self):
        """开始检测"""
        domains = self.parse_domains()
        if not domains:
            messagebox.showwarning("警告", "请输入要检测的域名")
            return
        
        # 设置线程数
        thread_count = self.thread_count.get()
        if thread_count < 1 or thread_count > 100:
            messagebox.showwarning("警告", "线程数必须在1-100之间")
            return
        
        self.tool.set_max_workers(thread_count)
        
        # 清空之前的结果
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)
        
        self.current_results = []
        
        # 更新界面状态
        self.start_button.config(state='disabled')
        self.stop_button.config(state='normal')
        self.progress_bar['maximum'] = len(domains)
        self.progress_bar['value'] = 0
        
        # 更新状态栏
        self.status_var.set(f"开始检测 {len(domains)} 个域名，使用 {thread_count} 个线程...")
        
        # 启动检测线程
        self.detection_thread = threading.Thread(
            target=self.run_detection,
            args=(domains,),
            daemon=True
        )
        self.detection_thread.start()
    
    def run_detection(self, domains):
        """运行检测（在后台线程中）"""
        try:
            def progress_callback(current, total, result):
                # 更新进度
                self.root.after(0, lambda: self.update_progress(current, total, result))
            
            # 执行批量检测
            results = self.tool.batch_check_sites(domains, progress_callback)
            
            # 检测完成
            self.root.after(0, lambda: self.detection_completed(results))
            
        except Exception as e:
            self.root.after(0, lambda: self.detection_error(str(e)))
    
    def update_progress(self, current, total, result):
        """更新进度显示"""
        self.progress_bar['value'] = current
        self.progress_var.set(f"正在检测 {current}/{total}: {result.get('domain', '')}")
        
        # 添加结果到表格
        if 'error' not in result:
            self.add_result_to_tree(result)
            self.current_results.append(result)
    
    def add_result_to_tree(self, result):
        """添加结果到表格"""
        domain = result.get('domain', '')
        
        normal_check = result.get('normal_check', {})
        violations = normal_check.get('violations', [])
        hidden_links = normal_check.get('hidden_links', [])
        js_redirects = normal_check.get('js_redirects', [])
        
        indexing = result.get('indexing_status', {})
        baidu_indexed = indexing.get('baidu_indexed', False)
        google_indexed = indexing.get('google_indexed', False)
        
        # 确定状态
        if 'error' in normal_check:
            status = "无法访问"
            status_color = 'red'
        elif violations:
            status = "发现违规"
            status_color = 'red'
        else:
            status = "站点正常"
            status_color = 'green'
        
        # 违规类型
        violation_types = ', '.join(violations[:3]) if violations else "无"
        
        # 收录状态 - 显示详细信息（支持调试信息）
        baidu_count = indexing.get('baidu_count', 0)
        google_count = indexing.get('google_count', 0)
        baidu_debug = indexing.get('baidu_debug', {})
        
        indexing_status = []
        
        # 百度收录状态 - 增强显示
        if baidu_indexed is True:
            if isinstance(baidu_count, int) and baidu_count > 0:
                indexing_status.append(f"百度({baidu_count})")
            elif baidu_count == 'unknown':
                baidu_reason = indexing.get('baidu_reason', '')
                if baidu_reason == 'domain_found_in_results':
                    indexing_status.append("百度(数量未知)")
                else:
                    indexing_status.append("百度")
            else:
                indexing_status.append("百度")
        elif baidu_indexed is False:
            baidu_reason = indexing.get('baidu_reason', '')
            if baidu_reason == 'no_results_found':
                indexing_status.append("百度未收录(无结果)")
            elif baidu_reason == 'no_domain_in_results':
                indexing_status.append("百度未收录(域名不在结果中)")
            else:
                indexing_status.append("百度未收录")
        elif baidu_indexed is None:
            baidu_reason = indexing.get('baidu_reason', '')
            if baidu_reason == 'anti_crawler_detected':
                indexing_status.append("百度查询被拦截")
            else:
                indexing_status.append("百度查询失败")
        
        # 谷歌收录状态
        if google_indexed:
            if isinstance(google_count, int) and google_count > 0:
                indexing_status.append(f"谷歌({google_count})")
            else:
                indexing_status.append("谷歌")
        elif google_indexed is False:
            google_reason = indexing.get('google_reason', '')
            if google_reason:
                indexing_status.append(f"谷歌未收录({google_reason})")
            else:
                indexing_status.append("谷歌未收录")
        elif 'google_error' in indexing:
            indexing_status.append("谷歌查询失败")
        
        # 如果都没有收录，显示具体原因
        if not indexing_status:
            indexing_text = "未收录"
        else:
            indexing_text = ', '.join(indexing_status)
            
        # 添加调试信息提示
        if baidu_debug and baidu_debug.get('status_code'):
            indexing_text += f" [状态:{baidu_debug['status_code']}]"
        
        # 隐藏内容
        hidden_text = f"{len(hidden_links)}个" if hidden_links else "无"
        
        # JS劫持
        js_text = f"{len(js_redirects)}个" if js_redirects else "无"
        
        # 检测时间
        check_time = result.get('check_time', '')[:19] if result.get('check_time') else ''
        
        # 插入到表格
        item = self.results_tree.insert('', 'end', values=(
            domain, status, violation_types, indexing_text, 
            hidden_text, js_text, check_time
        ))
        
        # 设置颜色
        if status == "违规":
            self.results_tree.set(item, '状态', status)
    
    def detection_completed(self, results):
        """检测完成"""
        self.start_button.config(state='normal')
        self.stop_button.config(state='disabled')
        
        # 生成统计报告
        report = self.tool.generate_report(results)
        
        self.progress_var.set("检测完成")
        self.status_var.set(f"检测完成，共 {report['total_sites']} 个站点")
        
        stats_text = (f"违规: {report['violation_sites']} | "
                     f"收录: {report['indexed_sites']} | "
                     f"隐藏内容: {report['hidden_content_sites']} | "
                     f"JS劫持: {report['js_redirect_sites']}")
        self.stats_var.set(stats_text)
        
        # 如果启用自动举报
        if self.auto_report.get():
            self.auto_report_violations(results)
    
    def detection_error(self, error_msg):
        """检测出错"""
        self.start_button.config(state='normal')
        self.stop_button.config(state='disabled')
        self.progress_var.set("检测出错")
        messagebox.showerror("错误", f"检测过程中出现错误：{error_msg}")
    
    def stop_detection(self):
        """停止检测"""
        # 设置停止标志
        self.tool.stop_detection()
        
        # 更新界面状态
        self.start_button.config(state='normal')
        self.stop_button.config(state='disabled')
        self.progress_var.set("检测已停止")
        self.status_var.set("检测已被用户停止")
        
        # 等待检测线程结束（非阻塞）
        if hasattr(self, 'detection_thread') and self.detection_thread.is_alive():
            # 在后台等待线程结束
            def wait_for_thread():
                if self.detection_thread.is_alive():
                    self.root.after(100, wait_for_thread)
                else:
                    self.root.after(0, lambda: self.status_var.set("检测完全停止"))
            wait_for_thread()
    
    def show_detail(self, event):
        """显示详细信息"""
        selection = self.results_tree.selection()
        if not selection:
            return
        
        item = selection[0]
        domain = self.results_tree.item(item)['values'][0]
        
        # 查找对应的结果数据
        result_data = None
        for result in self.current_results:
            if result.get('domain') == domain:
                result_data = result
                break
        
        if result_data:
            self.show_detail_window(result_data)
    
    def show_detail_window(self, result_data):
        """显示详细信息窗口"""
        detail_window = tk.Toplevel(self.root)
        detail_window.title(f"详细信息 - {result_data.get('domain', '')}")
        detail_window.geometry("800x600")
        
        # 创建文本框显示详细信息
        text_widget = scrolledtext.ScrolledText(detail_window, wrap=tk.WORD, font=('Consolas', 10))
        text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 格式化显示结果
        domain = result_data.get('domain', '')
        normal_check = result_data.get('normal_check', {})
        indexing_status = result_data.get('indexing_status', {})
        
        detail_text = f"""域名检测详细报告
{'='*50}

【基本信息】
域名: {domain}
检测时间: {result_data.get('check_time', '')}

【网站内容检测】
状态码: {normal_check.get('status_code', 'N/A')}
标题: {normal_check.get('title', 'N/A')}
描述: {normal_check.get('description', 'N/A')[:100]}{'...' if len(normal_check.get('description', '')) > 100 else ''}

【违规内容检测】
违规关键词: {', '.join(normal_check.get('violations', [])) if normal_check.get('violations') else '无'}
TDK篡改: {len(normal_check.get('tdk_issues', []))}个问题

【收录状态检测】
百度收录: {'是' if indexing_status.get('baidu_indexed') else '否'}
百度收录数量: {indexing_status.get('baidu_count', 'N/A')}
百度收录原因: {indexing_status.get('baidu_reason', '无')}
百度查询错误: {indexing_status.get('baidu_error', '无')}
百度调试信息: {indexing_status.get('baidu_debug', {})}

谷歌收录: {'是' if indexing_status.get('google_indexed') else '否'}
谷歌收录数量: {indexing_status.get('google_count', 'N/A')}
谷歌查询错误: {indexing_status.get('google_error', '无')}

【隐藏内容检测】
隐藏链接数量: {len(normal_check.get('hidden_links', []))}
隐藏链接详情:
"""
        
        # 添加隐藏链接详情
        for i, link in enumerate(normal_check.get('hidden_links', [])[:5], 1):
            detail_text += f"  {i}. {link.get('url', 'N/A')} ({link.get('reason', 'N/A')})\n"
        
        if len(normal_check.get('hidden_links', [])) > 5:
            detail_text += f"  ... 还有 {len(normal_check.get('hidden_links', [])) - 5} 个隐藏链接\n"
        
        detail_text += f"""
【JS劫持检测】
JS劫持数量: {len(normal_check.get('js_redirects', []))}
JS劫持详情:
"""
        
        # 添加JS劫持详情
        for i, js in enumerate(normal_check.get('js_redirects', [])[:3], 1):
            detail_text += f"  {i}. 类型: {js.get('type', 'N/A')} | 模式: {js.get('pattern', 'N/A')}\n"
            detail_text += f"     内容: {js.get('content', 'N/A')[:100]}{'...' if len(js.get('content', '')) > 100 else ''}\n"
        
        if len(normal_check.get('js_redirects', [])) > 3:
            detail_text += f"  ... 还有 {len(normal_check.get('js_redirects', [])) - 3} 个JS劫持\n"
        
        # 如果有错误信息，显示错误详情
        if 'error' in normal_check:
            detail_text += f"""
【错误信息】
{normal_check['error']}
"""
        
        detail_text += f"""
{'='*50}
原始数据 (JSON格式):
{json.dumps(result_data, ensure_ascii=False, indent=2)}
"""
        
        text_widget.insert(1.0, detail_text)
        text_widget.config(state='disabled')
    
    def export_results(self):
        """导出结果"""
        if not self.current_results:
            messagebox.showwarning("警告", "没有可导出的结果")
            return
        
        file_path = filedialog.asksaveasfilename(
            title="保存结果",
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx"), ("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                if file_path.endswith('.xlsx'):
                    # 导出为Excel
                    export_data = []
                    for result in self.current_results:
                        if 'error' in result:
                            continue
                        
                        normal_check = result.get('normal_check', {})
                        violations = normal_check.get('violations', [])
                        indexing = result.get('indexing_status', {})
                        
                        export_data.append({
                            '域名': result.get('domain', ''),
                            '关键词': result.get('keywords', ''),
                            '违规内容': ', '.join(violations),
                            '百度收录': '是' if indexing.get('baidu_indexed') else '否',
                            '谷歌收录': '是' if indexing.get('google_indexed') else '否',
                            '隐藏内容数量': len(normal_check.get('hidden_links', [])),
                            'JS劫持数量': len(normal_check.get('js_redirects', [])),
                            '检测时间': result.get('check_time', '')
                        })
                    
                    df = pd.DataFrame(export_data)
                    df.to_excel(file_path, index=False)
                    
                else:
                    # 导出为JSON
                    with open(file_path, 'w', encoding='utf-8') as f:
                        json.dump(self.current_results, f, ensure_ascii=False, indent=2)
                
                messagebox.showinfo("成功", f"结果已导出到：{file_path}")
                
            except Exception as e:
                messagebox.showerror("错误", f"导出失败：{str(e)}")
    
    def batch_report(self):
        """批量举报"""
        if not self.current_results:
            messagebox.showwarning("警告", "没有可举报的结果")
            return
        
        # 筛选出违规站点
        violation_sites = []
        for result in self.current_results:
            normal_check = result.get('normal_check', {})
            violations = normal_check.get('violations', [])
            if violations:
                violation_sites.append(result)
        
        if not violation_sites:
            messagebox.showinfo("信息", "没有发现违规站点")
            return
        
        # 确认举报
        if messagebox.askyesno("确认", f"发现 {len(violation_sites)} 个违规站点，是否进行批量举报？"):
            self.perform_batch_report(violation_sites)
    
    def perform_batch_report(self, violation_sites):
        """执行批量举报"""
        report_window = tk.Toplevel(self.root)
        report_window.title("批量举报进度")
        report_window.geometry("500x300")
        
        # 进度显示
        progress_label = ttk.Label(report_window, text="正在举报...")
        progress_label.pack(pady=10)
        
        progress_bar = ttk.Progressbar(report_window, mode='determinate', maximum=len(violation_sites))
        progress_bar.pack(fill=tk.X, padx=20, pady=10)
        
        result_text = scrolledtext.ScrolledText(report_window, height=10)
        result_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        def report_thread():
            for i, site in enumerate(violation_sites):
                domain = site.get('domain', '')
                violations = site.get('normal_check', {}).get('violations', [])
                
                # 向百度举报
                baidu_result = self.tool.submit_report_to_baidu(
                    f"http://{domain}", 
                    f"违规内容：{', '.join(violations)}"
                )
                
                # 向12377举报
                report_12377 = self.tool.submit_report_to_12377(
                    f"http://{domain}", 
                    f"违规内容：{', '.join(violations)}"
                )
                
                # 更新进度
                report_window.after(0, lambda i=i, d=domain: (
                    progress_bar.config(value=i+1),
                    progress_label.config(text=f"已举报 {i+1}/{len(violation_sites)}: {d}"),
                    result_text.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] 已举报 {d}\n"),
                    result_text.see(tk.END)
                ))
                
                time.sleep(1)  # 避免请求过快
            
            # 完成
            report_window.after(0, lambda: (
                progress_label.config(text="举报完成"),
                result_text.insert(tk.END, f"\n批量举报完成，共举报 {len(violation_sites)} 个站点\n")
            ))
        
        threading.Thread(target=report_thread, daemon=True).start()
    
    def auto_report_violations(self, results):
        """自动举报违规站点"""
        violation_sites = []
        for result in results:
            normal_check = result.get('normal_check', {})
            violations = normal_check.get('violations', [])
            if violations:
                violation_sites.append(result)
        
        if violation_sites:
            self.perform_batch_report(violation_sites)
    
    def view_history(self):
        """查看历史记录"""
        history_window = tk.Toplevel(self.root)
        history_window.title("历史记录")
        history_window.geometry("1200x700")
        history_window.resizable(True, True)
        
        # 创建主框架
        main_frame = ttk.Frame(history_window, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置网格权重
        history_window.columnconfigure(0, weight=1)
        history_window.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # 标题
        title_label = ttk.Label(main_frame, text="检测历史记录", font=('Arial', 14, 'bold'))
        title_label.grid(row=0, column=0, pady=(0, 10))
        
        # 创建选项卡
        notebook = ttk.Notebook(main_frame)
        notebook.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 站点历史选项卡
        sites_frame = ttk.Frame(notebook)
        notebook.add(sites_frame, text="站点记录")
        self.create_sites_history_tab(sites_frame)
        
        # 检测日志选项卡
        logs_frame = ttk.Frame(notebook)
        notebook.add(logs_frame, text="检测日志")
        self.create_logs_history_tab(logs_frame)
        
        # 举报记录选项卡
        reports_frame = ttk.Frame(notebook)
        notebook.add(reports_frame, text="举报记录")
        self.create_reports_history_tab(reports_frame)
        
        # 按钮框架
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, pady=(10, 0))
        
        ttk.Button(button_frame, text="刷新", command=lambda: self.refresh_history(notebook)).grid(row=0, column=0, padx=(0, 10))
        ttk.Button(button_frame, text="导出历史", command=self.export_history).grid(row=0, column=1, padx=(0, 10))
        ttk.Button(button_frame, text="清空历史", command=self.clear_history).grid(row=0, column=2, padx=(0, 10))
        ttk.Button(button_frame, text="关闭", command=history_window.destroy).grid(row=0, column=3)
    
    def create_sites_history_tab(self, parent):
        """创建站点历史选项卡"""
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(0, weight=1)
        
        # 创建Treeview
        columns = ('ID', '域名', '关键词', '状态', '违规类型', '首次检测', '最后检测', '百度收录', '谷歌收录', '举报次数')
        self.sites_tree = ttk.Treeview(parent, columns=columns, show='headings', height=20)
        
        # 设置列标题和宽度
        column_widths = {'ID': 50, '域名': 150, '关键词': 100, '状态': 80, '违规类型': 120, 
                        '首次检测': 130, '最后检测': 130, '百度收录': 80, '谷歌收录': 80, '举报次数': 80}
        
        for col in columns:
            self.sites_tree.heading(col, text=col)
            self.sites_tree.column(col, width=column_widths.get(col, 100))
        
        # 添加滚动条
        sites_scrollbar_y = ttk.Scrollbar(parent, orient=tk.VERTICAL, command=self.sites_tree.yview)
        sites_scrollbar_x = ttk.Scrollbar(parent, orient=tk.HORIZONTAL, command=self.sites_tree.xview)
        self.sites_tree.configure(yscrollcommand=sites_scrollbar_y.set, xscrollcommand=sites_scrollbar_x.set)
        
        self.sites_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        sites_scrollbar_y.grid(row=0, column=1, sticky=(tk.N, tk.S))
        sites_scrollbar_x.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        # 加载站点数据
        self.load_sites_history()
    
    def create_logs_history_tab(self, parent):
        """创建检测日志选项卡"""
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(0, weight=1)
        
        # 创建Treeview
        columns = ('ID', '域名', '检测时间', '发现违规', '违规详情')
        self.logs_tree = ttk.Treeview(parent, columns=columns, show='headings', height=20)
        
        # 设置列标题和宽度
        column_widths = {'ID': 50, '域名': 150, '检测时间': 130, '发现违规': 80, '违规详情': 400}
        
        for col in columns:
            self.logs_tree.heading(col, text=col)
            self.logs_tree.column(col, width=column_widths.get(col, 100))
        
        # 添加滚动条
        logs_scrollbar_y = ttk.Scrollbar(parent, orient=tk.VERTICAL, command=self.logs_tree.yview)
        logs_scrollbar_x = ttk.Scrollbar(parent, orient=tk.HORIZONTAL, command=self.logs_tree.xview)
        self.logs_tree.configure(yscrollcommand=logs_scrollbar_y.set, xscrollcommand=logs_scrollbar_x.set)
        
        self.logs_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        logs_scrollbar_y.grid(row=0, column=1, sticky=(tk.N, tk.S))
        logs_scrollbar_x.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        # 绑定双击事件查看详情
        self.logs_tree.bind('<Double-1>', self.show_log_detail)
        
        # 加载日志数据
        self.load_logs_history()
    
    def create_reports_history_tab(self, parent):
        """创建举报记录选项卡"""
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(0, weight=1)
        
        # 创建Treeview
        columns = ('ID', '域名', '平台', '举报时间', '举报原因', '状态')
        self.reports_tree = ttk.Treeview(parent, columns=columns, show='headings', height=20)
        
        # 设置列标题和宽度
        column_widths = {'ID': 50, '域名': 150, '平台': 100, '举报时间': 130, '举报原因': 200, '状态': 80}
        
        for col in columns:
            self.reports_tree.heading(col, text=col)
            self.reports_tree.column(col, width=column_widths.get(col, 100))
        
        # 添加滚动条
        reports_scrollbar_y = ttk.Scrollbar(parent, orient=tk.VERTICAL, command=self.reports_tree.yview)
        reports_scrollbar_x = ttk.Scrollbar(parent, orient=tk.HORIZONTAL, command=self.reports_tree.xview)
        self.reports_tree.configure(yscrollcommand=reports_scrollbar_y.set, xscrollcommand=reports_scrollbar_x.set)
        
        self.reports_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        reports_scrollbar_y.grid(row=0, column=1, sticky=(tk.N, tk.S))
        reports_scrollbar_x.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        # 加载举报数据
        self.load_reports_history()
    
    def load_sites_history(self):
        """加载站点历史数据"""
        try:
            import sqlite3
            conn = sqlite3.connect('k_site_data.db')
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, domain, keywords, status, violation_type, 
                       first_detected, last_checked, baidu_indexed, 
                       google_indexed, report_count
                FROM sites
                ORDER BY last_checked DESC
            ''')
            
            # 清空现有数据
            for item in self.sites_tree.get_children():
                self.sites_tree.delete(item)
            
            # 添加数据
            for row in cursor.fetchall():
                # 格式化日期
                first_detected = row[5] if row[5] else "未知"
                last_checked = row[6] if row[6] else "未知"
                
                # 格式化收录状态
                baidu_status = "是" if row[7] else "否"
                google_status = "是" if row[8] else "否"
                
                self.sites_tree.insert('', 'end', values=(
                    row[0], row[1], row[2] or "", row[3], row[4] or "无",
                    first_detected, last_checked, baidu_status, google_status, row[9]
                ))
            
            conn.close()
            
        except Exception as e:
            messagebox.showerror("错误", f"加载站点历史失败：{str(e)}")
    
    def load_logs_history(self):
        """加载检测日志数据"""
        try:
            import sqlite3
            conn = sqlite3.connect('k_site_data.db')
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT dl.id, s.domain, dl.check_time, dl.violation_found, dl.violation_details
                FROM detection_logs dl
                JOIN sites s ON dl.site_id = s.id
                ORDER BY dl.check_time DESC
                LIMIT 1000
            ''')
            
            # 清空现有数据
            for item in self.logs_tree.get_children():
                self.logs_tree.delete(item)
            
            # 添加数据
            for row in cursor.fetchall():
                violation_found = "是" if row[3] else "否"
                
                # 简化违规详情显示
                details = row[4] if row[4] else ""
                if len(details) > 100:
                    details = details[:100] + "..."
                
                self.logs_tree.insert('', 'end', values=(
                    row[0], row[1], row[2], violation_found, details
                ))
            
            conn.close()
            
        except Exception as e:
            messagebox.showerror("错误", f"加载检测日志失败：{str(e)}")
    
    def load_reports_history(self):
        """加载举报记录数据"""
        try:
            import sqlite3
            conn = sqlite3.connect('k_site_data.db')
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT r.id, s.domain, r.platform, r.report_time, r.report_reason, r.status
                FROM reports r
                JOIN sites s ON r.site_id = s.id
                ORDER BY r.report_time DESC
            ''')
            
            # 清空现有数据
            for item in self.reports_tree.get_children():
                self.reports_tree.delete(item)
            
            # 添加数据
            for row in cursor.fetchall():
                self.reports_tree.insert('', 'end', values=row)
            
            conn.close()
            
        except Exception as e:
            messagebox.showerror("错误", f"加载举报记录失败：{str(e)}")
    
    def show_log_detail(self, event):
        """显示日志详情"""
        selection = self.logs_tree.selection()
        if not selection:
            return
        
        item = self.logs_tree.item(selection[0])
        log_id = item['values'][0]
        
        try:
            import sqlite3
            conn = sqlite3.connect('k_site_data.db')
            cursor = conn.cursor()
            
            cursor.execute('SELECT violation_details FROM detection_logs WHERE id = ?', (log_id,))
            result = cursor.fetchone()
            conn.close()
            
            if result and result[0]:
                detail_window = tk.Toplevel(self.root)
                detail_window.title("检测日志详情")
                detail_window.geometry("800x600")
                
                text_widget = scrolledtext.ScrolledText(detail_window, wrap=tk.WORD)
                text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
                
                # 格式化JSON数据
                try:
                    import json
                    data = json.loads(result[0])
                    formatted_text = json.dumps(data, indent=2, ensure_ascii=False)
                    text_widget.insert(tk.END, formatted_text)
                except:
                    text_widget.insert(tk.END, result[0])
                
                text_widget.config(state=tk.DISABLED)
            
        except Exception as e:
            messagebox.showerror("错误", f"加载日志详情失败：{str(e)}")
    
    def refresh_history(self, notebook):
        """刷新历史记录"""
        current_tab = notebook.index(notebook.select())
        
        if current_tab == 0:  # 站点记录
            self.load_sites_history()
        elif current_tab == 1:  # 检测日志
            self.load_logs_history()
        elif current_tab == 2:  # 举报记录
            self.load_reports_history()
        
        messagebox.showinfo("提示", "历史记录已刷新")
    
    def export_history(self):
        """导出历史记录"""
        try:
            file_path = filedialog.asksaveasfilename(
                title="导出历史记录",
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")]
            )
            
            if not file_path:
                return
            
            import sqlite3
            import pandas as pd
            
            conn = sqlite3.connect('k_site_data.db')
            
            # 导出站点数据
            sites_df = pd.read_sql_query('''
                SELECT domain as '域名', keywords as '关键词', status as '状态', 
                       violation_type as '违规类型', first_detected as '首次检测', 
                       last_checked as '最后检测', baidu_indexed as '百度收录', 
                       google_indexed as '谷歌收录', report_count as '举报次数'
                FROM sites
                ORDER BY last_checked DESC
            ''', conn)
            
            # 导出检测日志
            logs_df = pd.read_sql_query('''
                SELECT s.domain as '域名', dl.check_time as '检测时间', 
                       dl.violation_found as '发现违规', dl.violation_details as '违规详情'
                FROM detection_logs dl
                JOIN sites s ON dl.site_id = s.id
                ORDER BY dl.check_time DESC
            ''', conn)
            
            # 导出举报记录
            reports_df = pd.read_sql_query('''
                SELECT s.domain as '域名', r.platform as '平台', 
                       r.report_time as '举报时间', r.report_reason as '举报原因', 
                       r.status as '状态'
                FROM reports r
                JOIN sites s ON r.site_id = s.id
                ORDER BY r.report_time DESC
            ''', conn)
            
            conn.close()
            
            # 写入Excel文件
            with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
                sites_df.to_excel(writer, sheet_name='站点记录', index=False)
                logs_df.to_excel(writer, sheet_name='检测日志', index=False)
                reports_df.to_excel(writer, sheet_name='举报记录', index=False)
            
            messagebox.showinfo("成功", f"历史记录已导出到：{file_path}")
            
        except Exception as e:
            messagebox.showerror("错误", f"导出历史记录失败：{str(e)}")
    
    def clear_history(self):
        """清空历史记录"""
        result = messagebox.askyesno(
            "确认清空", 
            "确定要清空所有历史记录吗？\n此操作不可恢复！",
            icon='warning'
        )
        
        if result:
            try:
                import sqlite3
                conn = sqlite3.connect('k_site_data.db')
                cursor = conn.cursor()
                
                # 清空所有表
                cursor.execute('DELETE FROM detection_logs')
                cursor.execute('DELETE FROM reports')
                cursor.execute('DELETE FROM sites')
                
                # 重置自增ID
                cursor.execute('DELETE FROM sqlite_sequence WHERE name IN ("sites", "reports", "detection_logs")')
                
                conn.commit()
                conn.close()
                
                # 刷新显示
                self.load_sites_history()
                self.load_logs_history()
                self.load_reports_history()
                
                messagebox.showinfo("成功", "历史记录已清空")
                
            except Exception as e:
                messagebox.showerror("错误", f"清空历史记录失败：{str(e)}")

def main():
    root = tk.Tk()
    app = KSiteGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()