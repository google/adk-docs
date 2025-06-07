# 에이전트 테스트하기

에이전트를 배포하기 전에 의도한 대로 작동하는지 확인하기 위해 테스트해야 합니다. 개발 환경에서 에이전트를 테스트하는 가장 쉬운 방법은 다음 명령과 함께 ADK 웹 UI를 사용하는 것입니다.

=== "Python"

    ```py
    adk api_server
    ```

=== "Java"

    포트 번호를 업데이트해야 합니다.

    ```java
    mvn compile exec:java \
         -Dexec.args="--adk.agents.source-dir=src/main/java/agents --server.port=8080"
    ```
    Java에서는 개발 UI와 API 서버가 함께 번들로 제공됩니다.

이 명령은 로컬 웹 서버를 시작하며, 여기서 cURL 명령을 실행하거나 API 요청을 보내 에이전트를 테스트할 수 있습니다.

## 로컬 테스트

로컬 테스트는 로컬 웹 서버를 시작하고, 세션을 생성하고, 에이전트에 쿼리를 보내는 과정을 포함합니다. 먼저, 올바른 작업 디렉토리에 있는지 확인하세요:

```console
parent_folder/
└── my_sample_agent/
    └── agent.py (또는 Agent.java)
```

**로컬 서버 시작**

다음으로, 위에 나열된 명령을 사용하여 로컬 서버를 시작합니다.

출력은 다음과 유사하게 나타나야 합니다:

=== "Python"

    ```shell
    INFO:     Started server process [12345]
    INFO:     Waiting for application startup.
    INFO:     Application startup complete.
    INFO:     Uvicorn running on http://localhost:8000 (Press CTRL+C to quit)
    ```

=== "Java"

    ```shell
    2025-05-13T23:32:08.972-06:00  INFO 37864 --- [ebServer.main()] o.s.b.w.embedded.tomcat.TomcatWebServer  : Tomcat started on port 8080 (http) with context path '/'
    2025-05-13T23:32:08.980-06:00  INFO 37864 --- [ebServer.main()] com.google.adk.web.AdkWebServer          : Started AdkWebServer in 1.15 seconds (process running for 2.877)
    2025-05-13T23:32:08.981-06:00  INFO 37864 --- [ebServer.main()] com.google.adk.web.AdkWebServer          : AdkWebServer application started successfully.
    ```

이제 서버가 로컬에서 실행 중입니다. 이후의 모든 명령에서 올바른 **_포트 번호_**를 사용해야 합니다.

**새 세션 만들기**

API 서버가 계속 실행 중인 상태에서 새 터미널 창이나 탭을 열고 다음을 사용하여 에이전트와 새 세션을 만듭니다:

```shell
curl -X POST http://localhost:8000/apps/my_sample_agent/users/u_123/sessions/s_123 \
  -H "Content-Type: application/json" \
  -d '{"state": {"key1": "value1", "key2": 42}}'
```

무슨 일이 일어나고 있는지 분석해 보겠습니다:

* `http://localhost:8000/apps/my_sample_agent/users/u_123/sessions/s_123`: 이것은 에이전트 폴더의 이름인 `my_sample_agent` 에이전트에 대해 사용자 ID(`u_123`)와 세션 ID(`s_123`)로 새 세션을 만듭니다. `my_sample_agent`를 에이전트 폴더의 이름으로 바꿀 수 있습니다. `u_123`을 특정 사용자 ID로, `s_123`을 특정 세션 ID로 바꿀 수 있습니다.
* `{"state": {"key1": "value1", "key2": 42}}`: 이것은 선택 사항입니다. 세션을 만들 때 에이전트의 기존 상태(dict)를 사용자 정의하는 데 사용할 수 있습니다.

성공적으로 생성되면 세션 정보가 반환되어야 합니다. 출력은 다음과 유사하게 나타나야 합니다:

```shell
{"id":"s_123","appName":"my_sample_agent","userId":"u_123","state":{"state":{"key1":"value1","key2":42}},"events":[],"lastUpdateTime":1743711430.022186}
```

!!! info

    정확히 동일한 사용자 ID와 세션 ID로 여러 세션을 만들 수 없습니다. 시도하면 `{"detail":"Session already exists: s_123"}`와 같은 응답을 볼 수 있습니다. 이 문제를 해결하려면 해당 세션(예: `s_123`)을 삭제하거나 다른 세션 ID를 선택하면 됩니다.

**쿼리 보내기**

`/run` 또는 `/run_sse` 라우트를 통해 에이전트에 POST로 쿼리를 보내는 두 가지 방법이 있습니다.

* `POST http://localhost:8000/run`: 모든 이벤트를 목록으로 수집하여 한 번에 반환합니다. 대부분의 사용자에게 적합합니다 (확실하지 않은 경우 이것을 사용하는 것이 좋습니다).
* `POST http://localhost:8000/run_sse`: 서버 전송 이벤트(Server-Sent-Events)로 반환하며, 이는 이벤트 객체의 스트림입니다. 이벤트가 사용 가능해지는 즉시 알림을 받고 싶은 사람들에게 적합합니다. `/run_sse`를 사용하면 `streaming`을 `true`로 설정하여 토큰 수준 스트리밍을 활성화할 수도 있습니다.

**`/run` 사용하기**

```shell
curl -X POST http://localhost:8000/run \
-H "Content-Type: application/json" \
-d '{
"appName": "my_sample_agent",
"userId": "u_123",
"sessionId": "s_123",
"newMessage": {
    "role": "user",
    "parts": [{
    "text": "Hey whats the weather in new york today"
    }]
}
}'
```

