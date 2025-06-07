# ADK의 양방향 스트리밍(라이브)

!!! info

    이것은 실험적인 기능입니다. 현재 Python에서 사용할 수 있습니다.

!!! info

    이는 서버 측 스트리밍이나 토큰 수준 스트리밍과는 다릅니다. 이 섹션은 양방향 스트리밍(라이브)에 관한 것입니다.
    
ADK의 양방향 스트리밍(라이브)은 [Gemini Live API](https://ai.google.dev/gemini-api/docs/live)의 저지연 양방향 음성 및 영상 상호작용 기능을 AI 에이전트에 추가합니다.

양방향 스트리밍(라이브) 모드를 사용하면, 사용자가 음성 명령으로 에이전트의 응답을 중단할 수 있는 기능을 포함하여, 자연스럽고 사람과 유사한 음성 대화 경험을 최종 사용자에게 제공할 수 있습니다. 스트리밍 기능이 있는 에이전트는 텍스트, 오디오, 비디오 입력을 처리할 수 있으며, 텍스트 및 오디오 출력을 제공할 수 있습니다.

<div class="video-grid">
  <div class="video-item">
    <div class="video-container">
      <iframe src="https://www.youtube-nocookie.com/embed/Tu7-voU7nnw?si=RKs7EWKjx0bL96i5" title="쇼퍼스 컨시어지" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>
    </div>
  </div>

  <div class="video-item">
    <div class="video-container">
      <iframe src="https://www.youtube-nocookie.com/embed/LwHPYyw7u6U?si=xxIEhnKBapzQA6VV" title="쇼퍼스 컨시어지" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>
    </div>
  </div>
</div>

<div class="grid cards" markdown>

-   :material-console-line: **빠른 시작 (스트리밍)**

    ---

    이 빠른 시작에서는 간단한 에이전트를 구축하고 ADK의 스트리밍을 사용하여 저지연 양방향 음성 및 영상 통신을 구현합니다.

    [:octicons-arrow-right-24: 더 알아보기](../get-started/streaming/quickstart-streaming.md)

-   :material-console-line: **스트리밍 도구**

    ---

    스트리밍 도구를 사용하면 도구(함수)가 중간 결과를 에이전트에게 다시 스트리밍할 수 있으며, 에이전트는 이러한 중간 결과에 응답할 수 있습니다. 예를 들어, 스트리밍 도구를 사용하여 주가 변동을 모니터링하고 에이전트가 이에 반응하도록 할 수 있습니다. 또 다른 예로는 에이전트가 비디오 스트림을 모니터링하다가 비디오 스트림에 변화가 있을 때 에이전트가 그 변화를 보고하도록 할 수 있습니다.

    [:octicons-arrow-right-24: 더 알아보기](streaming-tools.md)

-   :material-console-line: **사용자 정의 오디오 스트리밍 앱 샘플**

    ---

    이 글은 ADK 스트리밍과 FastAPI로 구축된 사용자 정의 비동기 웹 앱의 서버 및 클라이언트 코드를 개괄적으로 설명하며, 서버 전송 이벤트(SSE)와 WebSocket을 모두 사용한 실시간 양방향 오디오 및 텍스트 통신을 가능하게 합니다.

    [:octicons-arrow-right-24: 더 알아보기 (SSE)](custom-streaming.md)
    [:octicons-arrow-right-24: 더 알아보기 (WebSocket)](custom-streaming-ws.md)

-   :material-console-line: **쇼퍼스 컨시어지 데모**

    ---

    ADK의 스트리밍을 사용하여 개인 스타일을 이해하고 맞춤형 추천을 제공하는 개인 쇼핑 컨시어지를 구축하는 방법을 알아보세요.

    [:octicons-arrow-right-24: 더 알아보기](https://youtu.be/LwHPYyw7u6U)

-   :material-console-line: **스트리밍 구성**

    ---

    라이브(스트리밍) 에이전트에 대해 설정할 수 있는 몇 가지 구성이 있습니다.

    [:octicons-arrow-right-24: 더 알아보기](configuration.md)
</div>