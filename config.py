#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
K站工具配置文件
包含各种设置参数和配置选项
"""

# 基础配置
CONFIG = {
    # 数据库配置
    'database': {
        'path': 'k_site_data.db',
        'backup_interval': 24,  # 小时
    },
    
    # 请求配置
    'request': {
        'timeout': 8,
        'max_retries': 2,
        'delay_range': (0.5, 2),  # 请求间隔范围（秒）
        'concurrent_limit': 20,  # 并发限制（可调整1-100）
        'connection_pool_size': 50,  # 连接池大小
        'max_workers': 20,  # 最大工作线程数
    },
    
    # 检测配置
    'detection': {
        'enable_content_check': True,
        'enable_indexing_check': True,
        'enable_hidden_check': True,
        'enable_js_check': True,
        'deep_scan': False,  # 深度扫描
    },
    
    # 举报配置
    'report': {
        'auto_report': False,
        'report_platforms': ['baidu', '12377'],
        'report_delay': 2,  # 举报间隔（秒）
    },
    
    # 日志配置
    'logging': {
        'level': 'INFO',
        'file': 'k_site_tool.log',
        'max_size': 10,  # MB
        'backup_count': 5,
    }
}

# 违规关键词库（可扩展）
VIOLATION_KEYWORDS = {
    # 博彩类
    'gambling': [
        '博彩', '赌博', '赌场', '赌钱', '赌球', '赌马',
        '六合彩', '时时彩', '快三', '北京赛车', '幸运飞艇',
        '澳门赌场', '真人荷官', '百家乐', '轮盘', '老虎机',
        '德州扑克', '21点', '骰宝', '龙虎斗', '牛牛',
        '投注', '下注', '押注', '竞猜', '彩票',
        'casino', 'gambling', 'poker', 'bet', 'lottery'
    ],
    
    # 色情类
    'adult': [
        '色情', '黄色', '成人', '裸体', '性爱', '做爱',
        '淫荡', '骚货', '鸡巴', '阴道', '乳房', '屁股',
        '自慰', '手淫', '口交', '肛交', '群交', '乱伦',
        '援交', '卖淫', '嫖娼', '性服务', '按摩',
        'porn', 'sex', 'adult', 'nude', 'xxx'
    ],
    
    # 违法服务类
    'illegal_services': [
        '代孕', '假证', '假币', '假钞', '制假', '造假',
        '刻章', '办证', '代开', '发票', '增值税发票',
        '普通发票', '专用发票', '税务发票', '假发票',
        '枪支', '手枪', '步枪', '子弹', '炸药', '雷管',
        '毒品', '海洛因', '冰毒', '摇头丸', '大麻', '可卡因',
        '迷药', '催情', '春药', '蒙汗药', '安眠药',
        '身份证', '驾驶证', '护照', '学历证', '资格证'
    ],
    
    # 金融诈骗类
    'financial_fraud': [
        '套现', '洗钱', '黑钱', '资金盘', '传销', '微商',
        '刷单', '兼职', '日赚', '月入', '躺赚', '暴富',
        '投资理财', '高收益', '无风险', '保本', '稳赚',
        '外汇', '期货', '股票内幕', '庄家', '操盘手',
        '贷款', '无抵押', '秒批', '黑户', '征信修复'
    ],
    
    # 医疗虚假广告类
    'medical_fraud': [
        '包治', '根治', '特效药', '神药', '偏方',
        '祖传秘方', '包好', '无效退款', '立竿见影',
        '癌症', '艾滋病', '糖尿病', '高血压', '心脏病',
        '肝病', '肾病', '性病', '不孕不育', '阳痿',
        '早泄', '前列腺', '妇科病', '皮肤病', '减肥药'
    ]
}

# 搜索引擎User-Agent
SEARCH_ENGINE_UA = {
    'baidu': 'Mozilla/5.0 (compatible; Baiduspider/2.0; +http://www.baidu.com/search/spider.html)',
    'google': 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)',
    'sogou': 'Sogou web spider/4.0(+http://www.sogou.com/docs/help/webmasters.htm#07)',
    '360': 'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; 360Spider)',
    'bing': 'Mozilla/5.0 (compatible; bingbot/2.0; +http://www.bing.com/bingbot.htm)'
}

# 常用User-Agent列表
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/91.0.864.59',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
]

# 举报平台配置
REPORT_PLATFORMS = {
    'baidu': {
        'name': '百度举报',
        'url': 'https://jubao.baidu.com/',
        'api_endpoint': None,  # 实际API地址
        'enabled': True
    },
    '12377': {
        'name': '违法和不良信息举报中心',
        'url': 'https://www.12377.cn/',
        'api_endpoint': None,  # 实际API地址
        'enabled': True
    },
    'google': {
        'name': 'Google举报',
        'url': 'https://www.google.com/webmasters/tools/spamreport',
        'api_endpoint': None,
        'enabled': False
    }
}

# 检测规则配置
DETECTION_RULES = {
    # 隐藏内容检测规则
    'hidden_content': {
        'css_selectors': [
            '[style*="display:none"]',
            '[style*="visibility:hidden"]',
            '[style*="position:absolute;left:-9999px"]',
            '[style*="text-indent:-9999px"]',
            '[style*="font-size:0"]',
            '[style*="color:transparent"]'
        ],
        'suspicious_tags': ['iframe', 'object', 'embed'],
        'min_content_length': 10
    },
    
    # JS劫持检测规则
    'js_redirect': {
        'patterns': [
            r'window\.location\s*=',
            r'document\.location\s*=',
            r'location\.href\s*=',
            r'location\.replace\s*\(',
            r'window\.open\s*\(',
            r'document\.write\s*\(',
            r'eval\s*\(',
            r'setTimeout\s*\(',
            r'setInterval\s*\('
        ],
        'suspicious_functions': [
            'eval', 'unescape', 'fromCharCode',
            'atob', 'btoa', 'decodeURIComponent'
        ]
    },
    
    # TDK篡改检测规则
    'tdk_tampering': {
        'title_max_length': 60,
        'description_max_length': 160,
        'keywords_max_count': 10,
        'suspicious_patterns': [
            r'[\u4e00-\u9fa5]{50,}',  # 连续中文过长
            r'[a-zA-Z]{100,}',       # 连续英文过长
            r'(.)\1{10,}',           # 重复字符
        ]
    }
}

# 代理配置（可选）
PROXY_CONFIG = {
    'enabled': False,
    'proxies': [
        # {'http': 'http://proxy1:port', 'https': 'https://proxy1:port'},
        # {'http': 'http://proxy2:port', 'https': 'https://proxy2:port'},
    ],
    'rotation': True,  # 是否轮换代理
    'timeout': 10
}

# 输出格式配置
OUTPUT_FORMATS = {
    'excel': {
        'enabled': True,
        'columns': [
            '域名', '关键词', '状态', '违规类型', '百度收录', '谷歌收录',
            '隐藏内容', 'JS劫持', 'TDK问题', '检测时间', '最终URL'
        ]
    },
    'json': {
        'enabled': True,
        'pretty_print': True
    },
    'csv': {
        'enabled': True,
        'encoding': 'utf-8-sig'
    }
}

# 安全配置
SECURITY_CONFIG = {
    'max_concurrent_requests': 100,  # 最大并发请求数（1-100可调）
    'request_rate_limit': 10,  # 每秒最大请求数
    'user_agent_rotation': True,
    'random_delay': True,
    'respect_robots_txt': False,
    'max_redirects': 3,
    'connection_timeout': 5,  # 连接超时
    'read_timeout': 8,  # 读取超时
    'keep_alive': True,  # 保持连接
    'pool_connections': 50,  # 连接池连接数
    'pool_maxsize': 100,  # 连接池最大大小
}