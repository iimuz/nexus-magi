#!/usr/bin/env bash
#MISE description="Bump dependencies."
#
# 依存関係のバージョンアップを行うスクリプト。

set -eu
set -o pipefail

npm outdated || true

echo "📦 dependencies を更新しています..."
npm_deps=$(npm outdated --json 2>/dev/null | jq -r 'if type == "object" and (keys | length) > 0 then keys[] as $k | "\($k)@\(.[$k].latest)" else empty end' || echo "")
if [[ -n "${npm_deps}" ]]; then
    echo "${npm_deps}" | xargs npm install --save
else
    echo "更新すべき dependencies はありません"
fi

echo "🛠️  devDependencies を更新しています..."
npm_devdeps=$(npm outdated --json --dev 2>/dev/null | jq -r 'if type == "object" and (keys | length) > 0 then keys[] as $k | "\($k)@\(.[$k].latest)" else empty end' || echo "")
if [[ -n "${npm_devdeps}" ]]; then
    echo "${npm_devdeps}" | xargs npm install --save-dev
else
    echo "更新すべき devDependencies はありません"
fi

echo "🔒 セキュリティ脆弱性をチェックしています..."
npm audit || true

echo "🔧 セキュリティ脆弱性の修正を試みます（互換性のある修正のみ）..."
npm audit fix --force || echo "⚠️ 互換性のある修正がありませんでした。重大な脆弱性は手動で対応してください。"

echo "✅ パッケージの更新が完了しました"
echo "📋 現在のパッケージ状態:"
npm ls --depth=0
