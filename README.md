# 微博/头条文章爬取工具

一个简单易用的 Python 爬虫工具，支持爬取微博单条内容、用户微博列表，以及头条文章/视频内容。

## ✨ 功能特性

- 🔍 **智能URL识别** - 自动识别微博/头条链接，无需手动选择平台
- 📝 **微博支持** - 单条微博详情、用户微博列表、转发微博、图片、视频
- 📰 **头条支持** - 文章详情、视频内容、阅读/评论/点赞数据
- 💾 **多种输出格式** - JSON（结构化数据）、TXT（纯文本阅读）
- 🛡️ **防封策略** - 随机延时、请求重试、真实浏览器请求头
- 🎯 **数据清洗** - 自动清理HTML标签，提取纯文本内容

## 📋 支持的链接格式

### 微博
- 单条微博：`https://weibo.com/用户ID/微博ID`
- 移动端详情：`https://m.weibo.cn/detail/微博ID`
- 用户主页：`https://weibo.com/u/用户ID`

### 头条
- 文章：`https://www.toutiao.com/article/文章ID/`
- 视频：`https://www.toutiao.com/video/视频ID/`

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install requests
```

### 2. 基础使用

```python
from crawler import CrawlerApp

# 创建爬虫实例
app = CrawlerApp()

# 爬取单条微博
result = app.crawl("https://m.weibo.cn/detail/1234567890")

# 爬取用户微博（默认3页）
posts = app.crawl("https://weibo.com/u/123456", max_pages=5)

# 爬取头条文章
article = app.crawl("https://www.toutiao.com/article/1234567890/")

# 保存结果
app.save_to_json(result, "output.json")
app.save_to_txt(result, "output.txt")
```

### 3. 命令行使用

```bash
# 爬取单条微博
python crawler.py "https://m.weibo.cn/detail/1234567890"

# 爬取用户微博（5页）
python crawler.py "https://weibo.com/u/123456" --max-pages 5

# 爬取头条文章
python crawler.py "https://www.toutiao.com/article/1234567890/"

# 指定输出文件名
python crawler.py "URL" -o my_result

# 只输出JSON
python crawler.py "URL" --format json
```

## 📊 数据结构

### 微博帖子 (WeiboPost)

```json
{
  "id": "1234567890",
  "content": "微博正文内容",
  "author": "用户名",
  "author_id": "123456",
  "created_at": "Mon Jan 01 12:00:00 +0800 2024",
  "reposts": 100,
  "comments": 50,
  "attitudes": 200,
  "source": "iPhone客户端",
  "pics": ["https://...", "https://..."],
  "video_url": "https://...",
  "is_repost": false,
  "original_post": null
}
```

### 头条文章 (ToutiaoArticle)

```json
{
  "id": "1234567890",
  "title": "文章标题",
  "content": "文章正文内容...",
  "author": "作者名",
  "author_id": "123456",
  "publish_time": "2024-01-01 12:00:00",
  "read_count": 10000,
  "comment_count": 100,
  "digg_count": 500,
  "url": "https://www.toutiao.com/article/1234567890/",
  "cover_image": "https://...",
  "images": ["https://..."],
  "video_url": null
}
```

## 🔧 高级用法

### 自定义请求配置

```python
from crawler import WeiboCrawler, ToutiaoCrawler

# 微博爬虫
weibo = WeiboCrawler()

# 爬取单条微博
post = weibo.crawl_single_post("https://m.weibo.cn/detail/1234567890")

# 爬取用户微博
posts = weibo.crawl_user_posts("https://weibo.com/u/123456", max_pages=5)

# 头条爬虫
toutiao = ToutiaoCrawler()

# 爬取文章
article = toutiao.crawl_article("https://www.toutiao.com/article/1234567890/")
```

### 批量处理

```python
from crawler import CrawlerApp

app = CrawlerApp()

urls = [
    "https://m.weibo.cn/detail/111",
    "https://m.weibo.cn/detail/222",
    "https://www.toutiao.com/article/333/",
]

for url in urls:
    result = app.crawl(url)
    if result:
        app.save_to_json(result, f"result_{url.split('/')[-1]}.json")
```

## ⚠️ 注意事项

1. **遵守法律法规** - 仅供学习研究使用，请勿用于商业用途
2. **尊重版权** - 爬取的内容版权归原作者所有
3. **控制频率** - 工具已内置随机延时，建议不要频繁爬取
4. **IP限制** - 频繁请求可能导致IP被暂时封禁
5. **内容变动** - 微博/头条的页面结构可能变化，如遇问题请提Issue

## 🐛 常见问题

### Q: 爬取失败，提示"无法从URL提取ID"

A: 请检查URL格式是否正确，支持的格式见上文。

### Q: 爬取用户微博时只能获取少量数据

A: 这是正常的，微博API对未登录用户有限制。如需更多数据，建议：
- 减少max_pages参数
- 增加请求间隔时间（修改代码中的sleep时间）

### Q: 头条文章爬取返回空内容

A: 头条页面结构较复杂，工具会尝试多种方式提取。如果都失败，可能是：
- 文章已被删除或下架
- 头条更新了页面结构

### Q: 如何爬取需要登录才能查看的内容？

A: 当前版本不支持登录功能。如需此功能，可以：
1. 使用Selenium等工具模拟浏览器登录
2. 手动获取Cookie后添加到请求头中

## 📄 许可证

MIT License

## 🤝 贡献

欢迎提交Issue和Pull Request！

## 📮 联系方式

如有问题或建议，请通过GitHub Issue联系。

---

**免责声明**：本工具仅供学习研究使用，使用者需自行承担使用风险。请遵守相关法律法规和平台服务条款。
