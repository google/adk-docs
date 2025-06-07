---
hide:
  - toc
---

!!! tip "Google I/O'25 - ADK 업데이트"

    중요한 소식입니다!

    - 에이전트 기능을 자바 생태계로 확장하는 **[Java ADK v0.1.0](https://github.com/google/adk-java/)**을 소개합니다.

    - **[Python ADK](https://github.com/google/adk-python/)**가 공식 v1.0.0이 되어 프로덕션용 에이전트를 위한 안정성을 제공합니다.

<div style="text-align: center;">
  <div class="centered-logo-text-group">
    <img src="assets/agent-development-kit.png" alt="Agent Development Kit 로고" width="100">
    <h1>Agent Development Kit (에이전트 개발 키트)</h1>
  </div>
</div>

## Agent Development Kit란 무엇인가요?

Agent Development Kit (ADK)는 **AI 에이전트를 개발하고 배포**하기 위한 유연하고 모듈화된 프레임워크입니다. Gemini 및 Google 생태계에 최적화되어 있지만, ADK는 **모델에 구애받지 않고(model-agnostic)**, **배포 환경에 구애받지 않으며(deployment-agnostic)**, **다른 프레임워크와의 호환성**을 위해 만들어졌습니다. ADK는 개발자들이 에이전트 개발을 소프트웨어 개발처럼 느끼게 하여, 간단한 작업부터 복잡한 워크플로우에 이르는 에이전트 아키텍처를 더 쉽게 만들고, 배포하고, 오케스트레이션할 수 있도록 설계되었습니다.

<div id="centered-install-tabs" class="install-command-container" markdown="1">

<p class="get-started-text" style="text-align: center;">시작하기:</p>

=== "Python"
    <br>
    <p style="text-align: center;">
    <code>pip install google-adk</code>
    </p>

=== "Java"

    ```xml title="pom.xml"
    <dependency>
        <groupId>com.google.adk</groupId>
        <artifactId>google-adk</artifactId>
        <version>0.1.0</version>
    </dependency>
    ```

    ```gradle title="build.gradle"
    dependencies {
        implementation 'com.google.adk:google-adk:0.1.0'
    }
    ```
</div>


<p style="text-align:center;">
  <a href="get-started/quickstart/" class="md-button" style="margin:3px">빠른 시작</a>
  <a href="tutorials/" class="md-button" style="margin:3px">튜토리얼</a>
  <a href="http://github.com/google/adk-samples" class="md-button" target="_blank" style="margin:3px">샘플 에이전트</a>
  <a href="api-reference/" class="md-button" style="margin:3px">API 레퍼런스</a>
  <a href="contributing-guide/" class="md-button" style="margin:3px">기여하기 ❤️</a>
</p>

---

## 더 알아보기

[:fontawesome-brands-youtube:{.youtube-red-icon} "Agent Development Kit 소개" 영상 보기!](https://www.youtube.com/watch?v=zgrOwow_uTQ target="_blank" rel="noopener noreferrer")

<div class="grid cards" markdown>

-   :material-transit-connection-variant: **유연한 오케스트레이션**

    ---

    예측 가능한 파이프라인을 위해 워크플로우 에이전트(`Sequential`, `Parallel`, `Loop`)를 사용하여 워크플로우를 정의하거나, 적응형 동작을 위해 LLM 기반의 동적 라우팅(`LlmAgent` 이전)을 활용하세요.

    [**에이전트에 대해 알아보기**](agents/index.md)

-   :material-graph: **멀티 에이전트 아키텍처**

    ---

    계층 구조 내에서 여러 전문화된 에이전트를 조합하여 모듈식의 확장 가능한 애플리케이션을 구축하세요. 복잡한 조정 및 위임이 가능해집니다.

    [**멀티 에이전트 시스템 탐색하기**](agents/multi-agents.md)

-   :material-toolbox-outline: **풍부한 도구 생태계**

    ---

    미리 빌드된 도구(검색, 코드 실행)를 사용하거나, 커스텀 함수를 생성하거나, 서드파티 라이브러리(LangChain, CrewAI)를 통합하거나, 심지어 다른 에이전트를 도구로 사용하여 에이전트에 다양한 기능을 갖추게 하세요.

    [**도구 찾아보기**](tools/index.md)

-   :material-rocket-launch-outline: **배포 준비 완료**

    ---

    에이전트를 컨테이너화하여 어디에나 배포하세요 – 로컬에서 실행하거나, Vertex AI Agent Engine으로 확장하거나, Cloud Run 또는 Docker를 사용하여 커스텀 인프라에 통합할 수 있습니다.

    [**에이전트 배포하기**](deploy/index.md)

-   :material-clipboard-check-outline: **내장된 평가 기능**

    ---

    미리 정의된 테스트 케이스에 대해 최종 응답의 품질과 단계별 실행 궤적을 모두 평가하여 에이전트의 성능을 체계적으로 평가하세요.

    [**에이전트 평가하기**](evaluate/index.md)

-   :material-console-line: **안전하고 보안이 유지되는 에이전트 구축**

    ---

    보안 및 안전 패턴과 모범 사례를 에이전트 설계에 구현하여 강력하고 신뢰할 수 있는 에이전트를 구축하는 방법을 배우세요.

    [**안전 및 보안**](safety/index.md)

</div>