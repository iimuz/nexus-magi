"""OpenAPI仕様からPydanticモデルを生成するスクリプト."""

import subprocess
import sys
from pathlib import Path

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

print(f"Generating Python models from OpenAPI spec: {OPENAPI_SPEC}")
print(f"Output directory: {OUTPUT_DIR}")
print(f"Command: {' '.join(cmd)}")

try:
    subprocess.run(cmd, check=True)
    print("Model generation completed successfully.")
except subprocess.CalledProcessError as e:
    print(f"Error generating models: {e}")
    sys.exit(1)
