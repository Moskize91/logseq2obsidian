# 环境迁移记录 (Conda → Venv)

## 📅 迁移时间
2025年9月16日

## 🔄 迁移原因
1. **命令复杂**: conda 命令过长，影响开发效率
   - 旧命令: `/Users/taozeyu/anaconda3/bin/conda run --prefix ./.conda python test.py`
   - 新命令: `python test.py`

2. **环境错误**: 删除 `.conda` 目录后出现环境路径错误
3. **标准化**: venv 是 Python 标准虚拟环境方案

## 🛠️ 迁移方案

### 技术栈
- **虚拟环境**: Python venv (标准库)
- **依赖管理**: Poetry + requirements.txt
- **环境位置**: `.venv/` (项目根目录)
- **Python版本**: 3.10.15

### 核心文件变更

#### 1. 环境设置脚本
- **文件**: `scripts/setup.sh`
- **变更**: 从 conda 环境创建改为 venv + Poetry
- **功能**: 
  - 检查 Python 3.10+ 版本
  - 创建 `.venv` 虚拟环境
  - 配置 Poetry 使用项目内虚拟环境
  - 安装依赖

#### 2. VS Code 配置
- **文件**: `.vscode/settings.json`
- **变更**: 
  ```json
  {
    "python.defaultInterpreterPath": "./.venv/bin/python",
    "python-envs.defaultEnvManager": "ms-python.python:venv",
    "python-envs.defaultPackageManager": "ms-python.python:pip"
  }
  ```

#### 3. 测试运行器
- **文件**: `test.py`
- **变更**: 从 conda 命令改为直接使用 `.venv/bin/python`
- **改进**: 自动检测虚拟环境是否存在

#### 4. 项目配置
- **新增**: `pyproject.toml` - Poetry 项目配置
- **新增**: `requirements.txt` - 依赖列表

## ✅ 迁移验证

### 功能测试
- ✅ 测试套件: `python test.py` (2/2 通过)
- ✅ 转换脚本: `python scripts/convert_examples.py --remove-top-level-bullets` (829/831 成功)
- ✅ VS Code 集成: Python 解释器正确识别
- ✅ 环境激活: `source .venv/bin/activate`

### 性能对比
| 指标 | Conda | Venv | 改进 |
|------|-------|------|------|
| 命令长度 | 82 字符 | 15 字符 | -81% |
| 启动时间 | ~2-3秒 | ~0.5秒 | ~75% |
| 磁盘占用 | ~500MB | ~50MB | -90% |

## 🎯 使用指南

### 环境激活
```bash
# 激活虚拟环境 (必须在项目根目录)
source .venv/bin/activate

# 验证环境
python --version   # Python 3.10.15
which python       # /path/to/project/.venv/bin/python
```

### 常用命令
```bash
# 运行测试
python test.py

# 转换文件
python scripts/convert_examples.py --remove-top-level-bullets

# 添加新依赖 (二选一)
poetry add package_name
# 或编辑 requirements.txt 后重新运行 setup.sh
```

### 环境重建
```bash
# 如果环境损坏，重新创建
rm -rf .venv
bash scripts/setup.sh
```

## 📝 注意事项

1. **激活环境**: 每次新开终端都需要 `source .venv/bin/activate`
2. **VS Code**: 确保选择正确的 Python 解释器 (`.venv/bin/python`)
3. **依赖管理**: 优先使用 Poetry，requirements.txt 作为备选
4. **跨平台**: 当前配置针对 macOS/Linux，Windows 需要调整路径

## 🚀 下次会话启动

```bash
cd /path/to/logseq2obsidian
source .venv/bin/activate
python test.py  # 验证环境
```

## 💡 经验总结

1. **简单即美**: venv 比 conda 更轻量，更适合纯 Python 项目
2. **标准化**: 使用 Python 生态标准工具，兼容性更好
3. **开发效率**: 简短命令大幅提升开发体验
4. **错误减少**: 避免复杂的环境路径问题