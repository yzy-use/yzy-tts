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
            "        body {background-color: #cce8cf;}\n"
            "        .content { white-space: break-spaces; text-indent: 2em;font-size:24px;}\n"
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
