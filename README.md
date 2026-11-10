# Python Project Template

Pythonプロジェクトを始めるためのテンプレートです。Python 3.12とuvを使用します。

## 含まれるもの

- `src/`: アプリケーションコード
- `tests/`: pytestによるテスト
- `.github/agents/`、`.github/instructions/`、`.github/skills/`: Copilot向けの共通設定
- `.github/hooks/`: Copilotのツール操作を補助的に制御するHook
- `.github/workflows/`: GitHub Actionsによるテスト
- `.vscode/`: VS Codeの共通設定と推奨拡張機能

## 新しいプロジェクトで最初に行うこと

GitHubの **Use this template** から新しいリポジトリを作成した後、プロジェクト名と説明を更新します。テンプレートの内容は自動で置換されません。

1. `pyproject.toml` の `project.name` を新しいプロジェクト名に変更します。名前には小文字、数字、ハイフンを使います。
2. `pyproject.toml` の `project.description` を更新します。
3. このREADMEを新しいプロジェクトの説明に合わせて編集します。
4. ロックファイルを更新し、依存関係を同期します。

```powershell
uv lock
uv sync
```

`uv lock`により、`uv.lock`内のプロジェクト情報も更新されます。

## 開発環境

Python 3.12と[uv](https://docs.astral.sh/uv/)をインストールしてから、リポジトリのルートで実行します。

```powershell
uv sync
```

### 外部パッケージ

SAM3とUltralyticsは公開パッケージを使うよう `pyproject.toml` に設定済みです。プロジェクトのルートで `uv sync` を実行すると、GitHubリポジトリをcloneせずにパッケージとしてインストールできます。

- `sam3`: [PyPIのsam3パッケージ](https://pypi.org/project/sam3/)。パッケージのプロジェクト情報は[MetaのSAM 3リポジトリ](https://github.com/facebookresearch/sam3)を参照します。
- `ultralytics`: [PyPIのUltralyticsパッケージ](https://pypi.org/project/ultralytics/)。添付例にあるYOLOv12向けのGitHub forkではなく、公開されている標準のUltralyticsです。
- `torch` と `torchvision`: 既存の `pytorch-cu128` インデックスからCUDA 12.8対応版を取得します。SAM3の要件に合わせ、PyTorchは2.7以上としています。
- `triton-windows`: 添付例に合わせ、Windows向けのTritonを依存関係に含めています。

依存関係と取得元は `pyproject.toml`、解決済みのバージョンは `uv.lock` で管理します。CUDAインデックスとPyTorchのソース指定はこのPC向けの設定です。追加の外部ライブラリも、公開パッケージとして利用できる場合は `uv add <package>` で追加し、Git依存を必要とする場合は追加前に確認してください。

このテンプレートの `uv sync` は依存パッケージをインストールしますが、プロジェクト自身はインストールしません。外部パッケージを利用するだけなら、このプロジェクトの `[build-system]` は不要です。ただし、依存パッケージがソース配布の場合は、そのパッケージ用のビルド環境が別途必要になることがあります。プロジェクト自身をパッケージとして配布する場合に `[build-system]` の追加を検討してください。

### 環境変数

環境変数を使うプロジェクトでは、ルートの`.env.example`を`.env`にコピーし、必要な値を設定してください。`.env`はGit管理対象外です。

```powershell
Copy-Item .env.example .env
```

`.env` は自動では読み込まれません。必要な場合は、アプリケーションの起動時に `python-dotenv` の `load_dotenv()` を呼び出す処理を追加してください。

### ログ

リポジトリのルートで `uv run python` を起動した場合、次のようにロガーを初期化できます。

```python
import logging

from src.logging_config import setup_logging

setup_logging()
logger = logging.getLogger(__name__)
logger.info("アプリケーションを開始しました")
```

ログはコンソールと `logs/YYYY-MM-DD.log` に出力され、過去のログは自動削除されません。詳細は[ロガー仕様](./docs/logger-spec.md)を参照してください。

### テスト

テストを実行します。

```powershell
uv run --locked python -m pytest
```

`pyproject.toml` の `testpaths` により、アプリケーションとHookの両方のテストを実行します。GitHub Actionsもpushとpull requestで同じ範囲のテストを実行します。複製直後に未実行の場合は、GitHubのActions画面から `Tests` を手動実行できます。

### Copilot Hook

HookはCopilot実行環境向けです。VS Codeではセッション対象を **Copilot** にし、Hookが動作する環境から `uv` とPython 3.12を利用できるようにしてください。カスタムエージェントの `target` 指定だけではセッション対象は切り替わりません。

Hookは `.env` の直接操作や代表的な危険操作を検知する補助手段です。すべての操作を検知できるわけではなく、無効化やタイムアウト時には通常の権限処理に従う場合があります。OSのアクセス制御や秘密情報の管理の代わりにはなりません。

## 設定

ツールやCopilot、VS Codeの設定は、原則としてリポジトリに含まれる共通設定を使用します。プロジェクト固有の要件ができた場合は、既存設定との整合性を確認してから変更してください。

秘密情報や個人用の設定値はコミットせず、必要になった時点で環境変数や`.env`など適切な方法を用意してください。

新しいリポジトリのブランチ保護やSecretsなどのGitHub側の設定は、複製先で確認してください。
