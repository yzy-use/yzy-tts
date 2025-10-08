import re
from typing import Any

# 替换特殊符号
def replace_symbols_with_space(text):
    # 定义要替换的符号模式
    pattern = r'[@#$%^&*＊()~`;:\'_<>\/]'
    # 使用正则表达式替换为空格
    result = re.sub(pattern, ' ', text)
    return result

# 将文本按 "第.*章" 分割成列表，保留章节标题
def split_text_by_chapters(text):
    """
    将文本按 "第.*章" 分割成列表，保留章节标题

    Args:
        text (str): 输入的长文本（如小说内容）

    Returns:
        list: 结构示例：
            [
                {"title": "第1章 开端", "content": "这是第一章的内容..."},
                {"title": "第2章 发展", "content": "这是第二章的内容..."},
                ...
            ]
            如果无章节，返回 [{"title": "", "content": "全文内容"}]
    """
    # 使用正则表达式匹配 "第.*章" 及其后的内容（非贪婪模式）
    # 数字 [零一二三四五六七八九十百\d]+

    pattern = r'(第[零一二三四五六七八九十百\d]+[卷章节集][^\n\r]*)'
    # pattern = r'(【[\d]+】[^\n\r]*)'
    chapters = re.split(pattern, text)

    # 处理分割结果
    result = []
    for i in range(1, len(chapters), 2):
        # title = chapters[i].strip()
        sp = chapters[i].strip().split()
        sp[0] = convert_chinese_number(sp[0])
        title = ' '.join(sp)
        content = chapters[i + 1].strip() if i + 1 < len(chapters) else ""
        result.append({"title": title, "content": title + "\n" + content})

    # 如果没有章节，返回全文

    if not result:
        result.append({"title": "全文", "content": text.strip()})

    return result

# 合并章节文本，每段不超过指定长度，并标注章节范围
def merge_chapters_with_limit(chapters, max_length=23000):
    """
    合并章节文本，每段不超过指定长度，并标注章节范围

    Args:
        chapters (list): 结构如 [{"title": "第1章", "content": "..."}, ...]
        max_length (int): 单段最大字符数（默认25000）

    Returns:
        list: 合并后的段落，结构示例：
            [
                {
                    "name": "第1章-第3章",
                    "content": "合并后的文本..."
                },
                {
                    "name": "第4章-第5章",
                    "content": "另一段合并文本..."
                }
            ]
    """
    merged = []
    current_chunk = []
    current_length = 0
    start_chapter = chapters[0]["title"] if chapters else ""

    for chapter in chapters:
        chapter_content = chapter["content"]
        chapter_length = len(chapter_content)

        # 如果当前块不为空且加入新章节后超限，则保存当前块
        if current_chunk and current_length + chapter_length > max_length:
            end_chapter = current_chunk[-1]["title"]
            merged.append({
                "name": f"{start_chapter}-{end_chapter}",
                "content": "\n\n".join([chap["content"] for chap in current_chunk])
            })
            # 重置当前块
            current_chunk = [chapter]
            current_length = chapter_length
            start_chapter = chapter["title"]
        else:
            current_chunk.append(chapter)
            current_length += chapter_length

    # 添加最后一块
    if current_chunk:
        end_chapter = current_chunk[-1]["title"]
        merged.append({
            "name": f"{start_chapter}-{end_chapter}",
            "content": "\n\n".join([chap["content"] for chap in current_chunk])
        })

    return merged


