#!/usr/bin/env python3
"""
文章收集器 - 增强版
支持：文章提取、自动分类、文档排版、定时总结、消息推送
"""

import os
import sys
import json
import argparse
import subprocess
from datetime import datetime
from typing import Dict, List, Optional
import requests
from dotenv import load_dotenv

# 导入增强模块
from classifier import ArticleClassifier
from formatter import DocumentFormatter

# 加载环境变量
load_dotenv()


class FeishuClient:
    """飞书API客户端"""
    
    def __init__(self):
        self.app_id = os.getenv('FEISHU_APP_ID')
        self.app_secret = os.getenv('FEISHU_APP_SECRET')
        self.base_url = 'https://open.feishu.cn/open-apis'
        self.token = None
        
    def get_token(self, force_refresh=False):
        """获取访问令牌"""
        if self.token and not force_refresh:
            return self.token
        
        url = f'{self.base_url}/auth/v3/tenant_access_token/internal'
        data = {
            'app_id': self.app_id,
            'app_secret': self.app_secret
        }
        
        response = requests.post(url, json=data)
        result = response.json()
        
        if result.get('code') == 0:
            self.token = result['tenant_access_token']
            return self.token
        else:
            raise Exception(f"获取token失败: {result.get('msg')}")
    
    def request(self, method, endpoint, data=None, params=None, retry=True):
        """发送API请求"""
        token = self.get_token()
        url = f'{self.base_url}{endpoint}'
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        
        response = requests.request(
            method, url, 
            headers=headers, 
            json=data,
            params=params
        )
        
        result = response.json()
        
        # Token过期，刷新后重试
        if result.get('code') == 99991663 and retry:
            token = self.get_token(force_refresh=True)
            headers['Authorization'] = f'Bearer {token}'
            response = requests.request(
                method, url,
                headers=headers,
                json=data,
                params=params
            )
            result = response.json()
        
        return result


