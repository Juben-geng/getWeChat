#!/usr/bin/env python3
"""
完整版文章收集器 - 支持文档和表格
包含图片URL展示和文档内容写入
"""

import sys
import os
sys.path.insert(0, '/workspace/article-collector')

from collector import ArticleCollector, FeishuClient
from datetime import datetime
from typing import Dict, List
import json


class CompleteArticleCollector(ArticleCollector):
    """完整版文章收集器"""
    
    def create_complete_doc(
        self,
        article: Dict,
        classification: Dict
    ) -> Dict:
        """创建完整的文档"""
        title = article.get('msg_title', '未命名文章')
        
        # 创建文档
        result = self.feishu.request(
            'POST',
            '/docx/v1/documents',
            {'title': title}
        )
        
        if result.get('code') != 0:
            raise Exception(f"创建文档失败: {result.get('msg')}")
        
        doc_id = result['data']['document']['document_id']
        print(f"✓ 文档已创建: {title}")
        
        # 构建文档内容
        blocks = self._build_document_content(article, classification)
        
        # 写入内容
        if blocks:
            print(f"正在写入 {len(blocks)} 个内容块...")
            for i, block in enumerate(blocks):
                try:
                    result = self.feishu.request(
                        'POST',
                        f'/docx/v1/documents/{doc_id}/blocks/{doc_id}/children',
                        {'children': [block], 'index': i}
                    )
                    
                    if result.get('code') != 0:
                        print(f"  警告: 第 {i+1} 个块写入失败")
                except Exception as e:
                    print(f"  警告: 第 {i+1} 个块写入出错: {e}")
            
            print(f"✓ 文档内容写入完成")
        
        return {
            'document_id': doc_id,
            'url': f'https://feishu.cn/docx/{doc_id}'
        }
    
    def _build_document_content(
        self,
        article: Dict,
        classification: Dict
    ) -> List[Dict]:
        """构建文档内容块"""
        blocks = []
        
        # 标题
        blocks.append({
            'block_type': 2,  # heading1
            'heading1': {
                'elements': [{'text_run': {'content': article.get('msg_title', '未命名文章')}}]
            }
        })
        
        # 元信息
        meta_parts = []
        if article.get('msg_author'):
            meta_parts.append(f"作者: {article['msg_author']}")
        if article.get('account_name'):
            meta_parts.append(f"来源: {article['account_name']}")
        if article.get('msg_publish_time_str'):
            meta_parts.append(f"发布时间: {article['msg_publish_time_str'][:10]}")
        
        if meta_parts:
            blocks.append({
                'block_type': 2,
                'text': {
                    'elements': [{'text_run': {'content': ' | '.join(meta_parts)}}]
                }
            })
        
        # 分类和标签
        if classification.get('primary_category'):
            tag_text = f"分类: {classification['primary_category']}"
            if classification.get('tags'):
                tag_text += f" | 标签: {', '.join(classification['tags'][:5])}"
            
            blocks.append({
                'block_type': 2,
                'text': {
                    'elements': [{'text_run': {'content': tag_text}}]
                }
            })
        
        # 分隔线
        blocks.append({
            'block_type': 2,
            'text': {
                'elements': [{'text_run': {'content': '─' * 50}}]
            }
        })
        
        # 图片信息
        images = article.get('msg_images', [])
        if images:
            blocks.append({
                'block_type': 2,
                'text': {
                    'elements': [{'text_run': {'content': f'📷 文章包含 {len(images)} 张图片'}}]
                }
            })
            
            # 显示图片链接
            for i, img in enumerate(images[:5], 1):
                blocks.append({
                    'block_type': 2,
                    'text': {
                        'elements': [
                            {'text_run': {'content': f'图片{i}: '}},
                            {'text_run': {'content': img['url'][:80] + '...'}}
                        ]
                    }
                })
        
        # 摘要
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
        
        if summary:
            blocks.append({
                'block_type': 2,
                'text': {
                    'elements': [
                        {'text_run': {'content': '📌 摘要：'}},
                        {'text_run': {'content': summary[:500]}}
                    ]
                }
            })
        
        # 分隔线
        blocks.append({
            'block_type': 2,
            'text': {
                'elements': [{'text_run': {'content': '─' * 50}}]
            }
        })
        
        # 正文内容（分段）
        content_text = article.get('msg_content_text', '')
        if content_text:
            blocks.append({
                'block_type': 2,
                'text': {
                    'elements': [{'text_run': {'content': '📖 正文内容：'}}]
                }
            })
            
            # 按段落分割
            paragraphs = content_text.split('\n\n')
            
            for para in paragraphs[:10]:  # 限制段落数量
                para = para.strip()
                if para and len(para) > 10:
                    if len(para) > 1000:
                        para = para[:1000] + '...'
                    blocks.append({
                        'block_type': 2,
                        'text': {
                            'elements': [{'text_run': {'content': para}}]
                        }
                    })
        
        # 原文链接
        if article.get('msg_link'):
            blocks.append({
                'block_type': 2,
                'text': {
                    'elements': [
                        {'text_run': {'content': '\n原文链接：'}},
                        {'text_run': {'content': article['msg_link']}}
                    ]
                }
            })
        
        return blocks
    
    def collect_complete(
        self,
        url: str,
        mode: str = 'both',
        app_token: str = None,
        table_id: str = None
    ):
        """完整收集文章"""
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
                table_id = table.get('table_id')
                print(f"数据表ID: {table_id}")
                
                print("添加字段...")
                self.add_article_fields(app_token, table_id)
            
            # 添加图片相关字段
            self._ensure_image_fields(app_token, table_id)
            
            # 添加文章记录（含图片信息）
            print("添加文章记录...")
            self._add_article_with_images(app_token, table_id, article, classification)
            
            results['bitable'] = {
                'app_token': app_token,
                'table_id': table_id,
                'url': f'https://feishu.cn/base/{app_token}'
            }
            print(f"✓ 表格已更新: {results['bitable']['url']}")
        
        # 创建文档
        if mode in ['doc', 'both']:
            print("\n正在创建飞书文档...")
            doc = self.create_complete_doc(article, classification)
            
            results['doc'] = {
                'doc_token': doc['document_id'],
                'url': doc['url']
            }
            print(f"✓ 文档已创建: {results['doc']['url']}")
        
        results['classification'] = classification
        results['image_count'] = len(images)
        
        return results
    
    def _ensure_image_fields(self, app_token: str, table_id: str):
        """确保图片字段存在"""
        # 获取现有字段
        result = self.feishu.request(
            'GET',
            f'/bitable/v1/apps/{app_token}/tables/{table_id}/fields'
        )
        
        existing = {f['field_name'] for f in result.get('data', {}).get('items', [])}
        
        # 添加图片字段
        new_fields = [
            {'field_name': '图片数', 'type': 2},
            {'field_name': '封面图', 'type': 15},
            {'field_name': '图片列表', 'type': 1},
        ]
        
        for field in new_fields:
            if field['field_name'] not in existing:
                print(f"  添加字段: {field['field_name']}")
                self.feishu.request(
                    'POST',
                    f'/bitable/v1/apps/{app_token}/tables/{table_id}/fields',
                    field
                )
    
    def _add_article_with_images(
        self,
        app_token: str,
        table_id: str,
        article: Dict,
        classification: Dict
    ):
        """添加文章记录（含图片信息）"""
        # 转换时间
        publish_time = None
        if article.get('msg_publish_time'):
            try:
                dt = datetime.fromisoformat(
                    article['msg_publish_time'].replace('Z', '+00:00')
                )
                publish_time = int(dt.timestamp() * 1000)
            except:
                pass
        
        collect_time = int(datetime.now().timestamp() * 1000)
        
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
        first_image_url = images[0]['url'] if images else ''
        images_text = '\n'.join([f"{i+1}. {img['url']}" for i, img in enumerate(images)])
        
        # 构建记录
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
            '重要性': int(classification.get('scores', {}).get(
                classification.get('primary_category', ''), 0
            )),
            '图片数': image_count,
        }
        
        # 图片相关字段
        if first_image_url:
            fields['封面图'] = {
                'text': '查看封面图',
                'link': first_image_url
            }
        
        if images_text:
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