# 生成与 merge_chapters_with_limit 相同的分段，但将 content 转为 HTML 结构
def merge_chapters_with_limit_html(chapters, max_length=23000):
    """
    基于 merge_chapters_with_limit 的合并规则，输出每段的 HTML 内容。

    返回结构：[{"name": "第1章-第3章", "content": "<html>..."}, ...]
    HTML 模板示例：
    <html >
    <head>
    	<h2 style="padding: 0;margin: 0;">title内容</h2>
        <div style="white-space: break-spaces;">\tcontent内容<div>
    </body>
    </html>
    """
    merged = merge_chapters_with_limit(chapters, max_length)
    html_chunks = []
    for item in merged:
        range_title = item.get("name", "")
        body = item.get("content", "")

        # 将合并后的 body 再次按章节切分，确保每个章节标题都是 <h2>
        pattern = r'(第[零一二三四五六七八九十百\d]+[卷章节集][^\n\r]*)'
        parts = re.split(pattern, body)

        sections_html = []
        for i in range(1, len(parts), 2):
            chap_title = parts[i].strip()
            chap_content = parts[i + 1].strip() if i + 1 < len(parts) else ""
            sections_html.append(
                "    <h1>" + chap_title + "</h1>\n" +
                "    <div class=\"content\">" + chap_content + "</div>\n"
            )

        # 如果没有匹配到章节标题，则整体作为一段内容输出
        if not sections_html and body.strip():
            sections_html.append(
                "    <div class=\"content\">" + body.strip() + "</div>\n"
            )

        html = (
            "<!DOCTYPE html>\n"
            "<html>\n"
            "<head>\n"
            "    <meta charset=\"utf-8\" />\n"
            "    <style>\n"
            "        body {background-color: #cce8cf; margin: 0; padding: 20px;}\n"
            "        .content { white-space: break-spaces; text-indent: 2em; font-size: 24px; margin-bottom: 20px;}\n"
            "        h1 { color: #2c5530; margin: 20px 0; text-align: center; }\n"
            "        .pagination { position: fixed; bottom: 20px; left: 50%; transform: translateX(-50%); background: rgba(255,255,255,0.9); padding: 10px; border-radius: 5px; }\n"
            "        .pagination button { margin: 0 10px; padding: 8px 16px; background: #4CAF50; color: white; border: none; border-radius: 4px; cursor: pointer; }\n"
            "        .pagination button:hover { background: #45a049; }\n"
            "        .pagination button:disabled { background: #cccccc; cursor: not-allowed; }\n"
            "    </style>\n"
            "</head>\n"
            "<body>\n"
            + ''.join(sections_html) +
            "</body>\n"
            "</html>"
        )

        html_chunks.append({
            "name": range_title,
            "content": html
        })

    return html_chunks