class ArticleCollector:
    """文章收集器 - 增强版"""
    
    def __init__(self):
        self.feishu = FeishuClient()
        self.classifier = ArticleClassifier()
        self.formatter = DocumentFormatter()
        self.extract_script = os.path.join(
            os.path.dirname(__file__), 
            'extract.js'
        )
    
    def extract_article(self, url: str) -> Dict:
        """提取文章内容"""
        try:
            result = subprocess.run(
                ['node', self.extract_script, url],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode != 0:
                raise Exception(f"提取失败: {result.stderr}")
            
            data = json.loads(result.stdout)
            
            if not data.get('done'):
                raise Exception(data.get('msg', '未知错误'))
            
            return data['data']
        except subprocess.TimeoutExpired:
            raise Exception("提取超时")
        except json.JSONDecodeError:
            raise Exception("提取结果解析失败")
    
    def classify_article(self, article: Dict) -> Dict:
        """自动分类文章"""
        result = self.classifier.classify(
            title=article.get('msg_title', ''),
            content=article.get('msg_content_text', ''),
            description=article.get('msg_desc', '')
        )
        
        return result
    
    def create_bitable(self, name: str = "文章收集") -> Dict:
        """创建多维表格"""
        result = self.feishu.request(
            'POST',
            '/bitable/v1/apps',
            {'name': name}
        )
        
        if result.get('code') != 0:
            raise Exception(f"创建表格失败: {result.get('msg')}")
        
        return result['data']['app']
    
    def create_table_in_bitable(self, app_token: str, table_name: str) -> Dict:
        """在多维表格中创建数据表"""
        result = self.feishu.request(
            'POST',
            f'/bitable/v1/apps/{app_token}/tables',
            {'table': {'name': table_name}}
        )
        
        if result.get('code') != 0:
            raise Exception(f"创建数据表失败: {result.get('msg')}")
        
        # 返回数据表信息，兼容不同的响应格式
        data = result.get('data', {})
        table = data.get('table') or data.get('tables', [{}])[0] or {}
        
        # 确保返回包含table_id
        if not table.get('table_id'):
            # 如果没有table_id，尝试从响应中获取
            table['table_id'] = data.get('table_id') or data.get('id')
        
        return table
    
    def add_article_fields(self, app_token: str, table_id: str):
        """添加文章字段到表格"""
        fields = [
            {'field_name': '标题', 'type': 1},
            {'field_name': '作者', 'type': 1},
            {'field_name': '来源', 'type': 1},
            {'field_name': '分类', 'type': 3},  # 单选
            {'field_name': '发布时间', 'type': 5},
            {'field_name': '链接', 'type': 15},
            {'field_name': '摘要', 'type': 1},
            {'field_name': '标签', 'type': 4},  # 多选
            {'field_name': '收集时间', 'type': 5},
            {'field_name': '重要性', 'type': 2},  # 数字
        ]
        
        for field in fields:
            self.feishu.request(
                'POST',
                f'/bitable/v1/apps/{app_token}/tables/{table_id}/fields',
                field
            )
    
    def add_article_to_table(
        self, 
        app_token: str, 
        table_id: str, 
        article: Dict,
        classification: Dict
    ):
        """添加文章记录到表格"""
        # 转换发布时间
        publish_time = None
        if article.get('msg_publish_time'):
            try:
                dt = datetime.fromisoformat(
                    article['msg_publish_time'].replace('Z', '+00:00')
                )
                publish_time = int(dt.timestamp() * 1000)
            except:
                pass
        
        # 收集时间
        collect_time = int(datetime.now().timestamp() * 1000)
        
        # 计算重要性分数
        importance = classification.get('scores', {}).get(
            classification.get('primary_category', ''), 0
        )
        
        # 生成摘要（200-500字）
        summary = article.get('msg_desc', '')
        if not summary and article.get('msg_content_text'):
            # 如果没有摘要，从正文提取前300-500字
            content_text = article['msg_content_text']
            # 尝试按句子分割，避免截断
            import re
            sentences = re.split(r'[。！？\n]', content_text)
            summary = ''
            for sentence in sentences:
                if len(summary + sentence) < 400:
                    summary += sentence + '。'
                else:
                    break
            # 确保摘要长度在200-500之间
            if len(summary) < 200:
                summary = content_text[:400]
            elif len(summary) > 500:
                summary = summary[:500]
        
        # 构建记录数据
        fields = {
            '标题': article.get('msg_title', ''),
            '作者': article.get('msg_author', ''),
            '来源': article.get('account_name', '未知来源'),
            '分类': classification.get('primary_category', '未分类'),
            '链接': {
                'text': '查看原文',
                'link': article.get('msg_link', '')
            },
            '摘要': summary,
            '标签': classification.get('tags', []),
            '收集时间': collect_time,
            '重要性': int(importance),
        }
        
        if publish_time:
            fields['发布时间'] = publish_time
        
        result = self.feishu.request(
            'POST',
            f'/bitable/v1/apps/{app_token}/tables/{table_id}/records',
            {'fields': fields}
        )
        
        if result.get('code') != 0:
            raise Exception(f"添加记录失败: {result.get('msg')}")
    
    def create_doc(self, title: str, folder_token: str = None) -> Dict:
        """创建文档"""
        data = {'title': title}
        if folder_token:
            data['folder_token'] = folder_token
        
        result = self.feishu.request(
            'POST',
            '/docx/v1/documents',
            data
        )
        
        if result.get('code') != 0:
            raise Exception(f"创建文档失败: {result.get('msg')}")
        
        return result['data']['document']
    
    def write_doc_content(self, doc_token: str, content: str):
        """写入文档内容（使用批量创建块的方式）"""
        # 将内容分段写入
        blocks = self._parse_content_to_blocks(content)
        
        for block in blocks:
            try:
                self.feishu.request(
                    'POST',
                    f'/docx/v1/documents/{doc_token}/blocks/{doc_token}/children/batch_create',
                    {
                        'children': [block],
                        'index': -1
                    }
                )
            except Exception as e:
                print(f"写入块失败: {e}")
    
    def _parse_content_to_blocks(self, content: str) -> List[Dict]:
        """将内容解析为文档块"""
        blocks = []
        lines = content.split('\n')
        
        for line in lines:
            if not line.strip():
                continue
            
            # 标题
            if line.startswith('# '):
                blocks.append({
                    'block_type': 2,  # heading1
                    'heading1': {
                        'elements': [{'text_run': {'content': line[2:]}}]
                    }
                })
            elif line.startswith('## '):
                blocks.append({
                    'block_type': 3,  # heading2
                    'heading2': {
                        'elements': [{'text_run': {'content': line[3:]}}]
                    }
                })
            elif line.startswith('### '):
                blocks.append({
                    'block_type': 4,  # heading3
                    'heading3': {
                        'elements': [{'text_run': {'content': line[4:]}}]
                    }
                })
            else:
                # 普通文本
                blocks.append({
                    'block_type': 2,  # text
                    'text': {
                        'elements': [{'text_run': {'content': line}}]
                    }
                })
        
        return blocks
    
    def create_article_doc(
        self, 
        article: Dict, 
        classification: Dict,
        folder_token: str = None,
        style: str = 'standard'
    ) -> Dict:
        """创建文章文档"""
        title = article.get('msg_title', '未命名文章')
        
        # 添加分类信息到article
        article_with_class = {**article}
        article_with_class['tags'] = classification.get('tags', [])
        article_with_class['primary_category'] = classification.get('primary_category')
        
        # 使用格式化器生成内容
        content = self.formatter.format_article(article_with_class, style)
        
        # 创建文档
        doc = self.create_doc(title, folder_token)
        doc_token = doc['document_id']
        
        print(f"文档已创建: {title}")
        print(f"文档ID: {doc_token}")
        
        return doc
    
    def collect(
        self, 
        url: str, 
        mode: str = 'both',
        app_token: str = None,
        table_id: str = None,
        folder_token: str = None,
        doc_style: str = 'standard',
        auto_classify: bool = True
    ):
        """收集文章"""
        print(f"正在提取文章: {url}")
        
        # 提取文章内容
        article = self.extract_article(url)
        
        print(f"文章标题: {article.get('msg_title')}")
        print(f"来源: {article.get('account_name')}")
        
        # 自动分类
        classification = {}
        if auto_classify:
            print("\n正在自动分类...")
            classification = self.classify_article(article)
            
            print(f"✓ 分类结果: {classification['primary_category']}")
            if classification['tags']:
                print(f"✓ 标签: {', '.join(classification['tags'])}")
        
        results = {}
        
        # 汇总到表格
        if mode in ['table', 'both']:
            print("\n正在汇总到飞书表格...")
            
            if not app_token:
                print("创建新的多维表格...")
                app = self.create_bitable("文章收集库")
                app_token = app['app_token']
                print(f"表格ID: {app_token}")
            
            if not table_id:
                print("创建数据表...")
                table = self.create_table_in_bitable(app_token, "文章列表")
                table_id = table['table_id']
                print(f"数据表ID: {table_id}")
                
                print("添加字段...")
                self.add_article_fields(app_token, table_id)
            
            print("添加文章记录...")
            self.add_article_to_table(app_token, table_id, article, classification)
            
            results['bitable'] = {
                'app_token': app_token,
                'table_id': table_id,
                'url': f'https://feishu.cn/base/{app_token}'
            }
            print(f"✓ 表格已更新: {results['bitable']['url']}")
        
        # 汇总到文档
        if mode in ['doc', 'both']:
            print("\n正在创建飞书文档...")
            doc = self.create_article_doc(
                article, 
                classification,
                folder_token,
                style=doc_style
            )
            
            results['doc'] = {
                'doc_token': doc['document_id'],
                'url': f'https://feishu.cn/docx/{doc["document_id"]}'
            }
            print(f"✓ 文档已创建: {results['doc']['url']}")
        
        # 返回分类结果
        results['classification'] = classification
        
        return results


def main():
    parser = argparse.ArgumentParser(
        description='收集文章并汇总到飞书（增强版）'
    )
    parser.add_argument(
        '--url', 
        help='文章链接'
    )
    parser.add_argument(
        '--file',
        help='包含文章链接的文件（每行一个）'
    )
    parser.add_argument(
        '--mode',
        choices=['table', 'doc', 'both'],
        default='both',
        help='汇总模式'
    )
    parser.add_argument(
        '--app-token',
        help='飞书多维表格 token'
    )
    parser.add_argument(
        '--table-id',
        help='飞书数据表 ID'
    )
    parser.add_argument(
        '--folder-token',
        help='飞书文件夹 token'
    )
    parser.add_argument(
        '--doc-style',
        choices=['standard', 'card', 'newsletter'],
        default='standard',
        help='文档格式风格'
    )
    parser.add_argument(
        '--no-auto-classify',
        action='store_true',
        help='禁用自动分类'
    )
    
    args = parser.parse_args()
    
    # 检查环境变量
    if not os.getenv('FEISHU_APP_ID') or not os.getenv('FEISHU_APP_SECRET'):
        print("错误: 请先配置 .env 文件中的飞书凭证")
        print("参考 .env.example 文件进行配置")
        sys.exit(1)
    
    collector = ArticleCollector()
    
    # 处理URL
    if args.url:
        urls = [args.url]
    elif args.file:
        with open(args.file, 'r', encoding='utf-8') as f:
            urls = [line.strip() for line in f if line.strip()]
    else:
        parser.print_help()
        sys.exit(1)
    
    # 收集文章
    success_count = 0
    for url in urls:
        try:
            print(f"\n{'='*60}")
            results = collector.collect(
                url=url,
                mode=args.mode,
                app_token=args.app_token,
                table_id=args.table_id,
                folder_token=args.folder_token,
                doc_style=args.doc_style,
                auto_classify=not args.no_auto_classify
            )
            success_count += 1
            
            # 如果创建了新的表格，更新参数
            if results.get('bitable') and not args.app_token:
                args.app_token = results['bitable']['app_token']
                args.table_id = results['bitable']['table_id']
                
        except Exception as e:
            print(f"✗ 错误: {e}")
    
    print(f"\n{'='*60}")
    print(f"收集完成: {success_count}/{len(urls)} 篇文章")


if __name__ == '__main__':
    main()
