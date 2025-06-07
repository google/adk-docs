# ADK 설치하기

=== "Python"

    ## 가상 환경 생성 및 활성화
    
    [venv](https://docs.python.org/3/library/venv.html)를 사용하여 가상 Python 환경을 만드는 것을 권장합니다:
    
    ```shell
    python -m venv .venv
    ```
    
    이제 운영체제와 환경에 맞는 명령어를 사용하여 가상 환경을 활성화할 수 있습니다:
    
    ```
    # Mac / Linux
    source .venv/bin/activate
    
    # Windows CMD:
    .venv\Scripts\activate.bat
    
    # Windows PowerShell:
    .venv\Scripts\Activate.ps1
    ```

    ### ADK 설치
    
    ```bash
    pip install google-adk
    ```
    
    (선택 사항) 설치 확인:
    
    ```bash
    pip show google-adk
    ```

=== "Java"

    Maven 또는 Gradle을 사용하여 `google-adk` 및 `google-adk-dev` 패키지를 추가할 수 있습니다.

    `google-adk`는 핵심 Java ADK 라이브러리입니다. Java ADK는 또한 에이전트를 원활하게 실행할 수 있는 플러그형 예제 SpringBoot 서버와 함께 제공됩니다. 이 선택적 패키지는 `google-adk-dev`의 일부로 제공됩니다.
    
    Maven을 사용하는 경우, `pom.xml`에 다음을 추가하세요:

    ```xml title="pom.xml"
    <dependencies>
      <!-- ADK 코어 의존성 -->
      <dependency>
        <groupId>com.google.adk</groupId>
        <artifactId>google-adk</artifactId>
        <version>0.1.0</version>
      </dependency>
      
      <!-- 에이전트 디버깅을 위한 ADK 개발 웹 UI (선택 사항) -->
      <dependency>
        <groupId>com.google.adk</groupId>
        <artifactId>google-adk-dev</artifactId>
        <version>0.1.0</version>
      </dependency>
    </dependencies>
    ```

    참고용 [전체 pom.xml](https://github.com/google/adk-docs/tree/main/examples/java/cloud-run/pom.xml) 파일입니다.

    Gradle을 사용하는 경우, build.gradle에 의존성을 추가하세요:

    ```title="build.gradle"
    dependencies {
        implementation 'com.google.adk:google-adk:0.1.0'
        implementation 'com.google.adk:google-adk-dev:0.1.0'
    }
    ```


## 다음 단계

*   [**빠른 시작**](quickstart.md)으로 첫 번째 에이전트를 만들어보세요