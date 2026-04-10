"""
文档格式化器 - 生成精美的飞书文档格式
"""

import re
from typing import Dict, List, Optional
from datetime import datetime


class DocumentFormatter:
    """文档格式化器"""
    
    def __init__(self):
        self.max_line_length = 80
    
    def format_article(self, article: Dict, style: str = 'standard') -> str:
        """
        格式化文章内容
        
        Args:
            article: 文章数据
            style: 格式风格 ('standard', 'card', 'newsletter')
        
        Returns:
            格式化的Markdown内容
        """
        if style == 'card':
            return self._format_card_style(article)
        elif style == 'newsletter':
            return self._format_newsletter_style(article)
        else:
            return self._format_standard_style(article)
    
    def _format_standard_style(self, article: Dict) -> str:
        """标准格式"""
        lines = []
        
        # 标题
        title = article.get('msg_title', '未命名文章')
        lines.append(f"# {title}")
        lines.append("")
        
        # 元信息
        lines.append("---")
        lines.append("")
        
        # 作者和来源
        meta_items = []
        if article.get('msg_author'):
            meta_items.append(f"**作者**: {article['msg_author']}")
        if article.get('account_name'):
            meta_items.append(f"**来源**: {article['account_name']}")
        
        if meta_items:
            lines.append(" | ".join(meta_items))
            lines.append("")
        
        # 时间信息
        time_items = []
        if article.get('msg_publish_time_str'):
            time_items.append(f"**发布时间**: {article['msg_publish_time_str']}")
        
        collect_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        time_items.append(f"**收集时间**: {collect_time}")
        
        lines.append(" | ".join(time_items))
        lines.append("")
        
        # 原文链接
        if article.get('msg_link'):
            lines.append(f"**原文链接**: [{article['msg_link'][:50]}...]({article['msg_link']})")
            lines.append("")
        
        # 分类标签
        if article.get('tags'):
            tags_str = " ".join([f"`{tag}`" for tag in article['tags']])
            lines.append(f"**标签**: {tags_str}")
            lines.append("")
        
        lines.append("---")
        lines.append("")
        
        # 摘要
        if article.get('msg_desc'):
            lines.append("## 📌 文章摘要")
            lines.append("")
            lines.append(f"> {article['msg_desc']}")
            lines.append("")
        
        # 正文
        if article.get('msg_content_text'):
            lines.append("## 📖 正文内容")
            lines.append("")
            content = self._format_content(article['msg_content_text'])
            lines.append(content)
        
        return "\n".join(lines)
    
    def _format_card_style(self, article: Dict) -> str:
        """卡片格式 - 适合快速浏览"""
        lines = []
        
        title = article.get('msg_title', '未命名文章')
        
        # 卡片头部
        lines.append("┌─────────────────────────────────────┐")
        lines.append(f"│ **{title[:30]}{'...' if len(title) > 30 else ''}**")
        lines.append("├─────────────────────────────────────┤")
        
        # 来源信息
        if article.get('account_name'):
            lines.append(f"│ 📰 {article['account_name']}")
        
        if article.get('msg_author'):
            lines.append(f"│ ✍️  {article['msg_author']}")
        
        if article.get('msg_publish_time_str'):
            lines.append(f"│ 🕒 {article['msg_publish_time_str']}")
        
        lines.append("├─────────────────────────────────────┤")
        
        # 摘要
        if article.get('msg_desc'):
            desc = article['msg_desc'][:100]
            lines.append(f"│ {desc}...")
        
        lines.append("└─────────────────────────────────────┘")
        
        # 标签
        if article.get('tags'):
            tags = " ".join([f"`{tag}`" for tag in article['tags'][:3]])
            lines.append(f"\n🏷️ {tags}")
        
        # 链接
        if article.get('msg_link'):
            lines.append(f"\n🔗 [阅读原文]({article['msg_link']})")
        
        return "\n".join(lines)
    
    def _format_newsletter_style(self, article: Dict) -> str:
        """Newsletter格式 - 适合定期推送"""
        lines = []
        
        title = article.get('msg_title', '未命名文章')
        
        # 标题带emoji
        lines.append(f"### 🔹 {title}")
        lines.append("")
        
        # 来源和时间
        source_info = []
        if article.get('account_name'):
            source_info.append(article['account_name'])
        if article.get('msg_publish_time_str'):
            source_info.append(article['msg_publish_time_str'][:10])
        
        if source_info:
            lines.append(f"*{' | '.join(source_info)}*")
            lines.append("")
        
        # 摘要
        if article.get('msg_desc'):
            lines.append(article['msg_desc'])
            lines.append("")
        
        # 标签
        if article.get('tags'):
            tags = " • ".join(article['tags'][:3])
            lines.append(f"🏷️ {tags}")
            lines.append("")
        
        # 链接
        if article.get('msg_link'):
            lines.append(f"[→ 阅读全文]({article['msg_link']})")
        
        lines.append("")
        lines.append("---")
        lines.append("")
        
        return "\n".join(lines)
    
    def _format_content(self, content: str) -> str:
        """格式化正文内容"""
        # 清理多余的空白
        content = re.sub(r'\n{3,}', '\n\n', content)
        
        # 段落分隔
        paragraphs = content.split('\n\n')
        
        formatted = []
        for para in paragraphs:
            para = para.strip()
            if para:
                # 如果段落太长，尝试分行
                if len(para) > self.max_line_length:
                    # 简单的分行处理（按句子）
                    sentences = re.split(r'([。！？\n])', para)
                    lines = []
                    current_line = ""
                    
                    for i in range(0, len(sentences), 2):
                        sentence = sentences[i]
                        if i + 1 < len(sentences):
                            sentence += sentences[i + 1]
                        
                        if len(current_line + sentence) > self.max_line_length:
                            if current_line:
                                lines.append(current_line)
                            current_line = sentence
                        else:
                            current_line += sentence
                    
                    if current_line:
                        lines.append(current_line)
                    
                    formatted.append('\n'.join(lines))
                else:
                    formatted.append(para)
        
        return '\n\n'.join(formatted)
    
    def create_summary_doc(
        self,
        articles: List[Dict],
        title: str = "文章汇总",
        period: str = ""
    ) -> str:
        """
        创建汇总文档
        
        Args:
            articles: 文章列表
            title: 文档标题
            period: 时间周期描述
        
        Returns:
            格式化的Markdown内容
        """
        lines = []
        
        # 标题
        lines.append(f"# {title}")
        lines.append("")
        
        if period:
            lines.append(f"**时间周期**: {period}")
            lines.append("")
        
        lines.append(f"**文章数量**: {len(articles)} 篇")
        lines.append("")
        lines.append("---")
        lines.append("")
        
        # 目录
        lines.append("## 📑 目录")
        lines.append("")
        
        for i, article in enumerate(articles, 1):
            title = article.get('msg_title', '未命名')[:40]
            category = article.get('primary_category', '未分类')
            lines.append(f"{i}. [{title}...](#article-{i}) - *{category}*")
        
        lines.append("")
        lines.append("---")
        lines.append("")
        
        # 文章详情
        lines.append("## 📚 文章详情")
        lines.append("")
        
        for i, article in enumerate(articles, 1):
            lines.append(f"### Article-{i}")
            lines.append("")
            lines.append(self._format_newsletter_style(article))
        
        return "\n".join(lines)


def main():
    """测试格式化器"""
    formatter = DocumentFormatter()
    
    # 测试文章
    test_article = {
        'msg_title': '人工智能的最新进展：GPT-5即将发布',
        'msg_author': '张三',
        'account_name': 'AI前沿观察',
        'msg_publish_time_str': '2025-01-17 10:30:00',
        'msg_desc': 'OpenAI正在开发下一代语言模型GPT-5，预计将在多个领域实现重大突破。',
        'msg_content_text': '人工智能技术正在快速发展。最新的GPT-5模型将具备更强的推理能力和创造力。' * 10,
        'msg_link': 'https://mp.weixin.qq.com/s/test123',
        'tags': ['AI', 'GPT', '人工智能', 'OpenAI'],
        'primary_category': '技术'
    }
    
    print("标准格式:")
    print("="*60)
    print(formatter.format_article(test_article, 'standard'))
    
    print("\n\n卡片格式:")
    print("="*60)
    print(formatter.format_article(test_article, 'card'))
    
    print("\n\nNewsletter格式:")
    print("="*60)
    print(formatter.format_article(test_article, 'newsletter'))


if __name__ == '__main__':
    main()
