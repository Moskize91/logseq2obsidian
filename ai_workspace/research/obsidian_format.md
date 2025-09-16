# Obsidian 格式要求

## 📋 概述
Obsidian 是基于 Markdown 的知识管理工具，支持标准 Markdown 语法和一些扩展功能。

## 📁 文件组织

### 基础结构
```
obsidian-vault/
├── 01-Inbox/          # 收集箱 (可选)
├── 02-Areas/          # 领域文件夹 (可选)
├── 03-Resources/      # 资源文件夹 (可选)
├── attachments/       # 附件文件夹
│   ├── images/
│   └── files/
├── templates/         # 模板文件夹 (可选)
└── .obsidian/        # Obsidian 配置 (自动生成)
    ├── app.json
    ├── workspace.json
    └── plugins/
```

## 📝 Markdown 语法

### 1. 内部链接 (双链)
```markdown
[[文件名]]
[[文件名|显示文本]]
[[文件名#标题]]          # 链接到特定标题
[[文件名#^block-id]]     # 链接到特定块
```

### 2. 标签
```markdown
#标签
#嵌套/标签
#标签/子标签
```

### 3. YAML Frontmatter
```yaml
---
title: 页面标题
tags: [tag1, tag2, tag3]
aliases: [别名1, 别名2]
created: 2024-01-01
modified: 2024-01-02
---
```

### 4. 块引用和嵌入
```markdown
![[文件名]]              # 嵌入整个文件
![[文件名#标题]]         # 嵌入特定标题下的内容
![[文件名#^block-id]]    # 嵌入特定块

^block-id              # 块标识符 (行末)
```

### 5. 图片和附件
```markdown
![图片描述](attachments/image.png)
![[image.png]]          # Obsidian 风格链接
[PDF文件](attachments/document.pdf)
```

### 6. 数学公式 (MathJax)
```markdown
$行内公式$
$$
块级公式
$$
```

### 7. 代码块
```markdown
```python
# Python 代码
print("Hello World")
```
```

### 8. 表格
```markdown
| 列1 | 列2 | 列3 |
|-----|-----|-----|
| 数据1 | 数据2 | 数据3 |
```

## 🔧 Obsidian 特色功能

### 1. Canvas (画布)
- `.canvas` 文件格式
- 可视化笔记连接
- 不在本项目转换范围内

### 2. 插件系统
- Dataview - 数据查询
- Templater - 高级模板
- Calendar - 日历视图

### 3. 图谱视图
- 自动基于双链生成
- 可配置显示规则

## 📋 文件命名规范

### 推荐规范
- 使用英文和数字
- 避免特殊字符: `< > : " | ? * /`
- 用短横线 `-` 或下划线 `_` 替换空格
- 保持文件名简洁有意义

### 示例转换
```
Logseq: "我的想法.md"
Obsidian: "我的想法.md" 或 "my-thoughts.md"
```

## 🎯 转换目标格式

### 基础 Markdown
- 标准 Markdown 语法
- 保持原有层级结构
- 转换列表和缩进

### 双链系统
```markdown
# Logseq
[[页面名称]]

# Obsidian
[[页面名称]]  # 文件存在时
```

### 标签转换
```markdown
# Logseq
#标签 #[[带空格的标签]]

# Obsidian  
#标签 #带空格的标签
```

### 属性转换
```markdown
# Logseq
title:: 我的页面
tags:: [[tag1]], [[tag2]]

# Obsidian
---
title: 我的页面
tags: [tag1, tag2]
---
```

## ⚠️ 限制和注意事项

1. **文件名限制**: 不支持某些特殊字符
2. **块引用**: 语法不同，需要转换策略
3. **查询功能**: 需要插件支持 (Dataview)
4. **属性系统**: 主要依赖 YAML frontmatter

## 📈 转换优先级

### 必需功能
- [x] 标准 Markdown 支持
- [x] 双链转换
- [x] 标签系统
- [x] 文件组织

### 推荐功能
- [ ] YAML frontmatter
- [ ] 块引用适配
- [ ] 图片链接转换
- [ ] 附件管理

### 可选功能
- [ ] 插件配置
- [ ] 主题适配
- [ ] 高级查询转换

---
*基于 Obsidian v1.4.x 版本*