`/run`을 사용하면 전체 이벤트 출력을 목록으로 동시에 볼 수 있으며, 다음과 유사하게 나타나야 합니다:

```shell
[{"content":{"parts":[{"functionCall":{"id":"af-e75e946d-c02a-4aad-931e-49e4ab859838","args":{"city":"new york"},"name":"get_weather"}}],"role":"model"},"invocationId":"e-71353f1e-aea1-4821-aa4b-46874a766853","author":"weather_time_agent","actions":{"stateDelta":{},"artifactDelta":{},"requestedAuthConfigs":{}},"longRunningToolIds":[],"id":"2Btee6zW","timestamp":1743712220.385936},{"content":{"parts":[{"functionResponse":{"id":"af-e75e946d-c02a-4aad-931e-49e4ab859838","name":"get_weather","response":{"status":"success","report":"The weather in New York is sunny with a temperature of 25 degrees Celsius (41 degrees Fahrenheit)."}}}],"role":"user"},"invocationId":"e-71353f1e-aea1-4821-aa4b-46874a766853","author":"weather_time_agent","actions":{"stateDelta":{},"artifactDelta":{},"requestedAuthConfigs":{}},"id":"PmWibL2m","timestamp":1743712221.895042},{"content":{"parts":[{"text":"OK. The weather in New York is sunny with a temperature of 25 degrees Celsius (41 degrees Fahrenheit).\n"}],"role":"model"},"invocationId":"e-71353f1e-aea1-4821-aa4b-46874a766853","author":"weather_time_agent","actions":{"stateDelta":{},"artifactDelta":{},"requestedAuthConfigs":{}},"id":"sYT42eVC","timestamp":1743712221.899018}]
```

**`/run_sse` 사용하기**

```shell
curl -X POST http://localhost:8000/run_sse \
-H "Content-Type: application/json" \
-d '{
"appName": "my_sample_agent",
"userId": "u_123",
"sessionId": "s_123",
"newMessage": {
    "role": "user",
    "parts": [{
    "text": "Hey whats the weather in new york today"
    }]
},
"streaming": false
}'
```

`streaming`을 `true`로 설정하여 토큰 수준 스트리밍을 활성화할 수 있습니다. 즉, 응답이 여러 청크로 반환되며 출력은 다음과 유사하게 나타나야 합니다:

```shell
data: {"content":{"parts":[{"functionCall":{"id":"af-f83f8af9-f732-46b6-8cb5-7b5b73bbf13d","args":{"city":"new york"},"name":"get_weather"}}],"role":"model"},"invocationId":"e-3f6d7765-5287-419e-9991-5fffa1a75565","author":"weather_time_agent","actions":{"stateDelta":{},"artifactDelta":{},"requestedAuthConfigs":{}},"longRunningToolIds":[],"id":"ptcjaZBa","timestamp":1743712255.313043}

data: {"content":{"parts":[{"functionResponse":{"id":"af-f83f8af9-f732-46b6-8cb5-7b5b73bbf13d","name":"get_weather","response":{"status":"success","report":"The weather in New York is sunny with a temperature of 25 degrees Celsius (41 degrees Fahrenheit)."}}}],"role":"user"},"invocationId":"e-3f6d7765-5287-419e-9991-5fffa1a75565","author":"weather_time_agent","actions":{"stateDelta":{},"artifactDelta":{},"requestedAuthConfigs":{}},"id":"5aocxjaq","timestamp":1743712257.387306}

data: {"content":{"parts":[{"text":"OK. The weather in New York is sunny with a temperature of 25 degrees Celsius (41 degrees Fahrenheit).\n"}],"role":"model"},"invocationId":"e-3f6d7765-5287-419e-9991-5fffa1a75565","author":"weather_time_agent","actions":{"stateDelta":{},"artifactDelta":{},"requestedAuthConfigs":{}},"id":"rAnWGSiV","timestamp":1743712257.391317}
```

!!! info

    `/run_sse`를 사용하면 각 이벤트를 사용할 수 있게 되는 즉시 볼 수 있어야 합니다.

## 통합

ADK는 [콜백](../callbacks/index.md)을 사용하여 타사 관찰 가능성 도구와 통합합니다. 이러한 통합은 에이전트 호출 및 상호 작용의 상세한 추적을 캡처하며, 이는 동작을 이해하고 문제를 디버깅하며 성능을 평가하는 데 중요합니다.

*   [Comet Opik](https://github.com/comet-ml/opik)은 [ADK를 기본적으로 지원](https://www.comet.com/docs/opik/tracing/integrations/adk)하는 오픈 소스 LLM 관찰 가능성 및 평가 플랫폼입니다.

## 에이전트 배포

이제 에이전트의 로컬 작동을 확인했으므로 에이전트 배포로 넘어갈 준비가 되었습니다! 에이전트를 배포할 수 있는 몇 가지 방법은 다음과 같습니다.

*   [Agent Engine](../deploy/agent-engine.md)에 배포하여 Google Cloud의 Vertex AI에서 관리형 서비스로 ADK 에이전트를 가장 쉽게 배포하세요.
*   [Cloud Run](../deploy/cloud-run.md)에 배포하여 Google Cloud의 서버리스 아키텍처를 사용하여 에이전트를 확장하고 관리하는 방법을 완전히 제어하세요.