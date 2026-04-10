#!/usr/bin/env python3
"""
报告生成器 - 定期生成并发送文章报告
"""

import os
import sys
import json
import argparse
from datetime import datetime, timedelta
from typing import Dict, Optional

from collector import FeishuClient
from summarizer import ArticleSummarizer, create_summary_report
from notifier import FeishuNotifier


class ArticleReporter:
    """文章报告生成器"""
    
    def __init__(self):
        self.feishu = FeishuClient()
        self.summarizer = ArticleSummarizer(self.feishu)
        self.notifier = FeishuNotifier(self.feishu)
    
    def generate_and_send_report(
        self,
        app_token: str,
        table_id: Optional[str] = None,
        days: int = 7,
        receive_id: Optional[str] = None,
        receive_type: str = 'email',
        webhook_url: Optional[str] = None,
        output_file: Optional[str] = None
    ) -> Dict:
        """
        生成并发送报告
        
        Args:
            app_token: 多维表格token
            table_id: 数据表ID
            days: 统计天数
            receive_id: 接收者ID
            receive_type: 接收者类型
            webhook_url: Webhook URL
            output_file: 输出文件路径
        
        Returns:
            报告结果
        """
        print(f"正在生成最近 {days} 天的文章报告...")
        
        # 获取table_id
        if not table_id:
            result = self.feishu.request(
                'GET',
                f'/bitable/v1/apps/{app_token}/tables'
            )
            
            if result.get('code') == 0 and result.get('data', {}).get('items'):
                table_id = result['data']['items'][0]['table_id']
            else:
                return {
                    'success': False,
                    'error': '无法获取数据表ID'
                }
        
        # 生成摘要
        summary = self.summarizer.generate_daily_summary(
            app_token=app_token,
            table_id=table_id,
            days=days
        )
        
        if not summary['success']:
            return summary
        
        # 添加表格链接
        summary['bitable_url'] = f'https://feishu.cn/base/{app_token}'
        
        # 创建报告
        report_content = create_summary_report(summary, 'markdown')
        
        # 保存到文件
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(report_content)
            print(f"✓ 报告已保存到: {output_file}")
        
        # 发送通知
        if receive_id or webhook_url:
            print("正在发送报告通知...")
            
            if webhook_url:
                result = self.notifier.send_webhook_message(
                    webhook_url,
                    report_content
                )
            elif receive_id:
                # 如果是邮箱，转换为邮箱类型
                if '@' in receive_id:
                    receive_type = 'email'
                
                result = self.notifier.send_daily_report(
                    receive_id=receive_id,
                    receive_type=receive_type,
                    report_data=summary
                )
            
            if result.get('success'):
                print("✓ 报告已发送")
            else:
                print(f"✗ 发送失败: {result.get('error', '未知错误')}")
        
        return {
            'success': True,
            'summary': summary,
            'report': report_content,
            'file': output_file
        }
    
    def create_summary_doc(
        self,
        app_token: str,
        table_id: Optional[str] = None,
        days: int = 7,
        folder_token: Optional[str] = None
    ) -> Dict:
        """
        创建汇总文档
        
        Args:
            app_token: 多维表格token
            table_id: 数据表ID
            days: 统计天数
            folder_token: 文件夹token
        
        Returns:
            文档信息
        """
        # 生成摘要
        if not table_id:
            result = self.feishu.request(
                'GET',
                f'/bitable/v1/apps/{app_token}/tables'
            )
            
            if result.get('code') == 0 and result.get('data', {}).get('items'):
                table_id = result['data']['items'][0]['table_id']
        
        summary = self.summarizer.generate_daily_summary(
            app_token=app_token,
            table_id=table_id,
            days=days
        )
        
        if not summary['success']:
            return summary
        
        # 创建报告内容
        report_content = create_summary_report(summary, 'markdown')
        
        # 创建飞书文档
        doc_title = f"文章收集报告 - {datetime.now().strftime('%Y-%m-%d')}"
        
        doc_data = {'title': doc_title}
        if folder_token:
            doc_data['folder_token'] = folder_token
        
        result = self.feishu.request(
            'POST',
            '/docx/v1/documents',
            doc_data
        )
        
        if result.get('code') != 0:
            return {
                'success': False,
                'error': f"创建文档失败: {result.get('msg')}"
            }
        
        doc_token = result['data']['document']['document_id']
        
        print(f"✓ 报告文档已创建: https://feishu.cn/docx/{doc_token}")
        
        return {
            'success': True,
            'doc_token': doc_token,
            'doc_url': f'https://feishu.cn/docx/{doc_token}'
        }


def main():
    """命令行接口"""
    parser = argparse.ArgumentParser(description='生成并发送文章报告')
    parser.add_argument('--app-token', required=True, help='多维表格token')
    parser.add_argument('--table-id', help='数据表ID')
    parser.add_argument('--days', type=int, default=7, help='统计天数')
    parser.add_argument('--receive-id', help='接收者ID（邮箱或open_id）')
    parser.add_argument('--receive-type', default='email', help='接收者类型')
    parser.add_argument('--webhook', help='飞书Webhook URL')
    parser.add_argument('--output', help='输出文件路径')
    parser.add_argument('--create-doc', action='store_true', help='创建飞书文档')
    parser.add_argument('--folder-token', help='文档文件夹token')
    
    args = parser.parse_args()
    
    reporter = ArticleReporter()
    
    if args.create_doc:
        # 创建飞书文档
        result = reporter.create_summary_doc(
            app_token=args.app_token,
            table_id=args.table_id,
            days=args.days,
            folder_token=args.folder_token
        )
    else:
        # 生成并发送报告
        result = reporter.generate_and_send_report(
            app_token=args.app_token,
            table_id=args.table_id,
            days=args.days,
            receive_id=args.receive_id,
            receive_type=args.receive_type,
            webhook_url=args.webhook,
            output_file=args.output
        )
    
    if result['success']:
        print("\n✓ 报告生成成功")
        
        if result.get('doc_url'):
            print(f"📄 文档链接: {result['doc_url']}")
    else:
        print(f"\n✗ 报告生成失败: {result.get('error', '未知错误')}")
        sys.exit(1)


if __name__ == '__main__':
    main()
