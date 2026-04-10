"""
飞书消息推送器 - 发送消息通知给用户
"""

import os
import json
from typing import Dict, List, Optional
import requests


class FeishuNotifier:
    """飞书消息推送"""
    
    def __init__(self, feishu_client):
        self.feishu = feishu_client
    
    def send_text_message(
        self,
        receive_id: str,
        receive_type: str = 'open_id',
        content: str
    ) -> Dict:
        """
        发送文本消息
        
        Args:
            receive_id: 接收者ID
            receive_type: 接收者类型 ('open_id', 'user_id', 'union_id', 'email', 'chat_id')
            content: 消息内容
        
        Returns:
            发送结果
        """
        return self._send_message(
            receive_id=receive_id,
            receive_type=receive_type,
            msg_type='text',
            content={'text': content}
        )
    
    def send_card_message(
        self,
        receive_id: str,
        receive_type: str,
        title: str,
        content: Dict,
        button: Optional[Dict] = None
    ) -> Dict:
        """
        发送卡片消息
        
        Args:
            receive_id: 接收者ID
            receive_type: 接收者类型
            title: 卡片标题
            content: 卡片内容
            button: 按钮配置
        
        Returns:
            发送结果
        """
        card_content = {
            "type": "template",
            "data": {
                "template_variable": {
                    "title": title,
                    **content
                }
            }
        }
        
        if button:
            card_content['data']['template_variable']['button'] = button
        
        return self._send_message(
            receive_id=receive_id,
            receive_type=receive_type,
            msg_type='interactive',
            content=card_content
        )
    
    def send_article_notification(
        self,
        receive_id: str,
        receive_type: str,
        articles: List[Dict],
        summary: str = ""
    ) -> Dict:
        """
        发送文章通知
        
        Args:
            receive_id: 接收者ID
            receive_type: 接收者类型
            articles: 文章列表
            summary: 摘要文本
        
        Returns:
            发送结果
        """
        # 构建消息内容
        content_lines = []
        
        if summary:
            content_lines.append(summary)
            content_lines.append("")
        
        content_lines.append("📚 最近收集的文章:")
        content_lines.append("")
        
        for i, article in enumerate(articles[:5], 1):
            title = article.get('title', '未命名')[:40]
            source = article.get('source', '未知来源')
            
            content_lines.append(f"{i}. {title}")
            content_lines.append(f"   来源: {source}")
            
            if article.get('link'):
                content_lines.append(f"   链接: {article['link']}")
            
            content_lines.append("")
        
        if len(articles) > 5:
            content_lines.append(f"... 还有 {len(articles) - 5} 篇文章")
        
        message = "\n".join(content_lines)
        
        return self.send_text_message(
            receive_id=receive_id,
            receive_type=receive_type,
            content=message
        )
    
    def send_daily_report(
        self,
        receive_id: str,
        receive_type: str,
        report_data: Dict
    ) -> Dict:
        """
        发送每日报告
        
        Args:
            receive_id: 接收者ID
            receive_type: 接收者类型
            report_data: 报告数据
        
        Returns:
            发送结果
        """
        # 构建报告消息
        lines = []
        
        lines.append("📊 每日文章收集报告")
        lines.append("=" * 40)
        lines.append("")
        lines.append(f"📅 时间周期: {report_data.get('period', '')}")
        lines.append(f"📝 收集数量: {report_data.get('total_count', 0)} 篇")
        lines.append("")
        
        # 精选文章
        if report_data.get('highlights'):
            lines.append("⭐ 精选文章:")
            lines.append("-" * 40)
            
            for i, article in enumerate(report_data['highlights'][:3], 1):
                title = article.get('title', '未命名')[:30]
                lines.append(f"{i}. {title}")
            
            lines.append("")
        
        # 分类统计
        if report_data.get('categories'):
            lines.append("📂 分类统计:")
            lines.append("-" * 40)
            
            for category, articles in list(report_data['categories'].items())[:5]:
                lines.append(f"• {category}: {len(articles)} 篇")
            
            lines.append("")
        
        # 查看链接
        if report_data.get('bitable_url'):
            lines.append(f"📎 查看详情: {report_data['bitable_url']}")
        
        message = "\n".join(lines)
        
        return self.send_text_message(
            receive_id=receive_id,
            receive_type=receive_type,
            content=message
        )
    
    def send_webhook_message(
        self,
        webhook_url: str,
        content: str
    ) -> Dict:
        """
        通过Webhook发送消息
        
        Args:
            webhook_url: Webhook URL
            content: 消息内容
        
        Returns:
            发送结果
        """
        try:
            data = {
                "msg_type": "text",
                "content": {
                    "text": content
                }
            }
            
            response = requests.post(webhook_url, json=data)
            result = response.json()
            
            return {
                'success': result.get('StatusCode') == 0,
                'result': result
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _send_message(
        self,
        receive_id: str,
        receive_type: str,
        msg_type: str,
        content: Dict
    ) -> Dict:
        """
        发送消息的核心方法
        
        Args:
            receive_id: 接收者ID
            receive_type: 接收者类型
            msg_type: 消息类型
            content: 消息内容
        
        Returns:
            发送结果
        """
        try:
            result = self.feishu.request(
                'POST',
                '/im/v1/messages',
                params={
                    'receive_id_type': receive_type
                },
                data={
                    'receive_id': receive_id,
                    'msg_type': msg_type,
                    'content': json.dumps(content)
                }
            )
            
            return {
                'success': result.get('code') == 0,
                'result': result
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }


def send_notification(
    receive_id: str,
    message: str,
    receive_type: str = 'email',
    webhook_url: Optional[str] = None
) -> bool:
    """
    发送通知的便捷函数
    
    Args:
        receive_id: 接收者ID（邮箱或open_id）
        message: 消息内容
        receive_type: 接收者类型
        webhook_url: Webhook URL（可选）
    
    Returns:
        是否成功
    """
    # 如果提供了webhook，使用webhook
    if webhook_url:
        from collector import FeishuClient
        feishu = FeishuClient()
        notifier = FeishuNotifier(feishu)
        result = notifier.send_webhook_message(webhook_url, message)
        return result['success']
    
    # 否则使用API发送
    from collector import FeishuClient
    
    feishu = FeishuClient()
    notifier = FeishuNotifier(feishu)
    
    # 如果是邮箱，转换为邮箱类型
    if '@' in receive_id:
        receive_type = 'email'
    
    result = notifier.send_text_message(
        receive_id=receive_id,
        receive_type=receive_type,
        content=message
    )
    
    return result['success']


def main():
    """测试消息推送"""
    import argparse
    
    parser = argparse.ArgumentParser(description='发送飞书消息')
    parser.add_argument('--receive-id', required=True, help='接收者ID')
    parser.add_argument('--receive-type', default='email', help='接收者类型')
    parser.add_argument('--message', required=True, help='消息内容')
    parser.add_argument('--webhook', help='Webhook URL')
    
    args = parser.parse_args()
    
    success = send_notification(
        receive_id=args.receive_id,
        message=args.message,
        receive_type=args.receive_type,
        webhook_url=args.webhook
    )
    
    if success:
        print("✓ 消息发送成功")
    else:
        print("✗ 消息发送失败")


if __name__ == '__main__':
    main()
