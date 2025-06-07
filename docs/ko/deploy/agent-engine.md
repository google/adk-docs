# Vertex AI Agent Engine에 배포하기

![python_only](https://img.shields.io/badge/현재_지원되는_언어-Python-blue){ title="Vertex AI Agent Engine은 현재 Python만 지원합니다."}

[Agent Engine](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/overview)은 개발자가 프로덕션 환경에서 AI 에이전트를 배포, 관리 및 확장할 수 있도록 지원하는 완전 관리형 Google Cloud 서비스입니다. Agent Engine은 프로덕션 환경에서 에이전트를 확장하기 위한 인프라를 처리하므로, 개발자는 지능적이고 영향력 있는 애플리케이션을 만드는 데 집중할 수 있습니다.

```python
from vertexai import agent_engines

remote_app = agent_engines.create(
    agent_engine=root_agent,
    requirements=[
        "google-cloud-aiplatform[adk,agent_engines]",
    ]
)
```

## Vertex AI SDK 설치

Agent Engine은 Python용 Vertex AI SDK의 일부입니다. 자세한 내용은 [Agent Engine 빠른 시작 문서](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/quickstart)를 참조하세요.

### Vertex AI SDK 설치

```shell
pip install google-cloud-aiplatform[adk,agent_engines]
```

!!!info
    Agent Engine은 Python 버전 >=3.9 및 <=3.12만 지원합니다.

### 초기화

```py
import vertexai

PROJECT_ID = "your-project-id"
LOCATION = "us-central1"
STAGING_BUCKET = "gs://your-google-cloud-storage-bucket"

vertexai.init(
    project=PROJECT_ID,
    location=LOCATION,
    staging_bucket=STAGING_BUCKET,
)
```

`LOCATION`에 대해서는 [Agent Engine에서 지원하는 리전](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/overview#supported-regions) 목록을 확인할 수 있습니다.

### 에이전트 생성

아래의 샘플 에이전트를 사용할 수 있습니다. 이 에이전트는 두 개의 도구(지정된 도시의 날씨 또는 시간 검색)를 가지고 있습니다:

```python
--8<-- "examples/python/snippets/get-started/multi_tool_agent/agent.py"
```

### Agent Engine용 에이전트 준비

`reasoning_engines.AdkApp()`을 사용하여 에이전트를 래핑하여 Agent Engine에 배포할 수 있도록 만드세요.

```py
from vertexai.preview import reasoning_engines

app = reasoning_engines.AdkApp(
    agent=root_agent,
    enable_tracing=True,
)
```

### 로컬에서 에이전트 테스트하기

Agent Engine에 배포하기 전에 로컬에서 테스트할 수 있습니다.

#### 세션 생성 (로컬)

```py
session = app.create_session(user_id="u_123")
session
```

`create_session`의 예상 출력 (로컬):

```console
Session(id='c6a33dae-26ef-410c-9135-b434a528291f', app_name='default-app-name', user_id='u_123', state={}, events=[], last_update_time=1743440392.8689594)
```

#### 세션 목록 보기 (로컬)

```py
app.list_sessions(user_id="u_123")
```

`list_sessions`의 예상 출력 (로컬):

```console
ListSessionsResponse(session_ids=['c6a33dae-26ef-410c-9135-b434a528291f'])
```

#### 특정 세션 가져오기 (로컬)

```py
session = app.get_session(user_id="u_123", session_id=session.id)
session
```

`get_session`의 예상 출력 (로컬):

```console
Session(id='c6a33dae-26ef-410c-9135-b434a528291f', app_name='default-app-name', user_id='u_123', state={}, events=[], last_update_time=1743681991.95696)
```

#### 에이전트에 쿼리 보내기 (로컬)

```py
for event in app.stream_query(
    user_id="u_123",
    session_id=session.id,
    message="뉴욕 날씨는 어때요",
):
print(event)
```

`stream_query`의 예상 출력 (로컬):

```console
{'parts': [{'function_call': {'id': 'af-a33fedb0-29e6-4d0c-9eb3-00c402969395', 'args': {'city': 'new york'}, 'name': 'get_weather'}}], 'role': 'model'}
{'parts': [{'function_response': {'id': 'af-a33fedb0-29e6-4d0c-9eb3-00c402969395', 'name': 'get_weather', 'response': {'status': 'success', 'report': '뉴욕의 날씨는 맑고 섭씨 25도(화씨 41도)입니다.'}}}], 'role': 'user'}
{'parts': [{'text': '뉴욕의 날씨는 맑고 섭씨 25도(화씨 41도)입니다.'}], 'role': 'model'}
```

### Agent Engine에 에이전트 배포하기

```python
from vertexai import agent_engines

remote_app = agent_engines.create(
    agent_engine=root_agent,
    requirements=[
        "google-cloud-aiplatform[adk,agent_engines]"   
    ]
)
```

이 단계는 완료하는 데 몇 분이 걸릴 수 있습니다. 각 배포된 에이전트에는 고유한 식별자가 있습니다. 다음 명령을 실행하여 배포된 에이전트의 resource_name 식별자를 얻을 수 있습니다:

```python
remote_app.resource_name
```

응답은 다음 문자열과 같아야 합니다:

```
f"projects/{PROJECT_NUMBER}/locations/{LOCATION}/reasoningEngines/{RESOURCE_ID}"
```

자세한 내용은 Agent Engine 문서의 [에이전트 배포](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/deploy) 및 [배포된 에이전트 관리](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/manage/overview)를 참조하세요.

### Agent Engine에서 에이전트 테스트하기

#### 세션 생성 (원격)

```py
remote_session = remote_app.create_session(user_id="u_456")
remote_session
```

`create_session`의 예상 출력 (원격):

```console
{'events': [],
'user_id': 'u_456',
'state': {},
'id': '7543472750996750336',
'app_name': '7917477678498709504',
'last_update_time': 1743683353.030133}
```

`id`는 세션 ID이고, `app_name`은 Agent Engine에 배포된 에이전트의 리소스 ID입니다.

#### 세션 목록 보기 (원격)

```py
remote_app.list_sessions(user_id="u_456")
```

#### 특정 세션 가져오기 (원격)

```py
remote_app.get_session(user_id="u_456", session_id=remote_session["id"])
```

!!!note
    로컬에서 에이전트를 사용할 때 세션 ID는 `session.id`에 저장되지만, Agent Engine에서 원격으로 에이전트를 사용할 때 세션 ID는 `remote_session["id"]`에 저장됩니다.

#### 에이전트에 쿼리 보내기 (원격)

```py
for event in remote_app.stream_query(
    user_id="u_456",
    session_id=remote_session["id"],
    message="뉴욕 날씨는 어때요",
):
    print(event)
```

`stream_query`의 예상 출력 (원격):

```console
{'parts': [{'function_call': {'id': 'af-f1906423-a531-4ecf-a1ef-723b05e85321', 'args': {'city': 'new york'}, 'name': 'get_weather'}}], 'role': 'model'}
{'parts': [{'function_response': {'id': 'af-f1906423-a531-4ecf-a1ef-723b05e85321', 'name': 'get_weather', 'response': {'status': 'success', 'report': '뉴욕의 날씨는 맑고 섭씨 25도(화씨 41도)입니다.'}}}], 'role': 'user'}
{'parts': [{'text': '뉴욕의 날씨는 맑고 섭씨 25도(화씨 41도)입니다.'}], 'role': 'model'}
```



## 정리

작업을 마친 후에는 클라우드 리소스를 정리하는 것이 좋습니다.
Google Cloud 계정에 예기치 않은 요금이 부과되는 것을 방지하기 위해 배포된 Agent Engine 인스턴스를 삭제할 수 있습니다.

```python
remote_app.delete(force=True)
```

`force=True`는 세션과 같이 배포된 에이전트에서 생성된 모든 하위 리소스도 삭제합니다.