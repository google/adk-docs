# ストリーミングツール

!!! info

    これはストリーミング（ライブ）エージェント/APIでのみサポートされています。

ストリーミングツールを使用すると、ツール（関数）が中間結果をエージェントにストリーミングで返し、エージェントはそれらの中間結果に応答できます。
例えば、ストリーミングツールを使用して株価の変動を監視し、エージェントにそれに反応させることができます。別の例として、エージェントにビデオストリームを監視させ、ビデオストリームに変化があったときにエージェントにその変化を報告させることができます。

ストリーミングツールを定義するには、以下に従う必要があります。

1.  **非同期関数:** ツールは`async` Python関数でなければなりません。
2.  **AsyncGeneratorの戻り値の型:** 関数は`AsyncGenerator`を返すように型付けする必要があります。`AsyncGenerator`の最初の型パラメータは`yield`するデータの型（例: テキストメッセージの場合は`str`、構造化データの場合はカスタムオブジェクト）です。2番目の型パラメータは、ジェネレータが`send()`を介して値を受け取らない場合は通常`None`です。

2種類のストリーミングツールをサポートしています。
-   シンプルな型。これは、入力としてビデオ/音声ストリーム（ADK WebやADKランナーに供給するもの）以外のストリームのみを受け取るタイプのストリーミングツールです。
-   ビデオストリーミングツール。これはビデオストリーミングでのみ機能し、ビデオストリーム（ADK WebやADKランナーに供給するもの）がこの関数に渡されます。

それでは、株価の変動を監視し、ビデオストリームの変化を監視できるエージェントを定義してみましょう。

```python
import asyncio
from typing import AsyncGenerator

from google.adk.agents import LiveRequestQueue
from google.adk.agents.llm_agent import Agent
from google.adk.tools.function_tool import FunctionTool
from google.genai import Client
from google.genai import types as genai_types


async def monitor_stock_price(stock_symbol: str) -> AsyncGenerator[str, None]:
  """この関数は、指定されたstock_symbolの価格を継続的、ストリーミング、非同期で監視します。"""
  print(f"{stock_symbol}の株価監視を開始します！")

  # 株価の変動をモックします。
  await asyncio.sleep(4)
  price_alert1 = f"{stock_symbol}の価格は300です"
  yield price_alert1
  print(price_alert1)

  await asyncio.sleep(4)
  price_alert1 = f"{stock_symbol}の価格は400です"
  yield price_alert1
  print(price_alert1)

  await asyncio.sleep(20)
  price_alert1 = f"{stock_symbol}の価格は900です"
  yield price_alert1
  print(price_alert1)

  await asyncio.sleep(20)
  price_alert1 = f"{stock_symbol}の価格は500です"
  yield price_alert1
  print(price_alert1)


# ビデオストリーミングの場合、`input_stream: LiveRequestQueue`はADKがビデオストリームを渡すために必須かつ予約済みのキーパラメータです。
async def monitor_video_stream(
    input_stream: LiveRequestQueue,
) -> AsyncGenerator[str, None]:
  """ビデオストリームに何人いるかを監視します。"""
  print("monitor_video_streamを開始します！")
  client = Client(vertexai=False)
  prompt_text = (
      "この画像に写っている人数を数えてください。数字のみで応答してください。"
  )
  last_count = None
  while True:
    last_valid_req = None
    print("監視ループを開始します")

    # このループを使用して最新の画像をプルし、古いものを破棄します
    while input_stream._queue.qsize() != 0:
      live_req = await input_stream.get()

      if live_req.blob is not None and live_req.blob.mime_type == "image/jpeg":
        last_valid_req = live_req

    # 有効な画像が見つかった場合、それを処理します
    if last_valid_req is not None:
      print("キューから最新のフレームを処理しています")

      # blobのデータとMIMEタイプを使用して画像パートを作成します
      image_part = genai_types.Part.from_bytes(
          data=last_valid_req.blob.data, mime_type=last_valid_req.blob.mime_type
      )

      contents = genai_types.Content(
          role="user",
          parts=[image_part, genai_types.Part.from_text(prompt_text)],
      )

      # 提供された画像とプロンプトに基づいてコンテンツを生成するためにモデルを呼び出します
      response = client.models.generate_content(
          model="gemini-2.0-flash-exp",
          contents=contents,
          config=genai_types.GenerateContentConfig(
              system_instruction=(
                  "あなたは役立つビデオ分析アシスタントです。この画像やビデオに写っている"
                  "人数を数えることができます。数字のみで応答してください。"
              )
          ),
      )
      if not last_count:
        last_count = response.candidates[0].content.parts[0].text
      elif last_count != response.candidates[0].content.parts[0].text:
        last_count = response.candidates[0].content.parts[0].text
        yield response
        print("response:", response)

    # 新しい画像をチェックする前に待機します
    await asyncio.sleep(0.5)


# 要求されたときにADKがストリーミングツールを停止するのを助けるために、この正確な関数を使用します。
# 例えば、`monitor_stock_price`を停止したい場合、エージェントはこの関数を
# stop_streaming(function_name=monitor_stock_price)として呼び出します。
def stop_streaming(function_name: str):
  """ストリーミングを停止します

  Args:
    function_name: 停止するストリーミング関数の名前。
  """
  pass


root_agent = Agent(
    model="gemini-2.0-flash-exp",
    name="video_streaming_agent",
    instruction="""
      あなたは監視エージェントです。提供されたツール/関数を使用して、
      ビデオ監視と株価監視ができます。
      ユーザーがビデオストリームを監視したい場合、
      monitor_video_stream関数を使用してそれを行うことができます。monitor_video_streamが
      アラートを返した場合、ユーザーにそれを伝えるべきです。
      ユーザーが株価を監視したい場合、monitor_stock_priceを使用できます。
      あまり多くの質問をしないでください。おしゃべりになりすぎないでください。
    """,
    tools=[
        monitor_video_stream,
        monitor_stock_price,
        FunctionTool(stop_streaming),
    ]
)
```

テスト用のサンプルクエリは次のとおりです。
-   $XYZ株の株価を監視するのを手伝ってください。
-   ビデオストリームに何人いるか監視するのを手伝ってください。