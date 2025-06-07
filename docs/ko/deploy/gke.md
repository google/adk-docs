# GKE에 배포하기

[GKE](https://cloud.google.com/gke)는 Google Cloud의 관리형 Kubernetes 서비스입니다. Kubernetes를 사용하여 컨테이너화된 애플리케이션을 배포하고 관리할 수 있습니다.

에이전트를 배포하려면 GKE에서 실행되는 Kubernetes 클러스터가 필요합니다. Google Cloud Console 또는 `gcloud` 명령줄 도구를 사용하여 클러스터를 만들 수 있습니다.

이 예제에서는 간단한 에이전트를 GKE에 배포합니다. 에이전트는 LLM으로 `Gemini 2.0 Flash`를 사용하는 FastAPI 애플리케이션이 될 것입니다. 환경 변수를 사용하여 LLM 제공자로 Vertex AI 또는 AI Studio를 사용할 수 있습니다.

## 에이전트 샘플

각 명령어에 대해 [LLM 에이전트](../agents/llm-agents.md) 페이지에 정의된 `capital_agent` 샘플을 참조합니다. 이 샘플이 `capital_agent` 디렉토리에 있다고 가정합니다.

계속 진행하려면 에이전트 코드가 다음과 같이 구성되어 있는지 확인하세요:

1. 에이전트 코드는 에이전트 디렉토리 내 `agent.py`라는 파일에 있습니다.
2. 에이전트 변수 이름은 `root_agent`입니다.
3. `__init__.py`는 에이전트 디렉토리 내에 있으며 `from . import agent`를 포함합니다.

## 환경 변수

[설정 및 설치](../get-started/installation.md) 가이드에 설명된 대로 환경 변수를 설정하세요. 또한 `kubectl` 명령줄 도구를 설치해야 합니다. [Google Kubernetes Engine 문서](https://cloud.google.com/kubernetes-engine/docs/how-to/cluster-access-for-kubectl)에서 지침을 찾을 수 있습니다.

```bash
export GOOGLE_CLOUD_PROJECT=your-project-id # GCP 프로젝트 ID
export GOOGLE_CLOUD_LOCATION=us-central1 # 또는 선호하는 위치
export GOOGLE_GENAI_USE_VERTEXAI=true # Vertex AI를 사용하는 경우 true로 설정
export GOOGLE_CLOUD_PROJECT_NUMBER=$(gcloud projects describe --format json $GOOGLE_CLOUD_PROJECT | jq -r ".projectNumber")
```

`jq`가 설치되어 있지 않은 경우 다음 명령을 사용하여 프로젝트 번호를 얻을 수 있습니다:

```bash
gcloud projects describe $GOOGLE_CLOUD_PROJECT
```

그리고 출력에서 프로젝트 번호를 복사하세요.

```bash
export GOOGLE_CLOUD_PROJECT_NUMBER=YOUR_PROJECT_NUMBER
```

## 배포 명령어

### gcloud CLI

`gcloud` 및 `kubectl` CLI와 Kubernetes 매니페스트 파일을 사용하여 GKE에 에이전트를 배포할 수 있습니다.

Google Cloud에 인증되었는지 확인하세요(`gcloud auth login` 및 `gcloud config set project <your-project-id>`).

### API 활성화

프로젝트에 필요한 API를 활성화하세요. `gcloud` 명령줄 도구를 사용하여 이 작업을 수행할 수 있습니다.

```bash
gcloud services enable \
    container.googleapis.com \
    artifactregistry.googleapis.com \
    cloudbuild.googleapis.com \
    aiplatform.googleapis.com
```

### GKE 클러스터 생성

`gcloud` 명령줄 도구를 사용하여 GKE 클러스터를 만들 수 있습니다. 이 예제는 `us-central1` 리전에 `adk-cluster`라는 Autopilot 클러스터를 만듭니다.

> GKE Standard 클러스터를 만드는 경우 [Workload Identity](https://cloud.google.com/kubernetes-engine/docs/how-to/workload-identity)가 활성화되어 있는지 확인하세요. Workload Identity는 AutoPilot 클러스터에서 기본적으로 활성화되어 있습니다.

```bash
gcloud container clusters create-auto adk-cluster \
    --location=$GOOGLE_CLOUD_LOCATION \
    --project=$GOOGLE_CLOUD_PROJECT
```

클러스터를 만든 후 `kubectl`을 사용하여 연결해야 합니다. 이 명령은 `kubectl`이 새 클러스터에 대한 자격 증명을 사용하도록 구성합니다.

```bash
gcloud container clusters get-credentials adk-cluster \
    --location=$GOOGLE_CLOUD_LOCATION \
    --project=$GOOGLE_CLOUD_PROJECT
```

### 프로젝트 구조

프로젝트 파일을 다음과 같이 구성하세요:

```txt
your-project-directory/
├── capital_agent/
│   ├── __init__.py
│   └── agent.py       # 에이전트 코드 ("에이전트 샘플" 탭 참조)
├── main.py            # FastAPI 애플리케이션 진입점
├── requirements.txt   # Python 종속성
└── Dockerfile         # 컨테이너 빌드 지침
```

`your-project-directory/`의 루트에 다음 파일(`main.py`, `requirements.txt`, `Dockerfile`)을 만드세요.

### 코드 파일

1. 이 파일은 ADK의 `get_fast_api_app()`을 사용하여 FastAPI 애플리케이션을 설정합니다:

    ```python title="main.py"
    import os

    import uvicorn
    from fastapi import FastAPI
    from google.adk.cli.fast_api import get_fast_api_app

    # main.py가 있는 디렉토리 가져오기
    AGENT_DIR = os.path.dirname(os.path.abspath(__file__))
    # 예제 세션 DB URL (예: SQLite)
    SESSION_DB_URL = "sqlite:///./sessions.db"
    # CORS를 위한 예제 허용 출처
    ALLOWED_ORIGINS = ["http://localhost", "http://localhost:8080", "*"]
    # 웹 인터페이스를 제공하려는 경우 web=True, 그렇지 않으면 False로 설정
    SERVE_WEB_INTERFACE = True

    # FastAPI 앱 인스턴스를 가져오는 함수 호출
    # 에이전트 디렉토리 이름('capital_agent')이 에이전트 폴더와 일치하는지 확인
    app: FastAPI = get_fast_api_app(
        agents_dir=AGENT_DIR,
        session_db_url=SESSION_DB_URL,
        allow_origins=ALLOWED_ORIGINS,
        web=SERVE_WEB_INTERFACE,
    )

    # 필요한 경우 아래에 더 많은 FastAPI 경로 또는 구성을 추가할 수 있음
    # 예제:
    # @app.get("/hello")
    # async def read_root():
    #     return {"Hello": "World"}

    if __name__ == "__main__":
        # Cloud Run에서 제공하는 PORT 환경 변수 사용, 기본값 8080
        uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
    ```

    *참고: `agent_dir`을 `main.py`가 있는 디렉토리로 지정하고 Cloud Run 호환성을 위해 `os.environ.get("PORT", 8080)`을 사용합니다.*

2. 필요한 Python 패키지를 나열합니다:

    ```txt title="requirements.txt"
    google_adk
    # 에이전트에 필요한 다른 종속성 추가
    ```

3. 컨테이너 이미지를 정의합니다:

    ```dockerfile title="Dockerfile"
    FROM python:3.13-slim
    WORKDIR /app

    COPY requirements.txt .
    RUN pip install --no-cache-dir -r requirements.txt

    RUN adduser --disabled-password --gecos "" myuser && \
        chown -R myuser:myuser /app

    COPY . .

    USER myuser

    ENV PATH="/home/myuser/.local/bin:$PATH"

    CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port $PORT"]
    ```

### 컨테이너 이미지 빌드

컨테이너 이미지를 저장하기 위해 Google Artifact Registry 저장소를 만들어야 합니다. `gcloud` 명령줄 도구를 사용하여 이 작업을 수행할 수 있습니다.

```bash
gcloud artifacts repositories create adk-repo \
    --repository-format=docker \
    --location=$GOOGLE_CLOUD_LOCATION \
    --description="ADK 저장소"
```

`gcloud` 명령줄 도구를 사용하여 컨테이너 이미지를 빌드합니다. 이 예제는 이미지를 빌드하고 `adk-repo/adk-agent:latest`로 태그를 지정합니다.

```bash
gcloud builds submit \
    --tag $GOOGLE_CLOUD_LOCATION-docker.pkg.dev/$GOOGLE_CLOUD_PROJECT/adk-repo/adk-agent:latest \
    --project=$GOOGLE_CLOUD_PROJECT \
    .
```

이미지가 빌드되어 Artifact Registry에 푸시되었는지 확인합니다:

```bash
gcloud artifacts docker images list \
  $GOOGLE_CLOUD_LOCATION-docker.pkg.dev/$GOOGLE_CLOUD_PROJECT/adk-repo \
  --project=$GOOGLE_CLOUD_PROJECT
```

### Vertex AI용 Kubernetes 서비스 계정 구성

에이전트가 Vertex AI를 사용하는 경우 필요한 권한을 가진 Kubernetes 서비스 계정을 만들어야 합니다. 이 예제는 `adk-agent-sa`라는 서비스 계정을 만들고 `Vertex AI User` 역할에 바인딩합니다.

> AI Studio를 사용하고 API 키로 모델에 액세스하는 경우 이 단계를 건너뛸 수 있습니다.

```bash
kubectl create serviceaccount adk-agent-sa
```

```bash
gcloud projects add-iam-policy-binding projects/${GOOGLE_CLOUD_PROJECT} \
    --role=roles/aiplatform.user \
    --member=principal://iam.googleapis.com/projects/${GOOGLE_CLOUD_PROJECT_NUMBER}/locations/global/workloadIdentityPools/${GOOGLE_CLOUD_PROJECT}.svc.id.goog/subject/ns/default/sa/adk-agent-sa \
    --condition=None
```

### Kubernetes 매니페스트 파일 생성

프로젝트 디렉토리에 `deployment.yaml`이라는 Kubernetes 배포 매니페스트 파일을 만듭니다. 이 파일은 GKE에 애플리케이션을 배포하는 방법을 정의합니다.

```yaml title="deployment.yaml"
cat <<  EOF > deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: adk-agent
spec:
  replicas: 1
  selector:
    matchLabels:
      app: adk-agent
  template:
    metadata:
      labels:
        app: adk-agent
    spec:
      serviceAccount: adk-agent-sa
      containers:
      - name: adk-agent
        imagePullPolicy: Always
        image: $GOOGLE_CLOUD_LOCATION-docker.pkg.dev/$GOOGLE_CLOUD_PROJECT/adk-repo/adk-agent:latest
        resources:
          limits:
            memory: "128Mi"
            cpu: "500m"
            ephemeral-storage: "128Mi"
          requests:
            memory: "128Mi"
            cpu: "500m"
            ephemeral-storage: "128Mi"
        ports:
        - containerPort: 8080
        env:
          - name: PORT
            value: "8080"
          - name: GOOGLE_CLOUD_PROJECT
            value: GOOGLE_CLOUD_PROJECT
          - name: GOOGLE_CLOUD_LOCATION
            value: GOOGLE_CLOUD_LOCATION
          - name: GOOGLE_GENAI_USE_VERTEXAI
            value: GOOGLE_GENAI_USE_VERTEXAI
          # AI Studio를 사용하는 경우 GOOGLE_GENAI_USE_VERTEXAI를 false로 설정하고 다음을 설정합니다:
          # - name: GOOGLE_API_KEY
          #   value: GOOGLE_API_KEY
          # 에이전트에 필요한 다른 환경 변수 추가
---
apiVersion: v1
kind: Service
metadata:
  name: adk-agent
spec:       
  type: LoadBalancer
  ports:
    - port: 80
      targetPort: 8080
  selector:
    app: adk-agent
EOF
```

### 애플리케이션 배포

`kubectl` 명령줄 도구를 사용하여 애플리케이션을 배포합니다. 이 명령은 배포 및 서비스 매니페스트 파일을 GKE 클러스터에 적용합니다.

```bash
kubectl apply -f deployment.yaml
```

잠시 후 다음을 사용하여 배포 상태를 확인할 수 있습니다:

```bash
kubectl get pods -l=app=adk-agent
```

이 명령은 배포와 관련된 파드를 나열합니다. `Running` 상태의 파드를 볼 수 있어야 합니다.

파드가 실행되면 다음을 사용하여 서비스 상태를 확인할 수 있습니다:

```bash
kubectl get service adk-agent
```

출력에 `External IP`가 표시되면 서비스가 인터넷에서 접근 가능하다는 의미입니다. 외부 IP가 할당되는 데 몇 분이 걸릴 수 있습니다.

다음을 사용하여 서비스의 외부 IP 주소를 얻을 수 있습니다:

```bash
kubectl get svc adk-agent -o=jsonpath='{.status.loadBalancer.ingress[0].ip}'
```

## 에이전트 테스트

에이전트가 GKE에 배포되면 배포된 UI(활성화된 경우)를 통해 또는 `curl`과 같은 도구를 사용하여 API 엔드포인트와 직접 상호 작용할 수 있습니다. 배포 후 제공된 서비스 URL이 필요합니다.

=== "UI 테스트"

    ### UI 테스트

    UI가 활성화된 상태로 에이전트를 배포한 경우:

    웹 브라우저에서 kubernetes 서비스 URL로 이동하여 에이전트를 테스트할 수 있습니다.

    ADK 개발 UI를 사용하면 에이전트와 상호 작용하고, 세션을 관리하며, 브라우저에서 직접 실행 세부 정보를 볼 수 있습니다.

    에이전트가 의도한 대로 작동하는지 확인하려면 다음을 수행할 수 있습니다:

    1. 드롭다운 메뉴에서 에이전트를 선택합니다.
    2. 메시지를 입력하고 에이전트로부터 예상되는 응답을 받는지 확인합니다.

    예상치 못한 동작이 발생하는 경우 다음을 사용하여 에이전트에 대한 파드 로그를 확인하세요:

    ```bash
    kubectl logs -l app=adk-agent
    ```

=== "API 테스트 (curl)"

    ### API 테스트 (curl)

    `curl`과 같은 도구를 사용하여 에이전트의 API 엔드포인트와 상호 작용할 수 있습니다. 이는 프로그래밍 방식의 상호 작용이나 UI 없이 배포한 경우에 유용합니다.

    #### 애플리케이션 URL 설정

    예제 URL을 배포된 Cloud Run 서비스의 실제 URL로 바꾸세요.

    ```bash
    export APP_URL="KUBERNETES_SERVICE_URL"
    ```

    #### 사용 가능한 앱 목록 보기

    배포된 애플리케이션 이름을 확인합니다.

    ```bash
    curl -X GET $APP_URL/list-apps
    ```

    *(필요한 경우 이 출력을 기반으로 다음 명령어에서 `app_name`을 조정하세요. 기본값은 종종 에이전트 디렉토리 이름입니다, 예: `capital_agent`)*.

    #### 세션 생성 또는 업데이트

    특정 사용자와 세션에 대한 상태를 초기화하거나 업데이트합니다. 다른 경우 `capital_agent`를 실제 앱 이름으로 바꾸세요. `user_123` 및 `session_abc` 값은 예제 식별자이며, 원하는 사용자 및 세션 ID로 바꿀 수 있습니다.

    ```bash
    curl -X POST \
        $APP_URL/apps/capital_agent/users/user_123/sessions/session_abc \
        -H "Content-Type: application/json" \
        -d '{"state": {"preferred_language": "English", "visit_count": 5}}'
    ```

    #### 에이전트 실행

    에이전트에 프롬프트를 보냅니다. `capital_agent`를 앱 이름으로 바꾸고 필요에 따라 사용자/세션 ID와 프롬프트를 조정하세요.

    ```bash
    curl -X POST $APP_URL/run_sse \
        -H "Content-Type: application/json" \
        -d '{
        "app_name": "capital_agent",
        "user_id": "user_123",
        "session_id": "session_abc",
        "new_message": {
            "role": "user",
            "parts": [{
            "text": "캐나다의 수도는 어디인가요?"
            }]
        },
        "streaming": false
        }'
    ```

    * 서버 전송 이벤트(SSE)를 받으려면 `"streaming": true`로 설정하세요.
    * 응답에는 최종 답변을 포함한 에이전트의 실행 이벤트가 포함됩니다.

## 문제 해결

GKE에 에이전트를 배포할 때 발생할 수 있는 몇 가지 일반적인 문제입니다:

### `Gemini 2.0 Flash`에 대한 403 권한 거부

이는 일반적으로 Kubernetes 서비스 계정이 Vertex AI API에 액세스하는 데 필요한 권한이 없음을 의미합니다. [Vertex AI용 Kubernetes 서비스 계정 구성](#configure-kubernetes-service-account-for-vertex-ai) 섹션에 설명된 대로 서비스 계정을 만들고 `Vertex AI User` 역할에 바인딩했는지 확인하세요. AI Studio를 사용하는 경우 배포 매니페스트에서 `GOOGLE_API_KEY` 환경 변수를 설정하고 유효한지 확인하세요.

### 읽기 전용 데이터베이스에 쓰기 시도

UI에 세션 ID가 생성되지 않고 에이전트가 어떤 메시지에도 응답하지 않는 것을 볼 수 있습니다. 이는 일반적으로 SQLite 데이터베이스가 읽기 전용이기 때문에 발생합니다. 로컬에서 에이전트를 실행한 다음 컨테이너 이미지를 만들 때 SQLite 데이터베이스를 컨테이너에 복사하면 이런 일이 발생할 수 있습니다. 그러면 데이터베이스는 컨테이너에서 읽기 전용이 됩니다.

```bash
sqlalchemy.exc.OperationalError: (sqlite3.OperationalError) attempt to write a readonly database
[SQL: UPDATE app_states SET state=?, update_time=CURRENT_TIMESTAMP WHERE app_states.app_name = ?]
```

이 문제를 해결하려면 다음 중 하나를 수행할 수 있습니다:

컨테이너 이미지를 빌드하기 전에 로컬 머신에서 SQLite 데이터베이스 파일을 삭제하세요. 이렇게 하면 컨테이너가 시작될 때 새 SQLite 데이터베이스가 생성됩니다.

```bash
rm -f sessions.db
```

또는 (권장) 프로젝트 디렉토리에 `.dockerignore` 파일을 추가하여 SQLite 데이터베이스가 컨테이너 이미지에 복사되지 않도록 제외할 수 있습니다.

```txt title=".dockerignore"
sessions.db
```

컨테이너 이미지를 빌드하고 애플리케이션을 다시 배포하세요.

## 정리

GKE 클러스터 및 모든 관련 리소스를 삭제하려면 다음을 실행하세요:

```bash
gcloud container clusters delete adk-cluster \
    --location=$GOOGLE_CLOUD_LOCATION \
    --project=$GOOGLE_CLOUD_PROJECT
```

Artifact Registry 저장소를 삭제하려면 다음을 실행하세요:

```bash
gcloud artifacts repositories delete adk-repo \
    --location=$GOOGLE_CLOUD_LOCATION \
    --project=$GOOGLE_CLOUD_PROJECT
```

더 이상 필요하지 않으면 프로젝트를 삭제할 수도 있습니다. 이렇게 하면 GKE 클러스터, Artifact Registry 저장소 및 생성한 다른 모든 리소스를 포함하여 프로젝트와 관련된 모든 리소스가 삭제됩니다.

```bash
gcloud projects delete $GOOGLE_CLOUD_PROJECT
```