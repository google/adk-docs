# ADK의 양방향 스트리밍(Bidi-streaming, live)

!!! info "정보"

    이 기능은 실험적 기능입니다. 현재 Python에서 사용할 수 있습니다.

!!! info "정보"

    이 기능은 서버 측 스트리밍이나 토큰 수준 스트리밍과는 다릅니다. 이 섹션은 양방향 스트리밍(bidi-streaming, live)에 대한 내용입니다.
    
ADK의 양방향 스트리밍(live)은 [Gemini Live API](https://ai.google.dev/gemini-api/docs/live)의 저지연 양방향 음성 및 영상 상호작용 기능을 AI 에이전트에 추가합니다.

양방향 스트리밍(live) 모드를 사용하면, 최종 사용자에게 자연스럽고 인간과 유사한 음성 대화 경험을 제공할 수 있습니다. 여기에는 사용자가 음성 명령으로 에이전트의 응답을 중단시키는 기능도 포함됩니다. 스트리밍을 사용하는 에이전트는 텍스트, 오디오, 영상 입력을 처리할 수 있으며, 텍스트와 오디오 출력을 제공할 수 있습니다.

<div class="video-grid">
  <div class="video-item">
    <div class="video-container">
      <iframe src="https://www.youtube-nocookie.com/embed/Tu7-voU7nnw?si=RKs7EWKjx0bL96i5" title="Shopper's Concierge" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>
    </div>
  </div>

  <div class="video-item">
    <div class="video-container">
      <iframe src="https://www.youtube-nocookie.com/embed/LwHPYyw7u6U?si=xxIEhnKBapzQA6VV" title="Shopper's Concierge" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>
    </div>
  </div>
</div>

<div class="grid cards" markdown>

-   :material-console-line: **퀵스타트 (스트리밍)**

    ---

    이 퀵스타트에서는 간단한 에이전트를 구축하고 ADK의 스트리밍을 사용하여 저지연 양방향 음성 및 영상 통신을 구현합니다.

    [:octicons-arrow-right-24: 자세히 알아보기](../get-started/streaming/quickstart-streaming.md)

-   :material-console-line: **스트리밍 도구**

    ---

    스트리밍 도구를 사용하면 도구(함수)가 중간 결과를 에이전트에게 스트리밍으로 다시 보낼 수 있으며, 에이전트는 이러한 중간 결과에 응답할 수 있습니다. 예를 들어, 스트리밍 도구를 사용하여 주가 변동을 모니터링하고 에이전트가 이에 반응하도록 할 수 있습니다. 또 다른 예로, 에이전트가 비디오 스트림을 모니터링하다가 스트림에 변화가 생기면 그 변화를 보고하도록 할 수 있습니다.

    [:octicons-arrow-right-24: 자세히 알아보기](streaming-tools.md)

-   :material-console-line: **커스텀 오디오 스트리밍 앱 샘플**

    ---

    이 문서는 ADK 스트리밍과 FastAPI로 구축된 커스텀 비동기 웹 앱의 서버 및 클라이언트 코드를 개괄적으로 설명합니다. 서버-전송 이벤트(SSE)와 웹소켓(WebSocket)을 모두 사용하여 실시간 양방향 오디오 및 텍스트 통신을 구현합니다.

    [:octicons-arrow-right-24: 자세히 알아보기 (SSE)](custom-streaming.md) 및 
    [:octicons-arrow-right-24: (웹소켓)](custom-streaming-ws.md)

-   :material-console-line: **블로그 게시물: Google ADK + Vertex AI Live API**

    ---

    이 글은 ADK의 양방향 스트리밍(live)을 사용하여 실시간 오디오/비디오 스트리밍을 구현하는 방법을 보여줍니다. 커스텀 대화형 AI 에이전트를 구축하기 위해 `LiveRequestQueue`를 사용하는 Python 서버 예제를 제공합니다.

    [:octicons-arrow-right-24: 자세히 알아보기](https://medium.com/google-cloud/google-adk-vertex-ai-live-api-125238982d5e)

-   :material-console-line: **Shopper's Concierge 데모**

    ---

    ADK의 스트리밍을 사용하여 개인의 스타일을 이해하고 맞춤형 추천을 제공하는 개인 쇼핑 컨시어지를 구축하는 방법을 알아보세요.

    [:octicons-arrow-right-24: 자세히 알아보기](https://youtu.be/LwHPYyw7u6U)

-   :material-console-line: **스트리밍 구성**

    ---

    라이브(스트리밍) 에이전트에 대해 설정할 수 있는 몇 가지 구성 옵션이 있습니다.

    [:octicons-arrow-right-24: 자세히 알아보기](configuration.md)
</div>