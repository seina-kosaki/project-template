# Python Project Template

Pythonプロジェクトを始めるためのテンプレートです。Python 3.12とuvを使用します。

## 含まれるもの

- `src/`: アプリケーションコード
- `tests/`: pytestによるテスト
- `.github/agents/`、`.github/instructions/`、`.github/skills/`: Copilot向けの共通設定
- `.github/hooks/`: Copilotのツール操作を補助的に制御するHook
- `.github/workflows/`: GitHub Actionsによるテスト
- `.vscode/`: VS Codeの共通設定と推奨拡張機能
- `frontend/`: Vite + React + TypeScriptによるラベル選択・ブラウザーデバッグ用サンプル

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

## フロントエンドの画面とデバッグ（Windows）

Pythonとは独立したサンプルです。フロントエンドだけの利用に `uv sync` は不要です。
画面には同梱の猫のイラストと「猫・犬・鳥」のラベルを表示します。初期状態は未選択で、選べるラベルは1つだけです。
選ぶと「選択中のラベル」と「直前の選択処理（例: 未選択 → 猫、猫 → 犬）」が更新されます。正誤判定はしません。
API・バックエンド未接続、永続保存なしです。再読み込みすると未選択に戻ります。

### 前提と初回セットアップ

1. [Node.js公式サイト](https://nodejs.org/)から **Node.js 24 LTSのWindowsインストーラー**を入れてください。npmも同時に入ります（Python/uvとは別に必要です）。
2. インストール後、VS Codeとターミナルを開き直します。ブラウザーデバッグにはWindowsのMicrosoft Edgeと、最新版のVS Codeを使います。JavaScript/TypeScriptとブラウザーデバッガーはVS Codeに標準搭載されており、追加拡張は不要です。
3. VS Codeで**このREADMEがあるルートフォルダー**を開き、メニューの「ターミナル」→「新しいターミナル」からPowerShellを開きます。

```powershell
node --version
npm.cmd --version
cd frontend
npm.cmd ci
```

`node --version` は `v24.x.x` を確認してください。`npm.cmd ci` は初回およびロックファイル更新後に実行します。
依存関係は `frontend/package.json` と `frontend/package-lock.json` で管理します。
PowerShellの実行ポリシーで `npm.ps1` が拒否される場合を避けるため、Windowsの手順では `npm.cmd` を使います。実行ポリシーの変更は不要です。

### 起動・操作

上記と同じターミナル（`frontend` 内）で実行します。

```powershell
npm.cmd run dev
```

表示された `http://127.0.0.1:5173` をブラウザーで開き、ラベルを順に選んで表示の変化を確認します。
ラジオボタンはマウスのほか、Tabキーと矢印キーでも操作できます。
開発サーバーは自分のPCからのみ接続できます。5173番ポートが使用中なら起動は失敗するので、そのポートを使っている既存の開発サーバーを停止して再実行してください。
終了はターミナルで **Ctrl+C** です。確認が表示された場合は `Y` を入力します。

### VS CodeでF5・ブレークポイントデバッグ

1. `npm.cmd run dev` を起動したままにします。**F5は開発サーバーを起動しません**。
2. `frontend/src/App.tsx` を開き、`handleLabelChange` 内の `const previousLabel = ...` の行番号の左をクリックし、赤いブレークポイントを置きます。
3. 左の「実行とデバッグ」で **「フロントエンド: Edge (先に npm run dev)」** を選び、**F5**（必要ならFn+F5）を押します。デバッグ用のEdgeが開きます。
4. そのEdgeでラベルを選ぶとVS Codeで停止します。「変数」または「ウォッチ」で `nextLabel`（今回の選択）と `selectedLabel`（変更前）を確認します。
5. **F10**で1行ずつ進め、**F5**で再開します。画面の更新は処理を再開した後に反映されます。別のラベルを選ぶと再び停止します。同じ選択済みラベルでは変更イベントは発生しません。
6. **Shift+F5**でブラウザーデバッグを終了します。開発サーバーは別途Ctrl+Cで停止してください。

ブレークポイントが灰色のままの場合は、ルートフォルダーを開いているか、5173番で開発サーバーが起動しているか、F5で開いたEdgeを操作しているかを確認してください。
ブラウザーだけで調べる場合はEdgeで **F12** を押し、「Console」でエラー、「Sources」で `src/App.tsx` を探してブレークポイントを設定できます。F5デバッグ中はVS Code側での停止確認を推奨します。

### Copilot自身に画面操作・開発・デバッグを依頼する

1. VS CodeのCopilotチャットで、セッション対象を **Copilot** にします。
2. エージェント一覧から **「05 フロントエンド開発エージェント」** を選びます。表示されない場合はチャットを新しく開き、カスタマイズ一覧で定義の認識状況を確認してください。
3. たとえば「既存のラベル選択画面をブラウザーで開き、猫→犬と選んで表示が変わること、再読み込みで未選択に戻ることを確認して」と依頼します。
4. ツール利用やローカルページへのアクセスを求められた場合は対象を確認して許可します。

定義は[フロントエンド開発エージェント](./.github/agents/frontend-development.agent.md)です。Copilotが画面を操作して確認する用途であり、上記のF5による手動デバッグとは別です。
ブラウザーツールの利用には対応するVS Codeとセッション環境が必要です。エージェント定義だけでブラウザーツールが導入・有効化されるわけではありません。接続できない場合は画面未検証として報告します。MCPの追加は自動では行いません。

### 型チェックとビルド

`frontend` 内で実行します。

```powershell
npm.cmd run build
```

TypeScriptの型チェック後に `frontend/dist/` へビルドします。型チェックだけなら `npm.cmd run typecheck` です。
仕様の詳細は[フロントエンドデバッグ仕様](./docs/frontend-debug-spec.md)を参照してください。

## 設定

ツールやCopilot、VS Codeの設定は、原則としてリポジトリに含まれる共通設定を使用します。プロジェクト固有の要件ができた場合は、既存設定との整合性を確認してから変更してください。

秘密情報や個人用の設定値はコミットせず、必要になった時点で環境変数や`.env`など適切な方法を用意してください。

新しいリポジトリのブランチ保護やSecretsなどのGitHub側の設定は、複製先で確認してください。
