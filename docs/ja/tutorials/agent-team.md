# 初めてのインテリジェントエージェントチームを構築する：ADKを使った先進的な天気ボット

<!-- オプション：全体的なパディング/スペーシングのための外側コンテナ -->
<div style="padding: 10px 0;">

  <!-- 1行目: Colabで開く -->
  <!-- このdivはリンクを独自の行にし、下にスペースを追加します -->
  <div style="margin-bottom: 10px;">
    <a href="https://colab.research.google.com/github/google/adk-docs/blob/main/examples/python/tutorial/agent_team/adk_tutorial.ipynb" target="_blank" style="display: inline-flex; align-items: center; gap: 5px; text-decoration: none; color: #4285F4;">
      <img width="32px" src="https://www.gstatic.com/pantheon/images/bigquery/welcome_page/colab-logo.svg" alt="Google Colaboratory ロゴ">
      <span>Colabで開く</span>
    </a>
  </div>

  <!-- 2行目: 共有リンク -->
  <!-- このdivは「共有先：」テキストとアイコンのフレックスコンテナとして機能します -->
  <div style="display: flex; align-items: center; gap: 10px; flex-wrap: wrap;">
    <!-- 共有テキスト -->
    <span style="font-weight: bold;">共有先：</span>

    <!-- ソーシャルメディアリンク -->
    <a href="https://www.linkedin.com/sharing/share-offsite/?url=https%3A//github/google/adk-docs/blob/main/examples/python/tutorial/agent_team/adk_tutorial.ipynb" target="_blank" title="LinkedInで共有">
      <img width="20px" src="https://upload.wikimedia.org/wikipedia/commons/8/81/LinkedIn_icon.svg" alt="LinkedIn ロゴ" style="vertical-align: middle;">
    </a>
    <a href="https://bsky.app/intent/compose?text=https%3A//github/google/adk-docs/blob/main/examples/python/tutorial/agent_team/adk_tutorial.ipynb" target="_blank" title="Blueskyで共有">
      <img width="20px" src="https://upload.wikimedia.org/wikipedia/commons/7/7a/Bluesky_Logo.svg" alt="Bluesky ロゴ" style="vertical-align: middle;">
    </a>
    <a href="https://twitter.com/intent/tweet?url=https%3A//github/google/adk-docs/blob/main/examples/python/tutorial/agent_team/adk_tutorial.ipynb" target="_blank" title="X (Twitter)で共有">
      <img width="20px" src="https://upload.wikimedia.org/wikipedia/commons/5/5a/X_icon_2.svg" alt="X ロゴ" style="vertical-align: middle;">
    </a>
    <a href="https://reddit.com/submit?url=https%3A//github/google/adk-docs/blob/main/examples/python/tutorial/agent_team/adk_tutorial.ipynb" target="_blank" title="Redditで共有">
      <img width="20px" src="https://redditinc.com/hubfs/Reddit%20Inc/Brand/Reddit_Logo.png" alt="Reddit ロゴ" style="vertical-align: middle;">
    </a>
    <a href="https://www.facebook.com/sharer/sharer.php?u=https%3A//github/google/adk-docs/blob/main/examples/python/tutorial/agent_team/adk_tutorial.ipynb" target="_blank" title="Facebookで共有">
      <img width="20px" src="https://upload.wikimedia.org/wikipedia/commons/5/51/Facebook_f_logo_%282019%29.svg" alt="Facebook ロゴ" style="vertical-align: middle;">
    </a>
  </div>

</div>

