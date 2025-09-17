"""
Obsidian 格式化器
负责将解析的 Logseq 数据转换为 Obsidian 兼容格式
"""

import re
from typing import Dict
import urllib.parse
from pathlib import Path


class ObsidianFormatter:
    """Obsidian 格式转换器"""
    
    def __init__(self, remove_top_level_bullets=False, category_tag=None, category_folder=None, 
                 input_assets_dir=None):
        # Obsidian 块引用计数器（用于生成唯一的块引用）
        self.block_ref_counter = 0
        # 是否删除第一级列表符号
        self.remove_top_level_bullets = remove_top_level_bullets
        # 分类标签配置
        self.category_tag = category_tag  # 例如 "wiki"
        self.category_folder = category_folder  # 例如 "wiki"
        # 输入assets目录路径（用于检查文件是否存在）
        self.input_assets_dir = input_assets_dir
        # 块引用映射：UUID -> (文件名, 块ID)
        self.block_uuid_map = {}
        # PDF 高亮映射：UUID -> (PDF路径, 页码, 高亮文本)
        self.pdf_highlight_map = {}
        # 当前正在处理的文件名
        self.current_filename = None
        # 当前目标文件夹
        self.current_target_folder = ""
    
    def collect_pdf_highlights(self, logseq_dir: str):
        """收集所有 PDF 高亮映射"""
        logseq_path = Path(logseq_dir)
        
        # 收集所有 hls__ 文件
        pages_dir = logseq_path / "pages"
        hls_files = pages_dir.glob("hls__*.md")
        
        for hls_file in hls_files:
            self._parse_hls_file(hls_file)
            
        # 收集 .edn 文件中的精确坐标信息
        self._collect_edn_highlights(logseq_path)
    
    def _parse_hls_file(self, hls_file: Path):
        """解析单个 hls__ 文件"""
        with open(hls_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        lines = content.split('\n')
        
        # 查找 PDF 文件路径
        pdf_path = None
        for line in lines:
            if line.startswith('file-path::'):
                pdf_path = line.split('::', 1)[1].strip()
                break
        
        if not pdf_path:
            return
        
        # 解析高亮注释
        current_highlight = {}
        for line in lines:
            line = line.strip()
            
            if line.startswith('- ') and not line.startswith('  '):
                # 新的高亮开始，保存之前的
                if current_highlight.get('id'):
                    self._save_highlight(pdf_path, current_highlight)
                    current_highlight = {}
                
                # 提取高亮文本
                highlight_text = line[2:].strip()
                if highlight_text and not highlight_text.startswith('[:span]'):
                    current_highlight['text'] = highlight_text
            
            elif line.startswith('id::'):
                current_highlight['id'] = line.split('::', 1)[1].strip()
            elif line.startswith('hl-page::'):
                current_highlight['page'] = line.split('::', 1)[1].strip()
            elif line.startswith('hl-color::'):
                current_highlight['color'] = line.split('::', 1)[1].strip()
        
        # 保存最后一个高亮
        if current_highlight.get('id'):
            self._save_highlight(pdf_path, current_highlight)
    
    def _save_highlight(self, pdf_path: str, highlight: dict):
        """保存高亮到映射表"""
        uuid = highlight.get('id')
        if uuid:
            self.pdf_highlight_map[uuid] = {
                'pdf_path': pdf_path,
                'page': highlight.get('page', ''),
                'text': highlight.get('text', ''),
                'color': highlight.get('color', ''),
                'coordinates': highlight.get('coordinates'),  # 新增：坐标信息
                'screenshot_path': highlight.get('screenshot_path')  # 新增：截图路径
            }

    def _collect_edn_highlights(self, logseq_path: Path):
        """收集 .edn 文件中的精确坐标信息"""
        
        # 查找 assets 目录下的 .edn 文件
        assets_dir = logseq_path / "assets"
        if not assets_dir.exists():
            return
            
        for edn_file in assets_dir.glob("*.edn"):
            try:
                # 读取 .edn 文件内容
                with open(edn_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 解析 PDF 名称
                pdf_name = edn_file.stem  # 去掉 .edn 扩展名
                pdf_path = f"../attachments/{pdf_name}.pdf"
                
                # 查找对应的截图目录
                screenshot_dir = assets_dir / pdf_name
                
                # 使用正则表达式解析 UUID 和坐标信息
                # 匹配格式：{:id #uuid "uuid-string", :page N, :position {...}}
                highlight_pattern = r':id #uuid "([^"]+)".*?:page (\d+).*?:position \{:bounding \{:x1 ([^,]+),.*?:y1 ([^,]+),.*?:x2 ([^,]+),.*?:y2 ([^,]+),.*?:width ([^,]+),.*?:height ([^}]+)'
                
                for match in re.finditer(highlight_pattern, content, re.DOTALL):
                    uuid = match.group(1)
                    page = match.group(2)
                    x1, y1, x2, y2 = match.group(3), match.group(4), match.group(5), match.group(6)
                    width, height = match.group(7), match.group(8)
                    
                    # 查找对应的截图文件
                    screenshot_path = None
                    if screenshot_dir.exists():
                        screenshot_pattern = f"{page}_{uuid}_*.png"
                        screenshot_files = list(screenshot_dir.glob(screenshot_pattern))
                        if screenshot_files:
                            # 使用相对路径
                            screenshot_path = f"attachments/{pdf_name}/{screenshot_files[0].name}"
                    
                    # 更新或创建高亮映射
                    coordinates_data = {
                        'x1': float(x1), 'y1': float(y1), 
                        'x2': float(x2), 'y2': float(y2),
                        'width': float(width), 'height': float(height)
                    }
                    
                    if uuid in self.pdf_highlight_map:
                        # 更新现有映射
                        self.pdf_highlight_map[uuid]['coordinates'] = coordinates_data
                        if screenshot_path:
                            self.pdf_highlight_map[uuid]['screenshot_path'] = screenshot_path
                    else:
                        # 创建新映射（可能 hls__ 文件不存在）
                        self.pdf_highlight_map[uuid] = {
                            'pdf_path': pdf_path,
                            'page': page,
                            'text': '',  # .edn 文件中没有文本内容
                            'color': '',
                            'coordinates': coordinates_data,
                            'screenshot_path': screenshot_path
                        }
                        
            except (FileNotFoundError, PermissionError, UnicodeDecodeError) as e:
                # 忽略文件处理错误，继续处理其他文件
                print(f"   ⚠️  解析 .edn 文件失败: {edn_file.name}: {e}")
                continue

    def collect_block_mappings(self, filename: str, parsed_data: Dict):
        """第一阶段：收集文件中的所有块ID映射"""
        lines = parsed_data['content'].split('\n')
        self.current_filename = filename
        
        for line in lines:
            # 查找 id:: uuid 格式的块ID定义
            id_match = re.search(r'id:: ([a-f0-9-]+)', line)
            if id_match:
                uuid = id_match.group(1)
                # 生成对应的块ID
                self.block_ref_counter += 1
                block_id = f"block{self.block_ref_counter}"
                # 存储映射：UUID -> (文件名, 块ID)
                self.block_uuid_map[uuid] = (filename, block_id)
    
    def format_content(self, parsed_data: Dict, filename: str = "", target_folder: str = "") -> str:
        """将解析的 Logseq 数据转换为 Obsidian 格式"""
        if filename:
            self.current_filename = filename
        
        # 保存目标文件夹信息，用于正确处理资源路径
        self.current_target_folder = target_folder
            
        lines = parsed_data['content'].split('\n')
        
        # 生成 YAML frontmatter（如果有 meta 属性）
        frontmatter = self._generate_frontmatter(parsed_data.get('meta_properties', []))
        
        # 移除原始内容中的 meta 属性行
        filtered_lines = self._filter_meta_lines(lines, parsed_data.get('meta_properties', []))
        
        # 如果文件被归类到特定文件夹，移除分类标签行
        category_folder = self.detect_category_folder(parsed_data)
        if category_folder:
            filtered_lines = self._remove_category_tag_lines(filtered_lines)
        
        # 处理每一行
        formatted_lines = []
        for line in filtered_lines:
            formatted_line = self._process_line(line, parsed_data)
            formatted_lines.append(formatted_line)
        
        # 如果启用了删除第一级列表符号，进行后处理
        if self.remove_top_level_bullets:
            formatted_lines = self._remove_top_level_bullets(formatted_lines)
        
        # 组合 frontmatter 和内容
        if frontmatter:
            return frontmatter + '\n' + '\n'.join(formatted_lines)
        else:
            return '\n'.join(formatted_lines)
    
    def _process_line(self, line: str, _parsed_data: Dict) -> str:
        """处理单行内容"""
        processed_line = line
        
        # 1. 处理 Logseq 引用块格式 "- >" -> ">"
        processed_line = self._convert_quote_blocks(processed_line)
        
        # 2. 处理页面链接 [[]]  
        processed_line = self._convert_page_links(processed_line)
        
        # 3. 处理块引用 (()) - 转换为注释或删除
        processed_line = self._convert_block_refs(processed_line)
        
        # 4. 处理块 ID - 转换为 Obsidian 块引用格式
        processed_line = self._convert_block_ids(processed_line)
        
        # 5. 处理资源文件路径
        processed_line = self._convert_asset_paths(processed_line)
        
        return processed_line
    
    def _convert_quote_blocks(self, line: str) -> str:
        """转换 Logseq 引用块格式 '- >' 为 Obsidian 引用格式 '>'"""
        # 匹配以任意数量的空格/制表符开头，然后是 "- >" 的行
        pattern = r'^(\s*)-\s*>\s*(.*)$'
        match = re.match(pattern, line)
        
        if match:
            indent = match.group(1)  # 保留原有的缩进
            content = match.group(2)  # 引用的内容
            return f"{indent}> {content}"
        
        return line
    
    def _convert_page_links(self, line: str) -> str:
        """转换页面链接格式"""
        def replace_link(match):
            link_text = match.group(1)
            
            # 检查是否为 hls__ 高亮文件的引用
            if link_text.startswith('hls__'):
                # 如果包含块ID，尝试转换为 PDF 引用
                if '#' in link_text:
                    _, block_id = link_text.split('#', 1)
                    
                    # 查找对应的 PDF 高亮
                    for _, highlight in self.pdf_highlight_map.items():
                        if highlight.get('block_id') == block_id:
                            pdf_path = highlight['pdf_path']
                            page = highlight['page']
                            text = highlight['text']
                            if text and page:
                                return f"[{text}]({pdf_path}#page={page})"
                            elif page:
                                return f"[PDF页{page}]({pdf_path}#page={page})"
                    
                    # 如果找不到，返回注释
                    return f"<!-- PDF高亮引用 (未找到): {link_text} -->"
                else:
                    # 直接引用 hls__ 文件，返回注释
                    return f"<!-- PDF高亮文件引用: {link_text} -->"
            
            # 对于普通页面链接，只进行 URL 解码，但保持页面名称不变
            # 页面链接在 Obsidian 中可以包含斜杠等特殊字符
            processed_link = urllib.parse.unquote(link_text)
            # Obsidian 双链基本兼容，保持原有的页面链接格式
            return f"[[{processed_link}]]"

        return re.sub(r'\[\[([^\]]+)\]\]', replace_link, line)

    def _convert_block_refs(self, line: str) -> str:
        """处理块引用 - 转换为 Obsidian 块链接或 PDF 注释引用格式"""
        def replace_block_ref(match):
            block_uuid = match.group(1)
            
            # 首先检查是否为 PDF 高亮引用
            if block_uuid in self.pdf_highlight_map:
                highlight = self.pdf_highlight_map[block_uuid]
                pdf_path = highlight['pdf_path']
                page = highlight['page']
                text = highlight['text']
                coordinates = highlight.get('coordinates')
                screenshot_path = highlight.get('screenshot_path')
                
                # 构建链接文本，优先使用高亮文本
                if text and page:
                    link_text = text
                elif page:
                    link_text = f"PDF页{page}"
                else:
                    link_text = "PDF注释"
                
                # 转换为 Obsidian 的 PDF 注释格式
                if page:
                    # 首先转换路径格式：../assets/ → ../attachments/ 或 attachments/
                    target_folder = getattr(self, 'current_target_folder', '')
                    if pdf_path.startswith('../assets/'):
                        if target_folder:
                            # 文件在子文件夹中，需要 ../attachments/
                            converted_pdf_path = pdf_path.replace('../assets/', '../attachments/')
                        else:
                            # 文件在根目录，直接使用 attachments/
                            converted_pdf_path = pdf_path.replace('../assets/', 'attachments/')
                    else:
                        converted_pdf_path = pdf_path
                    
                    # 构建基础 PDF 路径（移除相对路径前缀以适配 Obsidian 链接格式）
                    if converted_pdf_path.startswith('../attachments/'):
                        clean_pdf_path = converted_pdf_path.replace('../attachments/', '')
                    elif converted_pdf_path.startswith('attachments/'):
                        clean_pdf_path = converted_pdf_path.replace('attachments/', '')
                    else:
                        clean_pdf_path = converted_pdf_path
                    
                    # 如果有坐标信息，使用 Obsidian 的 selection 格式
                    if coordinates:
                        x1, y1, x2, y2 = coordinates['x1'], coordinates['y1'], coordinates['x2'], coordinates['y2']
                        
                        # 尝试不同的坐标格式转换
                        # 方法1: 归一化坐标 (如果有页面尺寸信息)
                        if 'width' in coordinates and 'height' in coordinates:
                            width, height = coordinates['width'], coordinates['height']
                            # 转换为0-100的百分比坐标
                            x1_norm = int((x1 / width) * 100)
                            y1_norm = int((y1 / height) * 100)
                            x2_norm = int((x2 / width) * 100)
                            y2_norm = int((y2 / height) * 100)
                            selection = f"{x1_norm},{y1_norm},{x2_norm},{y2_norm}"
                        else:
                            # 方法2: 缩放坐标 (将像素坐标缩放到较小范围)
                            scale_factor = 100  # 实验性缩放因子
                            x1_scaled = int(x1 / scale_factor)
                            y1_scaled = int(y1 / scale_factor)
                            x2_scaled = int(x2 / scale_factor)
                            y2_scaled = int(y2 / scale_factor)
                            selection = f"{x1_scaled},{y1_scaled},{x2_scaled},{y2_scaled}"
                        
                        pdf_link = f"{clean_pdf_path}#page={page}&selection={selection}"
                        
                        # 使用 Obsidian 的内部链接格式 [[file#params|display_text]]
                        # 只使用原始高亮文本作为显示文本，如果没有文本则使用简洁的页面格式
                        if text and text.strip():
                            display_text = text.strip()
                            result = f"[[{pdf_link}|{display_text}]]"
                        else:
                            # 没有文本时使用简洁格式
                            result = f"[[{pdf_link}|页面 {page}]]"
                    else:
                        # 没有坐标信息，使用标准页面链接
                        result = f"[{link_text}]({converted_pdf_path}#page={page})"
                    
                    # 如果有截图，添加截图引用
                    if screenshot_path:
                        if coordinates:
                            x1, y1 = coordinates['x1'], coordinates['y1']
                            result += f"\n\n![PDF截图 - 坐标({x1:.0f},{y1:.0f})]({screenshot_path})"
                        else:
                            result += f"\n\n![PDF截图]({screenshot_path})"
                    
                    return result
                else:
                    # 对于没有页面信息的情况，也需要转换路径
                    target_folder = getattr(self, 'current_target_folder', '')
                    if pdf_path.startswith('../assets/'):
                        if target_folder:
                            converted_pdf_path = pdf_path.replace('../assets/', '../attachments/')
                        else:
                            converted_pdf_path = pdf_path.replace('../assets/', 'attachments/')
                    else:
                        converted_pdf_path = pdf_path
                    return f"[{link_text}]({converted_pdf_path})"
            
            # 查找对应的块映射
            elif block_uuid in self.block_uuid_map:
                target_filename, block_id = self.block_uuid_map[block_uuid]
                
                # 使用嵌入格式 ![[]] 来实现类似 Notion 同步块的效果
                if target_filename == self.current_filename:
                    # 同文件内的块嵌入
                    return f"![[#^{block_id}]]"
                else:
                    # 跨文件的块嵌入
                    # 处理文件名：移除.md扩展名
                    clean_filename = target_filename.replace('.md', '') if target_filename.endswith('.md') else target_filename
                    return f"![[{clean_filename}#^{block_id}]]"
            else:
                # 找不到对应的映射，保留为注释以便调试
                return f"<!-- Block Reference (未找到): {block_uuid} -->"
        
        return re.sub(r'\(\(([^)]+)\)\)', replace_block_ref, line)
    
    def _convert_block_ids(self, line: str) -> str:
        """转换块 ID 为 Obsidian 块引用格式"""
        def replace_block_id(match):
            uuid = match.group(1)
            
            # 查找已经映射的块ID
            if uuid in self.block_uuid_map:
                _, block_id = self.block_uuid_map[uuid]
                return f"^{block_id}"
            else:
                # 这种情况不应该发生，因为我们已经预先收集了所有映射
                # 但为了安全起见，生成一个新的块ID
                self.block_ref_counter += 1
                block_id = f"block{self.block_ref_counter}"
                return f"^{block_id}"
        
        return re.sub(r'id:: ([a-f0-9-]+)', replace_block_id, line)
    
    def _convert_asset_paths(self, line: str) -> str:
        """转换资源文件路径"""
        def replace_asset(match):
            alt_text = match.group(1)
            file_path = match.group(2)
            
            # 处理相对路径 - 扁平化结构
            if file_path.startswith('../assets/'):
                # 根据目标文件夹决定正确的相对路径
                target_folder = getattr(self, 'current_target_folder', '')
                
                if target_folder:
                    # 文件在子文件夹中，需要 ../attachments/
                    new_path = file_path.replace('../assets/', '../attachments/')
                else:
                    # 文件在根目录，直接使用 attachments/
                    new_path = file_path.replace('../assets/', 'attachments/')
                
                # 暂时禁用文件存在性检查，因为它会破坏Markdown格式
                # # 检查文件是否存在（如果有输入路径信息）
                # if hasattr(self, 'input_assets_dir'):
                #     # 构建实际文件路径进行检查
                #     actual_file_path = self.input_assets_dir / file_path.replace('../assets/', '')
                #     if not actual_file_path.exists():
                #         # 文件不存在，添加注释
                #         return f"![{alt_text}]({new_path}) <!-- ⚠️ 文件不存在: {file_path} -->"
            else:
                new_path = file_path
            
            return f"![{alt_text}]({new_path})"
        
        return re.sub(r'!\[([^\]]*)\]\(([^)]+)\)', replace_asset, line)
    
    def generate_filename(self, original_name: str) -> str:
        """生成 Obsidian 兼容的文件名"""
        # 移除或替换 Obsidian 不支持的字符
        safe_name = re.sub(r'[<>:"/\\|?*]', '_', original_name)
        
        # 确保 .md 扩展名
        if not safe_name.endswith('.md'):
            safe_name += '.md'
        
        return safe_name
    
    def get_conversion_summary(self, original_data: Dict, converted_content: str) -> Dict:
        """生成转换摘要"""
        original_stats = {
            'page_links': len(re.findall(r'\[\[([^\]]+)\]\]', original_data['content'])),
            'block_refs': len(re.findall(r'\(\(([^)]+)\)\)', original_data['content'])),
            'block_ids': len(re.findall(r'id:: ([a-f0-9-]+)', original_data['content'])),
            'assets': len(re.findall(r'!\[([^\]]*)\]\(([^)]+)\)', original_data['content']))
        }
        
        converted_stats = {
            'page_links': len(re.findall(r'\[\[([^\]]+)\]\]', converted_content)),
            'block_refs': len(re.findall(r'<!-- Block Reference:', converted_content)),
            'block_ids': len(re.findall(r'\^block\d+', converted_content)),
            'assets': len(re.findall(r'!\[([^\]]*)\]\(([^)]+)\)', converted_content))
        }
        
        return {
            'original': original_stats,
            'converted': converted_stats,
            'changes': {
                'block_refs_to_comments': original_stats['block_refs'],
                'block_ids_converted': original_stats['block_ids']
            }
        }
    
    def _remove_top_level_bullets(self, lines: list) -> list:
        """删除第一级列表符号，转换为段落格式，并规范化列表缩进"""
        result = []
        i = 0
        
        while i < len(lines):
            line = lines[i]
            
            # 跳过只有 '-' 的空行
            if line.strip() == '-':
                i += 1
                continue
            
            # 检查是否是第一级列表项（没有前导空格的 "- "）
            if line.startswith('- ') and not line.startswith('  '):
                # 删除 "- " 前缀
                content = line[2:]
                
                # 如果内容不为空，添加到结果
                if content.strip():
                    result.append(content)
                else:
                    # 如果是空的列表项，跳过
                    i += 1
                    continue
                
                # 处理后续的子项，规范化缩进
                j = i + 1
                has_sub_items = False
                
                while j < len(lines):
                    next_line = lines[j]
                    
                    # 空行保持原样
                    if next_line.strip() == '':
                        result.append(next_line)
                        j += 1
                        continue
                    
                    # 检查是否是子项（以制表符或多个空格开头）
                    if next_line.startswith('\t') or next_line.startswith('  '):
                        has_sub_items = True
                        # 规范化缩进并提升一个层级（减少缩进）
                        normalized_line = self._normalize_list_indent(next_line)
                        
                        # 处理空的子列表项
                        if normalized_line.strip() in ['-', '- ']:
                            # 跳过空的子列表项
                            j += 1
                            continue
                        
                        # 提升一个层级：移除一级缩进（2个空格）
                        if normalized_line.startswith('  '):
                            promoted_line = normalized_line[2:]  # 移除前面的2个空格
                        else:
                            promoted_line = normalized_line  # 如果没有足够的缩进，保持原样
                        
                        result.append(promoted_line)
                        j += 1
                    else:
                        # 不是子项，停止处理
                        break
                
                i = j - 1
                
                # 只有在没有子项且下一行不是空行或另一个第一级列表项时才添加空行
                if not has_sub_items and i + 1 < len(lines):
                    next_line = lines[i + 1] if i + 1 < len(lines) else ''
                    if next_line.strip() != '' and not next_line.startswith('- '):
                        result.append('')
                    
            else:
                # 不是第一级列表项
                if line.startswith('\t') or line.startswith('  '):
                    # 规范化子项缩进
                    normalized_line = self._normalize_list_indent(line)
                    
                    # 处理空的子列表项
                    if normalized_line.strip() in ['-', '- ']:
                        # 跳过空的子列表项
                        i += 1
                        continue
                        
                    result.append(normalized_line)
                else:
                    # 普通行保持原样
                    result.append(line)
            
            i += 1
        
        return result
    
    def _normalize_list_indent(self, line: str) -> str:
        """规范化列表项的缩进"""
        # 计算前导空白的数量
        stripped = line.lstrip()
        leading_whitespace = line[:len(line) - len(stripped)]
        
        # 计算缩进级别：制表符按1级计算，每2个空格按1级计算
        indent_level = 0
        i = 0
        while i < len(leading_whitespace):
            char = leading_whitespace[i]
            if char == '\t':
                indent_level += 1
                i += 1
            elif char == ' ':
                # 连续的空格按2个为一级缩进
                space_count = 0
                while i < len(leading_whitespace) and leading_whitespace[i] == ' ':
                    space_count += 1
                    i += 1
                indent_level += space_count // 2  # 每2个空格算1级
            else:
                i += 1
        
        # 生成规范化的缩进（每级2个空格）
        normalized_indent = '  ' * indent_level
        
        return normalized_indent + stripped
    
    def _generate_frontmatter(self, meta_properties) -> str:
        """生成 YAML frontmatter"""
        if not meta_properties:
            return ""
        
        frontmatter_lines = ["---"]
        
        for prop in meta_properties:
            key = prop.key
            value = prop.value
            
            # 处理不同类型的属性
            if key == "alias":
                # 别名转换为 aliases 数组
                # 首先提取所有 [[]] 格式的页面链接
                page_link_matches = re.findall(r'\[\[([^\]]+)\]\]', value)
                if page_link_matches:
                    # 如果有页面链接，使用页面链接内容作为别名
                    aliases = page_link_matches
                else:
                    # 否则按逗号分割
                    aliases = [alias.strip() for alias in value.split(',')]
                
                frontmatter_lines.append("aliases:")
                for alias in aliases:
                    # 确保别名不为空
                    if alias.strip():
                        frontmatter_lines.append(f"  - {alias.strip()}")
            elif key == "tags":
                # 标签处理：提取 [[]] 内的内容
                tag_matches = re.findall(r'\[\[([^\]]+)\]\]', value)
                if tag_matches:
                    frontmatter_lines.append("tags:")
                    for tag in tag_matches:
                        frontmatter_lines.append(f"  - {tag}")
                else:
                    # 如果没有 [[]] 格式，按逗号分割
                    tags = [tag.strip() for tag in value.split(',')]
                    frontmatter_lines.append("tags:")
                    for tag in tags:
                        frontmatter_lines.append(f"  - {tag}")
            elif key == "created-at":
                # 日期属性
                frontmatter_lines.append(f"created: {value}")
            elif key == "type":
                # 类型属性
                frontmatter_lines.append(f"type: {value}")
            elif key == "author":
                # 作者属性
                frontmatter_lines.append(f"author: {value}")
            elif key == "status":
                # 状态属性
                frontmatter_lines.append(f"status: {value}")
            elif key == "priority":
                # 优先级属性
                frontmatter_lines.append(f"priority: {value}")
            elif key == "description":
                # 描述属性（可能包含换行，用引号包围）
                frontmatter_lines.append(f"description: \"{value}\"")
            else:
                # 其他属性直接添加
                frontmatter_lines.append(f"{key}: {value}")
        
        frontmatter_lines.append("---")
        return '\n'.join(frontmatter_lines)
    
    def _filter_meta_lines(self, lines, meta_properties):
        """过滤掉原始内容中的 meta 属性行"""
        if not meta_properties:
            return lines
        
        # 获取所有 meta 属性的行号
        meta_line_numbers = {prop.line_number for prop in meta_properties}
        
        # 过滤掉这些行，同时跳过文件开头的空行
        filtered_lines = []
        content_started = False
        
        for i, line in enumerate(lines, 1):
            if i in meta_line_numbers:
                continue  # 跳过 meta 属性行
            
            # 跳过文件开头的空行（在 meta 属性之后）
            if not content_started and not line.strip():
                continue
            
            content_started = True
            filtered_lines.append(line)
        
        return filtered_lines
    
    def detect_category_folder(self, parsed_data: Dict) -> str:
        """检测文件应该归类到哪个文件夹
        
        根据配置的分类标签，检测文件开头是否包含分类标签，
        决定文件应该归类到哪个文件夹
        
        Args:
            parsed_data: 解析后的文件数据
            
        Returns:
            文件夹名称，如果没有特殊分类则返回空字符串（默认 pages）
        """
        # 如果没有配置分类标签，直接返回默认
        if not self.category_tag or not self.category_folder:
            return ""
        
        lines = parsed_data['content'].split('\n')
        meta_properties = parsed_data.get('meta_properties', [])
        
        # 获取实际内容行（跳过 meta 属性和空行）
        content_lines = self._get_actual_content_lines(lines, meta_properties)
        
        if not content_lines:
            return ""
        
        # 检查第一行实际内容是否以分类标签开头
        first_content_line = content_lines[0].strip()
        category_tag_pattern = f"#{self.category_tag}"
        
        # 移除 Logseq 列表标记（- 开头），获取实际内容
        content_without_bullets = self._remove_logseq_bullets(first_content_line)
        
        # 检查标签是否在实际内容的开头
        if content_without_bullets.startswith(category_tag_pattern):
            # 确保这是一个完整的标签（后面是空格、行尾或其他标签）
            after_tag = content_without_bullets[len(category_tag_pattern):]
            if not after_tag or after_tag[0].isspace() or after_tag[0] == '#':
                return self.category_folder
        
        return ""
    
    def _remove_logseq_bullets(self, line: str) -> str:
        """移除 Logseq 列表标记，获取实际内容
        
        例如：
        "- #wiki 内容" -> "#wiki 内容"
        "  - #wiki 内容" -> "#wiki 内容"
        "#wiki 内容" -> "#wiki 内容"
        """
        stripped = line.strip()
        
        # 移除列表标记（- 或 * 后面跟空格）
        if stripped.startswith('- '):
            return stripped[2:].strip()
        elif stripped.startswith('* '):
            return stripped[2:].strip()
        elif stripped == '-' or stripped == '*':
            return ""
        
        return stripped
    
    def _get_actual_content_lines(self, lines, meta_properties):
        """获取实际内容行（排除 meta 属性和开头的空行）"""
        # 获取所有 meta 属性的行号
        meta_line_numbers = {prop.line_number for prop in meta_properties} if meta_properties else set()
        
        actual_content_lines = []
        
        for i, line in enumerate(lines, 1):
            # 跳过 meta 属性行
            if i in meta_line_numbers:
                continue
            
            # 跳过空行和只有空格的行
            if not line.strip():
                continue
            
            # 这是实际内容行
            actual_content_lines.append(line)
        
        return actual_content_lines
    
    def _remove_category_tag_lines(self, lines):
        """移除包含分类标签的行
        
        如果整行只有分类标签（如 "- #wiki"），则删除整行
        如果行中有其他内容，则只删除标签部分
        
        Args:
            lines: 文件行列表
            
        Returns:
            处理后的行列表
        """
        if not self.category_tag:
            return lines
        
        category_tag_pattern = f"#{self.category_tag}"
        result_lines = []
        
        for line in lines:
            # 移除 Logseq 列表标记，获取实际内容
            content_without_bullets = self._remove_logseq_bullets(line.strip())
            
            # 检查是否包含分类标签
            if category_tag_pattern in content_without_bullets:
                # 检查是否整行只有分类标签
                if content_without_bullets.strip() == category_tag_pattern:
                    # 整行只有标签，删除整行
                    continue
                elif content_without_bullets.startswith(category_tag_pattern):
                    # 标签在开头，检查后面是否只有空格或其他标签
                    after_tag = content_without_bullets[len(category_tag_pattern):]
                    if not after_tag.strip() or after_tag.strip().startswith('#'):
                        # 整行只有这个标签（可能还有其他标签），删除整行
                        continue
                    else:
                        # 有其他内容，只删除标签部分
                        # 保持原行的格式（列表标记等），只替换内容
                        original_prefix = line[:len(line) - len(line.lstrip())]  # 获取前导空格/制表符
                        list_marker = ""
                        
                        # 检查是否有列表标记
                        stripped_line = line.strip()
                        if stripped_line.startswith('- '):
                            list_marker = "- "
                        elif stripped_line.startswith('* '):
                            list_marker = "* "
                        
                        # 移除标签后的内容
                        remaining_content = after_tag.strip()
                        if remaining_content:
                            new_line = original_prefix + list_marker + remaining_content
                        else:
                            # 删除标签后没有内容了，删除整行
                            continue
                        
                        result_lines.append(new_line)
                else:
                    # 标签不在开头，替换标签部分
                    new_content = content_without_bullets.replace(category_tag_pattern, '').strip()
                    if new_content:
                        # 保持原行格式
                        original_prefix = line[:len(line) - len(line.lstrip())]
                        list_marker = ""
                        
                        stripped_line = line.strip()
                        if stripped_line.startswith('- '):
                            list_marker = "- "
                        elif stripped_line.startswith('* '):
                            list_marker = "* "
                        
                        new_line = original_prefix + list_marker + new_content
                        result_lines.append(new_line)
                    else:
                        # 删除标签后没有内容了，删除整行
                        continue
            else:
                # 不包含分类标签，保留原行
                result_lines.append(line)
        
        return result_lines