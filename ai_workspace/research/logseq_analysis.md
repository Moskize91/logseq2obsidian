# Logseq 格式分析

## 📋 概述
Logseq 是一个基于本地文件的知识管理工具，使用 Markdown 格式存储笔记。

## 📁 文件结构
```
logseq-graph/
├── journals/           # 日记页面
│   ├── 2024_01_01.md
│   └── ...
├── pages/             # 普通页面
│   ├── page1.md
│   └── ...
├── assets/            # 资源文件
│   ├── images/
│   └── files/
├── logseq/           # 配置文件
│   ├── config.edn
│   ├── custom.css
│   └── metadata.edn
└── draws/            # 绘图文件 (可选)
```

## 📝 Markdown 语法特点

### 1. 页面引用 (双链)
```markdown
[[页面名称]]
[[页面名称|显示文本]]
```

### 2. 块引用
```markdown
((block-uuid-here))
```

### 3. 标签
```markdown
#标签名
#[[标签名包含空格]]
```

### 4. 属性系统
```markdown
property:: value
multi-line-property:: 
  - item 1
  - item 2
```

### 5. 块结构 (缩进层级)
```markdown
- 这是一个块
  - 子块
    - 更深层的子块
  - 另一个子块
- 并列的块
```

### 6. 查询语法
```markdown
{{query (and [[tag1]] [[tag2]])}}
```

### 7. 宏和模板
```markdown
{{template "模板名"}}
{{embed [[页面名]]}}
```

## 🔍 特殊格式

### 日记页面
- 文件名格式: `YYYY_MM_DD.md`
- 自动创建的每日页面
- 通常包含时间戳和日常记录

### 页面属性 (Frontmatter)
```markdown
title:: 页面标题
tags:: [[tag1]], [[tag2]]
public:: true
---
```

### 块级属性
```markdown
- 这是一个块
  id:: unique-block-id
  created-at:: 1640995200000
```

## ⚠️ 转换挑战

1. **块引用**: Obsidian 没有对应概念
2. **查询语法**: 需要转换为静态内容或注释
3. **属性系统**: 部分需要转换为 YAML frontmatter
4. **文件命名**: 处理特殊字符和空格
5. **层级结构**: 保持缩进的语义
6. **宏和模板**: 需要展开或转换

## 🎯 转换优先级

### 高优先级
- [x] 双链转换
- [x] 基础 Markdown 内容
- [x] 标签转换
- [x] 文件结构迁移

### 中优先级
- [ ] 属性系统转换
- [ ] 图片和附件迁移
- [ ] 日记页面处理

### 低优先级
- [ ] 块引用替代方案
- [ ] 查询语法处理
- [ ] 宏和模板展开

---
*分析基于 Logseq v0.10.x 版本*