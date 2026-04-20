#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
微博/头条文章爬取工具
支持：微博单条/用户、头条文章/视频
作者：王明森
版本：1.0.0
"""

import re
import json
import time
import random
import hashlib
import urllib.parse
from datetime import datetime
from typing import Optional, Dict, List, Union
from dataclasses import dataclass, asdict

# 尝试导入requests，如果没有则提示安装
try:
    import requests
    from requests.adapters import HTTPAdapter
    from urllib3.util.retry import Retry
except ImportError:
    print("请先安装依赖: pip install requests")
    raise


@dataclass
class WeiboPost:
    """微博帖子数据结构"""
    id: str
    content: str
    author: str
    author_id: str
    created_at: str
    reposts: int
    comments: int
    attitudes: int
    source: str
    pics: List[str]
    video_url: Optional[str] = None
    is_repost: bool = False
    original_post: Optional[Dict] = None
    
    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class ToutiaoArticle:
    """头条文章数据结构"""
    id: str
    title: str
    content: str
    author: str
    author_id: str
    publish_time: str
    read_count: int
    comment_count: int
    digg_count: int
    url: str
    cover_image: Optional[str] = None
    images: List[str] = None
    video_url: Optional[str] = None
    
    def __post_init__(self):
        if self.images is None:
            self.images = []
    
    def to_dict(self) -> Dict:
        return asdict(self)


class BaseCrawler:
    """基础爬虫类"""
    
    def __init__(self):
        self.session = requests.Session()
        self._setup_session()
        
    def _setup_session(self):
        """配置请求会话"""
        # 设置重试策略
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        # 设置通用请求头
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
        })
    
    def _random_sleep(self, min_sec: float = 1.0, max_sec: float = 3.0):
        """随机延时，避免请求过快"""
        time.sleep(random.uniform(min_sec, max_sec))
    
    def _extract_json_from_html(self, html: str, pattern: str) -> Optional[Dict]:
        """从HTML中提取JSON数据"""
        match = re.search(pattern, html, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(1))
            except json.JSONDecodeError:
                return None
        return None


class WeiboCrawler(BaseCrawler):
    """微博爬虫"""
    
    BASE_URL = "https://weibo.com"
    MOBILE_URL = "https://m.weibo.cn"
    
    def __init__(self):
        super().__init__()
        self.session.headers.update({
            'Referer': 'https://weibo.com/',
        })
    
    def _extract_mid_from_url(self, url: str) -> Optional[str]:
        """从微博URL中提取mid"""
        # 支持格式：
        # https://weibo.com/123456/abcdef
        # https://m.weibo.cn/detail/123456
        # https://weibo.com/123456/abcdef?type=comment
        patterns = [
            r'weibo\.com/\d+/(\w+)',
            r'm\.weibo\.cn/detail/(\d+)',
            r'm\.weibo\.cn/status/(\w+)',
        ]
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None
    
    def _extract_uid_from_url(self, url: str) -> Optional[str]:
        """从用户主页URL中提取uid"""
        patterns = [
            r'weibo\.com/u/(\d+)',
            r'weibo\.com/(\d+)',
            r'm\.weibo\.cn/u/(\d+)',
        ]
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None
    
    def crawl_single_post(self, url: str) -> Optional[WeiboPost]:
        """
        爬取单条微博
        
        Args:
            url: 微博链接
            
        Returns:
            WeiboPost对象或None
        """
        mid = self._extract_mid_from_url(url)
        if not mid:
            print(f"无法从URL提取微博ID: {url}")
            return None
        
        print(f"正在爬取微博: {mid}")
        
        # 尝试移动端API
        api_url = f"{self.MOBILE_URL}/statuses/show?id={mid}"
        
        try:
            self._random_sleep()
            response = self.session.get(api_url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            if data.get('ok') != 1:
                print(f"API返回错误: {data.get('msg', '未知错误')}")
                return None
            
            post_data = data.get('data', {})
            return self._parse_weibo_post(post_data)
            
        except requests.RequestException as e:
            print(f"请求失败: {e}")
            return None
        except json.JSONDecodeError as e:
            print(f"JSON解析失败: {e}")
            return None
    
    def crawl_user_posts(self, url: str, max_pages: int = 3) -> List[WeiboPost]:
        """
        爬取用户微博列表
        
        Args:
            url: 用户主页链接
            max_pages: 最大爬取页数
            
        Returns:
            WeiboPost列表
        """
        uid = self._extract_uid_from_url(url)
        if not uid:
            print(f"无法从URL提取用户ID: {url}")
            return []
        
        print(f"正在爬取用户微博: uid={uid}")
        posts = []
        
        # 移动端用户微博API
        containerid = f"107603{uid}"
        
        for page in range(1, max_pages + 1):
            api_url = f"{self.MOBILE_URL}/api/container/getIndex"
            params = {
                'type': 'uid',
                'value': uid,
                'containerid': containerid,
                'page': page,
            }
            
            try:
                self._random_sleep(2, 4)
                response = self.session.get(api_url, params=params, timeout=10)
                response.raise_for_status()
                
                data = response.json()
                if data.get('ok') != 1:
                    print(f"第{page}页API返回错误")
                    break
                
                cards = data.get('data', {}).get('cards', [])
                if not cards:
                    print(f"第{page}页无数据")
                    break
                
                for card in cards:
                    if card.get('card_type') == 9:  # 微博卡片
                        mblog = card.get('mblog', {})
                        post = self._parse_weibo_post(mblog)
                        if post:
                            posts.append(post)
                
                print(f"第{page}页爬取完成，当前共{len(posts)}条")
                
            except requests.RequestException as e:
                print(f"第{page}页请求失败: {e}")
                break
            except Exception as e:
                print(f"第{page}页处理失败: {e}")
                continue
        
        return posts
    
    def _parse_weibo_post(self, data: Dict) -> Optional[WeiboPost]:
        """解析微博数据"""
        try:
            # 处理转发微博
            is_repost = False
            original_post = None
            retweeted = data.get('retweeted_status')
            
            if retweeted:
                is_repost = True
                original_post = self._parse_weibo_post(retweeted)
                if original_post:
                    original_post = original_post.to_dict()
            
            # 提取图片
            pics = []
            pic_infos = data.get('pic_infos', {})
            if pic_infos:
                for pic_id, pic_info in pic_infos.items():
                    # 优先获取大图
                    large_url = pic_info.get('large', {}).get('url')
                    if large_url:
                        pics.append(large_url)
                    else:
                        # 回退到原图
                        original_url = pic_info.get('original', {}).get('url')
                        if original_url:
                            pics.append(original_url)
            
            # 提取视频
            video_url = None
            page_info = data.get('page_info', {})
            if page_info.get('type') == 'video':
                media_info = page_info.get('media_info', {})
                # 优先获取高清视频
                for quality in ['stream_url_hd', 'stream_url', 'mp4_hd_url', 'mp4_url']:
                    video_url = media_info.get(quality)
                    if video_url:
                        break
            
            return WeiboPost(
                id=str(data.get('id', '')),
                content=self._clean_text(data.get('text', '')),
                author=data.get('user', {}).get('screen_name', '未知用户'),
                author_id=str(data.get('user', {}).get('id', '')),
                created_at=data.get('created_at', ''),
                reposts=int(data.get('reposts_count', 0) or 0),
                comments=int(data.get('comments_count', 0) or 0),
                attitudes=int(data.get('attitudes_count', 0) or 0),
                source=data.get('source', ''),
                pics=pics,
                video_url=video_url,
                is_repost=is_repost,
                original_post=original_post,
            )
        except Exception as e:
            print(f"解析微博数据失败: {e}")
            return None
    
    def _clean_text(self, text: str) -> str:
        """清理文本中的HTML标签"""
        # 移除HTML标签
        text = re.sub(r'<[^>]+>', '', text)
        # 解码HTML实体
        text = text.replace('&quot;', '"')
        text = text.replace('&amp;', '&')
        text = text.replace('&lt;', '<')
        text = text.replace('&gt;', '>')
        text = text.replace('&nbsp;', ' ')
        return text.strip()


class ToutiaoCrawler(BaseCrawler):
    """头条爬虫"""
    
    BASE_URL = "https://www.toutiao.com"
    
    def __init__(self):
        super().__init__()
        self.session.headers.update({
            'Referer': 'https://www.toutiao.com/',
        })
    
    def _extract_item_id_from_url(self, url: str) -> Optional[str]:
        """从头条URL中提取item_id"""
        # 支持格式：
        # https://www.toutiao.com/article/1234567890/
        # https://www.toutiao.com/a1234567890/
        # https://www.toutiao.com/video/1234567890/
        patterns = [
            r'toutiao\.com/article/(\d+)',
            r'toutiao\.com/a(\d+)',
            r'toutiao\.com/video/(\d+)',
            r'toutiao\.com/item/(\d+)',
        ]
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None
    
    def crawl_article(self, url: str) -> Optional[ToutiaoArticle]:
        """
        爬取头条文章/视频
        
        Args:
            url: 头条文章链接
            
        Returns:
            ToutiaoArticle对象或None
        """
        item_id = self._extract_item_id_from_url(url)
        if not item_id:
            print(f"无法从URL提取文章ID: {url}")
            return None
        
        print(f"正在爬取头条文章: {item_id}")
        
        try:
            self._random_sleep()
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            
            html = response.text
            
            # 尝试多种方式提取数据
            article = self._extract_from_ld_json(html, url)
            if article:
                return article
            
            article = self._extract_from_render_data(html, url)
            if article:
                return article
            
            article = self._extract_from_initial_state(html, url)
            if article:
                return article
            
            print("无法从页面提取文章数据")
            return None
            
        except requests.RequestException as e:
            print(f"请求失败: {e}")
            return None
    
    def _extract_from_ld_json(self, html: str, url: str) -> Optional[ToutiaoArticle]:
        """从LD+JSON中提取文章数据"""
        pattern = r'<script type="application/ld\+json">(.*?)</script>'
        matches = re.findall(pattern, html, re.DOTALL)
        
        for match in matches:
            try:
                data = json.loads(match)
                if data.get('@type') in ['NewsArticle', 'Article', 'VideoObject']:
                    return ToutiaoArticle(
                        id=self._extract_item_id_from_url(url) or '',
                        title=data.get('headline', ''),
                        content=data.get('articleBody', ''),
                        author=data.get('author', {}).get('name', '未知作者'),
                        author_id='',
                        publish_time=data.get('datePublished', ''),
                        read_count=0,
                        comment_count=int(data.get('commentCount', 0) or 0),
                        digg_count=0,
                        url=url,
                        cover_image=data.get('image', [None])[0] if isinstance(data.get('image'), list) else data.get('image'),
                    )
            except (json.JSONDecodeError, KeyError):
                continue
        return None
    
    def _extract_from_render_data(self, html: str, url: str) -> Optional[ToutiaoArticle]:
        """从SSR渲染数据中提取"""
        pattern = r'<script>window\._SSR_HYDRATED_DATA=(.*?)</script>'
        data = self._extract_json_from_html(html, pattern)
        
        if data:
            try:
                article_data = data.get('Article', {})
                if not article_data:
                    article_data = data.get('Video', {})
                
                if article_data:
                    content = article_data.get('content', '')
                    # 清理内容中的HTML
                    content = re.sub(r'<[^>]+>', '', content)
                    
                    return ToutiaoArticle(
                        id=str(article_data.get('item_id', '')),
                        title=article_data.get('title', ''),
                        content=content,
                        author=article_data.get('source', '未知作者'),
                        author_id=str(article_data.get('creator_uid', '')),
                        publish_time=article_data.get('publish_time', ''),
                        read_count=int(article_data.get('read_count', 0) or 0),
                        comment_count=int(article_data.get('comment_count', 0) or 0),
                        digg_count=int(article_data.get('digg_count', 0) or 0),
                        url=url,
                        cover_image=article_data.get('cover_image', ''),
                        images=article_data.get('image_list', []),
                        video_url=article_data.get('video_play_info', {}).get('url') if article_data.get('video_play_info') else None,
                    )
            except Exception as e:
                print(f"解析SSR数据失败: {e}")
        return None
    
    def _extract_from_initial_state(self, html: str, url: str) -> Optional[ToutiaoArticle]:
        """从INITIAL_STATE中提取"""
        pattern = r'<script>window\.__INITIAL_STATE__=(.*?);\(function\(\)'
        data = self._extract_json_from_html(html, pattern)
        
        if data:
            try:
                article = data.get('article', {})
                if article:
                    content = article.get('content', '')
                    content = re.sub(r'<[^>]+>', '', content)
                    
                    return ToutiaoArticle(
                        id=str(article.get('item_id', '')),
                        title=article.get('title', ''),
                        content=content,
                        author=article.get('source', '未知作者'),
                        author_id='',
                        publish_time=article.get('publish_time', ''),
                        read_count=int(article.get('read_count', 0) or 0),
                        comment_count=int(article.get('comment_count', 0) or 0),
                        digg_count=int(article.get('digg_count', 0) or 0),
                        url=url,
                        cover_image=article.get('cover_image', ''),
                    )
            except Exception as e:
                print(f"解析INITIAL_STATE失败: {e}")
        return None


class CrawlerApp:
    """爬虫应用主类"""
    
    def __init__(self):
        self.weibo_crawler = WeiboCrawler()
        self.toutiao_crawler = ToutiaoCrawler()
    
    def crawl(self, url: str, **kwargs) -> Union[WeiboPost, ToutiaoArticle, List[WeiboPost], None]:
        """
        智能识别URL类型并爬取
        
        Args:
            url: 微博或头条链接
            **kwargs: 额外参数（如max_pages）
            
        Returns:
            爬取结果
        """
        url = url.strip()
        
        # 识别微博链接
        if 'weibo.com' in url or 'm.weibo.cn' in url:
            # 判断是单条微博还是用户主页
            if '/u/' in url or re.search(r'weibo\.com/\d+$', url):
                # 用户主页
                max_pages = kwargs.get('max_pages', 3)
                return self.weibo_crawler.crawl_user_posts(url, max_pages)
            else:
                # 单条微博
                return self.weibo_crawler.crawl_single_post(url)
        
        # 识别头条链接
        elif 'toutiao.com' in url:
            return self.toutiao_crawler.crawl_article(url)
        
        else:
            print(f"不支持的URL: {url}")
            print("支持的链接格式:")
            print("  微博: https://weibo.com/xxx/xxx 或 https://m.weibo.cn/detail/xxx")
            print("  头条: https://www.toutiao.com/article/xxx")
            return None
    
    def save_to_json(self, data: Union[WeiboPost, ToutiaoArticle, List], filename: str):
        """保存数据到JSON文件"""
        if isinstance(data, list):
            json_data = [item.to_dict() if hasattr(item, 'to_dict') else item for item in data]
        elif hasattr(data, 'to_dict'):
            json_data = data.to_dict()
        else:
            json_data = data
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, ensure_ascii=False, indent=2)
        
        print(f"数据已保存到: {filename}")
    
    def save_to_txt(self, data: Union[WeiboPost, ToutiaoArticle, List], filename: str):
        """保存数据到TXT文件（纯文本格式）"""
        with open(filename, 'w', encoding='utf-8') as f:
            if isinstance(data, list):
                for i, item in enumerate(data, 1):
                    f.write(f"{'='*60}\n")
                    f.write(f"【{i}】{self._format_item_text(item)}\n\n")
            else:
                f.write(self._format_item_text(data))
        
        print(f"数据已保存到: {filename}")
    
    def _format_item_text(self, item) -> str:
        """格式化项目为文本"""
        if isinstance(item, WeiboPost):
            lines = [
                f"微博ID: {item.id}",
                f"作者: {item.author}",
                f"发布时间: {item.created_at}",
                f"内容:\n{item.content}",
                f"",
                f"转发: {item.reposts} | 评论: {item.comments} | 点赞: {item.attitudes}",
                f"来源: {item.source}",
            ]
            if item.pics:
                lines.append(f"图片: {len(item.pics)}张")
            if item.video_url:
                lines.append(f"视频: {item.video_url}")
            if item.is_repost and item.original_post:
                lines.append(f"\n【原微博】")
                lines.append(f"作者: {item.original_post.get('author', '')}")
                lines.append(f"内容: {item.original_post.get('content', '')[:100]}...")
            return '\n'.join(lines)
        
        elif isinstance(item, ToutiaoArticle):
            lines = [
                f"标题: {item.title}",
                f"作者: {item.author}",
                f"发布时间: {item.publish_time}",
                f"阅读: {item.read_count} | 评论: {item.comment_count} | 点赞: {item.digg_count}",
                f"",
                f"内容:\n{item.content[:500]}..." if len(item.content) > 500 else f"内容:\n{item.content}",
                f"",
                f"链接: {item.url}",
            ]
            if item.video_url:
                lines.append(f"视频: {item.video_url}")
            return '\n'.join(lines)
        
        return str(item)


def main():
    """命令行入口"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='微博/头条文章爬取工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
