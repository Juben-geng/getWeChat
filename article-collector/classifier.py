"""
文章分类器 - 基于关键词和规则的智能分类
"""

import re
from typing import List, Dict, Set
from collections import defaultdict


class ArticleClassifier:
    """文章自动分类器"""
    
    def __init__(self):
        # 预定义分类及其关键词
        self.categories = {
            '技术': {
                'keywords': [
                    'AI', '人工智能', '机器学习', '深度学习', 'GPT', 'ChatGPT',
                    'Python', 'Java', 'JavaScript', 'Go', 'Rust', '编程', '代码',
                    '前端', '后端', '全栈', '架构', '微服务', '容器', 'Docker', 'K8s',
                    '算法', '数据结构', '区块链', 'Web3', '云计算', '大数据',
                    'API', 'SDK', '框架', '开源', 'GitHub', 'Git'
                ],
                'weight': 1.0
            },
            '产品': {
                'keywords': [
                    '产品经理', '产品思维', '用户体验', 'UX', 'UI设计',
                    '需求分析', '竞品分析', '产品迭代', 'MVP', '用户调研',
                    '产品策略', '产品规划', '功能设计', '交互设计'
                ],
                'weight': 1.0
            },
            '运营': {
                'keywords': [
                    '运营', '增长黑客', '用户增长', '转化率', '留存率',
                    'SEO', 'SEM', 'ASO', '新媒体运营', '社群运营',
                    '内容运营', '活动运营', '数据分析', 'GMV', 'DAU', 'MAU'
                ],
                'weight': 1.0
            },
            '设计': {
                'keywords': [
                    '设计', 'UI', 'UX', '视觉设计', '交互设计', '平面设计',
                    'Figma', 'Sketch', 'Adobe', '配色', '排版', '字体',
                    '设计系统', '设计规范', '用户体验设计'
                ],
                'weight': 1.0
            },
            '商业': {
                'keywords': [
                    '商业模式', '创业', '融资', '投资', 'IPO', '上市',
                    '商业计划', 'BP', '估值', '股权', '期权', '合伙人',
                    '企业管理', '战略', '市场分析', '行业报告'
                ],
                'weight': 1.0
            },
            '职场': {
                'keywords': [
                    '职场', '面试', '简历', '薪资', '晋升', '跳槽',
                    '团队管理', '领导力', '沟通技巧', '时间管理',
                    '工作效率', '职业规划', '个人成长'
                ],
                'weight': 1.0
            },
            '生活': {
                'keywords': [
                    '生活', '健康', '运动', '美食', '旅行', '摄影',
                    '读书', '电影', '音乐', '游戏', '心理', '情感'
                ],
                'weight': 1.0
            },
            '金融': {
                'keywords': [
                    '金融', '理财', '基金', '股票', '投资', '理财',
                    '银行', '保险', '贷款', '征信', '资产配置',
                    '财务自由', '复利', '定投'
                ],
                'weight': 1.0
            },
            '教育': {
                'keywords': [
                    '教育', '学习', '课程', '培训', '考试', '考研',
                    '留学', '在线教育', '知识付费', '技能提升'
                ],
                'weight': 1.0
            },
            '科技资讯': {
                'keywords': [
                    '科技', '数码', '手机', '电脑', '新品发布', '评测',
                    '苹果', '华为', '小米', '特斯拉', '电动车', '智能家居'
                ],
                'weight': 1.0
            }
        }
        
        # 编译正则表达式以提高性能
        self._compile_patterns()
    
    def _compile_patterns(self):
        """编译正则表达式模式"""
        self.category_patterns = {}
        for category, config in self.categories.items():
            patterns = []
            for keyword in config['keywords']:
                # 不区分大小写匹配
                pattern = re.compile(re.escape(keyword), re.IGNORECASE)
                patterns.append(pattern)
            self.category_patterns[category] = patterns
    
    def classify(self, title: str, content: str = '', description: str = '') -> Dict:
        """
        对文章进行分类
        
        Args:
            title: 文章标题
            content: 文章内容
            description: 文章摘要
            
        Returns:
            {
                'primary_category': '主要分类',
                'categories': ['分类1', '分类2'],
                'scores': {'分类': 分数},
                'tags': ['标签1', '标签2']
            }
        """
        # 合并文本用于分析
        text = f"{title} {description} {content[:2000]}"  # 限制内容长度
        
        # 计算每个分类的得分
        scores = defaultdict(float)
        matched_keywords = defaultdict(list)
        
        for category, patterns in self.category_patterns.items():
            for pattern in patterns:
                matches = pattern.findall(text)
                if matches:
                    # 根据匹配次数和关键词权重计算得分
                    score = len(matches) * self.categories[category]['weight']
                    scores[category] += score
                    matched_keywords[category].extend(matches)
        
        # 排序分类
        sorted_categories = sorted(
            scores.items(), 
            key=lambda x: x[1], 
            reverse=True
        )
        
        # 提取标签（从匹配的关键词中去重）
        all_keywords = []
        for keywords in matched_keywords.values():
            all_keywords.extend(keywords)
        
        # 去重并保留前5个
        tags = list(set(all_keywords))[:5]
        
        # 确定主要分类和次要分类
        if sorted_categories:
            primary_category = sorted_categories[0][0]
            # 得分超过主要分类50%的也作为相关分类
            categories = [cat for cat, score in sorted_categories[:3] 
                         if score >= sorted_categories[0][1] * 0.3]
        else:
            primary_category = '其他'
            categories = ['其他']
        
        return {
            'primary_category': primary_category,
            'categories': categories,
            'scores': dict(scores),
            'tags': tags
        }
    
    def add_custom_category(self, name: str, keywords: List[str], weight: float = 1.0):
        """
        添加自定义分类
        
        Args:
            name: 分类名称
            keywords: 关键词列表
            weight: 权重
        """
        self.categories[name] = {
            'keywords': keywords,
            'weight': weight
        }
        
        # 重新编译模式
        patterns = []
        for keyword in keywords:
            pattern = re.compile(re.escape(keyword), re.IGNORECASE)
            patterns.append(pattern)
        self.category_patterns[name] = patterns
    
    def get_all_categories(self) -> List[str]:
        """获取所有分类名称"""
        return list(self.categories.keys())


def main():
    """测试分类器"""
    classifier = ArticleClassifier()
    
    # 测试用例
    test_cases = [
        {
            'title': 'ChatGPT背后的人工智能技术原理深度解析',
            'description': '本文深入探讨GPT模型的架构和训练方法',
            'content': '人工智能 GPT 语言模型 深度学习...'
        },
        {
            'title': '产品经理必读：如何做好用户需求分析',
            'description': '分享产品需求分析的方法论和实践经验',
            'content': '产品经理 需求分析 用户调研...'
        },
        {
            'title': '2024年最值得投资的10只基金',
            'description': '基金投资策略和推荐',
            'content': '基金 投资 理财 收益...'
        }
    ]
    
    for i, case in enumerate(test_cases, 1):
        print(f"\n{'='*60}")
        print(f"测试用例 {i}: {case['title']}")
        print('='*60)
        
        result = classifier.classify(
            title=case['title'],
            description=case['description'],
            content=case['content']
        )
        
        print(f"主要分类: {result['primary_category']}")
        print(f"相关分类: {', '.join(result['categories'])}")
        print(f"标签: {', '.join(result['tags'])}")
        print(f"\n分类得分:")
        for cat, score in sorted(result['scores'].items(), key=lambda x: x[1], reverse=True):
            print(f"  {cat}: {score}")


if __name__ == '__main__':
    main()
