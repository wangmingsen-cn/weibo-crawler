#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
使用示例：微博/头条爬取工具
"""

from crawler import CrawlerApp


def example_1_single_weibo():
    """示例1：爬取单条微博"""
    print("=" * 60)
    print("示例1：爬取单条微博")
    print("=" * 60)
    
    app = CrawlerApp()
    
    # 替换为实际的微博链接
    url = "https://m.weibo.cn/detail/1234567890"
    
    result = app.crawl(url)
    
    if result:
        print(f"\n✅ 成功获取微博")
        print(f"作者: {result.author}")
        print(f"内容: {result.content[:100]}...")
        print(f"转发: {result.reposts} | 评论: {result.comments} | 点赞: {result.attitudes}")
        
        # 保存结果
        app.save_to_json(result, "single_weibo.json")
        app.save_to_txt(result, "single_weibo.txt")
    else:
        print("❌ 爬取失败")


def example_2_user_posts():
    """示例2：爬取用户微博列表"""
    print("\n" + "=" * 60)
    print("示例2：爬取用户微博列表")
    print("=" * 60)
    
    app = CrawlerApp()
    
    # 替换为实际的用户主页链接
    url = "https://weibo.com/u/1234567890"
    
    # 爬取前3页
    posts = app.crawl(url, max_pages=3)
    
    if posts:
        print(f"\n✅ 成功获取 {len(posts)} 条微博")
        
        for i, post in enumerate(posts[:3], 1):
            print(f"\n【{i}】{post.author}")
            print(f"    {post.content[:80]}...")
            print(f"    转发:{post.reposts} 评论:{post.comments} 点赞:{post.attitudes}")
        
        # 保存结果
        app.save_to_json(posts, "user_posts.json")
        app.save_to_txt(posts, "user_posts.txt")
    else:
        print("❌ 爬取失败")


def example_3_toutiao_article():
    """示例3：爬取头条文章"""
    print("\n" + "=" * 60)
    print("示例3：爬取头条文章")
    print("=" * 60)
    
    app = CrawlerApp()
    
    # 替换为实际的头条文章链接
    url = "https://www.toutiao.com/article/1234567890/"
    
    result = app.crawl(url)
    
    if result:
        print(f"\n✅ 成功获取头条文章")
        print(f"标题: {result.title}")
        print(f"作者: {result.author}")
        print(f"阅读: {result.read_count} | 评论: {result.comment_count} | 点赞: {result.digg_count}")
        print(f"\n内容预览:\n{result.content[:200]}...")
        
        # 保存结果
        app.save_to_json(result, "toutiao_article.json")
        app.save_to_txt(result, "toutiao_article.txt")
    else:
        print("❌ 爬取失败")


def example_4_batch_crawl():
    """示例4：批量爬取多个链接"""
    print("\n" + "=" * 60)
    print("示例4：批量爬取多个链接")
    print("=" * 60)
    
    app = CrawlerApp()
    
    # 多个链接列表
    urls = [
        "https://m.weibo.cn/detail/1111111111",
        "https://m.weibo.cn/detail/2222222222",
        "https://www.toutiao.com/article/3333333333/",
    ]
    
    for i, url in enumerate(urls, 1):
        print(f"\n正在处理 [{i}/{len(urls)}]: {url}")
        result = app.crawl(url)
        
        if result:
            app.save_to_json(result, f"batch_result_{i}.json")
            print(f"  ✅ 成功保存")
        else:
            print(f"  ❌ 处理失败")


def example_5_custom_crawler():
    """示例5：使用特定爬虫类"""
    print("\n" + "=" * 60)
    print("示例5：使用特定爬虫类")
    print("=" * 60)
    
    from crawler import WeiboCrawler, ToutiaoCrawler
    
    # 微博爬虫
    weibo = WeiboCrawler()
    
    # 爬取单条微博
    post = weibo.crawl_single_post("https://m.weibo.cn/detail/1234567890")
    if post:
        print(f"\n✅ 微博: {post.content[:100]}...")
    
    # 头条爬虫
    toutiao = ToutiaoCrawler()
    
    # 爬取文章
    article = toutiao.crawl_article("https://www.toutiao.com/article/1234567890/")
    if article:
        print(f"\n✅ 头条: {article.title}")


if __name__ == '__main__':
    print("微博/头条爬取工具 - 使用示例")
    print("=" * 60)
    print("\n注意：请将示例中的URL替换为实际的链接")
    print("=" * 60)
    
    # 取消注释要运行的示例
    # example_1_single_weibo()
    # example_2_user_posts()
    # example_3_toutiao_article()
    # example_4_batch_crawl()
    # example_5_custom_crawler()
    
    print("\n请编辑此文件，取消注释要运行的示例函数")
