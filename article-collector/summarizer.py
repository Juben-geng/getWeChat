"""
文章总结器 - 自动生成文章摘要和周期报告
"""

import os
import sys
import json
import argparse
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from collections import defaultdict
import requests


class ArticleSummarizer:
    """文章总结生成器"""
    
    def __init__(self, feishu_client):
        self.feishu = feishu_client
    
    def generate_daily_summary(
        self,
        app_token: str,
        table_id: str,
        days: int = 1
    ) -> Dict:
        """
        生成每日/每周文章摘要
        
        Args:
            app_token: 多维表格token
            table_id: 数据表ID
            days: 统计天数
        
        Returns:
            摘要数据
        """
        # 获取文章列表
        articles = self._fetch_articles(app_token, table_id, days)
        
        if not articles:
            return {
                'success': False,
                'message': f'最近{days}天没有收集文章'
            }
        
        # 统计分析
        stats = self._analyze_articles(articles)
        
        # 生成摘要
        summary = {
            'success': True,
            'period': f'最近{days}天',
            'total_count': len(articles),
            'stats': stats,
            'articles': articles,
            'highlights': self._extract_highlights(articles),
            'categories': self._group_by_category(articles)
        }
        
        return summary
    
    def _fetch_articles(
        self,
        app_token: str,
        table_id: str,
        days: int
    ) -> List[Dict]:
        """获取指定天数内的文章"""
        # 计算时间范围
        end_time = datetime.now()
        start_time = end_time - timedelta(days=days)
        
        # 调用飞书API查询
        all_records = []
        page_token = None
        
        while True:
            body = {
                "page_size": 500,
                "filter": {
                    "conditions": [
                        {
                            "field_name": "收集时间",
                            "operator": "isGreater",
                            "value": [int(start_time.timestamp() * 1000)]
                        }
                    ]
                }
            }
            
            if page_token:
                body["page_token"] = page_token
            
            result = self.feishu.request(
                'POST',
                f'/bitable/v1/apps/{app_token}/tables/{table_id}/records/search',
                body
            )
            
            if result.get('code') != 0:
                print(f"查询失败: {result.get('msg')}")
                break
            
            items = result.get('data', {}).get('items', [])
            all_records.extend(items)
            
            if not result.get('data', {}).get('has_more'):
                break
            
            page_token = result.get('data', {}).get('page_token')
        
        # 转换为文章列表
        articles = []
        for record in all_records:
            fields = record.get('fields', {})
            
            article = {
                'record_id': record.get('record_id'),
                'title': fields.get('标题', ''),
                'author': fields.get('作者', ''),
                'source': fields.get('来源', ''),
                'link': fields.get('链接', {}).get('link', ''),
                'summary': fields.get('摘要', ''),
                'collect_time': fields.get('收集时间'),
                'publish_time': fields.get('发布时间'),
                'tags': fields.get('标签', [])
            }
            
            articles.append(article)
        
        # 按收集时间倒序排序
        articles.sort(key=lambda x: x.get('collect_time', 0), reverse=True)
        
        return articles
    
    def _analyze_articles(self, articles: List[Dict]) -> Dict:
        """分析文章数据"""
        stats = {
            'total': len(articles),
            'sources': defaultdict(int),
            'authors': defaultdict(int),
            'daily_distribution': defaultdict(int),
            'tags': defaultdict(int)
        }
        
        for article in articles:
            # 统计来源
            if article.get('source'):
                stats['sources'][article['source']] += 1
            
            # 统计作者
            if article.get('author'):
                stats['authors'][article['author']] += 1
            
            # 统计每日分布
            if article.get('collect_time'):
                date = datetime.fromtimestamp(
                    article['collect_time'] / 1000
                ).strftime('%Y-%m-%d')
                stats['daily_distribution'][date] += 1
            
            # 统计标签
            for tag in article.get('tags', []):
                stats['tags'][tag] += 1
        
        # 转换为普通字典
        stats['sources'] = dict(stats['sources'])
        stats['authors'] = dict(stats['authors'])
        stats['daily_distribution'] = dict(stats['daily_distribution'])
        stats['tags'] = dict(stats['tags'])
        
        return stats
    
    def _extract_highlights(self, articles: List[Dict], top_n: int = 5) -> List[Dict]:
        """提取重要文章（基于标题和摘要的关键词）"""
        # 简单的关键词权重
        important_keywords = [
            '重磅', '突破', '最新', '首次', '独家', '必读',
            '干货', '总结', '深度', '解析', '实战'
        ]
        
        scored_articles = []
        
        for article in articles:
            score = 0
            title = article.get('title', '')
            summary = article.get('summary', '')
            
            # 检查关键词
            for keyword in important_keywords:
                if keyword in title:
                    score += 10
                if keyword in summary:
                    score += 5
            
            scored_articles.append({
                'article': article,
                'score': score
            })
        
        # 排序并返回前N篇
        scored_articles.sort(key=lambda x: x['score'], reverse=True)
        
        return [item['article'] for item in scored_articles[:top_n]]
    
    def _group_by_category(self, articles: List[Dict]) -> Dict[str, List[Dict]]:
        """按分类分组文章"""
        categories = defaultdict(list)
        
        for article in articles:
            # 从标签中提取分类（假设第一个标签是分类）
            tags = article.get('tags', [])
            if tags:
                category = tags[0]
            else:
                category = '未分类'
            
            categories[category].append(article)
        
        return dict(categories)


