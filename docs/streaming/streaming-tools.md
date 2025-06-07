# 스트리밍 도구

!!! info

    이것은 스트리밍(라이브) 에이전트/API에서만 지원됩니다.

스트리밍 도구를 사용하면 도구(함수)가 중간 결과를 에이전트에게 다시 스트리밍할 수 있으며, 에이전트는 이러한 중간 결과에 응답할 수 있습니다.
예를 들어, 스트리밍 도구를 사용하여 주가 변동을 모니터링하고 에이전트가 이에 반응하도록 할 수 있습니다. 또 다른 예로는 에이전트가 비디오 스트림을 모니터링하다가 비디오 스트림에 변화가 있을 때 에이전트가 그 변화를 보고하도록 할 수 있습니다.

스트리밍 도구를 정의하려면 다음을 준수해야 합니다:

1.  **비동기 함수:** 도구는 `async` Python 함수여야 합니다.
2.  **AsyncGenerator 반환 유형:** 함수는 `AsyncGenerator`를 반환하도록 유형이 지정되어야 합니다. `AsyncGenerator`의 첫 번째 유형 매개변수는 `yield`하는 데이터의 유형입니다(예: 텍스트 메시지의 경우 `str`, 구조화된 데이터의 경우 사용자 정의 객체). 두 번째 유형 매개변수는 생성기가 `send()`를 통해 값을 받지 않는 경우 일반적으로 `None`입니다.


두 가지 유형의 스트리밍 도구를 지원합니다:
- 간단한 유형. 이것은 비디오/오디오 스트림이 아닌 스트림(adk web 또는 adk runner에 공급하는 스트림)만 입력으로 받는 한 가지 유형의 스트리밍 도구입니다.
- 비디오 스트리밍 도구. 이것은 비디오 스트리밍에서만 작동하며 비디오 스트림(adk web 또는 adk runner에 공급하는 스트림)이 이 함수에 전달됩니다.

이제 주가 변동을 모니터링하고 비디오 스트림 변화를 모니터링할 수 있는 에이전트를 정의해 보겠습니다.

```python
import asyncio
from typing import AsyncGenerator

from google.adk.agents import LiveRequestQueue
from google.adk.agents.llm_agent import Agent
from google.adk.tools.function_tool import FunctionTool
from google.genai import Client
from google.genai import types as genai_types


async def monitor_stock_price(stock_symbol: str) -> AsyncGenerator[str, None]:
  """이 함수는 주어진 stock_symbol에 대한 가격을 지속적이고, 스트리밍하며, 비동기적인 방식으로 모니터링합니다."""
  print(f"{stock_symbol}의 주가 모니터링 시작!")

  # 주가 변동을 모의 실험해 보겠습니다.
  await asyncio.sleep(4)
  price_alert1 = f"{stock_symbol}의 가격은 300입니다"
  yield price_alert1
  print(price_alert1)

  await asyncio.sleep(4)
  price_alert1 = f"{stock_symbol}의 가격은 400입니다"
  yield price_alert1
  print(price_alert1)

  await asyncio.sleep(20)
  price_alert1 = f"{stock_symbol}의 가격은 900입니다"
  yield price_alert1
  print(price_alert1)

  await asyncio.sleep(20)
  price_alert1 = f"{stock_symbol}의 가격은 500입니다"
  yield price_alert1
  print(price_alert1)


# 비디오 스트리밍의 경우, `input_stream: LiveRequestQueue`는 ADK가 비디오 스트림을 전달하기 위해 필요한 예약된 키 매개변수입니다.
async def monitor_video_stream(
    input_stream: LiveRequestQueue,
) -> AsyncGenerator[str, None]:
  """비디오 스트림에 몇 명의 사람이 있는지 모니터링합니다."""
  print("monitor_video_stream 시작!")
  client = Client(vertexai=False)
  prompt_text = (
      "이 이미지에 있는 사람 수를 세어주세요. 숫자만 응답해 주세요."
  )
  last_count = None
  while True:
    last_valid_req = None
    print("모니터링 루프 시작")

    # 이 루프를 사용하여 최신 이미지를 가져오고 오래된 이미지는 버립니다.
    while input_stream._queue.qsize() != 0:
      live_req = await input_stream.get()

      if live_req.blob is not None and live_req.blob.mime_type == "image/jpeg":
        last_valid_req = live_req

    # 유효한 이미지를 찾으면 처리합니다.
    if last_valid_req is not None:
      print("큐에서 가장 최근 프레임 처리 중")

      # blob의 데이터와 마임 유형을 사용하여 이미지 파트 생성
      image_part = genai_types.Part.from_bytes(
          data=last_valid_req.blob.data, mime_type=last_valid_req.blob.mime_type
      )

      contents = genai_types.Content(
          role="user",
          parts=[image_part, genai_types.Part.from_text(prompt_text)],
      )

      # 제공된 이미지와 프롬프트를 기반으로 콘텐츠를 생성하도록 모델 호출
      response = client.models.generate_content(
          model="gemini-2.0-flash-exp",
          contents=contents,
          config=genai_types.GenerateContentConfig(
              system_instruction=(
                  "당신은 유용한 비디오 분석 어시스턴트입니다. 이 이미지나 비디오에 있는 사람 수를 셀 수 있습니다. 숫자만 응답해 주세요."
              )
          ),
      )
      if not last_count:
        last_count = response.candidates[0].content.parts[0].text
      elif last_count != response.candidates[0].content.parts[0].text:
        last_count = response.candidates[0].content.parts[0].text
        yield response
        print("응답:", response)

    # 새 이미지를 확인하기 전에 대기
    await asyncio.sleep(0.5)


# ADK가 요청 시 스트리밍 도구를 중지하도록 돕기 위해 이 함수를 정확히 사용하세요.
# 예를 들어, `monitor_stock_price`를 중지하려면 에이전트는
# stop_streaming(function_name=monitor_stock_price)으로 이 함수를 호출합니다.
def stop_streaming(function_name: str):
  """스트리밍 중지

  Args:
    function_name: 중지할 스트리밍 함수의 이름.
  """
  pass


root_agent = Agent(
    model="gemini-2.0-flash-exp",
    name="video_streaming_agent",
    instruction="""
      당신은 모니터링 에이전트입니다. 제공된 도구/함수를 사용하여 비디오 모니터링과 주가 모니터링을 할 수 있습니다.
      사용자가 비디오 스트림을 모니터링하기를 원할 때,
      monitor_video_stream 함수를 사용하여 그렇게 할 수 있습니다. monitor_video_stream이
      경고를 반환하면 사용자에게 알려야 합니다.
      사용자가 주가를 모니터링하기를 원할 때, monitor_stock_price를 사용할 수 있습니다.
      너무 많은 질문을 하지 마세요. 너무 말이 많지 마세요.
    """,
    tools=[
        monitor_video_stream,
        monitor_stock_price,
        FunctionTool(stop_streaming),
    ]
)
```

테스트할 샘플 쿼리는 다음과 같습니다:
- XYZ 주식의 주가를 모니터링하는 데 도움을 주세요.
- 비디오 스트림에 몇 명의 사람이 있는지 모니터링하는 데 도움을 주세요.