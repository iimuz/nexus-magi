# NEXUS MAGI

カスタマイズ可能なLLM（大規模言語モデル）を使用した個人用エージェントアプリケーションです。MAGI合議システムを模した複数の視点からの回答生成機能を備えています。

## 特徴

- 複数の視点（MELCHIOR:科学者、BALTHASAR:母親、CASPER:女性）からの回答生成
- 視点間での討論機能によるより深い回答
- テキストベースのTUIインターフェイス（[Textual](https://github.com/Textualize/textual)使用）
- ローカルLLM対応（[Ollama](https://ollama.com/)または[LiteLLM](https://github.com/BerriAI/litellm)経由）
- [langgraph](https://github.com/langchain-ai/langgraph)を使用したワークフロー管理

## 環境構築

### 必要条件

- Python 3.11以上
- ローカルLLMサーバー（OllamaまたはLiteLLM）

### インストール方法

1. リポジトリをクローン

```bash
git clone https://github.com/iimuz/nexus-magi.git
cd nexus-magi
```

2. 仮想環境を作成（任意）

```bash
python -m venv .venv
source .venv/bin/activate  # Linuxの場合
# または
.venv\Scripts\activate  # Windowsの場合
```

3. パッケージのインストール

```bash
pip install -e .  # 開発モードでインストール
# または
pip install -e ".[dev]"  # 開発ツールを含めてインストール
```

4. LLMサーバーの準備

   - [Ollama](https://ollama.com/)をインストールして起動
   - 使用するモデル（例: phi4-mini）をダウンロード

```bash
ollama pull phi4-mini
```

## 実行方法

アプリケーションを起動：

```bash
# パッケージとしてインストールした場合
nexus-magi

# または直接モジュールを実行
python -m nexus_magi
```

### 設定オプション

アプリケーションは以下の設定で動作します：

- デフォルトAPI: `http://localhost:11434/api`（Ollama API）
- デフォルトモデル: `phi4-mini`
- API種類: `ollama`（または`litellm`）

これらの設定は`chat_model.py`内で変更できます。

## 使用方法

1. アプリケーションを起動するとチャットインターフェースが表示されます
2. メッセージを入力すると、MAGIシステムの各視点からの回答が順次表示されます
3. 討論機能により、異なる視点からの意見交換と最終的な合議結果が表示されます

## 開発者向け情報

### コードスタイル

コードの整形などは下記を利用しています：

- json, markdown, toml
  - [dprint](https://github.com/dprint/dprint): formatter
- python
  - [ruff](https://github.com/astral-sh/ruff): python linter and formatter.
  - [mypy](https://github.com/python/mypy): static typing.
  - docstring: [numpy 形式](https://numpydoc.readthedocs.io/en/latest/format.html)を想定しています。
    - vscodeの場合は[autodocstring](https://marketplace.visualstudio.com/items?itemName=njpwerner.autodocstring)拡張機能によりひな型を自動生成できます。
- yml
  - [prettier](https://prettier.io/): formatter

### 開発ツールのセットアップ

開発ツールをインストール：

```bash
pip install -e ".[dev]"
```

コード品質チェック：

```bash
ruff check .
mypy src
```

### プロジェクト構造

```
/
├── src/             # ソースコード
│   └── nexus_magi/  # メインパッケージ
│       ├── __init__.py
│       ├── __main__.py  # エントリーポイント
│       ├── app.py       # TUIアプリケーション
│       └── chat_model.py # LLM連携機能
├── memory-bank/     # プロジェクト関連ドキュメント
├── pyproject.toml   # Python設定
├── setup.cfg        # Python設定
└── setup.py         # Pythonパッケージ設定
```

## ライセンス

このプロジェクトは[リポジトリ内のLICENSEファイル](./LICENSE)の条件の下で提供されています。
