# 工作流程设计决策

## 🎯 核心工作流程

### 问题背景
- 初始设计将测试输出写到 `examples/obsidian_output/`，混淆了 examples 的含义
- examples 应该是给别人看的示例，不是内部测试输出
- 需要明确的工作流程来处理真实数据转换和验证

### 最终决策：简单全量复制方案

#### 📁 目录结构
```
logseq2obsidian/
├── src/                      # 源代码
├── tests/                    # 单元测试 (输出到 tests/output/)
├── examples/                 # 真实数据示例和转换结果
│   ├── logseq_data/         # 从真实 Logseq 全量复制的数据
│   └── obsidian_output/     # 转换后的 Obsidian 格式
├── scripts/                 # 工具脚本
│   ├── copy_logseq_data.py  # 全量复制真实数据到 examples
│   └── convert_examples.py  # 转换 examples 中的数据
└── ai_workspace/            # AI 工作区
```

#### 🔄 工作流程
1. **数据准备**: 运行 `scripts/copy_logseq_data.py` 全量复制真实 Logseq 数据
2. **转换执行**: 运行 `scripts/convert_examples.py` 转换到 Obsidian 格式  
3. **验证反馈**: 用户用 Obsidian 打开 `examples/obsidian_output/` 测试
4. **迭代优化**: 根据反馈修改代码，重新转换，覆盖输出

#### 💡 设计原则
- **简单为先**: 全量复制虽然占空间，但逻辑清晰不易出错
- **只读安全**: 代码对源数据只读，长期保留安全
- **明确分工**: examples 是真实示例，tests 是开发测试

#### 🛡️ 安全保护
- `examples/` 目录添加到 `.gitignore`
- 复制的数据与原始数据隔离，避免意外修改
- 提供清理和重新复制的功能

## 🔗 相关路径
- **源 Logseq 目录**: `/Users/taozeyu/Library/Mobile Documents/iCloud~com~logseq~logseq/Documents`
- **目标示例目录**: `examples/logseq_data/`
- **转换输出目录**: `examples/obsidian_output/`

---
*决策日期: 2025-09-16*
*状态: 已确认，开始实现*