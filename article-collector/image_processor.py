"""
图片处理器 - 下载和上传图片到飞书
"""

import os
import re
import requests
import tempfile
from typing import List, Dict, Optional
from io import BytesIO


class ImageProcessor:
    """图片处理器"""
    
    def __init__(self, feishu_client):
        self.feishu = feishu_client
    
    def extract_images_from_content(self, content: str) -> List[str]:
        """
        从HTML内容中提取所有图片URL
        
        Args:
            content: HTML内容
        
        Returns:
            图片URL列表
        """
        images = []
        
        # 提取 data-src
        images.extend(re.findall(r'data-src="(https?://[^"]+)"', content))
        
        # 提取 src
        images.extend(re.findall(r'src="(https?://[^"]+)"', content))
        
        # 去重
        images = list(set(images))
        
        # 过滤掉无效URL
        images = [img for img in images if img.startswith('http')]
        
        return images
    
    def download_image(self, url: str) -> Optional[bytes]:
        """
        下载图片
        
        Args:
            url: 图片URL
        
        Returns:
            图片二进制数据
        """
        try:
            # 处理URL中的HTML实体
            url = url.replace('&amp;', '&')
            
            response = requests.get(
                url,
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                },
                timeout=30
            )
            
            if response.status_code == 200:
                return response.content
            else:
                print(f"下载图片失败: HTTP {response.status_code}")
                return None
        except Exception as e:
            print(f"下载图片失败: {e}")
            return None
    
    def upload_image_to_feishu(
        self,
        image_data: bytes,
        file_name: str = "image.png",
        parent_type: str = "ccm_import_open",
        parent_node: str = ""
    ) -> Optional[Dict]:
        """
        上传图片到飞书
        
        Args:
            image_data: 图片二进制数据
            file_name: 文件名
            parent_type: 父节点类型
            parent_node: 父节点ID
        
        Returns:
            上传结果
        """
        try:
            # 获取token
            token = self.feishu.get_token()
            
            # 上传URL
            url = "https://open.feishu.cn/open-apis/drive/v1/medias/upload_all"
            
            # 准备文件
            files = {
                'file': (file_name, BytesIO(image_data), 'image/png')
            }
            
            # 准备数据
            data = {
                'file_name': file_name,
                'parent_type': parent_type,
                'parent_node': parent_node,
                'size': str(len(image_data))
            }
            
            # 发送请求
            headers = {
                'Authorization': f'Bearer {token}'
            }
            
            response = requests.post(url, files=files, data=data, headers=headers)
            result = response.json()
            
            if result.get('code') == 0:
                return result.get('data', {})
            else:
                print(f"上传图片失败: {result.get('msg')}")
                return None
        except Exception as e:
            print(f"上传图片失败: {e}")
            return None
    
    def process_article_images(
        self,
        content: str,
        max_images: int = 10
    ) -> List[Dict]:
        """
        处理文章中的所有图片
        
        Args:
            content: HTML内容
            max_images: 最多处理多少张图片
        
        Returns:
            图片信息列表
        """
        # 提取图片URL
        image_urls = self.extract_images_from_content(content)
        
        print(f"发现 {len(image_urls)} 张图片")
        
        results = []
        
        for i, url in enumerate(image_urls[:max_images], 1):
            print(f"正在处理第 {i}/{min(len(image_urls), max_images)} 张图片...")
            
            # 下载图片
            image_data = self.download_image(url)
            
            if image_data:
                # 上传到飞书
                file_name = f"image_{i}.png"
                upload_result = self.upload_image_to_feishu(image_data, file_name)
                
                if upload_result:
                    results.append({
                        'original_url': url,
                        'file_token': upload_result.get('file_token'),
                        'file_name': file_name,
                        'size': len(image_data)
                    })
                    print(f"✓ 图片 {i} 上传成功")
                else:
                    print(f"✗ 图片 {i} 上传失败")
            else:
                print(f"✗ 图片 {i} 下载失败")
        
        print(f"\n成功处理 {len(results)} 张图片")
        
        return results


def create_image_blocks(images: List[Dict]) -> List[Dict]:
    """
    创建飞书文档图片块
    
    Args:
        images: 图片信息列表
    
    Returns:
        飞书文档块列表
    """
    blocks = []
    
    for img in images:
        if img.get('file_token'):
            blocks.append({
                'block_type': 4,  # image
                'image': {
                    'token': img['file_token'],
                    'width': 600,
                    'height': 400
                }
            })
    
    return blocks


def main():
    """测试图片处理"""
    import sys
    sys.path.insert(0, '/workspace/article-collector')
    from dotenv import load_dotenv
    load_dotenv('/workspace/article-collector/.env')
    from collector import FeishuClient
    
    # 测试内容
    test_content = '''
    <img data-src="https://example.com/image1.jpg">
    <img src="https://example.com/image2.jpg">
    '''
    
    feishu = FeishuClient()
    processor = ImageProcessor(feishu)
    
    # 提取图片URL
    images = processor.extract_images_from_content(test_content)
    print(f"提取到 {len(images)} 张图片")
    
    for i, img in enumerate(images, 1):
        print(f"{i}. {img}")


if __name__ == '__main__':
    main()