示例:
  python crawler.py "https://weibo.com/123456/abcdef"
  python crawler.py "https://m.weibo.cn/detail/1234567890"
  python crawler.py "https://weibo.com/u/123456" --max-pages 5
  python crawler.py "https://www.toutiao.com/article/1234567890/"
  python crawler.py "https://www.toutiao.com/video/1234567890/"
        '''
    )
    
    parser.add_argument('url', help='要爬取的链接')
    parser.add_argument('-o', '--output', help='输出文件名（不含扩展名）')
    parser.add_argument('--max-pages', type=int, default=3, 
                        help='爬取用户微博时的最大页数（默认3页）')
    parser.add_argument('--format', choices=['json', 'txt', 'both'], default='both',
                        help='输出格式（默认both）')
    
    args = parser.parse_args()
    
    # 创建输出文件名
    if not args.output:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        args.output = f"crawl_result_{timestamp}"
    
    # 执行爬取
    app = CrawlerApp()
    result = app.crawl(args.url, max_pages=args.max_pages)
    
    if result:
        # 保存结果
        if args.format in ['json', 'both']:
            app.save_to_json(result, f"{args.output}.json")
        
        if args.format in ['txt', 'both']:
            app.save_to_txt(result, f"{args.output}.txt")
        
        # 打印摘要
        if isinstance(result, list):
            print(f"\n✅ 成功爬取 {len(result)} 条数据")
        else:
            print(f"\n✅ 成功爬取数据")
    else:
        print("\n❌ 爬取失败")
        return 1
    
    return 0


if __name__ == '__main__':
    exit(main())