def main():
    """命令行接口"""
    import argparse
    
    parser = argparse.ArgumentParser(description='完整版文章收集')
    parser.add_argument('--url', required=True, help='文章链接')
    parser.add_argument('--mode', choices=['table', 'doc', 'both'], default='both')
    parser.add_argument('--app-token', help='飞书多维表格token')
    parser.add_argument('--table-id', help='飞书数据表ID')
    
    args = parser.parse_args()
    
    # 检查环境变量
    from dotenv import load_dotenv
    load_dotenv('/workspace/article-collector/.env')
    
    if not os.getenv('FEISHU_APP_ID') or not os.getenv('FEISHU_APP_SECRET'):
        print("错误: 请先配置 .env 文件中的飞书凭证")
        sys.exit(1)
    
    collector = CompleteArticleCollector()
    
    try:
        results = collector.collect_complete(
            url=args.url,
            mode=args.mode,
            app_token=args.app_token,
            table_id=args.table_id
        )
        
        print("\n" + "=" * 60)
        print("✅ 收集完成！")
        print("=" * 60)
        
        if results.get('bitable'):
            print(f"📊 表格: {results['bitable']['url']}")
        
        if results.get('doc'):
            print(f"📄 文档: {results['doc']['url']}")
        
        print(f"📷 图片: {results.get('image_count', 0)} 张")
        
    except Exception as e:
        print(f"\n✗ 错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
