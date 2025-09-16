# 紧急提醒 - 下次会话必读

## 🚨 绝对不能忘记的信息

### 启动指令
**用户会说**: "请根据 ai_workspace 继续工作"
**我应该**: 立即读取 `NEXT_SESSION_GUIDE.md` 然后开始工作

### 项目核心信息
- **目标**: Logseq→Obsidian 迁移工具 (Python)
- **方法**: 实例驱动开发 (基于真实样本)
- **状态**: 已完成环境准备，下次开始编码

### 已有的关键资源
1. **真实样本**: `examples/logseq_samples/` (2个文件)
2. **样本分析**: `research/sample_analysis.md` 
3. **开发方法**: `docs/development_methodology.md`
4. **项目状态**: `PROJECT_STATUS.md`

### 下次会话第一件事
1. 配置 Python 环境
2. 创建 src/ 目录结构  
3. 基于 sample1.md 开始开发解析器

### 关键挑战 (从真实样本得出)
- 块引用 `((uuid))` - Obsidian 无对应
- 块ID `id:: uuid` - 转换为 `^block-id`
- 文件路径 `../assets/` - 需要调整
- 复杂嵌套结构 - 保持层级

### 工作分工
- **AI管理**: `ai_workspace/` 所有内容
- **协作开发**: `src/`, `tests/`, 用户文档等

---
**如果我忘记了任何东西，让用户提醒我查看这个文件！**