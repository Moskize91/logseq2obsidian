# Git 忽略配置更新

## 📅 更新时间
2025-09-16

## 🔧 添加的忽略规则
```gitignore
# Project specific - test samples and examples
examples/
```

## 📝 原因说明
- `examples/` 目录包含从用户真实 Logseq 数据复制的测试样本
- 这些文件可能包含个人笔记内容，不应提交到版本控制
- 每个开发环境可以有自己的测试样本
- 保护用户隐私和数据安全

## ✅ 确认状态
- [x] 已添加 `examples/` 到 `.gitignore`
- [x] 现有的 `examples/logseq_samples/` 和 `examples/obsidian_expected/` 将被忽略
- [x] 新的测试样本不会意外提交到代码仓库

---
*操作记录: 添加项目特定的 git 忽略规则*