#!/usr/bin/env python3
"""
表格图片展示方案 - 将图片URL和预览存储在多维表格中
"""

import sys
import os
sys.path.insert(0, '/workspace/article-collector')

from collector import ArticleCollector
from datetime import datetime
from typing import Dict, List
import json


class ArticleCollectorWithImageView(ArticleCollector):
    """支持图片URL展示的文章收集器"""
    
    def add_article_with_images_to_table(
        self,
        app_token: str,
        table_id: str,
        article: Dict,
        classification: Dict
    ):
        """添加文章记录到表格（包含图片信息）"""
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
        
        # 生成摘要
        summary = article.get('msg_desc', '')
        if not summary and article.get('msg_content_text'):
            import re
            content_text = article['msg_content_text']
            sentences = re.split(r'[。！？\n]', content_text)
            summary = ''
            for sentence in sentences:
                if len(summary + sentence) < 400:
                    summary += sentence + '。'
                else:
                    break
            if len(summary) < 200:
                summary = content_text[:400]
            elif len(summary) > 500:
                summary = summary[:500]
        
        # 提取图片信息
        images = article.get('msg_images', [])
        image_count = len(images)
        
        # 构建图片预览（第一张图片的URL）
        first_image_url = images[0]['url'] if images else ''
        
        # 构建所有图片URL的文本（用于飞书表格中的多行文本字段）
        images_text = '\n'.join([f"{i+1}. {img['url']}" for i, img in enumerate(images)])
        
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
            '图片数': image_count,
        }
        
        # 添加图片相关字段
        if first_image_url:
            # 封面图链接
            fields['封面图'] = {
                'text': '查看封面图',
                'link': first_image_url
            }
        
        if images_text:
            # 所有图片URL（多行文本）
            fields['图片列表'] = images_text
        
        if publish_time:
            fields['发布时间'] = publish_time
        
        # 添加记录
        result = self.feishu.request(
            'POST',
            f'/bitable/v1/apps/{app_token}/tables/{table_id}/records',
            {'fields': fields}
        )
        
        if result.get('code') != 0:
            raise Exception(f"添加记录失败: {result.get('msg')}")
        
        return image_count
    
    def ensure_image_fields(self, app_token: str, table_id: str):
        """确保表格有图片相关字段"""
        # 获取现有字段
        result = self.feishu.request(
            'GET',
            f'/bitable/v1/apps/{app_token}/tables/{table_id}/fields'
        )
        
        existing_fields = {
            field['field_name'] for field in 
            result.get('data', {}).get('items', [])
        }
        
        # 需要添加的字段
        new_fields = [
            {'field_name': '图片数', 'type': 2},  # 数字
            {'field_name': '封面图', 'type': 15},  # 超链接
            {'field_name': '图片列表', 'type': 1},  # 多行文本
        ]
        
        for field in new_fields:
            if field['field_name'] not in existing_fields:
                print(f"添加字段: {field['field_name']}")
                self.feishu.request(
                    'POST',
                    f'/bitable/v1/apps/{app_token}/tables/{table_id}/fields',
                    field
                )
    
    def collect_with_image_view(
        self,
        url: str,
        app_token: str = None,
        table_id: str = None
    ):
        """收集文章并在表格中展示图片"""
        print(f"正在提取文章: {url}")
        
        # 提取文章内容
        article = self.extract_article(url)
        
        print(f"文章标题: {article.get('msg_title')}")
        print(f"来源: {article.get('account_name')}")
        
        # 统计图片
        images = article.get('msg_images', [])
        print(f"📷 发现 {len(images)} 张图片")
        
        # 自动分类
        print("\n正在自动分类...")
        classification = self.classify_article(article)
        print(f"✓ 分类结果: {classification['primary_category']}")
        if classification['tags']:
            print(f"✓ 标签: {', '.join(classification['tags'])}")
        
        # 汇总到表格
        print("\n正在汇总到飞书表格...")
        
        if not app_token:
            print("创建新的多维表格...")
            app = self.create_bitable("文章收集库")
            app_token = app['app_token']
            print(f"表格ID: {app_token}")
        
        if not table_id:
            print("创建数据表...")
            table = self.create_table_in_bitable(app_token, "文章列表")
            table_id = table.get('table_id')
            print(f"数据表ID: {table_id}")
            
            print("添加基础字段...")
            self.add_article_fields(app_token, table_id)
        
        # 添加图片相关字段
        print("添加图片字段...")
        self.ensure_image_fields(app_token, table_id)
        
        # 添加文章记录
        print("添加文章记录...")
        image_count = self.add_article_with_images_to_table(
            app_token, table_id, article, classification
        )
        
        result = {
            'bitable': {
                'app_token': app_token,
                'table_id': table_id,
                'url': f'https://feishu.cn/base/{app_token}'
            },
            'image_count': image_count,
            'classification': classification
        }
        
        print(f"✓ 表格已更新: {result['bitable']['url']}")
        print(f"✓ 已存储 {image_count} 张图片信息")
        
        return result


def main():
    """命令行接口"""
    import argparse
    
    parser = argparse.ArgumentParser(description='收集文章并在表格中展示图片')
    parser.add_argument('--url', required=True, help='文章链接')
    parser.add_argument('--app-token', help='飞书多维表格token')
    parser.add_argument('--table-id', help='飞书数据表ID')
    
    args = parser.parse_args()
    
    # 检查环境变量
    from dotenv import load_dotenv
    load_dotenv('/workspace/article-collector/.env')
    
    if not os.getenv('FEISHU_APP_ID') or not os.getenv('FEISHU_APP_SECRET'):
        print("错误: 请先配置 .env 文件中的飞书凭证")
        sys.exit(1)
    
    collector = ArticleCollectorWithImageView()
    
    try:
        results = collector.collect_with_image_view(
            url=args.url,
            app_token=args.app_token,
            table_id=args.table_id
        )
        
        print("\n" + "=" * 60)
        print("✅ 收集完成！")
        print("=" * 60)
        print(f"📊 表格: {results['bitable']['url']}")
        print(f"📷 图片: {results['image_count']} 张")
        print()
        print("💡 查看图片方式：")
        print("1. 在表格中点击「封面图」字段查看第一张图片")
        print("2. 在「图片列表」字段中查看所有图片URL")
        print("3. 点击URL即可在新标签页中打开图片")
        
    except Exception as e:
        print(f"\n✗ 错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