def create_merged_html_with_pagination(chapters, max_length=23000):
    """
    创建包含所有章节的单个 HTML 文件，带翻页功能
    
    Args:
        chapters (list): 章节列表
        max_length (int): 单段最大字符数
        
    Returns:
        str: 完整的 HTML 内容
    """
    merged = merge_chapters_with_limit(chapters, max_length)
    
    # 构建所有页面的内容和目录
    pages_content = []
    toc_items = []  # 目录项
    
    for page_index, item in enumerate(merged):
        range_title = item.get("name", "")
        body = item.get("content", "")
        
        # 将合并后的 body 再次按章节切分
        pattern = r'(第[零一二三四五六七八九十百\d]+[卷章节集][^\n\r]*)'
        parts = re.split(pattern, body)
        
        page_html = ""
        for i in range(1, len(parts), 2):
            chap_title = parts[i].strip()
            chap_content = parts[i + 1].strip() if i + 1 < len(parts) else ""
            page_html += f"<h1 id=\"chapter-{page_index}-{i//2}\">{chap_title}</h1>\n<div class=\"content\">{chap_content}</div>\n"
            
            # 添加到目录
            toc_items.append({
                'title': chap_title,
                'page': page_index,
                'chapter': i // 2
            })
        
        if not page_html and body.strip():
            page_html = f"<div class=\"content\">{body.strip()}</div>"
            # 如果没有章节标题，使用范围标题作为目录项
            toc_items.append({
                'title': range_title,
                'page': page_index,
                'chapter': 0
            })
            
        pages_content.append(page_html)
    
    # 将页面内容转换为 JavaScript 数组格式
    js_pages = []
    for page in pages_content:
        # 转义特殊字符，确保JavaScript能正确解析
        escaped_page = (page
                       .replace('\\', '\\\\')  # 反斜杠
                       .replace('"', '\\"')    # 双引号
                       .replace("'", "\\'")    # 单引号
                       .replace('\n', '\\n')   # 换行符
                       .replace('\r', '\\r')   # 回车符
                       .replace('\t', '\\t'))  # 制表符
        js_pages.append(f'"{escaped_page}"')
    
    # 调试：检查页面内容是否为空
    if not pages_content or all(not page.strip() for page in pages_content):
        print("警告：所有页面内容为空！")
        print(f"章节数量: {len(chapters)}")
        print(f"合并后段落数量: {len(merged)}")
        print(f"页面内容: {pages_content}")
        
        # 如果页面内容为空，至少生成一个默认页面
        if not pages_content:
            pages_content = ["<div class=\"content\">暂无内容</div>"]
            js_pages = ['"<div class=\\"content\\">暂无内容</div>"']
    
    # 生成目录HTML
    toc_html = "<h2>目录</h2><ul>"
    for i, item in enumerate(toc_items):
        # 转义特殊字符
        title = item['title'].replace('"', '&quot;').replace("'", "&#39;")
        toc_html += f"<li><a href=\"#\" onclick=\"jumpToPage({item['page']})\">{title}</a></li>"
    toc_html += "</ul>"
    
    # 生成完整的 HTML
    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no" />
    <style>
        body {{background-color: #cce8cf; margin: 0; padding: 20px;}}
        .content {{ white-space: break-spaces; text-indent: 2em; font-size: 24px; margin-bottom: 20px;}}
        h1 {{ color: #2c5530; margin: 20px 0; text-align: center; }}
        
        /* 翻页栏样式 */
        .pagination {{ 
            position: fixed; 
            bottom: 0; 
            left: 0; 
            right: 0; 
            background: rgba(255,255,255,0.95); 
            padding: 15px; 
            border-radius: 0; 
            z-index: 1000; 
            display: flex; 
            flex-wrap: wrap; 
            justify-content: center; 
            align-items: center; 
            gap: 8px;
            box-shadow: 0 -2px 10px rgba(0,0,0,0.1);
        }}
        .pagination button {{ 
            margin: 2px; 
            padding: 12px 16px; 
            background: #4CAF50; 
            color: white; 
            border: none; 
            border-radius: 6px; 
            cursor: pointer; 
            font-size: 14px;
            min-width: 60px;
            touch-action: manipulation;
        }}
        .pagination button:hover {{ background: #45a049; }}
        .pagination button:disabled {{ background: #cccccc; cursor: not-allowed; }}
        .pagination input {{ 
            width: 60px; 
            padding: 8px; 
            margin: 2px; 
            border: 1px solid #ccc; 
            border-radius: 4px; 
            text-align: center;
            font-size: 14px;
        }}
        .pagination span {{ 
            margin: 0 10px; 
            font-size: 14px; 
            color: #666;
            white-space: nowrap;
        }}
        
        /* 目录样式 */
        .toc {{ 
            position: fixed; 
            top: 0; 
            left: 0; 
            right: 0; 
            bottom: 0; 
            background: rgba(255,255,255,0.98); 
            padding: 20px; 
            border-radius: 0; 
            max-width: 100%; 
            max-height: 100vh; 
            overflow-y: auto; 
            z-index: 1000; 
            display: none; 
        }}
        .toc h2 {{ 
            margin: 0 0 20px 0; 
            color: #2c5530; 
            font-size: 24px;
            text-align: center;
            border-bottom: 2px solid #4CAF50;
            padding-bottom: 10px;
        }}
        .toc ul {{ 
            list-style: none; 
            padding: 0; 
            margin: 0; 
        }}
        .toc li {{ 
            margin: 10px 0; 
        }}
        .toc a {{ 
            color: #2c5530; 
            text-decoration: none; 
            display: block; 
            padding: 15px; 
            border-radius: 8px; 
            font-size: 18px;
            border: 1px solid #e0e0e0;
            transition: all 0.3s ease;
        }}
        .toc a:hover {{ 
            background: #e8f5e8; 
            border-color: #4CAF50;
            transform: translateX(5px);
        }}
        .toc a:active {{ 
            background: #d4edda; 
        }}
        
        /* 目录按钮样式 */
        .toc-toggle {{ 
            position: fixed; 
            top: 20px; 
            right: 20px; 
            background: #4CAF50; 
            color: white; 
            border: none; 
            padding: 15px 20px; 
            border-radius: 8px; 
            cursor: pointer; 
            z-index: 1001; 
            font-size: 16px;
            font-weight: bold;
            box-shadow: 0 2px 8px rgba(0,0,0,0.2);
            touch-action: manipulation;
        }}
        .toc-toggle:hover {{ 
            background: #45a049; 
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        }}
        
        /* 移动端适配 */
        @media (max-width: 768px) {{
            body {{ padding: 10px; }}
            .content {{ font-size: 20px; }}
            h1 {{ font-size: 22px; }}
            
            .pagination {{
                padding: 10px;
                gap: 4px;
            }}
            .pagination button {{
                padding: 10px 12px;
                font-size: 12px;
                min-width: 50px;
            }}
            .pagination input {{
                width: 50px;
                padding: 6px;
                font-size: 12px;
            }}
            .pagination span {{
                font-size: 12px;
                margin: 0 5px;
            }}
            
            .toc {{
                padding: 15px;
            }}
            .toc h2 {{
                font-size: 20px;
            }}
            .toc a {{
                padding: 12px;
                font-size: 16px;
            }}
            
            .toc-toggle {{
                padding: 12px 16px;
                font-size: 14px;
                top: 15px;
                right: 15px;
            }}
        }}
        
        @media (max-width: 480px) {{
            .content {{ font-size: 18px; }}
            h1 {{ font-size: 20px; }}
            
            .pagination {{
                flex-direction: row;
                flex-wrap: nowrap;
                gap: 6px;
                padding: 10px 8px;
                overflow-x: auto;
                justify-content: flex-start;
                align-items: center;
            }}
            .pagination button {{
                flex-shrink: 0;
                padding: 10px 12px;
                font-size: 12px;
                min-width: 55px;
                white-space: nowrap;
                border-radius: 6px;
            }}
            .pagination input {{
                width: 50px;
                padding: 8px 4px;
                font-size: 12px;
                flex-shrink: 0;
                border-radius: 4px;
            }}
            .pagination span {{
                font-size: 11px;
                margin: 0 4px;
                flex-shrink: 0;
                white-space: nowrap;
                color: #888;
            }}
            
            .toc a {{
                padding: 10px;
                font-size: 14px;
            }}
        }}
    </style>
    <script>
        let currentPage = 0;
        const totalPages = {len(pages_content)};
        const pages = [{', '.join(js_pages)}];
        const tocItems = {repr(toc_items)};
        const STORAGE_KEY = 'yzy_tts_current_page';
        
        // 从缓存中读取页码
        function loadPageFromCache() {{
            try {{
                const savedPage = localStorage.getItem(STORAGE_KEY);
                if (savedPage !== null) {{
                    const pageIndex = parseInt(savedPage);
                    if (pageIndex >= 0 && pageIndex < totalPages) {{
                        return pageIndex;
                    }}
                }}
            }} catch (e) {{
                console.log('无法读取页码缓存:', e);
            }}
            return 0; // 默认返回第一页
        }}
        
        // 保存页码到缓存
        function savePageToCache(pageIndex) {{
            try {{
                localStorage.setItem(STORAGE_KEY, pageIndex.toString());
            }} catch (e) {{
                console.log('无法保存页码缓存:', e);
            }}
        }}
        
        
        function loadPage(pageIndex) {{
            if (pageIndex < 0 || pageIndex >= totalPages) return;
            if (!document.body) return; // 确保body元素存在
            
            currentPage = pageIndex; // 先更新当前页码
            savePageToCache(pageIndex); // 保存到缓存
            
            document.body.innerHTML = pages[pageIndex] + 
                '<button class="toc-toggle" onclick="toggleToc()">目录</button>' +
                '<div class="toc" style="display:none;">' + {repr(toc_html)} + '</div>' +
                '<div class="pagination">' +
                '<button onclick="loadPage(' + (currentPage - 1) + ')" ' + (currentPage === 0 ? 'disabled' : '') + '>上一页</button>' +
                '<button onclick="loadPage(0)">首页</button>' +
                '<input type="number" id="pageInput" min="1" max="' + totalPages + '" value="' + (currentPage + 1) + '" onchange="jumpToPageInput()">' +
                '<button onclick="loadPage(' + (totalPages - 1) + ')">末页</button>' +
                '<button onclick="loadPage(' + (currentPage + 1) + ')" ' + (currentPage === totalPages - 1 ? 'disabled' : '') + '>下一页</button>' +
                '<span>第 ' + (currentPage + 1) + ' 页 / 共 ' + totalPages + ' 页</span>' +
                '</div>';
        }}
        
        function jumpToPage(pageIndex) {{
            loadPage(pageIndex);
            hideToc();
        }}
        
        function jumpToPageInput() {{
            const input = document.getElementById('pageInput');
            const pageIndex = parseInt(input.value) - 1;
            if (pageIndex >= 0 && pageIndex < totalPages) {{
                loadPage(pageIndex);
            }}
        }}
        
        function toggleToc() {{
            const toc = document.querySelector('.toc');
            if (toc) {{
                if (toc.style.display === 'none' || toc.style.display === '') {{
                    toc.style.display = 'block';
                }} else {{
                    toc.style.display = 'none';
                }}
            }}
        }}
        
        function hideToc() {{
            const toc = document.querySelector('.toc');
            if (toc) {{
                toc.style.display = 'none';
            }}
        }}
        
        // 等待页面完全加载后再初始化
        function initPagination() {{
            if (document.body) {{
                const savedPage = loadPageFromCache();
                loadPage(savedPage);
            }} else {{
                // 如果body还没准备好，等待一下再试
                setTimeout(initPagination, 10);
            }}
        }}
        
        // 键盘翻页
        document.addEventListener('keydown', function(e) {{
            if (e.key === 'ArrowLeft' && currentPage > 0) loadPage(currentPage - 1);
            if (e.key === 'ArrowRight' && currentPage < totalPages - 1) loadPage(currentPage + 1);
            if (e.key === 'Home') loadPage(0);
            if (e.key === 'End') loadPage(totalPages - 1);
            if (e.key === 'Escape') hideToc();
        }});
        
        // 触摸手势支持
        let touchStartX = 0;
        let touchStartY = 0;
        
        document.addEventListener('touchstart', function(e) {{
            touchStartX = e.touches[0].clientX;
            touchStartY = e.touches[0].clientY;
        }}, {{ passive: true }});
        
        document.addEventListener('touchend', function(e) {{
            if (!touchStartX || !touchStartY) return;
            
            const touchEndX = e.changedTouches[0].clientX;
            const touchEndY = e.changedTouches[0].clientY;
            
            const diffX = touchStartX - touchEndX;
            const diffY = touchStartY - touchEndY;
            
            // 水平滑动距离大于垂直滑动距离，且滑动距离足够大
            if (Math.abs(diffX) > Math.abs(diffY) && Math.abs(diffX) > 50) {{
                if (diffX > 0 && currentPage < totalPages - 1) {{
                    // 向左滑动，下一页
                    loadPage(currentPage + 1);
                }} else if (diffX < 0 && currentPage > 0) {{
                    // 向右滑动，上一页
                    loadPage(currentPage - 1);
                }}
            }}
            
            touchStartX = 0;
            touchStartY = 0;
        }}, {{ passive: true }});
        
        // 页面关闭前保存当前页码
        window.addEventListener('beforeunload', function() {{
            savePageToCache(currentPage);
        }});
        
        // 页面隐藏时保存页码（移动端支持）
        document.addEventListener('visibilitychange', function() {{
            if (document.hidden) {{
                savePageToCache(currentPage);
            }}
        }});
        
        // 页面加载完成后初始化
        if (document.readyState === 'loading') {{
            document.addEventListener('DOMContentLoaded', initPagination);
        }} else {{
            initPagination();
        }}
    </script>
</head>
<body>
</body>
</html>"""
    
    return html

# def chinese_to_number(text):
#     return cn2an.cn2an(text.string)

# 支持多种中文数字格式转换
def convert_chinese_number(text):
    """
    全面支持多种中文数字格式转换：
    - 一零三 → 103
    - 一百零三 → 103
    - 一百三十三 → 133
    - 一一零 → 110
    """
    # 完整数字映射
    digit_map = {
        '零': '0', '〇': '0',
        '一': '1', '二': '2', '三': '3', '四': '4', '五': '5',
        '六': '6', '七': '7', '八': '8', '九': '9',
        '十': '10', '百': '100', '千': '1000', '万': '10000'
    }

    def repl(match):
        cn_num = match.group(1)
        # 处理纯连续数字（如 一零三）
        if all(c in ['零', '〇', '一', '二', '三', '四', '五', '六', '七', '八', '九'] for c in cn_num):
            return ''.join(digit_map[c] for c in cn_num)

        # 处理带单位的数字
        total = 0
        current = 0
        for c in cn_num:
            if c in ['十', '百', '千', '万']:
                if current == 0:
                    current = 1
                total += current * int(digit_map[c])
                current = 0
            else:
                current = int(digit_map[c])
        total += current
        return str(total)

    # 匹配模式：支持多种中文数字格式
    pattern = r'([零〇一二三四五六七八九十百千万]+)'
    return re.sub(pattern, repl, text)


def split_text_by_length(text, chunk_size=2000):
    """
    按指定字数拆分文本，尽量保留段落完整性

    Args:
        text (str): 输入文本
        chunk_size (int): 每段最大字数（默认1000）

    Returns:
        list: 拆分后的文本块列表
    """
    # 预处理：按段落分割（保留换行符）
    paragraphs = re.split(r'(?<=\n)', text)

    chunks = []
    current_chunk = []
    current_length = 0

    for para in paragraphs:
        para_length = len(para)

        # 情况1：当前段落可直接加入当前块
        if current_length + para_length <= chunk_size:
            current_chunk.append(para)
            current_length += para_length
        else:
            # 情况2：段落需拆分
            if para_length > chunk_size:
                # 长段落硬拆分
                words = list(para)
                for i in range(0, len(words), chunk_size):
                    chunk = ''.join(words[i:i + chunk_size])
                    chunks.append(chunk)
            else:
                # 情况3：当前块已满，新建块
                if current_chunk:
                    chunks.append(''.join(current_chunk))
                current_chunk = [para]
                current_length = para_length

    # 添加最后一块
    if current_chunk:
        chunks.append(''.join(current_chunk))

    return chunks
