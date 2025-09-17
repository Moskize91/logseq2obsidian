#!/usr/bin/env python3
"""
调试特定案例：方济各会与佛教分裂
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent / 'src'))

from tag_analyzer import TagAnalyzer, TagAnalysisConfig

def analyze_specific_case():
    """分析方济各会与佛教分裂案例"""
    
    # 读取原始文件
    file_path = Path('examples/logseq_data/pages/方济各会与佛教分裂.md')
    if not file_path.exists():
        print(f"文件不存在: {file_path}")
        return
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print("原始内容:")
    print("=" * 50)
    print(content)
    print("=" * 50)
    
    # 初始化分析器
    config = TagAnalysisConfig()
    analyzer = TagAnalyzer(Path('examples/logseq_data/pages'), config)
    
    # 分析文件中提到的页面
    pages_in_content = ['方济各会', '守规派', '住院派', '嘉布遣派', '佛教', '释迦摩尼', '上座部', '大众部']
    
    print("\n页面转换分析:")
    print("=" * 50)
    
    for page in pages_in_content:
        print(f"\n分析页面: {page}")
        print("-" * 30)
        
        # 检查页面是否存在
        page_path = Path(f'examples/logseq_data/pages/{page}.md')
        exists = page_path.exists()
        print(f"页面文件存在: {exists}")
        
        if exists:
            # 读取页面内容
            with open(page_path, 'r', encoding='utf-8') as f:
                page_content = f.read()
            
            print(f"页面内容长度: {len(page_content)} 字符")
            print(f"页面内容预览: {page_content[:100]}...")
            
            # 分析是否应该转为标签
            should_convert = analyzer.should_convert_to_tag(page)
            print(f"应该转为标签: {should_convert}")
            
            # 查看缓存中的页面信息来了解详细状态
            if page in analyzer.page_info_cache:
                page_info = analyzer.page_info_cache[page]
                print(f"内容行数: {page_info.content_lines}")
                print(f"是否符合标签特征: {page_info.is_tag_like}")
                print(f"有实质内容: {page_info.has_content}")
        else:
            # 分析不存在的页面
            should_convert = analyzer.should_convert_to_tag(page)
            print(f"应该转为标签: {should_convert}")
            print("页面文件不存在，将转为标签")

if __name__ == "__main__":
    analyze_specific_case()