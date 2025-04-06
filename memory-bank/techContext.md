# Technical Context

## Core Technologies

### Primary Language
- Python
  - 主要な開発言語として使用
  - 静的型付けを活用

### Development Tools

#### Code Quality
1. Python Tools
   - ruff: リンティングとフォーマッティング
   - mypy: 静的型チェック
   - numpy形式のdocstring

2. その他のフォーマッター
   - dprint: JSON, Markdown, TOML用
   - prettier: YAML用
   - cspell: スペルチェック

#### Documentation
- Docstring: numpy形式を採用
- VSCode拡張: autodocstring for docstring生成

## Development Environment

### Editor Configuration
- .editorconfig: エディタ設定の統一
- .gitignore: バージョン管理除外設定
- pyproject.toml: Python設定
- setup.cfg & setup.py: Pythonパッケージ設定

### Quality Assurance
- 静的型チェック（mypy）
- リンティング（ruff）
- コードフォーマット（ruff, dprint, prettier）
- スペルチェック（cspell）

## Project Structure
```
/
├── src/              # ソースコード
├── .cspell.json      # スペルチェック設定
├── .editorconfig     # エディタ設定
├── .prettierignore   # prettier除外設定
├── dprint.json       # dprintフォーマッター設定
├── pyproject.toml    # Python設定
├── setup.cfg         # Python設定
└── setup.py         # Pythonパッケージ設定