このチュートリアルは、[Agent Development Kit](https://google.github.io/adk-docs/get-started/)の[クイックスタート例](https://google.github.io/adk-docs/get-started/quickstart/)を拡張したものです。さあ、より深く掘り下げて、より洗練された**マルチエージェントシステム**を構築する準備をしましょう。

私たちは、単純な基盤の上に高度な機能を段階的に重ねながら、**天気ボットのエージェントチーム**の構築に着手します。天気を調べることができる単一のエージェントから始め、次のような機能を段階的に追加していきます：

*   異なるAIモデル（Gemini, GPT, Claude）の活用
*   挨拶や別れのような特定のタスクのための専門的なサブエージェントの設計
*   エージェント間のインテリジェントな委任の有効化
*   永続的なセッション状態を使用したエージェントへのメモリの付与
*   コールバックを使用した重要な安全ガードレールの実装

**なぜ天気ボットチームなのか？**

このユースケースは、一見シンプルですが、複雑で実世界のエージェントアプリケーションを構築するために不可欠なADKのコアコンセプトを探求するための、実践的で親しみやすいキャンバスを提供します。インタラクションの構造化、状態の管理、安全性の確保、そして協力して働く複数のAI「頭脳」のオーケストレーション方法を学びます。

**ADKとは？**

念のためですが、ADKは大規模言語モデル（LLM）を搭載したアプリケーションの開発を効率化するために設計されたPythonフレームワークです。推論、計画、ツールの利用、ユーザーとの動的な対話、そしてチーム内での効果的な協力を可能にするエージェントを作成するための堅牢なビルディングブロックを提供します。

**この高度なチュートリアルで、あなたは以下をマスターします：**

*   ✅ **ツールの定義と使用法：** エージェントに特定の能力（データ取得など）を与えるPython関数（`ツール`）を作成し、エージェントにそれらを効果的に使用する方法を指示します。
*   ✅ **マルチLLMの柔軟性：** LiteLLM統合を介して、エージェントが様々な主要LLM（Gemini, GPT-4o, Claude Sonnet）を利用するように設定し、各タスクに最適なモデルを選択できるようにします。
*   ✅ **エージェントの委任と協力：** 専門的なサブエージェントを設計し、ユーザーのリクエストをチーム内で最も適切なエージェントに自動的にルーティング（`auto flow`）できるようにします。
*   ✅ **メモリのためのセッション状態：** `Session State`と`ToolContext`を利用して、エージェントが会話のターンを越えて情報を記憶できるようにし、より文脈に沿ったインタラクションを実現します。
*   ✅ **コールバックによる安全ガードレール：** `before_model_callback`と`before_tool_callback`を実装して、事前定義されたルールに基づいてリクエストやツールの使用を検査、変更、またはブロックし、アプリケーションの安全性と制御を強化します。

**最終的な目標：**

このチュートリアルを完了することで、あなたは機能的なマルチエージェントの天気ボットシステムを構築します。このシステムは、天気情報を提供するだけでなく、会話の丁寧なやり取りを処理し、最後にチェックした都市を記憶し、定義された安全境界内で動作し、すべてADKを使用してオーケストレーションされます。

**前提条件：**

*   ✅ **Pythonプログラミングの確かな理解。**
*   ✅ **大規模言語モデル（LLM）、API、およびエージェントの概念に精通していること。**
*   ❗ **重要：ADKクイックスタートチュートリアルの完了、またはADKの基本（Agent, Runner, SessionService, 基本的なツールの使用法）に関する同等の基礎知識。** このチュートリアルは、これらの概念の上に直接構築されます。
*   ✅ 使用するLLMの**APIキー**（例：Gemini用のGoogle AI Studio、OpenAI Platform、Anthropic Console）。


---

**実行環境に関する注意：**

このチュートリアルは、Google Colab、Colab Enterprise、またはJupyterノートブックのようなインタラクティブなノートブック環境向けに構成されています。以下の点に留意してください：

*   **非同期コードの実行：** ノートブック環境は非同期コードを異なる方法で扱います。`await`（イベントループが既に実行中の場合、ノートブックで一般的）や`asyncio.run()`（スタンドアロンの`.py`スクリプトとして実行する場合や特定のノートブック設定で必要）を使用した例が表示されます。コードブロックは両方のシナリオのガイダンスを提供します。
*   **手動でのRunner/Sessionセットアップ：** 手順には、`Runner`と`SessionService`インスタンスを明示的に作成することが含まれます。このアプローチは、エージェントの実行ライフサイクル、セッション管理、および状態の永続化をきめ細かく制御できるため、示されています。

**代替案：ADKの組み込みツール（Web UI / CLI / APIサーバー）の使用**

ADKの標準ツールを使用してランナーとセッション管理を自動的に処理するセットアップを好む場合は、その目的で構成された同等のコードを[こちら](https://github.com/google/adk-docs/tree/main/examples/python/tutorial/agent_team/adk-tutorial)で見つけることができます。そのバージョンは、`adk web`（Web UI用）、`adk run`（CLIインタラクション用）、または`adk api_server`（APIを公開するため）のようなコマンドで直接実行するように設計されています。その代替リソースで提供されている`README.md`の指示に従ってください。

---

**エージェントチームを構築する準備はできましたか？さあ、始めましょう！**

> **注意：** このチュートリアルはadkバージョン1.0.0以上で動作します。

```python
# @title ステップ0：セットアップとインストール
# ADKとLiteLLMをインストールしてマルチモデルをサポート

!pip install google-adk -q
!pip install litellm -q

print("インストールが完了しました。")
```

```python
# @title 必要なライブラリのインポート
import os
import asyncio
from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm # マルチモデルサポート用
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.genai import types # メッセージのContent/Parts作成用

import warnings
# すべての警告を無視
warnings.filterwarnings("ignore")

import logging
logging.basicConfig(level=logging.ERROR)

print("ライブラリがインポートされました。")
```

```python
# @title APIキーの設定（実際のキーに置き換えてください！）

# --- 重要：プレースホルダーを実際のAPIキーに置き換えてください ---

# Gemini APIキー（Google AI Studioから取得：https://aistudio.google.com/app/apikey）
os.environ["GOOGLE_API_KEY"] = "YOUR_GOOGLE_API_KEY" # <--- 置き換えてください

# [オプション]
# OpenAI APIキー（OpenAI Platformから取得：https://platform.openai.com/api-keys）
os.environ['OPENAI_API_KEY'] = 'YOUR_OPENAI_API_KEY' # <--- 置き換えてください

# [オプション]
# Anthropic APIキー（Anthropic Consoleから取得：https://console.anthropic.com/settings/keys）
os.environ['ANTHROPIC_API_KEY'] = 'YOUR_ANTHROPIC_API_KEY' # <--- 置き換えてください

# --- キーの確認（オプションのチェック） ---
print("APIキー設定：")
print(f"Google APIキー設定済み：{'はい' if os.environ.get('GOOGLE_API_KEY') and os.environ['GOOGLE_API_KEY'] != 'YOUR_GOOGLE_API_KEY' else 'いいえ（プレースホルダーを置き換えてください！）'}")
print(f"OpenAI APIキー設定済み：{'はい' if os.environ.get('OPENAI_API_KEY') and os.environ['OPENAI_API_KEY'] != 'YOUR_OPENAI_API_KEY' else 'いいえ（プレースホルダーを置き換えてください！）'}")
print(f"Anthropic APIキー設定済み：{'はい' if os.environ.get('ANTHROPIC_API_KEY') and os.environ['ANTHROPIC_API_KEY'] != 'YOUR_ANTHROPIC_API_KEY' else 'いいえ（プレースホルダーを置き換えてください！）'}")

# ADKが直接APIキーを使用するように設定（このマルチモデル設定ではVertex AIは使用しない）
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "False"


# @markdown **セキュリティノート：** APIキーは、ノートブックに直接ハードコーディングするのではなく、安全に管理する（例：Colabのシークレット機能や環境変数を使用する）ことがベストプラクティスです。上記のプレースホルダー文字列を置き換えてください。
```

```python
# --- 使いやすいようにモデル定数を定義 ---

# サポートされているモデルの詳細はここで参照できます：https://ai.google.dev/gemini-api/docs/models#model-variations
MODEL_GEMINI_2_0_FLASH = "gemini-2.0-flash"

# サポートされているモデルの詳細はここで参照できます：https://docs.litellm.ai/docs/providers/openai#openai-chat-completion-models
MODEL_GPT_4O = "openai/gpt-4.1" # gpt-4.1-mini, gpt-4oなども試せます

# サポートされているモデルの詳細はここで参照できます：https://docs.litellm.ai/docs/providers/anthropic
MODEL_CLAUDE_SONNET = "anthropic/claude-sonnet-4-20250514" # claude-opus-4-20250514 , claude-3-7-sonnet-20250219なども試せます

print("\n環境が設定されました。")
```

---

## ステップ1：最初のエージェント - 基本的な天気の検索

天気ボットの基本的なコンポーネント、つまり特定のタスク（天気情報の検索）を実行できる単一のエージェントを構築することから始めましょう。これには、2つの主要な部分を作成することが含まれます：

1. **ツール：** エージェントに天気のデータを取得する*能力*を与えるPython関数。
2. **エージェント：** ユーザーのリクエストを理解し、天気ツールを持っていることを知り、いつどのようにそれを使用するかを決定するAIの「頭脳」。

---

**1. ツールの定義 (`get_weather`)**

ADKにおいて、**ツール**はエージェントに単なるテキスト生成を超えた具体的な能力を与える構成要素です。これらは通常、APIの呼び出し、データベースのクエリ、計算の実行など、特定のアクションを実行する通常のPython関数です。

最初のツールは、*模擬的な*天気予報を提供します。これにより、まだ外部のAPIキーを必要とせずにエージェントの構造に集中できます。後で、この模擬関数を実際の天気サービスを呼び出すものに簡単に交換できます。

**重要なコンセプト：docstringは非常に重要です！** エージェントのLLMは、関数の**docstring**に大きく依存して以下を理解します：

* ツールが*何をするか*。
* *いつ*それを使用するか。
* *どの引数*が必要か（`city: str`）。
* *どのような情報*を返すか。

**ベストプラクティス：** ツールには、明確で、説明的で、正確なdocstringを記述してください。これはLLMがツールを正しく使用するために不可欠です。

```python
# @title get_weatherツールを定義
def get_weather(city: str) -> dict:
    """指定された都市の現在の天気予報を取得します。

    Args:
        city (str): 都市の名前（例："New York", "London", "Tokyo"）。

    Returns:
        dict: 天気情報を含む辞書。
              'status'キー（'success'または'error'）を含む。
              'success'の場合、天気詳細を持つ'report'キーを含む。
              'error'の場合、'error_message'キーを含む。
    """
    print(f"--- ツール：get_weatherが都市：{city}で呼び出されました ---") # ツールの実行をログに記録
    city_normalized = city.lower().replace(" ", "") # 基本的な正規化

    # 模擬的な天気データ
    mock_weather_db = {
        "newyork": {"status": "success", "report": "ニューヨークの天気は晴れで、気温は25℃です。"},
        "london": {"status": "success", "report": "ロンドンは曇りで、気温は15℃です。"},
        "tokyo": {"status": "success", "report": "東京は小雨で、気温は18℃です。"},
    }

    if city_normalized in mock_weather_db:
        return mock_weather_db[city_normalized]
    else:
        return {"status": "error", "error_message": f"申し訳ありませんが、'{city}'の天気情報はありません。"}

# ツールの使用例（オプションのテスト）
print(get_weather("New York"))
print(get_weather("Paris"))
```

---

**2. エージェントの定義 (`weather_agent`)**

次に、**エージェント**自体を作成しましょう。ADKの`Agent`は、ユーザー、LLM、および利用可能なツール間のインタラクションを調整します。

いくつかの重要なパラメータで設定します：

* `name`: このエージェントの一意の識別子（例："weather_agent_v1"）。
* `model`: 使用するLLMを指定します（例：`MODEL_GEMINI_2_0_FLASH`）。まず特定のGeminiモデルから始めます。
* `description`: エージェントの全体的な目的の簡潔な要約。これは後で他のエージェントが*この*エージェントにタスクを委任するかどうかを決定する必要がある場合に重要になります。
* `instruction`: LLMに対する振る舞い、ペルソナ、目標、そして特に割り当てられた`tools`を*どのように、いつ*利用するかに関する詳細なガイダンス。
* `tools`: エージェントが使用を許可されている実際のPythonツール関数のリスト（例：`[get_weather]`）。

**ベストプラクティス：** 明確で具体的な`instruction`プロンプトを提供してください。指示が詳細であればあるほど、LLMはその役割とツールの使用方法をよりよく理解できます。必要であればエラーハンドリングについて明示的に記述してください。

**ベストプラクティス：** 説明的な`name`と`description`の値を選択してください。これらはADKによって内部的に使用され、自動委任（後述）のような機能にとって不可欠です。

```python
# @title 天気エージェントを定義
# 先に定義したモデル定数のいずれかを使用
AGENT_MODEL = MODEL_GEMINI_2_0_FLASH # Geminiから始める

weather_agent = Agent(
    name="weather_agent_v1",
    model=AGENT_MODEL, # Geminiの場合は文字列、またはLiteLlmオブジェクト
    description="特定の都市の天気情報を提供します。",
    instruction="あなたは親切な天気アシスタントです。"
                "ユーザーが特定の都市の天気を尋ねたときは、"
                "'get_weather'ツールを使って情報を見つけてください。"
                "ツールがエラーを返した場合は、ユーザーに丁寧に伝えてください。"
                "ツールが成功した場合は、天気予報を明確に提示してください。",
    tools=[get_weather], # 関数を直接渡す
)

print(f"エージェント'{weather_agent.name}'がモデル'{AGENT_MODEL}'を使用して作成されました。")
```

---

**3. RunnerとSession Serviceのセットアップ**

会話を管理し、エージェントを実行するために、さらに2つのコンポーネントが必要です：

* `SessionService`: 異なるユーザーやセッションの会話履歴と状態を管理する責任があります。`InMemorySessionService`は、すべてをメモリに保存する簡単な実装で、テストや単純なアプリケーションに適しています。交換されたメッセージを追跡します。ステップ4で状態の永続化について詳しく探ります。
* `Runner`: インタラクションフローを調整するエンジンです。ユーザー入力を受け取り、適切なエージェントにルーティングし、エージェントのロジックに基づいてLLMとツールへの呼び出しを管理し、`SessionService`を介してセッションの更新を処理し、インタラクションの進行状況を表すイベントを生成します。

```python
# @title Session ServiceとRunnerのセットアップ

# --- セッション管理 ---
# 重要なコンセプト：SessionServiceは会話履歴と状態を保存します。
# InMemorySessionServiceはこのチュートリアルのための単純で非永続的なストレージです。
session_service = InMemorySessionService()

# インタラクションコンテキストを識別するための定数を定義
APP_NAME = "weather_tutorial_app"
USER_ID = "user_1"
SESSION_ID = "session_001" # 簡単のため固定IDを使用

# 会話が行われる特定のセッションを作成
session = await session_service.create_session(
    app_name=APP_NAME,
    user_id=USER_ID,
    session_id=SESSION_ID
)
print(f"セッションが作成されました：App='{APP_NAME}', User='{USER_ID}', Session='{SESSION_ID}'")

# --- Runner ---
# 重要なコンセプト：Runnerはエージェントの実行ループを調整します。
runner = Runner(
    agent=weather_agent, # 実行したいエージェント
    app_name=APP_NAME,   # 実行をアプリに関連付ける
    session_service=session_service # セッションマネージャーを使用
)
print(f"Runnerがエージェント'{runner.agent.name}'のために作成されました。")
```

---

**4. エージェントとの対話**

エージェントにメッセージを送信し、その応答を受け取る方法が必要です。LLMの呼び出しやツールの実行には時間がかかることがあるため、ADKの`Runner`は非同期で動作します。

`async`ヘルパー関数（`call_agent_async`）を定義します。この関数は：

1. ユーザーのクエリ文字列を受け取ります。
2. それをADKの`Content`形式にパッケージ化します。
3. `runner.run_async`を呼び出し、ユーザー/セッションのコンテキストと新しいメッセージを提供します。
4. ランナーによって生成される**イベント**を反復処理します。イベントはエージェントの実行におけるステップ（例：ツール呼び出し要求、ツール結果受信、中間的なLLMの思考、最終応答）を表します。
5. `event.is_final_response()`を使用して**最終応答**イベントを識別し、出力します。

**なぜ`async`なのか？** LLMや潜在的なツール（外部APIなど）とのインタラクションはI/Oバウンドな操作です。`asyncio`を使用すると、プログラムは実行をブロックすることなくこれらの操作を効率的に処理できます。

```python
# @title エージェント対話関数を定義

from google.genai import types # メッセージのContent/Parts作成用

async def call_agent_async(query: str, runner, user_id, session_id):
  """エージェントにクエリを送信し、最終応答を出力します。"""
  print(f"\n>>> ユーザーのクエリ：{query}")

  # ユーザーのメッセージをADK形式で準備
  content = types.Content(role='user', parts=[types.Part(text=query)])

  final_response_text = "エージェントは最終応答を生成しませんでした。" # デフォルト

  # 重要なコンセプト：run_asyncはエージェントのロジックを実行し、イベントを生成します。
  # イベントを反復処理して最終的な答えを見つけます。
  async for event in runner.run_async(user_id=user_id, session_id=session_id, new_message=content):
      # 以下の行のコメントを外すと、実行中の*すべて*のイベントを見ることができます
      # print(f"  [イベント] Author: {event.author}, Type: {type(event).__name__}, Final: {event.is_final_response()}, Content: {event.content}")

      # 重要なコンセプト：is_final_response()はターンの結論となるメッセージをマークします。
      if event.is_final_response():
          if event.content and event.content.parts:
             # 最初のパートにテキスト応答があると仮定
             final_response_text = event.content.parts.text
          elif event.actions and event.actions.escalate: # 潜在的なエラー/エスカレーションを処理
             final_response_text = f"エージェントがエスカレーションしました：{event.error_message or '特定のエラーメッセージはありません。'}"
          # 必要に応じてここに追加のチェックを追加（例：特定のエラーコード）
          break # 最終応答が見つかったらイベントの処理を停止

  print(f"<<< エージェントの応答：{final_response_text}")
```

---

**5. 会話の実行**

最後に、エージェントにいくつかのクエリを送信してセットアップをテストしましょう。`async`呼び出しをメインの`async`関数でラップし、`await`を使用して実行します。

出力を観察してください：

* ユーザーのクエリが表示されます。
* エージェントがツールを使用すると`--- ツール：get_weatherが呼び出されました... ---`のログが表示されます。
* 天気データが利用できない場合（パリの場合）の処理方法を含む、エージェントの最終応答を観察してください。

```python
# @title 初回の会話を実行

# 対話ヘルパーを待機するためにasync関数が必要
async def run_conversation():
    await call_agent_async("ロンドンの天気はどうですか？",
                                       runner=runner,
                                       user_id=USER_ID,
                                       session_id=SESSION_ID)

    await call_agent_async("パリはどうですか？",
                                       runner=runner,
                                       user_id=USER_ID,
                                       session_id=SESSION_ID) # ツールのエラーメッセージを期待

    await call_agent_async("ニューヨークの天気を教えて",
                                       runner=runner,
                                       user_id=USER_ID,
                                       session_id=SESSION_ID)

# asyncコンテキスト（Colab/Jupyterなど）でawaitを使用して会話を実行
await run_conversation()

# --- または ---

# 標準のPythonスクリプト（.pyファイル）として実行する場合は、以下の行のコメントを外してください：
# import asyncio
# if __name__ == "__main__":
#     try:
#         asyncio.run(run_conversation())
#     except Exception as e:
#         print(f"エラーが発生しました：{e}")
```

---

おめでとうございます！これで最初のADKエージェントを正常に構築し、対話することができました。それはユーザーのリクエストを理解し、ツールを使って情報を見つけ、ツールの結果に基づいて適切に応答します。

次のステップでは、このエージェントを動かす基盤となる言語モデルを簡単に切り替える方法を探ります。

## ステップ2：LiteLLMでマルチモデル化 [オプション]

ステップ1では、特定のGeminiモデルを搭載した機能的な天気エージェントを構築しました。効果的ではありますが、実世界のアプリケーションでは、しばしば*異なる*大規模言語モデル（LLM）を使用する柔軟性が役立ちます。なぜでしょうか？

*   **パフォーマンス：** 特定のタスク（例：コーディング、推論、創造的な執筆）に優れたモデルがあります。
*   **コスト：** モデルによって価格帯が異なります。
*   **能力：** モデルは多様な機能、コンテキストウィンドウサイズ、ファインチューニングオプションを提供します。
*   **可用性/冗長性：** 代替手段を持つことで、あるプロバイダーで問題が発生してもアプリケーションが機能し続けることが保証されます。

ADKは、[**LiteLLM**](https://github.com/BerriAI/litellm)ライブラリとの統合を通じて、モデル間の切り替えをシームレスにします。LiteLLMは、100以上の異なるLLMへの一貫したインターフェースとして機能します。

**このステップでは、以下のことを行います：**

1.  ADKの`Agent`を、`LiteLlm`ラッパーを使用してOpenAI（GPT）やAnthropic（Claude）などのプロバイダーのモデルを使用するように設定する方法を学びます。
2.  それぞれが異なるLLMに支えられた天気エージェントのインスタンスを定義、設定（独自のセッションとランナーで）し、すぐにテストします。
3.  これらの異なるエージェントと対話し、同じ基盤となるツールを使用していても、応答に潜在的なバリエーションがあることを観察します。

---

**1. `LiteLlm`のインポート**

これは初期セットアップ（ステップ0）中にインポートしましたが、マルチモデルサポートの重要なコンポーネントです：

```python
# @title 1. LiteLlmをインポート
from google.adk.models.lite_llm import LiteLlm
```

**2. マルチモデルエージェントの定義とテスト**

モデル名の文字列だけを渡す（これはGoogleのGeminiモデルにデフォルト設定されます）代わりに、目的のモデル識別子文字列を`LiteLlm`クラスでラップします。

*   **重要なコンセプト：`LiteLlm`ラッパー：** `LiteLlm(model="provider/model_name")`という構文は、このエージェントへのリクエストをLiteLLMライブラリ経由で指定されたモデルプロバイダーにルーティングするようADKに伝えます。

ステップ0でOpenAIとAnthropicに必要なAPIキーを設定したことを確認してください。以前に定義した`call_agent_async`関数（現在は`runner`、`user_id`、`session_id`を受け入れます）を使用して、各エージェントのセットアップ直後に対話します。

以下の各ブロックは：

*   特定のLiteLLMモデル（`MODEL_GPT_4O`または`MODEL_CLAUDE_SONNET`）を使用してエージェントを定義します。
*   そのエージェントのテストラン専用に、*新しく、別の*`InMemorySessionService`とセッションを作成します。これにより、このデモンストレーションのために会話履歴が分離されます。
*   特定のエージェントとそのセッションサービス用に設定された`Runner`を作成します。
*   すぐに`call_agent_async`を呼び出してクエリを送信し、エージェントをテストします。

**ベストプラクティス：** タイプミスを避け、コードを管理しやすくするために、モデル名には定数（ステップ0で定義した`MODEL_GPT_4O`、`MODEL_CLAUDE_SONNET`など）を使用してください。

**エラーハンドリング：** エージェントの定義を`try...except`ブロックでラップします。これにより、特定のプロバイダーのAPIキーがないか無効な場合にコードセル全体が失敗するのを防ぎ、*設定されている*モデルでチュートリアルを続行できます。

まず、OpenAIのGPT-4oを使用してエージェントを作成し、テストしましょう。

```python
# @title GPTエージェントの定義とテスト

# ステップ1の'get_weather'関数が環境で定義されていることを確認してください。
# 'call_agent_async'が以前から定義されていることを確認してください。

# --- GPT-4oを使用するエージェント ---
weather_agent_gpt = None # Noneに初期化
runner_gpt = None      # runnerをNoneに初期化

try:
    weather_agent_gpt = Agent(
        name="weather_agent_gpt",
        # 主要な変更点：LiteLLMモデル識別子をラップする
        model=LiteLlm(model=MODEL_GPT_4O),
        description="天気情報を提供します（GPT-4o使用）。",
        instruction="あなたはGPT-4oを搭載した親切な天気アシスタントです。"
                    "都市の天気の問い合わせには'get_weather'ツールを使用してください。"
                    "ツールの出力ステータスに基づいて、成功したレポートまたは丁寧なエラーメッセージを明確に提示してください。",
        tools=[get_weather], # 同じツールを再利用
    )
    print(f"エージェント'{weather_agent_gpt.name}'がモデル'{MODEL_GPT_4O}'を使用して作成されました。")

    # InMemorySessionServiceはこのチュートリアルのための単純で非永続的なストレージです。
    session_service_gpt = InMemorySessionService() # 専用のサービスを作成

    # インタラクションコンテキストを識別するための定数を定義
    APP_NAME_GPT = "weather_tutorial_app_gpt" # このテスト用の一意のアプリ名
    USER_ID_GPT = "user_1_gpt"
    SESSION_ID_GPT = "session_001_gpt" # 簡単のため固定IDを使用

    # 会話が行われる特定のセッションを作成
    session_gpt = await session_service_gpt.create_session(
        app_name=APP_NAME_GPT,
        user_id=USER_ID_GPT,
        session_id=SESSION_ID_GPT
    )
    print(f"セッションが作成されました：App='{APP_NAME_GPT}', User='{USER_ID_GPT}', Session='{SESSION_ID_GPT}'")

    # このエージェントとそのセッションサービスに特化したランナーを作成
    runner_gpt = Runner(
        agent=weather_agent_gpt,
        app_name=APP_NAME_GPT,       # 特定のアプリ名を使用
        session_service=session_service_gpt # 特定のセッションサービスを使用
        )
    print(f"Runnerがエージェント'{runner_gpt.agent.name}'のために作成されました。")

    # --- GPTエージェントのテスト ---
    print("\n--- GPTエージェントのテスト中 ---")
    # call_agent_asyncが正しいrunner, user_id, session_idを使用することを確認
    await call_agent_async(query = "東京の天気はどうですか？",
                           runner=runner_gpt,
                           user_id=USER_ID_GPT,
                           session_id=SESSION_ID_GPT)
    # --- または ---

    # 標準のPythonスクリプト（.pyファイル）として実行する場合は、以下の行のコメントを外してください：
    # import asyncio
    # if __name__ == "__main__":
    #     try:
    #         asyncio.run(call_agent_async(query = "東京の天気はどうですか？",
    #                      runner=runner_gpt,
    #                       user_id=USER_ID_GPT,
    #                       session_id=SESSION_ID_GPT))
    #     except Exception as e:
    #         print(f"エラーが発生しました：{e}")

except Exception as e:
    print(f"❌ GPTエージェント'{MODEL_GPT_4O}'を作成または実行できませんでした。APIキーとモデル名を確認してください。エラー：{e}")
```

次に、AnthropicのClaude Sonnetで同じことを行います。

```python
# @title Claudeエージェントの定義とテスト

# ステップ1の'get_weather'関数が環境で定義されていることを確認してください。
# 'call_agent_async'が以前から定義されていることを確認してください。

# --- Claude Sonnetを使用するエージェント ---
weather_agent_claude = None # Noneに初期化
runner_claude = None      # runnerをNoneに初期化

try:
    weather_agent_claude = Agent(
        name="weather_agent_claude",
        # 主要な変更点：LiteLLMモデル識別子をラップする
        model=LiteLlm(model=MODEL_CLAUDE_SONNET),
        description="天気情報を提供します（Claude Sonnet使用）。",
        instruction="あなたはClaude Sonnetを搭載した親切な天気アシスタントです。"
                    "都市の天気の問い合わせには'get_weather'ツールを使用してください。"
                    "ツールの辞書出力（'status', 'report'/'error_message'）を分析してください。"
                    "成功したレポートまたは丁寧なエラーメッセージを明確に提示してください。",
        tools=[get_weather], # 同じツールを再利用
    )
    print(f"エージェント'{weather_agent_claude.name}'がモデル'{MODEL_CLAUDE_SONNET}'を使用して作成されました。")

    # InMemorySessionServiceはこのチュートリアルのための単純で非永続的なストレージです。
    session_service_claude = InMemorySessionService() # 専用のサービスを作成

    # インタラクションコンテキストを識別するための定数を定義
    APP_NAME_CLAUDE = "weather_tutorial_app_claude" # 一意のアプリ名
    USER_ID_CLAUDE = "user_1_claude"
    SESSION_ID_CLAUDE = "session_001_claude" # 簡単のため固定IDを使用

    # 会話が行われる特定のセッションを作成
    session_claude = await session_service_claude.create_session(
        app_name=APP_NAME_CLAUDE,
        user_id=USER_ID_CLAUDE,
        session_id=SESSION_ID_CLAUDE
    )
    print(f"セッションが作成されました：App='{APP_NAME_CLAUDE}', User='{USER_ID_CLAUDE}', Session='{SESSION_ID_CLAUDE}'")

    # このエージェントとそのセッションサービスに特化したランナーを作成
    runner_claude = Runner(
        agent=weather_agent_claude,
        app_name=APP_NAME_CLAUDE,       # 特定のアプリ名を使用
        session_service=session_service_claude # 特定のセッションサービスを使用
        )
    print(f"Runnerがエージェント'{runner_claude.agent.name}'のために作成されました。")

    # --- Claudeエージェントのテスト ---
    print("\n--- Claudeエージェントのテスト中 ---")
    # call_agent_asyncが正しいrunner, user_id, session_idを使用することを確認
    await call_agent_async(query = "ロンドンの天気を教えてください。",
                           runner=runner_claude,
                           user_id=USER_ID_CLAUDE,
                           session_id=SESSION_ID_CLAUDE)

    # --- または ---

    # 標準のPythonスクリプト（.pyファイル）として実行する場合は、以下の行のコメントを外してください：
    # import asyncio
    # if __name__ == "__main__":
    #     try:
    #         asyncio.run(call_agent_async(query = "ロンドンの天気を教えてください。",
    #                      runner=runner_claude,
    #                       user_id=USER_ID_CLAUDE,
    #                       session_id=SESSION_ID_CLAUDE))
    #     except Exception as e:
    #         print(f"エラーが発生しました：{e}")

except Exception as e:
    print(f"❌ Claudeエージェント'{MODEL_CLAUDE_SONNET}'を作成または実行できませんでした。APIキーとモデル名を確認してください。エラー：{e}")
```

両方のコードブロックからの出力を注意深く見てください。以下が確認できるはずです：

1.  各エージェント（`weather_agent_gpt`、`weather_agent_claude`）が正常に作成されます（APIキーが有効な場合）。
2.  それぞれに専用のセッションとランナーがセットアップされます。
3.  各エージェントは、クエリを処理する際に`get_weather`ツールを使用する必要があることを正しく識別します（`--- ツール：get_weatherが呼び出されました... ---`のログが表示されます）。
4.  *基盤となるツールのロジック*は同一であり、常に私たちの模擬データを返します。
5.  しかし、各エージェントによって生成される**最終的なテキスト応答**は、言い回し、トーン、またはフォーマットがわずかに異なる場合があります。これは、指示プロンプトが異なるLLM（GPT-4o対Claude Sonnet）によって解釈および実行されるためです。

このステップは、ADKとLiteLLMが提供するパワーと柔軟性を示しています。コアアプリケーションロジック（ツール、基本的なエージェント構造）を一貫させながら、さまざまなLLMを使用してエージェントを簡単に実験およびデプロイできます。

次のステップでは、単一のエージェントを超えて、エージェントが互いにタスクを委任できる小さなチームを構築します！

---

## ステップ3：エージェントチームの構築 - 挨拶と別れの委任

ステップ1と2では、天気の検索のみに焦点を当てた単一のエージェントを構築し、実験しました。その特定のタスクには効果的ですが、実世界のアプリケーションでは、より多様なユーザーインタラクションを処理する必要があります。単一の天気エージェントにツールを追加し続け、複雑な指示を与えることもできますが、これはすぐに管理が困難になり、効率が低下する可能性があります。

より堅牢なアプローチは、**エージェントチーム**を構築することです。これには以下が含まれます：

1.  それぞれが特定の能力（例：天気用、挨拶用、計算用）のために設計された、複数の**専門エージェント**を作成する。
2.  最初のユーザーリクエストを受け取る**ルートエージェント**（またはオーケストレーター）を指定する。
3.  ユーザーの意図に基づいて、ルートエージェントがリクエストを最も適切な専門サブエージェントに**委任**できるようにする。

**なぜエージェントチームを構築するのか？**

*   **モジュール性：** 個々のエージェントの開発、テスト、保守が容易になります。
*   **専門化：** 各エージェントは、その特定のタスクに合わせて（指示、モデル選択）微調整できます。
*   **スケーラビリティ：** 新しいエージェントを追加することで、新しい機能を簡単に追加できます。
*   **効率性：** より単純なタスク（挨拶など）には、潜在的により単純/安価なモデルを使用できます。

**このステップでは、以下のことを行います：**

1.  挨拶（`say_hello`）と別れ（`say_goodbye`）を処理するための簡単なツールを定義します。
2.  2つの新しい専門サブエージェントを作成します：`greeting_agent`と`farewell_agent`。
3.  メインの天気エージェント（`weather_agent_v2`）を**ルートエージェント**として機能するように更新します。
4.  ルートエージェントをそのサブエージェントで設定し、**自動委任**を有効にします。
5.  ルートエージェントに異なるタイプのリクエストを送信して、委任フローをテストします。

---

**1. サブエージェント用のツールの定義**

まず、新しい専門エージェントのツールとして機能する簡単なPython関数を作成しましょう。明確なdocstringが、それらを使用するエージェントにとって不可欠であることを忘れないでください。

```python
# @title 挨拶および別れエージェント用のツールを定義
from typing import Optional # Optionalを必ずインポート

# このステップを独立して実行する場合、ステップ1の'get_weather'が利用可能であることを確認してください。
# def get_weather(city: str) -> dict: ... (ステップ1から)

def say_hello(name: Optional[str] = None) -> str:
    """簡単な挨拶を提供します。名前が提供された場合は、それを使用します。

    Args:
        name (str, optional): 挨拶する人の名前。提供されない場合は、一般的な挨拶にデフォルト設定されます。

    Returns:
        str: 親しみやすい挨拶メッセージ。
    """
    if name:
        greeting = f"こんにちは、{name}！"
        print(f"--- ツール：say_helloが名前：{name}で呼び出されました ---")
    else:
        greeting = "こんにちは！" # nameがNoneまたは明示的に渡されない場合のデフォルトの挨拶
        print(f"--- ツール：say_helloが特定の名前なしで呼び出されました (name_arg_value: {name}) ---")
    return greeting

def say_goodbye() -> str:
    """会話を締めくくるための簡単な別れのメッセージを提供します。"""
    print(f"--- ツール：say_goodbyeが呼び出されました ---")
    return "さようなら！良い一日を。"

print("挨拶と別れのツールが定義されました。")

# オプションの自己テスト
print(say_hello("アリス"))
print(say_hello()) # 引数なしでテスト（デフォルトの「こんにちは！」を使用するはず）
print(say_hello(name=None)) # nameを明示的にNoneとしてテスト（デフォルトの「こんにちは！」を使用するはず）
```

---

**2. サブエージェントの定義（挨拶と別れ）**

次に、専門家たちの`Agent`インスタンスを作成します。彼らの非常に焦点の合った`instruction`と、決定的に重要な、明確な`description`に注目してください。`description`は、*ルートエージェント*がこれらのサブエージェントに*いつ*委任するかを決定するために使用する主要な情報です。

**ベストプラクティス：** サブエージェントの`description`フィールドは、その特定の能力を正確かつ簡潔に要約する必要があります。これは効果的な自動委任のために非常に重要です。

**ベストプラクティス：** サブエージェントの`instruction`フィールドは、その限られた範囲に合わせて調整し、何をすべきか、そして*何をすべきでないか*を正確に伝えるべきです（例：「あなたの*唯一の*タスクは...」）。

```python
# @title 挨拶および別れサブエージェントの定義

# Gemini以外のモデルを使用したい場合は、LiteLlmがインポートされ、APIキーが設定されていることを確認してください（ステップ0/2から）
# from google.adk.models.lite_llm import LiteLlm
# MODEL_GPT_4O, MODEL_CLAUDE_SONNETなどが定義されている必要があります
# そうでない場合は、引き続きmodel = MODEL_GEMINI_2_0_FLASHを使用します

# --- 挨拶エージェント ---
greeting_agent = None
try:
    greeting_agent = Agent(
        # 簡単なタスクには潜在的に異なる/安価なモデルを使用
        model = MODEL_GEMINI_2_0_FLASH,
        # model=LiteLlm(model=MODEL_GPT_4O), # 他のモデルで実験したい場合
        name="greeting_agent",
        instruction="あなたは挨拶エージェントです。あなたの唯一のタスクは、ユーザーに親しみやすい挨拶を提供することです。"
                    "'say_hello'ツールを使用して挨拶を生成してください。"
                    "ユーザーが名前を教えた場合は、必ずそれをツールに渡してください。"
                    "他の会話やタスクには一切関与しないでください。",
        description="'say_hello'ツールを使用して簡単な挨拶を処理します。", # 委任に重要
        tools=[say_hello],
    )
    print(f"✅ エージェント'{greeting_agent.name}'がモデル'{greeting_agent.model}'を使用して作成されました。")
except Exception as e:
    print(f"❌ 挨拶エージェントを作成できませんでした。APIキーを確認してください（{greeting_agent.model}）。エラー：{e}")

# --- 別れエージェント ---
farewell_agent = None
try:
    farewell_agent = Agent(
        # 同じか異なるモデルを使用可能
        model = MODEL_GEMINI_2_0_FLASH,
        # model=LiteLlm(model=MODEL_GPT_4O), # 他のモデルで実験したい場合
        name="farewell_agent",
        instruction="あなたは別れエージェントです。あなたの唯一のタスクは、丁寧なさようならのメッセージを提供することです。"
                    "ユーザーが会話を終了することを示した場合（例：「バイバイ」、「さようなら」、「ありがとう、バイバイ」、「またね」など）、"
                    "'say_goodbye'ツールを使用してください。"
                    "他のアクションは一切実行しないでください。",
        description="'say_goodbye'ツールを使用して簡単な別れを処理します。", # 委任に重要
        tools=[say_goodbye],
    )
    print(f"✅ エージェント'{farewell_agent.name}'がモデル'{farewell_agent.model}'を使用して作成されました。")
except Exception as e:
    print(f"❌ 別れエージェントを作成できませんでした。APIキーを確認してください（{farewell_agent.model}）。エラー：{e}")
```

---

**3. ルートエージェントの定義（天気エージェントv2）とサブエージェント**

次に、`weather_agent`をアップグレードします。主な変更点は次のとおりです：

* `sub_agents`パラメータの追加：作成した`greeting_agent`と`farewell_agent`のインスタンスを含むリストを渡します。
* `instruction`の更新：ルートエージェントに、そのサブエージェントについて、そして*いつ*タスクを委任すべきかを明示的に伝えます。

**重要なコンセプト：自動委任（Auto Flow）** `sub_agents`リストを提供することで、ADKは自動委任を有効にします。ルートエージェントがユーザーのクエリを受け取ると、そのLLMは自身の指示とツールだけでなく、各サブエージェントの`description`も考慮します。LLMがクエリがサブエージェントの記述された能力（例：「簡単な挨拶を処理します」）によりよく一致すると判断した場合、自動的にそのターンで*制御をそのサブエージェントに移す*ための特別な内部アクションを生成します。その後、サブエージェントは自身のモデル、指示、ツールを使用してクエリを処理します。

**ベストプラクティス：** ルートエージェントの指示が、その委任決定を明確に導くようにしてください。サブエージェントを名前で言及し、委任が発生すべき条件を説明してください。

```python
# @title サブエージェントを持つルートエージェントを定義

# ルートエージェントを定義する前に、サブエージェントが正常に作成されたことを確認してください。
# また、元の'get_weather'ツールが定義されていることを確認してください。
root_agent = None
runner_root = None # runnerを初期化

if greeting_agent and farewell_agent and 'get_weather' in globals():
    # オーケストレーションを処理するために、ルートエージェントには高性能なGeminiモデルを使用しましょう
    root_agent_model = MODEL_GEMINI_2_0_FLASH

    weather_agent_team = Agent(
        name="weather_agent_v2", # 新しいバージョン名を付ける
        model=root_agent_model,
        description="メインのコーディネーターエージェント。天気のリクエストを処理し、挨拶/別れを専門家に委任します。",
        instruction="あなたはチームを調整するメインの天気エージェントです。あなたの主な責任は天気情報を提供することです。"
                    "特定の天気のリクエスト（例：「ロンドンの天気」）にのみ'get_weather'ツールを使用してください。"
                    "あなたには専門のサブエージェントがいます："
                    "1. 'greeting_agent': 「こんにちは」「もしもし」のような簡単な挨拶を処理します。これらには委任してください。"
                    "2. 'farewell_agent': 「さようなら」「またね」のような簡単な別れを処理します。これらには委任してください。"
                    "ユーザーのクエリを分析してください。それが挨拶なら'greeting_agent'に委任し、別れなら'farewell_agent'に委任してください。"
                    "それが天気のリクエストなら、'get_weather'を使って自分で処理してください。"
                    "それ以外のものについては、適切に応答するか、処理できないと述べてください。",
        tools=[get_weather], # ルートエージェントはまだそのコアタスクのために天気ツールが必要です
        # 主要な変更点：ここでサブエージェントをリンクします！
        sub_agents=[greeting_agent, farewell_agent]
    )
    print(f"✅ ルートエージェント'{weather_agent_team.name}'がモデル'{root_agent_model}'とサブエージェント：{[sa.name for sa in weather_agent_team.sub_agents]}で作成されました。")

else:
    print("❌ 1つ以上のサブエージェントの初期化に失敗したか、'get_weather'ツールが見つからないため、ルートエージェントを作成できません。")
    if not greeting_agent: print(" - 挨拶エージェントが見つかりません。")
    if not farewell_agent: print(" - 別れエージェントが見つかりません。")
    if 'get_weather' not in globals(): print(" - get_weather関数が見つかりません。")
```

---

**4. エージェントチームとの対話**

専門のサブエージェントを持つルートエージェント（`weather_agent_team` - *注意：この変数名が、前のコードブロック、おそらく`# @title Define the Root Agent with Sub-Agents`で定義されたものと一致することを確認してください。そこでは`root_agent`と名付けられている可能性があります*）を定義したので、委任メカニズムをテストしましょう。

次のコードブロックは：

1.  `async`関数`run_team_conversation`を定義します。
2.  この関数内で、このテストラン専用に*新しく、専用の*`InMemorySessionService`と特定のセッション（`session_001_agent_team`）を作成します。これにより、チームのダイナミクスをテストするために会話履歴が分離されます。
3.  私たちの`weather_agent_team`（ルートエージェント）と専用のセッションサービスを使用するように設定された`Runner`（`runner_agent_team`）を作成します。
4.  更新された`call_agent_async`関数を使用して、異なるタイプのクエリ（挨拶、天気のリクエスト、別れ）を`runner_agent_team`に送信します。この特定のテストのために、ランナー、ユーザーID、セッションIDを明示的に渡します。
5.  すぐに`run_team_conversation`関数を実行します。

以下のフローを期待しています：

1.  「こんにちは！」というクエリが`runner_agent_team`に送られます。
2.  ルートエージェント（`weather_agent_team`）がそれを受け取り、その指示と`greeting_agent`の`description`に基づいてタスクを委任します。
3.  `greeting_agent`がクエリを処理し、その`say_hello`ツールを呼び出し、応答を生成します。
4.  「ニューヨークの天気は？」というクエリは委任されず、ルートエージェントが直接`get_weather`ツールを使用して処理します。
5.  「ありがとう、さようなら！」というクエリは`farewell_agent`に委任され、`say_goodbye`ツールが使用されます。

```python
# @title エージェントチームとの対話
import asyncio # asyncioがインポートされていることを確認

# ルートエージェント（例：前のセルの'weather_agent_team'または'root_agent'）が定義されていることを確認してください。
# call_agent_async関数が定義されていることを確認してください。

# 会話関数を定義する前にルートエージェント変数が存在するかチェック
root_agent_var_name = 'root_agent' # ステップ3のガイドのデフォルト名
if 'weather_agent_team' in globals(): # ユーザーが代わりにこの名前を使ったかチェック
    root_agent_var_name = 'weather_agent_team'
elif 'root_agent' not in globals():
    print("⚠️ ルートエージェント（'root_agent'または'weather_agent_team'）が見つかりません。run_team_conversationを定義できません。")
    # コードブロックがそれでも実行される場合にNameErrorを防ぐためにダミー値を割り当てる
    root_agent = None # または実行を防ぐためのフラグを設定

# ルートエージェントが存在する場合のみ定義して実行
if root_agent_var_name in globals() and globals()[root_agent_var_name]:
    # 会話ロジックのためのメインのasync関数を定義します。
    # この関数内の'await'キーワードは非同期操作に必要です。
    async def run_team_conversation():
        print("\n--- エージェントチームの委任をテスト中 ---")
        session_service = InMemorySessionService()
        APP_NAME = "weather_tutorial_agent_team"
        USER_ID = "user_1_agent_team"
        SESSION_ID = "session_001_agent_team"
        session = await session_service.create_session(
            app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID
        )
        print(f"セッションが作成されました：App='{APP_NAME}', User='{USER_ID}', Session='{SESSION_ID}'")

        actual_root_agent = globals()[root_agent_var_name]
        runner_agent_team = Runner( # またはInMemoryRunnerを使用
            agent=actual_root_agent,
            app_name=APP_NAME,
            session_service=session_service
        )
        print(f"Runnerがエージェント'{actual_root_agent.name}'のために作成されました。")

        # --- awaitを使用したインタラクション（async def内では正しい） ---
        await call_agent_async(query = "こんにちは！",
                               runner=runner_agent_team,
                               user_id=USER_ID,
                               session_id=SESSION_ID)
        await call_agent_async(query = "ニューヨークの天気は？",
                               runner=runner_agent_team,
                               user_id=USER_ID,
                               session_id=SESSION_ID)
        await call_agent_async(query = "ありがとう、さようなら！",
                               runner=runner_agent_team,
                               user_id=USER_ID,
                               session_id=SESSION_ID)

    # --- `run_team_conversation` async関数を実行 ---
    # 環境に応じて以下のいずれかの方法を選択してください。
    # 注意：これには使用するモデルのAPIキーが必要な場合があります！

    # 方法1：直接await（ノートブック/Async REPLのデフォルト）
    # 環境がトップレベルawaitをサポートしている場合（Colab/Jupyterノートブックなど）、
    # イベントループが既に実行中であることを意味するので、直接関数をawaitできます。
    print("'await'を使用した実行を試みています（ノートブックのデフォルト）...")
    await run_team_conversation()

    # 方法2：asyncio.run（標準のPythonスクリプト[.py]用）
    # このコードをターミナルから標準のPythonスクリプトとして実行する場合、
    # スクリプトコンテキストは同期的です。async関数を実行するためにイベントループを作成・管理するには
    # `asyncio.run()`が必要です。
    # この方法を使用するには：
    # 1. 上の`await run_team_conversation()`行をコメントアウトします。
    # 2. 以下のブロックのコメントを外します：
    """
    import asyncio
    if __name__ == "__main__": # スクリプトが直接実行されたときのみ実行されるようにする
        print("'asyncio.run()'を使用した実行（標準Pythonスクリプト用）...")
        try:
            # これはイベントループを作成し、async関数を実行し、ループを閉じます。
            asyncio.run(run_team_conversation())
        except Exception as e:
            print(f"エラーが発生しました：{e}")
    """

else:
    # このメッセージは、ルートエージェント変数が見つからなかった場合に表示されます
    print("\n⚠️ 前のステップでルートエージェントが正常に定義されなかったため、エージェントチームの会話実行をスキップします。")
```

---

出力ログ、特に`--- ツール：...が呼び出されました ---`メッセージをよく見てください。以下が観察できるはずです：

*   「こんにちは！」に対して、`say_hello`ツールが呼び出されました（`greeting_agent`が処理したことを示します）。
*   「ニューヨークの天気は？」に対して、`get_weather`ツールが呼び出されました（ルートエージェントが処理したことを示します）。
*   「ありがとう、さようなら！」に対して、`say_goodbye`ツールが呼び出されました（`farewell_agent`が処理したことを示します）。

これは、**自動委任**が成功したことを確認します！ルートエージェントは、その指示と`sub_agents`の`description`に導かれ、ユーザーリクエストをチーム内の適切な専門エージェントに正しくルーティングしました。

これで、複数の協力するエージェントを持つアプリケーションを構築しました。このモジュール設計は、より複雑で能力の高いエージェントシステムを構築するための基本です。次のステップでは、セッション状態を使用してエージェントがターンを越えて情報を記憶する能力を与えます。

## ステップ4：セッション状態でメモリとパーソナライズを追加する

これまでのところ、私たちのエージェントチームは委任を通じてさまざまなタスクを処理できますが、各インタラクションはゼロから始まります。つまり、エージェントはセッション内の過去の会話やユーザーの好みを記憶していません。より洗練された、文脈を意識した体験を創出するためには、エージェントに**メモリ**が必要です。ADKは**セッション状態**を通じてこれを提供します。

**セッション状態とは？**

*   特定のユーザーセッション（`APP_NAME`、`USER_ID`、`SESSION_ID`で識別）に紐づけられたPython辞書（`session.state`）です。
*   そのセッション内の*複数の会話ターン*にわたって情報を**永続化**します。
*   エージェントとツールはこの状態を読み書きでき、詳細を記憶したり、振る舞いを適応させたり、応答をパーソナライズしたりできます。

**エージェントが状態と対話する方法：**

1.  **`ToolContext`（主要な方法）：** ツールは`ToolContext`オブジェクトを受け取ることができます（最後の引数として宣言されている場合、ADKによって自動的に提供されます）。このオブジェクトは`tool_context.state`を介してセッション状態への直接アクセスを提供し、ツールが実行*中*に設定を読み取ったり、結果を保存したりできるようにします。
2.  **`output_key`（エージェント応答の自動保存）：** `Agent`は`output_key="your_key"`で設定できます。これにより、ADKはターンのエージェントの最終的なテキスト応答を`session.state["your_key"]`に自動的に保存します。

**このステップでは、天気ボットチームを次のように強化します：**

1.  状態を分離して示すために**新しい**`InMemorySessionService`を使用します。
2.  `temperature_unit`のユーザー設定でセッション状態を初期化します。
3.  この設定を`ToolContext`を介して読み取り、出力形式（摂氏/華氏）を調整する、状態を意識したバージョンの天気ツール（`get_weather_stateful`）を作成します。
4.  この状態対応ツールを使用するようにルートエージェントを更新し、`output_key`を設定して最終的な天気予報をセッション状態に自動的に保存するようにします。
5.  会話を実行して、初期状態がツールにどのように影響するか、手動での状態変更が後続の振る舞いをどのように変えるか、そして`output_key`がエージェントの応答をどのように永続化するかを観察します。

---

**1. 新しいセッションサービスと状態の初期化**

以前のステップからの干渉なしに状態管理を明確に示すため、新しい`InMemorySessionService`をインスタンス化します。また、ユーザーの好みの温度単位を定義する初期状態でセッションを作成します。

```python
# @title 1. 新しいセッションサービスと状態の初期化

# 必要なセッションコンポーネントをインポート
from google.adk.sessions import InMemorySessionService

# この状態デモンストレーションのために新しいセッションサービスインスタンスを作成
session_service_stateful = InMemorySessionService()
print("✅ 状態デモンストレーション用に新しいInMemorySessionServiceが作成されました。")

# このチュートリアルのこの部分のために新しいセッションIDを定義
SESSION_ID_STATEFUL = "session_state_demo_001"
USER_ID_STATEFUL = "user_state_demo"

# 初期状態データを定義 - ユーザーは最初に摂氏を好む
initial_state = {
    "user_preference_temperature_unit": "Celsius"
}

# 初期状態を提供してセッションを作成
session_stateful = await session_service_stateful.create_session(
    app_name=APP_NAME, # 一貫したアプリ名を使用
    user_id=USER_ID_STATEFUL,
    session_id=SESSION_ID_STATEFUL,
    state=initial_state # <<< 作成時に状態を初期化
)
print(f"✅ セッション'{SESSION_ID_STATEFUL}'がユーザー'{USER_ID_STATEFUL}'のために作成されました。")

# 初期状態が正しく設定されたことを確認
retrieved_session = await session_service_stateful.get_session(app_name=APP_NAME,
                                                         user_id=USER_ID_STATEFUL,
                                                         session_id = SESSION_ID_STATEFUL)
print("\n--- 初期セッション状態 ---")
if retrieved_session:
    print(retrieved_session.state)
else:
    print("エラー：セッションを取得できませんでした。")
```

---

**2. 状態対応の天気ツールを作成 (`get_weather_stateful`)**

次に、新しいバージョンの天気ツールを作成します。その主な特徴は、`tool_context: ToolContext`を受け入れることで、`tool_context.state`にアクセスできるようになることです。`user_preference_temperature_unit`を読み取り、それに応じて温度をフォーマットします。

*   **重要なコンセプト：`ToolContext`** このオブジェクトは、ツールロジックがセッションのコンテキスト（状態変数の読み書きを含む）と対話できるようにする橋渡しです。ツール関数の最後のパラメータとして定義されていれば、ADKが自動的に注入します。

*   **ベストプラクティス：** 状態から読み取る際は、`dictionary.get('key', default_value)`を使用して、キーが存在しない場合に対応し、ツールがクラッシュしないようにしてください。

```python
from google.adk.tools.tool_context import ToolContext

def get_weather_stateful(city: str, tool_context: ToolContext) -> dict:
    """天気を取得し、セッション状態に基づいて温度単位を変換します。"""
    print(f"--- ツール：get_weather_statefulが{city}で呼び出されました ---")

    # --- 状態から設定を読み取る ---
    preferred_unit = tool_context.state.get("user_preference_temperature_unit", "Celsius") # デフォルトは摂氏
    print(f"--- ツール：状態'user_preference_temperature_unit'を読み取り中：{preferred_unit} ---")

    city_normalized = city.lower().replace(" ", "")

    # 模擬的な天気データ（内部では常に摂氏で保存）
    mock_weather_db = {
        "newyork": {"temp_c": 25, "condition": "sunny"},
        "london": {"temp_c": 15, "condition": "cloudy"},
        "tokyo": {"temp_c": 18, "condition": "light rain"},
    }

    if city_normalized in mock_weather_db:
        data = mock_weather_db[city_normalized]
        temp_c = data["temp_c"]
        condition = data["condition"]

        # 状態の設定に基づいて温度をフォーマット
        if preferred_unit == "Fahrenheit":
            temp_value = (temp_c * 9/5) + 32 # 華氏を計算
            temp_unit = "°F"
        else: # デフォルトは摂氏
            temp_value = temp_c
            temp_unit = "°C"

        report = f"{city.capitalize()}の天気は{condition}で、気温は{temp_value:.0f}{temp_unit}です。"
        result = {"status": "success", "report": report}
        print(f"--- ツール：{preferred_unit}でレポートを生成しました。結果：{result} ---")

        # 状態への書き込み例（このツールではオプション）
        tool_context.state["last_city_checked_stateful"] = city
        print(f"--- ツール：状態'last_city_checked_stateful'を更新しました：{city} ---")

        return result
    else:
        # 都市が見つからない場合を処理
        error_msg = f"申し訳ありませんが、'{city}'の天気情報はありません。"
        print(f"--- ツール：都市'{city}'が見つかりませんでした。 ---")
        return {"status": "error", "error_message": error_msg}

print("✅ 状態対応の'get_weather_stateful'ツールが定義されました。")
```

---

**3. サブエージェントの再定義とルートエージェントの更新**

このステップが自己完結型で正しく構築されるように、まずステップ3と全く同じように`greeting_agent`と`farewell_agent`を再定義します。次に、新しいルートエージェント（`weather_agent_v4_stateful`）を定義します：

*   新しい`get_weather_stateful`ツールを使用します。
*   委任のために挨拶と別れのサブエージェントを含みます。
*   **重要なこと**に、`output_key="last_weather_report"`を設定し、最終的な天気応答をセッション状態に自動的に保存します。

```python
# @title 3. サブエージェントの再定義とoutput_keyを持つルートエージェントの更新

# 必要なインポートを確認：Agent, LiteLlm, Runner
from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from google.adk.runners import Runner
# 'say_hello', 'say_goodbye'ツールが定義されていることを確認（ステップ3から）
# モデル定数MODEL_GPT_4O, MODEL_GEMINI_2_0_FLASHなどが定義されていることを確認

# --- 挨拶エージェントの再定義（ステップ3から） ---
greeting_agent = None
try:
    greeting_agent = Agent(
        model=MODEL_GEMINI_2_0_FLASH,
        name="greeting_agent",
        instruction="あなたは挨拶エージェントです。あなたの唯一のタスクは'say_hello'ツールを使って親しみやすい挨拶を提供することです。他には何もしないでください。",
        description="'say_hello'ツールを使用して簡単な挨拶を処理します。",
        tools=[say_hello],
    )
    print(f"✅ エージェント'{greeting_agent.name}'が再定義されました。")
except Exception as e:
    print(f"❌ 挨拶エージェントを再定義できませんでした。エラー：{e}")

# --- 別れエージェントの再定義（ステップ3から） ---
farewell_agent = None
try:
    farewell_agent = Agent(
        model=MODEL_GEMINI_2_0_FLASH,
        name="farewell_agent",
        instruction="あなたは別れエージェントです。あなたの唯一のタスクは'say_goodbye'ツールを使って丁寧なさようならのメッセージを提供することです。他のアクションは実行しないでください。",
        description="'say_goodbye'ツールを使用して簡単な別れを処理します。",
        tools=[say_goodbye],
    )
    print(f"✅ エージェント'{farewell_agent.name}'が再定義されました。")
except Exception as e:
    print(f"❌ 別れエージェントを再定義できませんでした。エラー：{e}")

# --- 更新されたルートエージェントの定義 ---
root_agent_stateful = None
runner_root_stateful = None # runnerを初期化

# ルートエージェントを作成する前の前提条件をチェック
if greeting_agent and farewell_agent and 'get_weather_stateful' in globals():

    root_agent_model = MODEL_GEMINI_2_0_FLASH # オーケストレーションモデルを選択

    root_agent_stateful = Agent(
        name="weather_agent_v4_stateful", # 新しいバージョン名
        model=root_agent_model,
        description="メインエージェント：天気を提供し（状態対応の単位）、挨拶/別れを委任し、レポートを状態に保存します。",
        instruction="あなたはメインの天気エージェントです。あなたの仕事は'get_weather_stateful'を使って天気を提供することです。"
                    "ツールは状態に保存されているユーザーの好みに基づいて温度をフォーマットします。"
                    "簡単な挨拶は'greeting_agent'に、別れは'farewell_agent'に委任してください。"
                    "天気のリクエスト、挨拶、別れのみを処理してください。",
        tools=[get_weather_stateful], # 状態対応ツールを使用
        sub_agents=[greeting_agent, farewell_agent], # サブエージェントを含める
        output_key="last_weather_report" # <<< エージェントの最終的な天気応答を自動保存
    )
    print(f"✅ ルートエージェント'{root_agent_stateful.name}'が状態対応ツールとoutput_keyで作成されました。")

    # --- このルートエージェントと新しいセッションサービスのためのRunnerを作成 ---
    runner_root_stateful = Runner(
        agent=root_agent_stateful,
        app_name=APP_NAME,
        session_service=session_service_stateful # 新しい状態対応セッションサービスを使用
    )
    print(f"✅ 状態対応ルートエージェント'{runner_root_stateful.agent.name}'用のRunnerが状態対応セッションサービスを使用して作成されました。")

else:
    print("❌ 状態対応ルートエージェントを作成できません。前提条件がありません。")
    if not greeting_agent: print(" - greeting_agentの定義がありません。")
    if not farewell_agent: print(" - farewell_agentの定義がありません。")
    if 'get_weather_stateful' not in globals(): print(" - get_weather_statefulツールがありません。")
```

---

**4. 対話して状態フローをテストする**

さて、状態の相互作用をテストするために設計された会話を、`runner_root_stateful`（私たちの状態対応エージェントと`session_service_stateful`に関連付けられている）を使用して実行しましょう。以前に定義した`call_agent_async`関数を使用し、正しいランナー、ユーザーID（`USER_ID_STATEFUL`）、セッションID（`SESSION_ID_STATEFUL`）を渡すことを確認します。

会話のフローは次のようになります：

1.  **天気の確認（ロンドン）：** `get_weather_stateful`ツールは、セクション1で初期化されたセッション状態から初期の「摂氏」設定を読み取るはずです。ルートエージェントの最終応答（摂氏での天気予報）は、`output_key`設定を介して`state['last_weather_report']`に保存されるはずです。
2.  **状態の手動更新：** `InMemorySessionService`インスタンス（`session_service_stateful`）内に保存されている状態を*直接変更*します。
    *   **なぜ直接変更するのか？** `session_service.get_session()`メソッドはセッションの*コピー*を返します。そのコピーを変更しても、後続のエージェント実行で使用される状態には影響しません。`InMemorySessionService`でのこのテストシナリオでは、内部の`sessions`辞書にアクセスして、`user_preference_temperature_unit`の*実際に*保存されている状態値を「華氏」に変更します。*注意：実際のアプリケーションでは、状態の変更は通常、ツールや`EventActions(state_delta=...)`を返すエージェントロジックによってトリガーされ、手動での直接更新ではありません。*
3.  **再度天気の確認（ニューヨーク）：** `get_weather_stateful`ツールは、今度は状態から更新された「華氏」設定を読み取り、それに応じて温度を変換するはずです。ルートエージェントの*新しい*応答（華氏での天気）は、`output_key`のために`state['last_weather_report']`の前の値を上書きします。
4.  **エージェントに挨拶する：** `greeting_agent`への委任が状態操作と並行して正しく機能することを確認します。このインタラクションは、この特定のシーケンスで`output_key`によって保存される*最後の*応答になります。
5.  **最終状態の検査：** 会話の後、セッションをもう一度取得し（コピーを取得）、その状態を出力して、`user_preference_temperature_unit`が確かに「華氏」であることを確認し、`output_key`によって保存された最終値（この実行では挨拶になります）を観察し、ツールによって書き込まれた`last_city_checked_stateful`の値を確認します。

```python
# @title 4. 対話して状態フローとoutput_keyをテストする
import asyncio # asyncioがインポートされていることを確認

# 前のセルから状態対応ランナー（runner_root_stateful）が利用可能であることを確認
# call_agent_async, USER_ID_STATEFUL, SESSION_ID_STATEFUL, APP_NAMEが定義されていることを確認

if 'runner_root_stateful' in globals() and runner_root_stateful:
    # 状態対応会話ロジックのためのメインのasync関数を定義します。
    # この関数内の'await'キーワードは非同期操作に必要です。
    async def run_stateful_conversation():
        print("\n--- 状態のテスト：温度単位の変換とoutput_key ---")

        # 1. 天気の確認（初期状態を使用：摂氏）
        print("--- ターン1：ロンドンの天気をリクエスト（摂氏を期待） ---")
        await call_agent_async(query= "ロンドンの天気は？",
                               runner=runner_root_stateful,
                               user_id=USER_ID_STATEFUL,
                               session_id=SESSION_ID_STATEFUL
                              )

        # 2. 状態設定を手動で華氏に更新 - ストレージを直接変更
        print("\n--- 状態の手動更新：単位を華氏に設定 ---")
        try:
            # 内部ストレージに直接アクセス - これはテスト用のInMemorySessionServiceに特有です
            # 注意：永続的なサービス（データベース、VertexAI）を使用した本番環境では、
            # 通常、内部ストレージの直接操作ではなく、エージェントのアクションや
            # 利用可能な場合は特定のサービスAPIを介して状態を更新します。
            stored_session = session_service_stateful.sessions[APP_NAME][USER_ID_STATEFUL][SESSION_ID_STATEFUL]
            stored_session.state["user_preference_temperature_unit"] = "Fahrenheit"
            # オプション：何らかのロジックがタイムスタンプに依存する場合は、タイムスタンプも更新したいかもしれません
            # import time
            # stored_session.last_update_time = time.time()
            print(f"--- 保存されたセッション状態が更新されました。現在の'user_preference_temperature_unit'：{stored_session.state.get('user_preference_temperature_unit', '設定されていません')} ---") # 安全のため.get()を追加
        except KeyError:
            print(f"--- エラー：アプリ'{APP_NAME}'のユーザー'{USER_ID_STATEFUL}'のセッション'{SESSION_ID_STATEFUL}'を内部ストレージから取得して状態を更新できませんでした。IDとセッションが作成されたか確認してください。 ---")
        except Exception as e:
             print(f"--- 内部セッション状態の更新中にエラーが発生しました：{e} ---")

        # 3. 再度天気の確認（ツールは華氏を使用するはず）
        # これもoutput_keyを介して'last_weather_report'を更新します
        print("\n--- ターン2：ニューヨークの天気をリクエスト（華氏を期待） ---")
        await call_agent_async(query= "ニューヨークの天気を教えて。",
                               runner=runner_root_stateful,
                               user_id=USER_ID_STATEFUL,
                               session_id=SESSION_ID_STATEFUL
                              )

        # 4. 基本的な委任のテスト（まだ機能するはず）
        # これにより'last_weather_report'が再度更新され、NYの天気予報が上書きされます
        print("\n--- ターン3：挨拶を送信 ---")
        await call_agent_async(query= "こんにちは！",
                               runner=runner_root_stateful,
                               user_id=USER_ID_STATEFUL,
                               session_id=SESSION_ID_STATEFUL
                              )

    # --- `run_stateful_conversation` async関数を実行 ---
    # 環境に応じて以下のいずれかの方法を選択してください。

    # 方法1：直接await（ノートブック/Async REPLのデフォルト）
    # 環境がトップレベルawaitをサポートしている場合（Colab/Jupyterノートブックなど）、
    # イベントループが既に実行中であることを意味するので、直接関数をawaitできます。
    print("'await'を使用した実行を試みています（ノートブックのデフォルト）...")
    await run_stateful_conversation()

    # 方法2：asyncio.run（標準のPythonスクリプト[.py]用）
    # （...省略...）

    # --- 会話後の最終セッション状態を検査 ---
    # このブロックは、いずれかの実行方法が完了した後に実行されます。
    print("\n--- 最終セッション状態の検査 ---")
    final_session = await session_service_stateful.get_session(app_name=APP_NAME,
                                                         user_id= USER_ID_STATEFUL,
                                                         session_id=SESSION_ID_STATEFUL)
    if final_session:
        # 存在しない可能性のあるキーに安全にアクセスするために.get()を使用
        print(f"最終的な設定：{final_session.state.get('user_preference_temperature_unit', '設定されていません')}")
        print(f"最後の天気予報（output_keyから）：{final_session.state.get('last_weather_report', '設定されていません')}")
        print(f"最後に確認された都市（ツールによる）：{final_session.state.get('last_city_checked_stateful', '設定されていません')}")
        # 詳細表示のために完全な状態を出力
        # print(f"完全な状態辞書：{final_session.state}")
    else:
        print("\n❌ エラー：最終セッション状態を取得できませんでした。")

else:
    print("\n⚠️ 状態テストの会話をスキップします。状態対応ルートエージェントのランナー（'runner_root_stateful'）が利用できません。")
```

---

会話の流れと最終的なセッション状態の出力を見直すことで、以下を確認できます：

*   **状態の読み取り：** 天気ツール（`get_weather_stateful`）は、状態から`user_preference_temperature_unit`を正しく読み取り、最初はロンドンのために「摂氏」を使用しました。
*   **状態の更新：** 直接の変更により、保存されていた設定が「華氏」に正常に変更されました。
*   **状態の読み取り（更新後）：** ツールはその後、ニューヨークの天気を尋ねられた際に「華氏」を読み取り、変換を実行しました。
*   **ツールの状態書き込み：** ツールは、`tool_context.state`を介して`last_city_checked_stateful`（2回目の天気確認後の「New York」）を状態に正常に書き込みました。
*   **委任：** 「こんにちは！」に対する`greeting_agent`への委任は、状態変更後も正しく機能しました。
*   **`output_key`：** `output_key="last_weather_report"`は、ルートエージェントが最終的に応答した*各ターン*のルートエージェントの*最終*応答を正常に保存しました。このシーケンスでは、最後の応答は挨拶（「こんにちは！」）だったため、それが状態キーの天気予報を上書きしました。
*   **最終状態：** 最終確認で、設定が「華氏」として永続化されていることが確認されます。

これで、`ToolContext`を使用してエージェントの振る舞いをパーソナライズするためのセッション状態の統合、`InMemorySessionService`のテストのための状態の手動操作、そして`output_key`がエージェントの最後の応答を状態に保存するための簡単なメカニズムを提供する方法を正常に確認しました。この状態管理の基本的な理解は、次のステップでコールバックを使用して安全ガードレールを実装する上で重要です。

---

## ステップ5：安全性の追加 - `before_model_callback`による入力ガードレール

私たちのエージェントチームは、設定を記憶し、ツールを効果的に使用することで、ますます有能になっています。しかし、実世界のシナリオでは、潜在的に問題のあるリクエストが中核となる大規模言語モデル（LLM）に到達する*前*に、エージェントの振る舞いを制御するための安全メカニズムがしばしば必要になります。

ADKは**コールバック**を提供します。これは、エージェントの実行ライフサイクルの特定のポイントにフックできる関数です。`before_model_callback`は、入力の安全性に特に役立ちます。

**`before_model_callback`とは？**

*   エージェントがコンパイルされたリクエスト（会話履歴、指示、最新のユーザーメッセージを含む）を基盤となるLLMに送信する*直前*にADKが実行する、あなたが定義するPython関数です。
*   **目的：** リクエストを検査し、必要に応じて変更するか、事前定義されたルールに基づいて完全にブロックします。

**一般的なユースケース：**

*   **入力の検証/フィルタリング：** ユーザー入力が基準を満たしているか、許可されていないコンテンツ（PIIやキーワードなど）を含んでいないかを確認します。
*   **ガードレール：** 有害、トピック外、またはポリシーに違反するリクエストがLLMによって処理されるのを防ぎます。
*   **動的なプロンプトの変更：** 送信する直前に、タイムリーな情報（例：セッション状態から）をLLMリクエストのコンテキストに追加します。

**仕組み：**

1.  `callback_context: CallbackContext`と`llm_request: LlmRequest`を受け入れる関数を定義します。

    *   `callback_context`: エージェント情報、セッション状態（`callback_context.state`）などへのアクセスを提供します。
    *   `llm_request`: LLMに送られる予定の完全なペイロード（`contents`、`config`）を含みます。

2.  関数内で：

    *   **検査：** `llm_request.contents`（特に最後のユーザーメッセージ）を調べます。
    *   **変更（注意して使用）：** `llm_request`の一部を変更*できます*。
    *   **ブロック（ガードレール）：** `LlmResponse`オブジェクトを返します。ADKはこの応答をすぐに返し、そのターンのLLM呼び出しを*スキップ*します。
    *   **許可：** `None`を返します。ADKは（潜在的に変更された）リクエストでLLMを呼び出します。

**このステップでは、以下のことを行います：**

1.  ユーザーの入力に特定のキーワード（"BLOCK"）があるかチェックする`before_model_callback`関数（`block_keyword_guardrail`）を定義します。
2.  状態対応のルートエージェント（ステップ4の`weather_agent_v4_stateful`）を更新して、このコールバックを使用するようにします。
3.  この更新されたエージェントに関連付けられた新しいランナーを作成しますが、状態の継続性を維持するために*同じ状態対応セッションサービス*を使用します。
4.  通常のリクエストとキーワードを含むリクエストの両方を送信して、ガードレールをテストします。

---

**1. ガードレールコールバック関数の定義**

この関数は、`llm_request`のコンテンツ内の最後のユーザーメッセージを検査します。もし"BLOCK"（大文字と小文字を区別しない）が見つかった場合、`LlmResponse`を構築して返し、フローをブロックします。それ以外の場合は`None`を返します。

```python
# @title 1. before_model_callbackガードレールの定義

# 必要なインポートが利用可能であることを確認
from google.adk.agents.callback_context import CallbackContext
from google.adk.models.llm_request import LlmRequest
from google.adk.models.llm_response import LlmResponse
from google.genai import types # 応答コンテンツ作成用
from typing import Optional

def block_keyword_guardrail(
    callback_context: CallbackContext, llm_request: LlmRequest
) -> Optional[LlmResponse]:
    """
    最新のユーザーメッセージに'BLOCK'が含まれているか検査します。見つかった場合、LLM呼び出しをブロックし、
    事前定義されたLlmResponseを返します。それ以外の場合は、Noneを返して続行します。
    """
    agent_name = callback_context.agent_name # モデル呼び出しが傍受されているエージェントの名前を取得
    print(f"--- コールバック：block_keyword_guardrailがエージェント：{agent_name}で実行中 ---")

    # リクエスト履歴の最新のユーザーメッセージからテキストを抽出
    last_user_message_text = ""
    if llm_request.contents:
        # 'user'ロールを持つ最新のメッセージを検索
        for content in reversed(llm_request.contents):
            if content.role == 'user' and content.parts:
                # 簡単のため、テキストは最初のパートにあると仮定
                if content.parts.text:
                    last_user_message_text = content.parts.text
                    break # 最新のユーザーメッセージテキストを見つけた

    print(f"--- コールバック：最新のユーザーメッセージを検査中：'{last_user_message_text[:100]}...' ---") # 最初の100文字をログに記録

    # --- ガードレールロジック ---
    keyword_to_block = "BLOCK"
    if keyword_to_block in last_user_message_text.upper(): # 大文字小文字を区別しないチェック
        print(f"--- コールバック：'{keyword_to_block}'を発見。LLM呼び出しをブロックします！ ---")
        # オプション：ブロックイベントを記録するために状態にフラグを設定
        callback_context.state["guardrail_block_keyword_triggered"] = True
        print(f"--- コールバック：状態'guardrail_block_keyword_triggered'をTrueに設定しました ---")

        # フローを停止し、代わりにこれを返すLlmResponseを構築して返す
        return LlmResponse(
            content=types.Content(
                role="model", # エージェントの視点からの応答を模倣
                parts=[types.Part(text=f"ブロックされたキーワード'{keyword_to_block}'が含まれているため、このリクエストは処理できません。")],
            )
            # 注意：必要に応じて、ここにerror_messageフィールドを設定することもできます
        )
    else:
        # キーワードが見つからなかったため、リクエストをLLMに進める
        print(f"--- コールバック：キーワードが見つかりませんでした。{agent_name}のLLM呼び出しを許可します。 ---")
        return None # Noneを返すとADKは通常通り続行する

print("✅ block_keyword_guardrail関数が定義されました。")
```

---

**2. コールバックを使用するようにルートエージェントを更新**

ルートエージェントを再定義し、`before_model_callback`パラメータを追加して、新しいガードレール関数を指すようにします。明確にするために新しいバージョン名を付けます。

*重要：* ルートエージェントの定義がすべてのコンポーネントにアクセスできるように、このコンテキスト内でサブエージェント（`greeting_agent`、`farewell_agent`）と状態対応ツール（`get_weather_stateful`）を、以前のステップから利用可能でない場合は再定義する必要があります。

```python
# @title 2. before_model_callbackでルートエージェントを更新

# --- サブエージェントの再定義（このコンテキストに存在することを確認） ---
greeting_agent = None
try:
    # 定義済みのモデル定数を使用
    greeting_agent = Agent(
        model=MODEL_GEMINI_2_0_FLASH,
        name="greeting_agent", # 一貫性のために元の名前を維持
        instruction="あなたは挨拶エージェントです。あなたの唯一のタスクは'say_hello'ツールを使って親しみやすい挨拶を提供することです。他には何もしないでください。",
        description="'say_hello'ツールを使用して簡単な挨拶を処理します。",
        tools=[say_hello],
    )
    print(f"✅ サブエージェント'{greeting_agent.name}'が再定義されました。")
except Exception as e:
    print(f"❌ 挨拶エージェントを再定義できませんでした。モデル/APIキー({greeting_agent.model})を確認してください。エラー：{e}")

farewell_agent = None
try:
    # 定義済みのモデル定数を使用
    farewell_agent = Agent(
        model=MODEL_GEMINI_2_0_FLASH,
        name="farewell_agent", # 元の名前を維持
        instruction="あなたは別れエージェントです。あなたの唯一のタスクは'say_goodbye'ツールを使って丁寧なさようならのメッセージを提供することです。他のアクションは実行しないでください。",
        description="'say_goodbye'ツールを使用して簡単な別れを処理します。",
        tools=[say_goodbye],
    )
    print(f"✅ サブエージェント'{farewell_agent.name}'が再定義されました。")
except Exception as e:
    print(f"❌ 別れエージェントを再定義できませんでした。モデル/APIキー({farewell_agent.model})を確認してください。エラー：{e}")


# --- コールバックを持つルートエージェントの定義 ---
root_agent_model_guardrail = None
runner_root_model_guardrail = None

# 続行する前にすべてのコンポーネントを確認
if greeting_agent and farewell_agent and 'get_weather_stateful' in globals() and 'block_keyword_guardrail' in globals():

    # 定義済みのモデル定数を使用
    root_agent_model = MODEL_GEMINI_2_0_FLASH

    root_agent_model_guardrail = Agent(
        name="weather_agent_v5_model_guardrail", # 明確にするための新しいバージョン名
        model=root_agent_model,
        description="メインエージェント：天気を処理し、挨拶/別れを委任し、入力キーワードガードレールを含みます。",
        instruction="あなたはメインの天気エージェントです。'get_weather_stateful'を使って天気を提供してください。"
                    "簡単な挨拶は'greeting_agent'に、別れは'farewell_agent'に委任してください。"
                    "天気のリクエスト、挨拶、別れのみを処理してください。",
        tools=[get_weather],
        sub_agents=[greeting_agent, farewell_agent], # 再定義されたサブエージェントを参照
        output_key="last_weather_report", # ステップ4のoutput_keyを維持
        before_model_callback=block_keyword_guardrail # <<< ガードレールコールバックを割り当てる
    )
    print(f"✅ ルートエージェント'{root_agent_model_guardrail.name}'がbefore_model_callbackで作成されました。")

    # --- このエージェントのためのRunnerを作成、同じ状態対応セッションサービスを使用 ---
    # session_service_statefulがステップ4から存在することを確認
    if 'session_service_stateful' in globals():
        runner_root_model_guardrail = Runner(
            agent=root_agent_model_guardrail,
            app_name=APP_NAME, # 一貫したAPP_NAMEを使用
            session_service=session_service_stateful # <<< ステップ4のサービスを使用
        )
        print(f"✅ ガードレールエージェント'{runner_root_model_guardrail.agent.name}'用のRunnerが、状態対応セッションサービスを使用して作成されました。")
    else:
        print("❌ runnerを作成できません。ステップ4の'session_service_stateful'が見つかりません。")

else:
    print("❌ モデルガードレールを持つルートエージェントを作成できません。1つ以上の前提条件が見つからないか、初期化に失敗しました：")
    if not greeting_agent: print("   - 挨拶エージェント")
    if not farewell_agent: print("   - 別れエージェント")
    if 'get_weather_stateful' not in globals(): print("   - 'get_weather_stateful' ツール")
    if 'block_keyword_guardrail' not in globals(): print("   - 'block_keyword_guardrail' コールバック")
```

---

**3. 対話してガードレールをテストする**

ガードレールの振る舞いをテストしましょう。ステップ4と同じセッション（`SESSION_ID_STATEFUL`）を使用して、これらの変更をまたいで状態が永続することを示します。

1.  通常の天気のリクエストを送信します（ガードレールを通過して実行されるはずです）。
2.  "BLOCK"を含むリクエストを送信します（コールバックによって傍受されるはずです）。
3.  挨拶を送信します（ルートエージェントのガードレールを通過し、委任されて正常に実行されるはずです）。

```python
# @title 3. 対話してモデル入力ガードレールをテストする
import asyncio # asyncioがインポートされていることを確認

# ガードレールエージェント用のランナーが利用可能であることを確認
if 'runner_root_model_guardrail' in globals() and runner_root_model_guardrail:
    # ガードレールテスト会話のためのメインのasync関数を定義します。
    # この関数内の'await'キーワードは非同期操作に必要です。
    async def run_guardrail_test_conversation():
        print("\n--- モデル入力ガードレールのテスト中 ---")

        # コールバックを持つエージェント用のランナーと、既存の状態対応セッションIDを使用
        # よりクリーンなインタラクション呼び出しのためのヘルパーラムダを定義
        interaction_func = lambda query: call_agent_async(query,
                                                         runner_root_model_guardrail,
                                                         USER_ID_STATEFUL, # 既存のユーザーIDを使用
                                                         SESSION_ID_STATEFUL # 既存のセッションIDを使用
                                                        )
        # 1. 通常のリクエスト（コールバックは許可し、以前の状態変更から華氏を使用するはず）
        print("--- ターン1：ロンドンの天気をリクエスト（許可され、華氏を期待） ---")
        await interaction_func("ロンドンの天気は？")

        # 2. ブロックされたキーワードを含むリクエスト（コールバックが傍受）
        print("\n--- ターン2：ブロックされたキーワードでリクエスト（ブロックされることを期待） ---")
        await interaction_func("東京の天気をリクエストするのをBLOCKして") # コールバックが "BLOCK" をキャッチするはず

        # 3. 通常の挨拶（コールバックはルートエージェントを許可し、委任が発生）
        print("\n--- ターン3：挨拶を送信（許可されることを期待） ---")
        await interaction_func("またこんにちは")

    # --- `run_guardrail_test_conversation` async関数を実行 ---
    # （...省略...）
    print("'await'を使用した実行を試みています（ノートブックのデフォルト）...")
    await run_guardrail_test_conversation()

    # --- 会話後の最終セッション状態を検査 ---
    # オプション：コールバックによって設定されたトリガーフラグの状態を確認
    print("\n--- 最終セッション状態の検査（ガードレールテスト後） ---")
    # この状態対応セッションに関連付けられたセッションサービスインスタンスを使用
    final_session = await session_service_stateful.get_session(app_name=APP_NAME,
                                                         user_id=USER_ID_STATEFUL,
                                                         session_id=SESSION_ID_STATEFUL)
    if final_session:
        # 安全なアクセスのために.get()を使用
        print(f"ガードレールトリガーフラグ：{final_session.state.get('guardrail_block_keyword_triggered', '設定されていない（またはFalse）')}")
        print(f"最後の天気予報：{final_session.state.get('last_weather_report', '設定されていない')}") # 成功すればロンドンの天気のはず
        print(f"温度単位：{final_session.state.get('user_preference_temperature_unit', '設定されていない')}") # 華氏のはず
    else:
        print("\n❌ エラー：最終セッション状態を取得できませんでした。")

else:
    print("\n⚠️ モデルガードレールのテストをスキップします。ランナー（'runner_root_model_guardrail'）が利用できません。")
```

---

実行フローを観察してください：

1.  **ロンドンの天気：** コールバックが`weather_agent_v5_model_guardrail`に対して実行され、メッセージを検査し、「キーワードが見つかりません。LLM呼び出しを許可します。」と出力して`None`を返します。エージェントは続行し、`get_weather_stateful`ツールを呼び出し（ステップ4の状態変更から「華氏」設定を使用）、天気を返します。この応答は`output_key`を介して`last_weather_report`を更新します。
2.  **BLOCKリクエスト：** コールバックが`weather_agent_v5_model_guardrail`に対して再度実行され、メッセージを検査し、「BLOCK」を見つけ、「LLM呼び出しをブロックします！」と出力し、状態フラグを設定し、事前定義された`LlmResponse`を返します。このターンではエージェントの基盤となるLLMは*決して呼び出されません*。ユーザーはコールバックのブロッキングメッセージを見ます。
3.  **またこんにちは：** コールバックが`weather_agent_v5_model_guardrail`に対して実行され、リクエストを許可します。その後、ルートエージェントは`greeting_agent`に委任します。*注意：ルートエージェントで定義された`before_model_callback`は、サブエージェントに自動的には適用されません。*`greeting_agent`は通常通り続行し、`say_hello`ツールを呼び出して挨拶を返します。

これで、入力安全層を正常に実装しました！`before_model_callback`は、高価なまたは潜在的に危険なLLM呼び出しが行われる*前*に、ルールを強制し、エージェントの振る舞いを制御するための強力なメカニズムを提供します。次に、ツール自体の使用に関するガードレールを追加するために、同様の概念を適用します。

## ステップ6：安全性の追加 - ツール引数ガードレール (`before_tool_callback`)

ステップ5では、ユーザー入力がLLMに到達する*前*にそれを検査し、潜在的にブロックするガードレールを追加しました。次に、LLMがツールの使用を決定した後、しかしそのツールが実際に実行される*前*に、別の制御層を追加します。これは、LLMがツールに渡そうとする*引数*を検証するのに役立ちます。

ADKはこの正確な目的のために`before_tool_callback`を提供します。

**`before_tool_callback`とは？**

*   LLMがその使用を要求し、引数を決定した後、特定のツール関数が実行される*直前*に実行されるPython関数です。
*   **目的：** ツール引数の検証、特定の入力に基づくツール実行の防止、引数の動的な変更、またはリソース使用ポリシーの強制。

**一般的なユースケース：**

*   **引数の検証：** LLMによって提供された引数が有効であるか、許容範囲内であるか、または期待される形式に準拠しているかを確認します。
*   **リソース保護：** コストがかかる、制限されたデータにアクセスする、または望ましくない副作用を引き起こす可能性のある入力でツールが呼び出されるのを防ぎます（例：特定のパラメータに対するAPI呼び出しのブロック）。
*   **動的な引数の変更：** ツールが実行される前に、セッション状態や他のコンテキスト情報に基づいて引数を調整します。

**仕組み：**

1.  `tool: BaseTool`、`args: Dict[str, Any]`、および`tool_context: ToolContext`を受け入れる関数を定義します。

    *   `tool`: 呼び出されようとしているツールオブジェクト（`tool.name`を検査）。
    *   `args`: LLMがツール用に生成した引数の辞書。
    *   `tool_context`: セッション状態（`tool_context.state`）、エージェント情報などへのアクセスを提供します。

2.  関数内で：

    *   **検査：** `tool.name`と`args`辞書を調べます。
    *   **変更：** `args`辞書内の値を*直接*変更します。`None`を返すと、ツールはこれらの変更された引数で実行されます。
    *   **ブロック/上書き（ガードレール）：** **辞書**を返します。ADKはこの辞書をツール呼び出しの*結果*として扱い、元のツール関数の実行を完全に*スキップ*します。辞書は、ブロックしているツールの期待される戻り形式と一致することが理想的です。
    *   **許可：** `None`を返します。ADKは実際のツール関数を（潜在的に変更された）引数で実行します。

**このステップでは、以下のことを行います：**

1.  `get_weather_stateful`ツールが都市「Paris」で呼び出されたかどうかを具体的にチェックする`before_tool_callback`関数（`block_paris_tool_guardrail`）を定義します。
2.  「Paris」が検出された場合、コールバックはツールをブロックし、カスタムエラー辞書を返します。
3.  `before_model_callback`とこの新しい`before_tool_callback`の両方を含むようにルートエージェント（`weather_agent_v6_tool_guardrail`）を更新します。
4.  このエージェント用の新しいランナーを作成し、同じ状態対応セッションサービスを使用します。
5.  許可された都市とブロックされた都市（「Paris」）の天気をリクエストして、フローをテストします。

---

**1. ツールガードレールコールバック関数の定義**

この関数は`get_weather_stateful`ツールを対象とします。`city`引数をチェックし、それが「Paris」であれば、ツール自体のエラー応答のように見えるエラー辞書を返します。それ以外の場合は、`None`を返してツールを実行させます。

```python
# @title 1. before_tool_callbackガードレールの定義

# 必要なインポートが利用可能であることを確認
from google.adk.tools.base_tool import BaseTool
from google.adk.tools.tool_context import ToolContext
from typing import Optional, Dict, Any # 型ヒント用

def block_paris_tool_guardrail(
    tool: BaseTool, args: Dict[str, Any], tool_context: ToolContext
) -> Optional[Dict]:
    """
    'get_weather_stateful'が'Paris'に対して呼び出されたかチェックします。
    もしそうなら、ツール実行をブロックし、特定のエラー辞書を返します。
    それ以外の場合は、Noneを返してツール呼び出しを続行させます。
    """
    tool_name = tool.name
    agent_name = tool_context.agent_name # ツール呼び出しを試みているエージェント
    print(f"--- コールバック：block_paris_tool_guardrailがエージェント'{agent_name}'のツール'{tool_name}'で実行中 ---")
    print(f"--- コールバック：引数を検査中：{args} ---")

    # --- ガードレールロジック ---
    target_tool_name = "get_weather_stateful" # FunctionToolで使用される関数名と一致させる
    blocked_city = "paris"

    # 正しいツールであり、city引数がブロックされた都市と一致するかチェック
    if tool_name == target_tool_name:
        city_argument = args.get("city", "") # 'city'引数を安全に取得
        if city_argument and city_argument.lower() == blocked_city:
            print(f"--- コールバック：ブロックされた都市'{city_argument}'を検出。ツール実行をブロックします！ ---")
            # オプションで状態を更新
            tool_context.state["guardrail_tool_block_triggered"] = True
            print(f"--- コールバック：状態'guardrail_tool_block_triggered'をTrueに設定しました ---")

            # エラーに関するツールの期待される出力形式に一致する辞書を返す
            # この辞書がツールの結果となり、実際のツール実行はスキップされる
            return {
                "status": "error",
                "error_message": f"ポリシー制限：'{city_argument.capitalize()}'の天気チェックは現在、ツールガードレールによって無効化されています。"
            }
        else:
             print(f"--- コールバック：都市'{city_argument}'はツール'{tool_name}'で許可されています。 ---")
    else:
        print(f"--- コールバック：ツール'{tool_name}'は対象ツールではありません。許可します。 ---")

    # 上記のチェックが辞書を返さなかった場合、ツールの実行を許可
    print(f"--- コールバック：ツール'{tool_name}'の実行を許可します。 ---")
    return None # Noneを返すと実際のツール関数が実行される

print("✅ block_paris_tool_guardrail関数が定義されました。")
```

---

**2. 両方のコールバックを使用するようにルートエージェントを更新**

ルートエージェントを再度定義し（`weather_agent_v6_tool_guardrail`）、今回はステップ5の`before_model_callback`に加えて`before_tool_callback`パラメータを追加します。

*自己完結型実行ノート：* ステップ5と同様に、このエージェントを定義する前に、すべての前提条件（サブエージェント、ツール、`before_model_callback`）が実行コンテキストで定義または利用可能であることを確認してください。

```python
# @title 2. 両方のコールバックでルートエージェントを更新（自己完結型）

# --- 前提条件が定義されていることを確認 ---
# （Agent, LiteLlm, Runner, ToolContext, MODEL定数, say_hello, say_goodbye, 
#  greeting_agent, farewell_agent, get_weather_stateful, 
#  block_keyword_guardrail, block_paris_tool_guardrail の定義を含めるか実行を確認）

# --- サブエージェントの再定義（このコンテキストに存在することを確認） ---
# （...挨拶・別れエージェントの再定義コードは省略...）
print("✅ サブエージェントが再定義されました。")

# --- 両方のコールバックを持つルートエージェントの定義 ---
root_agent_tool_guardrail = None
runner_root_tool_guardrail = None

if ('greeting_agent' in globals() and greeting_agent and
    'farewell_agent' in globals() and farewell_agent and
    'get_weather_stateful' in globals() and
    'block_keyword_guardrail' in globals() and
    'block_paris_tool_guardrail' in globals()):

    root_agent_model = MODEL_GEMINI_2_0_FLASH

    root_agent_tool_guardrail = Agent(
        name="weather_agent_v6_tool_guardrail", # 新しいバージョン名
        model=root_agent_model,
        description="メインエージェント：天気を処理し、委任し、入力およびツールガードレールを含みます。",
        instruction="あなたはメインの天気エージェントです。'get_weather_stateful'を使って天気を提供してください。"
                    "挨拶は'greeting_agent'に、別れは'farewell_agent'に委任してください。"
                    "天気、挨拶、別れのみを処理してください。",
        tools=[get_weather_stateful],
        sub_agents=[greeting_agent, farewell_agent],
        output_key="last_weather_report",
        before_model_callback=block_keyword_guardrail, # モデルガードレールを維持
        before_tool_callback=block_paris_tool_guardrail # <<< ツールガードレールを追加
    )
    print(f"✅ ルートエージェント'{root_agent_tool_guardrail.name}'が両方のコールバックで作成されました。")

    # --- Runnerを作成、同じ状態対応セッションサービスを使用 ---
    if 'session_service_stateful' in globals():
        runner_root_tool_guardrail = Runner(
            agent=root_agent_tool_guardrail,
            app_name=APP_NAME,
            session_service=session_service_stateful # <<< ステップ4/5のサービスを使用
        )
        print(f"✅ ツールガードレールエージェント'{runner_root_tool_guardrail.agent.name}'用のRunnerが、状態対応セッションサービスを使用して作成されました。")
    else:
        print("❌ runnerを作成できません。ステップ4/5の'session_service_stateful'が見つかりません。")

else:
    print("❌ ツールガードレールを持つルートエージェントを作成できません。前提条件がありません。")
```

---

**3. 対話してツールガードレールをテストする**

前のステップから同じ状態対応セッション（`SESSION_ID_STATEFUL`）を使用して、インタラクションフローをテストしましょう。

1.  「New York」の天気をリクエスト：両方のコールバックを通過し、ツールが実行されます（状態から華氏設定を使用）。
2.  「Paris」の天気をリクエスト：`before_model_callback`を通過します。LLMは`get_weather_stateful(city='Paris')`を呼び出すことを決定します。`before_tool_callback`が傍受し、ツールをブロックし、エラー辞書を返します。エージェントはこのエラーを伝えます。
3.  「London」の天気をリクエスト：両方のコールバックを通過し、ツールが正常に実行されます。

```python
# @title 3. 対話してツール引数ガードレールをテストする
import asyncio # asyncioがインポートされていることを確認

# ツールガードレールエージェント用のランナーが利用可能であることを確認
if 'runner_root_tool_guardrail' in globals() and runner_root_tool_guardrail:
    # ツールガードレールのテスト会話のためのメインのasync関数を定義します。
    # この関数内の'await'キーワードは非同期操作に必要です。
    async def run_tool_guardrail_test():
        print("\n--- ツール引数ガードレールのテスト中（'Paris'がブロックされる） ---")

        # 両方のコールバックを持つエージェント用のランナーと、既存の状態対応セッションを使用
        # よりクリーンなインタラクション呼び出しのためのヘルパーラムダを定義
        interaction_func = lambda query: call_agent_async(query,
                                                         runner_root_tool_guardrail,
                                                         USER_ID_STATEFUL, # 既存のユーザーIDを使用
                                                         SESSION_ID_STATEFUL # 既存のセッションIDを使用
                                                        )
        # 1. 許可された都市（両方のコールバックを通過し、華氏の状態を使用するはず）
        print("--- ターン1：ニューヨークの天気をリクエスト（許可されることを期待） ---")
        await interaction_func("ニューヨークの天気は？")

        # 2. ブロックされた都市（モデルコールバックは通過するが、ツールコールバックでブロックされるはず）
        print("\n--- ターン2：パリの天気をリクエスト（ツールガードレールによってブロックされることを期待） ---")
        await interaction_func("パリはどうですか？") # ツールコールバックがこれを傍受するはず

        # 3. 別の許可された都市（再び正常に機能するはず）
        print("\n--- ターン3：ロンドンの天気をリクエスト（許可されることを期待） ---")
        await interaction_func("ロンドンの天気を教えてください。")

    # --- `run_tool_guardrail_test` async関数を実行 ---
    # （...省略...）
    print("'await'を使用した実行を試みています（ノートブックのデフォルト）...")
    await run_tool_guardrail_test()

    # --- 会話後の最終セッション状態を検査 ---
    # オプション：ツールブロックトリガーフラグの状態を確認
    print("\n--- 最終セッション状態の検査（ツールガードレールテスト後） ---")
    # この状態対応セッションに関連付けられたセッションサービスインスタンスを使用
    final_session = await session_service_stateful.get_session(app_name=APP_NAME,
                                                         user_id=USER_ID_STATEFUL,
                                                         session_id= SESSION_ID_STATEFUL)
    if final_session:
        # 安全なアクセスのために.get()を使用
        print(f"ツールガードレールトリガーフラグ：{final_session.state.get('guardrail_tool_block_triggered', '設定されていない（またはFalse）')}")
        print(f"最後の天気予報：{final_session.state.get('last_weather_report', '設定されていない')}") # 成功すればロンドンの天気のはず
        print(f"温度単位：{final_session.state.get('user_preference_temperature_unit', '設定されていない')}") # 華氏のはず
    else:
        print("\n❌ エラー：最終セッション状態を取得できませんでした。")

else:
    print("\n⚠️ ツールガードレールのテストをスキップします。ランナー（'runner_root_tool_guardrail'）が利用できません。")
```

---

出力を分析してください：

1.  **New York：** `before_model_callback`がリクエストを許可します。LLMは`get_weather_stateful`を要求します。`before_tool_callback`が実行され、引数（`{'city': 'New York'}`）を検査し、「Paris」ではないことを見て、「ツール実行を許可...」と出力して`None`を返します。実際の`get_weather_stateful`関数が実行され、状態から「華氏」を読み取り、天気予報を返します。エージェントはこれを中継し、`output_key`を介して保存されます。
2.  **Paris：** `before_model_callback`がリクエストを許可します。LLMは`get_weather_stateful(city='Paris')`を要求します。`before_tool_callback`が実行され、引数を検査し、「Paris」を検出し、「ツール実行をブロックします！」と出力し、状態フラグを設定し、エラー辞書`{'status': 'error', 'error_message': 'ポリシー制限...'}`を返します。実際の`get_weather_stateful`関数は**決して実行されません**。エージェントは、まるでそれがツールの出力であるかのようにエラー辞書を受け取り、そのエラーメッセージに基づいて応答を形成します。
3.  **London：** New Yorkのように振る舞い、両方のコールバックを通過してツールを正常に実行します。新しいロンドンの天気予報が状態の`last_weather_report`を上書きします。

これで、LLMに*何が*届くかだけでなく、LLMによって生成された特定の引数に基づいてエージェントのツールが*どのように*使用できるかを制御する、重要な安全層を追加しました。`before_model_callback`や`before_tool_callback`のようなコールバックは、堅牢で安全、かつポリシーに準拠したエージェントアプリケーションを構築するために不可欠です。

---

## 結論：あなたのエージェントチームは準備完了です！

おめでとうございます！あなたは、Agent Development Kit (ADK) を使用して、基本的な単一の天気エージェントの構築から、洗練されたマルチエージェントチームの構築まで、見事にやり遂げました。

**達成したことのまとめ：**

*   単一のツール（`get_weather`）を備えた**基本的なエージェント**から始めました。
*   LiteLLMを使用してADKの**マルチモデルの柔軟性**を探求し、Gemini、GPT-4o、Claudeなどの異なるLLMで同じコアロジックを実行しました。
*   専門のサブエージェント（`greeting_agent`、`farewell_agent`）を作成し、ルートエージェントからの**自動委任**を有効にすることで、**モジュール性**を取り入れました。
*   **セッション状態**を使用してエージェントに**メモリ**を与え、ユーザーの好み（`temperature_unit`）や過去の対話（`output_key`）を記憶できるようにしました。
*   `before_model_callback`（特定の入力キーワードのブロック）と`before_tool_callback`（「Paris」という都市のような引数に基づくツール実行のブロック）の両方を使用して、重要な**安全ガードレール**を実装しました。

この先進的な天気ボットチームの構築を通じて、複雑でインテリジェントなアプリケーションを開発するために不可欠なADKのコアコンセプトについて、実践的な経験を積みました。

**主要なポイント：**

*   **エージェントとツール：** 能力と推論を定義するための基本的な構成要素。明確な指示とdocstringが最も重要です。
*   **ランナーとセッションサービス：** エージェントの実行を調整し、会話のコンテキストを維持するエンジンとメモリ管理システム。
*   **委任：** マルチエージェントチームを設計することで、専門化、モジュール性、および複雑なタスクのより良い管理が可能になります。エージェントの`description`は自動フローの鍵です。
*   **セッション状態（`ToolContext`, `output_key`）：** 文脈を意識した、パーソナライズされた、複数ターンの会話型エージェントを作成するために不可欠です。
*   **コールバック（`before_model`, `before_tool`）：** 重要な操作（LLM呼び出しまたはツール実行）の*前*に、安全性、検証、ポリシーの強制、および動的な変更を実装するための強力なフック。
*   **柔軟性（`LiteLlm`）：** ADKは、パフォーマンス、コスト、機能を比較検討し、仕事に最適なLLMを選択する力を与えます。

**次のステップは？**

あなたの天気ボットチームは素晴らしい出発点です。ADKをさらに探求し、アプリケーションを強化するためのアイデアをいくつか紹介します：

1.  **実際の天気API：** `get_weather`ツールの`mock_weather_db`を、実際の天気API（OpenWeatherMap、WeatherAPIなど）への呼び出しに置き換えます。
2.  **より複雑な状態：** より多くのユーザー設定（例：好みの場所、通知設定）や会話の要約をセッション状態に保存します。
3.  **委任の洗練：** 委任ロジックを微調整するために、異なるルートエージェントの指示やサブエージェントの説明を試します。「予報」エージェントを追加できますか？
4.  **高度なコールバック：**
    *   `after_model_callback`を使用して、LLMの応答が生成された*後*に、それを再フォーマットまたはサニタイズする可能性があります。
    *   `after_tool_callback`を使用して、ツールから返された結果を処理またはログに記録します。
    *   エージェントレベルのエントリ/エグジットロジックのために`before_agent_callback`または`after_agent_callback`を実装します。
5.  **エラーハンドリング：** エージェントがツールのエラーや予期しないAPI応答を処理する方法を改善します。ツール内に再試行ロジックを追加するかもしれません。
6.  **永続的なセッションストレージ：** `InMemorySessionService`の代替として、セッション状態を永続的に保存する方法を探ります（例：FirestoreやCloud SQLのようなデータベースを使用 - カスタム実装または将来のADK統合が必要）。
7.  **ストリーミングUI：** エージェントチームをWebフレームワーク（FastAPIなど、ADKストリーミングクイックスタートで示されているように）と統合して、リアルタイムのチャットインターフェースを作成します。

Agent Development Kitは、洗練されたLLM搭載アプリケーションを構築するための堅牢な基盤を提供します。このチュートリアルでカバーされた概念（ツール、状態、委任、コールバック）を習得することで、ますます複雑なエージェントシステムに取り組む準備が整いました。

開発を楽しんでください！