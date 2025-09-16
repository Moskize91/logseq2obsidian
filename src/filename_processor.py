"""
文件名处理工具
负责处理 Logseq 到 Obsidian 的文件名转换
"""

import urllib.parse


class FilenameProcessor:
    """文件名处理器"""
    
    # Obsidian 不支持的文件名字符
    OBSIDIAN_FORBIDDEN_CHARS = [':', '\\', '/']
    
    # 替换字符
    REPLACEMENT_CHAR = '_'
    
    @classmethod
    def process_filename(cls, logseq_filename: str) -> str:
        """
        处理 Logseq 文件名为 Obsidian 兼容格式
        
        步骤:
        1. 解码 URL 编码 (%3A -> :)
        2. 替换 Obsidian 不支持的字符为 _
        
        Args:
            logseq_filename: Logseq 原始文件名
            
        Returns:
            Obsidian 兼容的文件名
        """
        # 1. 解码 URL 编码
        decoded_filename = urllib.parse.unquote(logseq_filename)
        
        # 2. 替换 Obsidian 不支持的字符
        obsidian_filename = decoded_filename
        for forbidden_char in cls.OBSIDIAN_FORBIDDEN_CHARS:
            obsidian_filename = obsidian_filename.replace(forbidden_char, cls.REPLACEMENT_CHAR)
        
        return obsidian_filename
    
    @classmethod
    def process_page_link(cls, page_link: str) -> str:
        """
        处理页面链接中的文件名
        
        Args:
            page_link: 原始页面链接名称
            
        Returns:
            处理后的页面链接名称
        """
        return cls.process_filename(page_link)
    
    @classmethod
    def get_conversion_mapping(cls, logseq_filenames: list) -> dict:
        """
        获取文件名转换映射表
        
        Args:
            logseq_filenames: Logseq 文件名列表
            
        Returns:
            {原文件名: 新文件名} 的映射字典
        """
        mapping = {}
        for filename in logseq_filenames:
            processed = cls.process_filename(filename)
            if processed != filename:
                mapping[filename] = processed
            
        return mapping


def test_filename_processing():
    """测试文件名处理功能"""
    test_cases = [
        '"天机不可泄漏"%3A古代中国对天学的官方垄断和法律控制.md',
        'From Local to Global%3A A Graph RAG Approach.md',
        'Object(a)%3A Cause of Desire.md',
        'How the Other Half %22Thinks%22.md',
        'normal_filename.md',
        'file\\with\\backslash.md',
        'file/with/slash.md'
    ]
    
    print("=== 文件名处理测试 ===")
    for filename in test_cases:
        processed = FilenameProcessor.process_filename(filename)
        changed = "✓" if processed != filename else " "
        print(f"{changed} {filename}")
        if processed != filename:
            print(f"  -> {processed}")
    
    # 测试映射功能
    print("\n=== 转换映射测试 ===")
    mapping = FilenameProcessor.get_conversion_mapping(test_cases)
    print(f"需要转换的文件: {len(mapping)} 个")
    for old, new in mapping.items():
        print(f"  {old} -> {new}")


if __name__ == "__main__":
    test_filename_processing()