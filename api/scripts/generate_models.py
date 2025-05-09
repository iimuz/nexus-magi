"""OpenAPI仕様からPydanticモデルを生成するスクリプト."""

import logging
import subprocess
import sys
from pathlib import Path

# ロギングの設定
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# プロジェクトのルートディレクトリを取得
SCRIPT_DIR = Path(__file__).parent.absolute()
ROOT_DIR = SCRIPT_DIR.parent
API_DIR = ROOT_DIR
BACKEND_DIR = ROOT_DIR.parent / "backend"

# OpenAPI仕様ファイルのパス
OPENAPI_SPEC = API_DIR / "tsp-output" / "@typespec" / "openapi3" / "openapi.yaml"

# 生成先のディレクトリ（バックエンド内）
OUTPUT_DIR = BACKEND_DIR / "nexus_magi" / "api_gen"
OUTPUT_DIR.mkdir(exist_ok=True, parents=True)

# __init__.py ファイルを生成
(OUTPUT_DIR / "__init__.py").touch()

# datamodel-code-generatorを使用してモデルを生成
cmd = [
    "datamodel-codegen",
    "--input",
    str(OPENAPI_SPEC),
    "--output",
    str(OUTPUT_DIR / "models.py"),
    "--input-file-type",
    "openapi",
    "--output-model-type",
    "pydantic.BaseModel",
    "--target-python-version",
    "3.11",
    "--use-schema-description",
    "--use-field-description",
]

logger.info("Generating Python models from OpenAPI spec: %s", OPENAPI_SPEC)
logger.info("Output directory: %s", OUTPUT_DIR)
logger.info("Command: %s", " ".join(cmd))

try:
    # 安全なコマンド実行 - 固定のコマンドリストを使用するため安全
    # ここでのS603警告は無視してよい - 実行されるコマンドは信頼済み
    result = subprocess.run(cmd, check=True, capture_output=True, text=True)  # noqa: S603
    logger.info("Model generation completed successfully.")
except subprocess.CalledProcessError:
    logger.exception("Error generating models")
    sys.exit(1)
