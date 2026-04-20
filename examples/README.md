# 使用示例

本文档展示微博/头条爬取工具的常见使用场景。

## 基础使用

### 1. 爬取单条微博

```bash
python crawler.py "https://m.weibo.cn/detail/1234567890"
```

输出文件：
- `crawl_result_20240101_120000.json` - 结构化数据
- `crawl_result_20240101_120000.txt` - 纯文本格式

### 2. 爬取用户微博

```bash
python crawler.py "https://weibo.com/u/123456" --max-pages 5
```

### 3. 爬取头条文章

```bash
python crawler.py "https://www.toutiao.com/article/1234567890/"
```

## Python API 使用

### 基础用法

```python
from crawler import CrawlerApp

app = CrawlerApp()

# 爬取并保存
result = app.crawl("https://m.weibo.cn/detail/1234567890")
app.save_to_json(result, "output.json")
app.save_to_txt(result, "output.txt")
```

### 批量处理

```python
urls = [
    "https://m.weibo.cn/detail/111",
    "https://m.weibo.cn/detail/222",
]

for url in urls:
    result = app.crawl(url)
    if result:
        app.save_to_json(result, f"{url.split('/')[-1]}.json")
```

## 更多示例

详见 `examples.py` 文件，包含：
- 单条微博爬取
- 用户微博列表爬取
- 头条文章爬取
- 批量爬取
- 自定义爬虫类使用
