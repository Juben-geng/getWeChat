#!/usr/bin/env python3
"""
文章收集器 - 图片增强版
支持：文章提取、图片下载上传、飞书文档视图展示
"""

import sys
import os
sys.path.insert(0, '/workspace/article-collector')

from collector import ArticleCollector, FeishuClient
from image_processor import ImageProcessor, create_image_blocks
from formatter import DocumentFormatter
from classifier import ArticleClassifier
import json
import subprocess
from datetime import datetime
from typing import Dict, List, Optional


class ArticleCollectorWithImages(ArticleCollector):
    """支持图片的文章收集器"""
    
    def __init__(self):
        super().__init__()
        self.image_processor = ImageProcessor(self.feishu)
        self.formatter = DocumentFormatter()
    
    def extract_article_with_images(self, url: str) -> Dict:
        """提取文章内容和图片"""
        try:
            result = subprocess.run(
                ['node', '/workspace/article-collector/extract.js', url],
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
        except Exception as e:
            raise Exception(f"文章提取失败: {e}")
    
    def process_and_upload_images(self, article: Dict, max_images: int = 10) -> List[Dict]:
        """处理并上传文章中的图片"""
        images = article.get('msg_images', [])
        
        if not images:
            print("文章中没有图片")
            return []
        
        print(f"\n发现 {len(images)} 张图片，开始处理...")
        
        uploaded_images = []
        
        for i, img_info in enumerate(images[:max_images], 1):
            print(f"正在处理第 {i}/{min(len(images), max_images)} 张图片...")
            
            # 下载图片
            image_data = self.image_processor.download_image(img_info['url'])
            
            if image_data:
                # 上传到飞书
                file_name = f"image_{i}.png"
                upload_result = self.image_processor.upload_image_to_feishu(
                    image_data,
                    file_name
                )
                
                if upload_result:
                    uploaded_images.append({
                        'original_url': img_info['url'],
                        'file_token': upload_result.get('file_token'),
                        'file_name': file_name,
                        'alt': img_info.get('alt', ''),
                        'size': len(image_data)
                    })
                    print(f"✓ 图片 {i} 上传成功 (file_token: {upload_result.get('file_token')[:20]}...)")
                else:
                    print(f"✗ 图片 {i} 上传失败")
            else:
                print(f"✗ 图片 {i} 下载失败")
        
        print(f"\n成功上传 {len(uploaded_images)} 张图片")
        
        return uploaded_images
    
    def create_doc_with_images(
        self,
        article: Dict,
        classification: Dict,
        uploaded_images: List[Dict],
        folder_token: str = None
    ) -> Dict:
        """创建包含图片的飞书文档"""
        title = article.get('msg_title', '未命名文章')
        
        # 创建文档
        doc_data = {'title': title}
        if folder_token:
            doc_data['folder_token'] = folder_token
        
        result = self.feishu.request(
            'POST',
            '/docx/v1/documents',
            doc_data
        )
        
        if result.get('code') != 0:
            raise Exception(f"创建文档失败: {result.get('msg')}")
        
        doc_token = result['data']['document']['document_id']
        print(f"✓ 文档已创建: {title}")
        print(f"  文档ID: {doc_token}")
        
        # 构建文档内容块
        blocks = self._build_document_blocks(article, classification, uploaded_images)
        
        # 批量创建块
        if blocks:
            self._create_blocks(doc_token, doc_token, blocks)
        
        return {
            'document_id': doc_token,
            'url': f'https://feishu.cn/docx/{doc_token}'
        }
    
    def _build_document_blocks(
        self,
        article: Dict,
        classification: Dict,
        uploaded_images: List[Dict]
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
        meta_text = []
        if article.get('msg_author'):
            meta_text.append(f"作者: {article['msg_author']}")
        if article.get('account_name'):
            meta_text.append(f"来源: {article['account_name']}")
        if article.get('msg_publish_time_str'):
            meta_text.append(f"发布时间: {article['msg_publish_time_str']}")
        
        if meta_text:
            blocks.append({
                'block_type': 2,  # text
                'text': {
                    'elements': [{'text_run': {'content': ' | '.join(meta_text)}}]
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
        
        # 分隔线（使用文本模拟）
        blocks.append({
            'block_type': 2,
            'text': {
                'elements': [{'text_run': {'content': '─' * 50}}]
            }
        })
        
        # 封面图（如果有）
        if uploaded_images and len(uploaded_images) > 0:
            # 第一张图片作为封面
            blocks.append({
                'block_type': 4,  # image
                'image': {
                    'token': uploaded_images[0]['file_token'],
                    'width': 600,
                    'height': 400
                }
            })
        
        # 摘要
        summary = article.get('msg_desc', '')
        if not summary and article.get('msg_content_text'):
            # 生成摘要
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
                        {'text_run': {'content': '摘要：'}},
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
            # 按段落分割
            paragraphs = content_text.split('\n\n')
            
            for para in paragraphs[:10]:  # 限制段落数量
                para = para.strip()
                if para and len(para) > 10:
                    blocks.append({
                        'block_type': 2,
                        'text': {
                            'elements': [{'text_run': {'content': para[:1000]}}]
                        }
                    })
        
        # 更多图片（画廊形式）
        if len(uploaded_images) > 1:
            blocks.append({
                'block_type': 2,
                'text': {
                    'elements': [{'text_run': {'content': '\n📷 文章配图：'}}]
                }
            })
            
            for i, img in enumerate(uploaded_images[1:6], 2):  # 最多再添加5张
                blocks.append({
                    'block_type': 4,
                    'image': {
                        'token': img['file_token'],
                        'width': 600,
                        'height': 400
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
    
    def _create_blocks(self, doc_token: str, block_id: str, blocks: List[Dict]):
        """批量创建文档块"""
        try:
            # 飞书API限制，每次只能创建一个块
            for block in blocks:
                result = self.feishu.request(
                    'POST',
                    f'/bitable/v1/documents/{doc_token}/blocks/{block_id}/children',
                    {
                        'children': [block],
                        'index': -1  # 追加到末尾
                    }
                )
                
                # 如果失败，使用备用方法
                if result.get('code') != 0:
                    # 尝试直接创建
                    result = self.feishu.request(
                        'POST',
                        f'/docx/v1/documents/{doc_token}/blocks/{doc_token}/children',
                        {'children': [block], 'index': -1}
                    )
        except Exception as e:
            print(f"创建文档块时出错: {e}")
    
    def collect_with_images(
        self,
        url: str,
        mode: str = 'both',
        max_images: int = 10,
        app_token: str = None,
        table_id: str = None,
        folder_token: str = None
    ):
        """收集文章并处理图片"""
        print(f"正在提取文章: {url}")
        
        # 提取文章内容（包含图片信息）
        article = self.extract_article_with_images(url)
        
        print(f"文章标题: {article.get('msg_title')}")
        print(f"来源: {article.get('account_name')}")
        
        # 自动分类
        print("\n正在自动分类...")
        classification = self.classify_article(article)
        print(f"✓ 分类结果: {classification['primary_category']}")
        if classification['tags']:
            print(f"✓ 标签: {', '.join(classification['tags'])}")
        
        # 处理图片
        uploaded_images = []
        if mode in ['doc', 'both']:
            print("\n正在处理图片...")
            uploaded_images = self.process_and_upload_images(article, max_images)
        
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
            
            print("添加文章记录...")
            self.add_article_to_table(app_token, table_id, article, classification)
            
            results['bitable'] = {
                'app_token': app_token,
                'table_id': table_id,
                'url': f'https://feishu.cn/base/{app_token}'
            }
            print(f"✓ 表格已更新: {results['bitable']['url']}")
        
        # 创建包含图片的文档
        if mode in ['doc', 'both']:
            print("\n正在创建飞书文档（含图片）...")
            doc = self.create_doc_with_images(
                article,
                classification,
                uploaded_images,
                folder_token
            )
            
            results['doc'] = {
                'doc_token': doc['document_id'],
                'url': doc['url'],
                'image_count': len(uploaded_images)
            }
            print(f"✓ 文档已创建（含 {len(uploaded_images)} 张图片）: {results['doc']['url']}")
        
        # 返回结果
        results['classification'] = classification
        results['images'] = uploaded_images
        
        return results


def main():
    """命令行接口"""
    import argparse
    
    parser = argparse.ArgumentParser(description='收集文章并推送图片到飞书')
    parser.add_argument('--url', required=True, help='文章链接')
    parser.add_argument('--mode', choices=['table', 'doc', 'both'], default='both')
    parser.add_argument('--max-images', type=int, default=10, help='最多处理多少张图片')
    parser.add_argument('--app-token', help='飞书多维表格token')
    parser.add_argument('--table-id', help='飞书数据表ID')
    parser.add_argument('--folder-token', help='飞书文件夹token')
    
    args = parser.parse_args()
    
    # 检查环境变量
    from dotenv import load_dotenv
    load_dotenv('/workspace/article-collector/.env')
    
    if not os.getenv('FEISHU_APP_ID') or not os.getenv('FEISHU_APP_SECRET'):
        print("错误: 请先配置 .env 文件中的飞书凭证")
        sys.exit(1)
    
    collector = ArticleCollectorWithImages()
    
    try:
        results = collector.collect_with_images(
            url=args.url,
            mode=args.mode,
            max_images=args.max_images,
            app_token=args.app_token,
            table_id=args.table_id,
            folder_token=args.folder_token
        )
        
        print("\n" + "=" * 60)
        print("收集完成！")
        print("=" * 60)
        
        if results.get('bitable'):
            print(f"📊 表格: {results['bitable']['url']}")
        
        if results.get('doc'):
            print(f"📄 文档: {results['doc']['url']}")
            print(f"📷 图片: {results['doc']['image_count']} 张")
        
    except Exception as e:
        print(f"\n✗ 错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
