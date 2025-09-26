<div align=center>
  <h1>Logseq to Obsidian</h1>
  <p><a href="./README.md">English</a> | <a href="./README_zh-CN.md">中文</a></p>
</div>

A Python tool to migrate [Logseq](https://logseq.com/) notes to [Obsidian](https://obsidian.md/) format.

[Logseq](https://logseq.com/) is a privacy-first, open-source knowledge management tool that uses an outliner editor with bidirectional linking and block references, perfect for building personal knowledge networks.

[Obsidian](https://obsidian.md/) is a Markdown-based local knowledge management tool that helps users build knowledge graphs through bidirectional linking, featuring a powerful plugin ecosystem and visualization capabilities.

## 🚀 Quick Start

### PyPI Installation (Recommended)

Install directly from PyPI:

```bash
pip install logseq2obsidian
```

### Running Conversion

#### After PyPI Installation
```bash
# Basic conversion
logseq2obsidian <logseq_dir> <obsidian_dir>

# Preview mode (no actual file writing)
logseq2obsidian <logseq_dir> <obsidian_dir> --dry-run
```

#### Development Environment Usage
```bash
# Basic conversion
python -m src.main <logseq_dir> <obsidian_dir>

# Preview mode (no actual file writing)
python -m src.main <logseq_dir> <obsidian_dir> --dry-run
```

#### Example Data Conversion
```bash
# Basic conversion (keep list format)
python scripts/convert_examples.py

# Convert to paragraph format (remove top-level list symbols)
python scripts/convert_examples.py --remove-top-level-bullets

# Conversion with categorization
python scripts/convert_examples.py \
  --remove-top-level-bullets \
  --category-tag wiki \
  --category-folder wiki
```

**Parameter Description:**
- `--remove-top-level-bullets`: Remove first-level list symbols, convert content to paragraph format
- `--category-tag <tag>`: Specify category tag name (e.g., "wiki")
- `--category-folder <folder>`: Specify category folder name, used with category-tag

## 🎯 Key Features

- ✅ **Logseq Format Parsing**: Parse Logseq markdown files
- ✅ **Page Link Conversion**: Maintain `[[page]]` format compatibility
- ✅ **Block Reference Processing**: Convert `((uuid))` to Obsidian block references
- ✅ **Meta Property Conversion**: Convert `property:: value` to YAML frontmatter
- ✅ **Format Optimization**: Empty line processing, title spacing, content cleanup
- ✅ **Filename Processing**: URL encoding and special character handling
- ✅ **Categorization**: Automatically categorize files to folders based on tags

### Running Tests

Provide multiple test running methods:

```bash
# Run all tests (recommended)
python test.py

# View all available tests
python test.py --list

# Run specific tests
python test.py --test test_basic
python test.py --test test_bug_fixes
python test.py --test test_formatting_comprehensive

# Use standard test framework
python test.py --unittest    # unittest auto discovery
python test.py --pytest     # use pytest (if installed)

# Run individual test files directly
python tests/test_basic.py
```

## 🛠️ Development Environment Setup

The project uses Poetry for dependency management, one-click installation:

```bash
# Run environment setup script
bash scripts/setup.sh
```

The script will automatically:
- Check Python 3.10+ version
- Check and configure Poetry
- Create virtual environment (.venv)
- Install all dependencies

Manually activate environment:
```bash
source .venv/bin/activate
```

Test-driven development ensures code quality:

```bash
# Continuously run tests during development
python test.py

# Verify after code changes
python test.py --test test_specific_feature
```

**Test Types:**
- `test_basic` - Basic functionality testing
- `test_bug_fixes` - Bug fix verification testing
- `test_formatting_comprehensive` - Format optimization comprehensive testing
- `test_block_id_comprehensive` - Block ID processing comprehensive testing
- `test_page_links_comprehensive` - Page link processing comprehensive testing
- `test_category_detection_comprehensive` - Category detection comprehensive testing