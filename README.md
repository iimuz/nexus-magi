# NEXUS MAGI

カスタマイズ可能なLLM（大規模言語モデル）を使用した個人用エージェントアプリケーションです。MAGI合議システムを模した複数の視点からの回答生成機能を備えています。

## 特徴

- 複数の視点（MELCHIOR:科学者、BALTHASAR:母親、CASPER:女性）からの回答生成
- 視点間での討論機能によるより深い回答
- フロントエンド（React）とバックエンド（FastAPI）の分離アーキテクチャ
- モダンなWeb UIインターフェイス
- WebSocketを活用したリアルタイムストリーミング応答
- ローカルLLM対応（[Ollama](https://ollama.com/)または[LiteLLM](https://github.com/BerriAI/litellm)経由）
- [langgraph](https://github.com/langchain-ai/langgraph)を使用したワークフロー管理
- [TypeSpec](https://typespec.io/)を利用したAPI定義の一元管理
- OpenAPI仕様から自動生成されたクライアントコードとバックエンドモデル

## 環境構築

### 必要条件

- Python 3.11以上
- Node.js 18以上
- ローカルLLMサーバー（OllamaまたはLiteLLM）

### インストール方法

1. リポジトリをクローン

```bash
git clone https://github.com/iimuz/nexus-magi.git
cd nexus-magi
```

2. バックエンドのセットアップ

```bash
# バックエンドディレクトリに移動
cd backend

# 仮想環境を作成（任意）
python -m venv .venv
source .venv/bin/activate  # Linuxの場合
# または
.venv\Scripts\activate  # Windowsの場合

# パッケージのインストール
pip install -e .  # 開発モードでインストール
# または
pip install -e ".[dev]"  # 開発ツールを含めてインストール
```

3. フロントエンドのセットアップ

```bash
# プロジェクトルートに戻る（必要に応じて）
cd ..
# フロントエンドディレクトリに移動
cd frontend
npm install
```

4. APIおよびクライアントコードの生成

```bash
# APIディレクトリに移動
cd ../api
npm install
npm run generate-all
```

5. LLMサーバーの準備

   - [Ollama](https://ollama.com/)をインストールして起動
   - 使用するモデル（例: phi4-mini）をダウンロード

```bash
ollama pull phi4-mini
```

## 実行方法

### バックエンドAPIサーバーの起動

```bash
# バックエンドディレクトリに移動
cd backend

# パッケージとしてインストールした場合
nexus-magi

# または直接モジュールを実行
python -m nexus_magi

# ポートやホストの指定
python -m nexus_magi --port 8080 --host 127.0.0.1

# 使用するLLMの指定
python -m nexus_magi --model phi3-mini --api-type litellm --api-base http://localhost:4000
```

### フロントエンドの起動

```bash
cd frontend
npm start

# カスタムAPIエンドポイントを指定する場合
REACT_APP_API_BASE_URL=http://localhost:8080 npm start
```

### 設定オプション

バックエンドAPIは以下の設定で動作します：

- デフォルトAPI: `http://localhost:11434/api`（Ollama API）
- デフォルトモデル: `phi4-mini`
- API種類: `ollama`（または`litellm`）

## 使用方法

1. バックエンドAPIサーバーとフロントエンドを起動します
2. ブラウザで `http://localhost:3000` にアクセスするとチャットインターフェースが表示されます
3. メッセージを入力すると、MAGIシステムの各視点からの回答が順次表示されます
4. 討論機能により、異なる視点からの意見交換と最終的な合議結果が表示されます

## アーキテクチャ

プロジェクトは以下の3つの主要コンポーネントで構成されています：

1. **API定義（TypeSpec）**
   - `/api` ディレクトリにTypeSpecでAPI定義を管理
   - OpenAPI仕様を自動生成
   - フロントエンド用TypeScriptクライアントコードとバックエンド用Pydanticモデルを生成

2. **バックエンド（FastAPI）**
   - RESTful APIとWebSocketエンドポイントを提供
   - LLMとの連携処理
   - MAGI合議システムのビジネスロジック
   - TypeSpecから生成されたPydanticモデルを使用

3. **フロントエンド（React）**
   - モダンなWeb UIインターフェース
   - WebSocketを通じたリアルタイム通信
   - Material UIを使用したレスポンシブデザイン
   - TypeSpecから生成されたクライアントコードを使用

## 開発者向け情報

### API開発ワークフロー

APIの変更が必要な場合は、以下の手順で行います：

1. `/api/main.tsp`でTypeSpec定義を更新
2. `/api`ディレクトリで`npm run generate-all`を実行
3. 自動的にOpenAPI仕様、フロントエンド用クライアントコード、バックエンド用Pydanticモデルが生成されます

これにより、フロントエンドとバックエンドの型定義が自動的に同期され、一貫性のあるAPIインターフェースが維持されます。

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
mypy backend
```

### プロジェクト構造

```
/
├── api/                   # API定義（TypeSpec）
│   ├── main.tsp           # TypeSpec API定義
│   ├── package.json       # API生成用依存関係
│   ├── pyproject.toml     # Pythonモデル生成用の設定
│   ├── scripts/           # APIコード生成スクリプト
│   │   └── generate_models.py  # Pythonモデル生成スクリプト
│   └── tsp-output/        # 生成されたOpenAPI仕様
├── backend/               # バックエンドコード
│   ├── nexus_magi/        # メインパッケージ
│   │   ├── api_gen/       # 生成されたPydanticモデル
│   │   │   ├── __init__.py
│   │   │   └── models.py  # 自動生成されたPythonモデル
│   │   └── ...            # その他のバックエンドコード
│   ├── pyproject.toml     # バックエンド用Python設定
│   ├── setup.cfg          # バックエンド用Python設定
│   └── setup.py           # バックエンド用Pythonパッケージ設定
├── frontend/              # フロントエンドコード
│   ├── package.json       # フロントエンド依存関係
│   ├── public/            # 静的ファイル
│   └── src/               # フロントエンドソースコード
│       ├── generated-api/ # 生成されたTypeScriptクライアント
│       └── ...            # その他のフロントエンドコード
├── dprint.json            # dprint設定
├── mise.toml              # mise設定
├── package.json           # プロジェクト依存関係
└── LICENSE                # ライセンスファイル
```

## ライセンス

このプロジェクトは[リポジトリ内のLICENSEファイル](./LICENSE)の条件の下で提供されています。