def create_summary_report(summary: Dict, format_type: str = 'markdown') -> str:
    """
    创建摘要报告
    
    Args:
        summary: 摘要数据
        format_type: 格式类型 ('markdown', 'text')
    
    Returns:
        格式化的报告内容
    """
    if format_type == 'markdown':
        return _create_markdown_report(summary)
    else:
        return _create_text_report(summary)


def _create_markdown_report(summary: Dict) -> str:
    """创建Markdown格式报告"""
    lines = []
    
    # 标题
    lines.append("# 📊 文章收集报告")
    lines.append("")
    lines.append(f"**时间周期**: {summary['period']}")
    lines.append(f"**收集数量**: {summary['total_count']} 篇")
    lines.append("")
    lines.append("---")
    lines.append("")
    
    # 统计概览
    lines.append("## 📈 数据概览")
    lines.append("")
    
    stats = summary['stats']
    
    # 来源分布
    if stats['sources']:
        lines.append("### 主要来源")
        lines.append("")
        for source, count in sorted(
            stats['sources'].items(), 
            key=lambda x: x[1], 
            reverse=True
        )[:5]:
            lines.append(f"- **{source}**: {count} 篇")
        lines.append("")
    
    # 标签云
    if stats['tags']:
        lines.append("### 热门标签")
        lines.append("")
        tags_line = " ".join([
            f"`{tag}({count})`" 
            for tag, count in sorted(
                stats['tags'].items(), 
                key=lambda x: x[1], 
                reverse=True
            )[:10]
        ])
        lines.append(tags_line)
        lines.append("")
    
    # 每日分布
    if stats['daily_distribution']:
        lines.append("### 每日收集趋势")
        lines.append("")
        for date, count in sorted(stats['daily_distribution'].items()):
            bar = '█' * count
            lines.append(f"{date}: {bar} {count}")
        lines.append("")
    
    lines.append("---")
    lines.append("")
    
    # 精选文章
    if summary['highlights']:
        lines.append("## ⭐ 精选文章")
        lines.append("")
        for i, article in enumerate(summary['highlights'], 1):
            lines.append(f"### {i}. {article['title']}")
            lines.append("")
            if article.get('source'):
                lines.append(f"**来源**: {article['source']}")
            if article.get('summary'):
                lines.append(f"\n> {article['summary'][:100]}...")
            if article.get('link'):
                lines.append(f"\n[阅读原文]({article['link']})")
            lines.append("")
    
    lines.append("---")
    lines.append("")
    
    # 分类浏览
    if summary['categories']:
        lines.append("## 📂 分类浏览")
        lines.append("")
        
        for category, articles in summary['categories'].items():
            lines.append(f"### {category} ({len(articles)} 篇)")
            lines.append("")
            
            for article in articles[:3]:  # 每个分类只显示前3篇
                lines.append(f"- {article['title']}")
            
            if len(articles) > 3:
                lines.append(f"- *... 还有 {len(articles) - 3} 篇*")
            
            lines.append("")
    
    return "\n".join(lines)


def _create_text_report(summary: Dict) -> str:
    """创建纯文本格式报告"""
    lines = []
    
    lines.append("=" * 60)
    lines.append("📊 文章收集报告")
    lines.append("=" * 60)
    lines.append(f"时间周期: {summary['period']}")
    lines.append(f"收集数量: {summary['total_count']} 篇")
    lines.append("")
    
    # 精选文章
    if summary['highlights']:
        lines.append("⭐ 精选文章:")
        lines.append("-" * 60)
        for i, article in enumerate(summary['highlights'], 1):
            lines.append(f"{i}. {article['title']}")
            lines.append(f"   来源: {article.get('source', '未知')}")
            lines.append("")
    
    # 分类统计
    if summary['categories']:
        lines.append("📂 分类统计:")
        lines.append("-" * 60)
        for category, articles in summary['categories'].items():
            lines.append(f"{category}: {len(articles)} 篇")
    
    return "\n".join(lines)


def main():
    """命令行接口"""
    parser = argparse.ArgumentParser(description='生成文章摘要报告')
    parser.add_argument('--app-token', required=True, help='多维表格token')
    parser.add_argument('--table-id', help='数据表ID')
    parser.add_argument('--days', type=int, default=1, help='统计天数')
    parser.add_argument('--output', help='输出文件路径')
    parser.add_argument('--format', choices=['markdown', 'text'], default='markdown')
    
    args = parser.parse_args()
    
    # 导入飞书客户端
    from collector import FeishuClient
    
    feishu = FeishuClient()
    summarizer = ArticleSummarizer(feishu)
    
    # 获取table_id
    if not args.table_id:
        # 获取第一个数据表
        result = feishu.request(
            'GET',
            f'/bitable/v1/apps/{args.app_token}/tables'
        )
        
        if result.get('code') == 0 and result.get('data', {}).get('items'):
            args.table_id = result['data']['items'][0]['table_id']
        else:
            print("错误: 无法获取数据表ID")
            sys.exit(1)
    
    # 生成摘要
    print(f"正在生成最近 {args.days} 天的文章摘要...")
    
    summary = summarizer.generate_daily_summary(
        app_token=args.app_token,
        table_id=args.table_id,
        days=args.days
    )
    
    if not summary['success']:
        print(summary['message'])
        return
    
    # 创建报告
    report = create_summary_report(summary, args.format)
    
    # 输出
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"✓ 报告已保存到: {args.output}")
    else:
        print(report)


if __name__ == '__main__':
    main()
