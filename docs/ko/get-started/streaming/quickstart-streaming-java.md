# 빠른 시작 (스트리밍 / Java) {#adk-streaming-quickstart-java}

이 빠른 시작 가이드는 기본 에이전트를 생성하고 Java용 ADK 스트리밍을 활용하여 저지연, 양방향 음성 상호작용을 구현하는 과정을 안내합니다.

Java 및 Maven 환경 설정, 프로젝트 구조화, 필요한 의존성 정의부터 시작합니다. 그 다음, 간단한 `ScienceTeacherAgent`를 만들고, 개발 UI를 사용하여 텍스트 기반 스트리밍 기능을 테스트한 후, 실시간 오디오 통신을 활성화하여 에이전트를 대화형 음성 기반 애플리케이션으로 전환하는 단계로 진행합니다.

## **첫 번째 에이전트 만들기** {#create-your-first-agent}

### **전제 조건**

*   이 시작 가이드에서는 Java로 프로그래밍합니다. 컴퓨터에 **Java**가 설치되어 있는지 확인하세요. Java 17 이상을 사용하는 것이 이상적입니다 (**java \-version**을 입력하여 확인할 수 있습니다).

*   또한 Java용 빌드 도구인 **Maven**을 사용합니다. 계속 진행하기 전에 컴퓨터에 [Maven이 설치되어 있는지](https://maven.apache.org/install.html) 확인하세요 (Cloud Top이나 Cloud Shell의 경우 이미 설치되어 있지만, 개인 노트북에는 아닐 수 있습니다).

### **프로젝트 구조 준비**

ADK Java를 시작하기 위해, 다음 디렉토리 구조를 가진 Maven 프로젝트를 생성해 보겠습니다.

```
adk-agents/
├── pom.xml
└── src/
    └── main/
        └── java/
            └── agents/
                └── ScienceTeacherAgent.java
```

[설치](../../get-started/installation.md) 페이지의 지침에 따라 ADK 패키지를 사용하기 위한 `pom.xml`을 추가하세요.

!!! Note
    프로젝트의 루트 디렉토리 이름은 `adk-agents` 대신 원하는 이름을 자유롭게 사용해도 좋습니다.

### **컴파일 실행하기**

컴파일을 실행하여 Maven이 이 빌드에 만족하는지 확인해 보겠습니다 (**mvn compile** 명령어):

```shell
$ mvn compile
[INFO] Scanning for projects...
[INFO]
[INFO] --------------------< adk-agents:adk-agents >--------------------
[INFO] Building adk-agents 1.0-SNAPSHOT
[INFO]   from pom.xml
[INFO] --------------------------------[ jar ]---------------------------------
[INFO]
[INFO] --- resources:3.3.1:resources (default-resources) @ adk-demo ---
[INFO] skip non existing resourceDirectory /home/user/adk-demo/src/main/resources
[INFO]
[INFO] --- compiler:3.13.0:compile (default-compile) @ adk-demo ---
[INFO] Nothing to compile - all classes are up to date.
[INFO] ------------------------------------------------------------------------
[INFO] BUILD SUCCESS
[INFO] ------------------------------------------------------------------------
[INFO] Total time:  1.347 s
[INFO] Finished at: 2025-05-06T15:38:08Z
[INFO] ------------------------------------------------------------------------
```

프로젝트가 컴파일을 위해 올바르게 설정된 것 같습니다!

### **에이전트 생성하기**

`src/main/java/agents/` 디렉토리 아래에 다음 내용으로 **ScienceTeacherAgent.java** 파일을 생성하세요:

```java
package samples.liveaudio;

import com.google.adk.agents.BaseAgent;
import com.google.adk.agents.LlmAgent;

/** 과학 선생님 에이전트. */
public class ScienceTeacherAgent {

  // Dev UI가 에이전트를 동적으로 로드하기 위해 필요한 필드
  // (에이전트는 선언 시점에 초기화되어야 합니다)
  public static BaseAgent ROOT_AGENT = initAgent();

  public static BaseAgent initAgent() {
    return LlmAgent.builder()
        .name("science-app")
        .description("과학 선생님 에이전트")
        .model("gemini-2.0-flash-exp")
        .instruction("""
            당신은 어린이와 청소년에게 과학 개념을 설명해주는
            친절한 과학 선생님입니다.
            """)
        .build();
  }
}
```

!!!note "문제 해결"

    `gemini-2.0-flash-exp` 모델은 향후 지원 중단될 예정입니다. 사용 중 문제가 발생하면 대신 `gemini-2.0-flash-live-001`을 사용해 보세요.

나중에 이 에이전트를 실행하기 위해 `Dev UI`를 사용할 것입니다. 도구가 에이전트를 자동으로 인식하려면, 해당 Java 클래스는 다음 두 가지 규칙을 준수해야 합니다.

*   에이전트는 **BaseAgent** 타입의 **public static** 전역 변수 **ROOT\_AGENT**에 저장되고 선언 시점에 초기화되어야 합니다.
*   에이전트 정의는 동적 컴파일링 클래스로더에 의해 클래스 초기화 중에 로드될 수 있도록 **static** 메서드여야 합니다.

## **Dev UI로 에이전트 실행하기** {#run-agent-with-adk-web-server}

`Dev UI`는 개발 목적으로 에이전트를 위한 자체 UI 애플리케이션을 빌드하지 않고도 빠르게 에이전트를 실행하고 테스트할 수 있는 웹 서버입니다.

### **환경 변수 정의**

서버를 실행하려면 두 개의 환경 변수를 내보내야 합니다:

*   [AI Studio에서 얻을 수 있는](https://ai.google.dev/gemini-api/docs/api-key) Gemini 키,
*   이번에는 Vertex AI를 사용하지 않음을 지정하는 변수.

```shell
export GOOGLE_GENAI_USE_VERTEXAI=FALSE
export GOOGLE_API_KEY=YOUR_API_KEY
```

### **Dev UI 실행**

터미널에서 다음 명령을 실행하여 Dev UI를 시작합니다.

```console title="터미널"
mvn exec:java \
    -Dexec.mainClass="com.google.adk.web.AdkWebServer" \
    -Dexec.args="--adk.agents.source-dir=src/main/java" \
    -Dexec.classpathScope="compile"
```

**1단계:** 제공된 URL(보통 `http://localhost:8080` 또는 `http://127.0.0.1:8080`)을 브라우저에서 직접 엽니다.

**2단계.** UI의 왼쪽 상단 모서리에서 드롭다운 메뉴로 에이전트를 선택할 수 있습니다. "science-app"을 선택하세요.

!!!note "문제 해결"

    드롭다운 메뉴에 "science-app"이 보이지 않으면, Java 소스 코드가 위치한 곳(보통 `src/main/java`)에서 `mvn` 명령을 실행하고 있는지 확인하세요.

## 텍스트로 Dev UI 사용해보기

선호하는 브라우저로 [http://127.0.0.1:8080/](http://127.0.0.1:8080/)으로 이동하세요.

다음과 같은 인터페이스가 표시됩니다:

![Dev UI](../../assets/quickstart-streaming-devui.png)

오른쪽 상단의 `Token Streaming` 스위치를 클릭하고, 과학 선생님에게 `전자가 뭐야?`와 같은 질문을 해보세요. 그러면 UI에서 스트리밍으로 출력되는 텍스트를 볼 수 있습니다.

보시다시피, 텍스트 스트리밍 기능을 위해 에이전트 자체에 특정 코드를 작성할 필요가 없습니다. 이는 기본적으로 ADK 에이전트 기능으로 제공됩니다.

### 음성 및 비디오로 시도해보기

음성으로 시도하려면 웹 브라우저를 새로고침하고, 마이크 버튼을 클릭하여 음성 입력을 활성화한 후, 같은 질문을 음성으로 해보세요. 실시간으로 음성 답변을 들을 수 있습니다.

비디오로 시도하려면 웹 브라우저를 새로고침하고, 카메라 버튼을 클릭하여 비디오 입력을 활성화한 후, "뭐가 보여?"와 같은 질문을 해보세요. 에이전트가 비디오 입력에서 보이는 것을 답변할 것입니다.

### 도구 중지하기

콘솔에서 `Ctrl-C`를 눌러 도구를 중지하세요.

## **사용자 지정 라이브 오디오 앱으로 에이전트 실행하기** {#run-agent-with-live-audio}

이제, 에이전트와 사용자 지정 라이브 오디오 애플리케이션으로 오디오 스트리밍을 시도해 보겠습니다.

### **라이브 오디오용 Maven pom.xml 빌드 파일**

기존 pom.xml을 다음 내용으로 교체하세요.

```xml
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
  xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
  xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 http://maven.apache.org/xsd/maven-4.0.0.xsd">
  <modelVersion>4.0.0</modelVersion>

  <groupId>com.google.adk.samples</groupId>
  <artifactId>google-adk-sample-live-audio</artifactId>
  <version>0.1.0</version>
  <name>Google ADK - Sample - Live Audio</name>
  <description>
    samples.liveaudio.LiveAudioRun을 통해 실행 가능한, ADK를 사용한 라이브 오디오 대화를 시연하는 샘플 애플리케이션입니다.
  </description>
  <packaging>jar</packaging>

  <properties>
    <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>
    <java.version>17</java.version>
    <auto-value.version>1.11.0</auto-value.version>
    <!-- exec-maven-plugin용 메인 클래스 -->
    <exec.mainClass>samples.liveaudio.LiveAudioRun</exec.mainClass>
    <google-adk.version>0.1.0</google-adk.version>
  </properties>

  <dependencyManagement>
    <dependencies>
      <dependency>
        <groupId>com.google.cloud</groupId>
        <artifactId>libraries-bom</artifactId>
        <version>26.53.0</version>
        <type>pom</type>
        <scope>import</scope>
      </dependency>
    </dependencies>
  </dependencyManagement>

  <dependencies>
    <dependency>
      <groupId>com.google.adk</groupId>
      <artifactId>google-adk</artifactId>
      <version>${google-adk.version}</version>
    </dependency>
    <dependency>
      <groupId>commons-logging</groupId>
      <artifactId>commons-logging</artifactId>
      <version>1.2</version> <!-- 또는 부모 POM에 정의된 속성 사용 -->
    </dependency>
  </dependencies>

  <build>
    <plugins>
      <plugin>
        <groupId>org.apache.maven.plugins</groupId>
        <artifactId>maven-compiler-plugin</artifactId>
        <version>3.13.0</version>
        <configuration>
          <source>${java.version}</source>
          <target>${java.version}</target>
          <parameters>true</parameters>
          <annotationProcessorPaths>
            <path>
              <groupId>com.google.auto.value</groupId>
              <artifactId>auto-value</artifactId>
              <version>${auto-value.version}</version>
            </path>
          </annotationProcessorPaths>
        </configuration>
      </plugin>
      <plugin>
        <groupId>org.codehaus.mojo</groupId>
        <artifactId>build-helper-maven-plugin</artifactId>
        <version>3.6.0</version>
        <executions>
          <execution>
            <id>add-source</id>
            <phase>generate-sources</phase>
            <goals>
              <goal>add-source</goal>
            </goals>
            <configuration>
              <sources>
                <source>.</source>
              </sources>
            </configuration>
          </execution>
        </executions>
      </plugin>
      <plugin>
        <groupId>org.codehaus.mojo</groupId>
        <artifactId>exec-maven-plugin</artifactId>
        <version>3.2.0</version>
        <configuration>
          <mainClass>${exec.mainClass}</mainClass>
          <classpathScope>runtime</classpathScope>
        </configuration>
      </plugin>
    </plugins>
  </build>
</project>
```

### **라이브 오디오 실행 도구 생성하기**

`src/main/java/` 디렉토리 아래에 다음 내용으로 **LiveAudioRun.java** 파일을 생성하세요. 이 도구는 라이브 오디오 입출력으로 에이전트를 실행합니다.

```java

package samples.liveaudio;

import com.google.adk.agents.LiveRequestQueue;
import com.google.adk.agents.RunConfig;
import com.google.adk.events.Event;
import com.google.adk.runner.Runner;
import com.google.adk.sessions.InMemorySessionService;
import com.google.common.collect.ImmutableList;
import com.google.genai.types.Blob;
import com.google.genai.types.Modality;
import com.google.genai.types.PrebuiltVoiceConfig;
import com.google.genai.types.Content;
import com.google.genai.types.Part;
import com.google.genai.types.SpeechConfig;
import com.google.genai.types.VoiceConfig;
import io.reactivex.rxjava3.core.Flowable;
import java.io.ByteArrayOutputStream;
import java.io.InputStream;
import java.net.URL;
import javax.sound.sampled.AudioFormat;
import javax.sound.sampled.AudioInputStream;
import javax.sound.sampled.AudioSystem;
import javax.sound.sampled.DataLine;
import javax.sound.sampled.LineUnavailableException;
import javax.sound.sampled.Mixer;
import javax.sound.sampled.SourceDataLine;
import javax.sound.sampled.TargetDataLine;
import java.util.UUID;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.ConcurrentMap;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicBoolean;
import agents.ScienceTeacherAgent;

/** 음성 대화를 위해 {@link LiveAudioAgent} 실행을 시연하는 메인 클래스입니다. */
public final class LiveAudioRun {
  private final String userId;
  private final String sessionId;
  private final Runner runner;

  private static final javax.sound.sampled.AudioFormat MIC_AUDIO_FORMAT =
      new javax.sound.sampled.AudioFormat(16000.0f, 16, 1, true, false);

  private static final javax.sound.sampled.AudioFormat SPEAKER_AUDIO_FORMAT =
      new javax.sound.sampled.AudioFormat(24000.0f, 16, 1, true, false);

  private static final int BUFFER_SIZE = 4096;

  public LiveAudioRun() {
    this.userId = "test_user";
    String appName = "LiveAudioApp";
    this.sessionId = UUID.randomUUID().toString();

    InMemorySessionService sessionService = new InMemorySessionService();
    this.runner = new Runner(ScienceTeacherAgent.ROOT_AGENT, appName, null, sessionService);

    ConcurrentMap<String, Object> initialState = new ConcurrentHashMap<>();
    var unused =
        sessionService.createSession(appName, userId, initialState, sessionId).blockingGet();
  }

  private void runConversation() throws Exception {
    System.out.println("마이크 입력 및 스피커 출력 초기화 중...");

    RunConfig runConfig =
        RunConfig.builder()
            .setStreamingMode(RunConfig.StreamingMode.BIDI)
            .setResponseModalities(ImmutableList.of(new Modality("AUDIO")))
            .setSpeechConfig(
                SpeechConfig.builder()
                    .voiceConfig(
                        VoiceConfig.builder()
                            .prebuiltVoiceConfig(
                                PrebuiltVoiceConfig.builder().voiceName("Aoede").build())
                            .build())
                    .languageCode("en-US")
                    .build())
            .build();

    LiveRequestQueue liveRequestQueue = new LiveRequestQueue();

    Flowable<Event> eventStream =
        this.runner.runLive(
            runner.sessionService().createSession(userId, sessionId).blockingGet(),
            liveRequestQueue,
            runConfig);

    AtomicBoolean isRunning = new AtomicBoolean(true);
    AtomicBoolean conversationEnded = new AtomicBoolean(false);
    ExecutorService executorService = Executors.newFixedThreadPool(2);

    // 마이크 입력을 캡처하는 태스크
    Future<?> microphoneTask =
        executorService.submit(() -> captureAndSendMicrophoneAudio(liveRequestQueue, isRunning));

    // 에이전트 응답을 처리하고 오디오를 재생하는 태스크
    Future<?> outputTask =
        executorService.submit(
            () -> {
              try {
                processAudioOutput(eventStream, isRunning, conversationEnded);
              } catch (Exception e) {
                System.err.println("오디오 출력 처리 오류: " + e.getMessage());
                e.printStackTrace();
                isRunning.set(false);
              }
            });

    // 사용자가 Enter를 눌러 대화를 중지할 때까지 대기
    System.out.println("대화가 시작되었습니다. 중지하려면 Enter를 누르세요...");
    System.in.read();

    System.out.println("대화 종료 중...");
    isRunning.set(false);

    try {
      // 진행 중인 처리가 완료될 시간을 줍니다.
      microphoneTask.get(2, TimeUnit.SECONDS);
      outputTask.get(2, TimeUnit.SECONDS);
    } catch (Exception e) {
      System.out.println("태스크 중지 중...");
    }

    liveRequestQueue.close();
    executorService.shutdownNow();
    System.out.println("대화가 종료되었습니다.");
  }

  private void captureAndSendMicrophoneAudio(
      LiveRequestQueue liveRequestQueue, AtomicBoolean isRunning) {
    TargetDataLine micLine = null;
    try {
      DataLine.Info info = new DataLine.Info(TargetDataLine.class, MIC_AUDIO_FORMAT);
      if (!AudioSystem.isLineSupported(info)) {
        System.err.println("마이크 라인이 지원되지 않습니다!");
        return;
      }

      micLine = (TargetDataLine) AudioSystem.getLine(info);
      micLine.open(MIC_AUDIO_FORMAT);
      micLine.start();

      System.out.println("마이크가 초기화되었습니다. 말씀하세요...");

      byte[] buffer = new byte[BUFFER_SIZE];
      int bytesRead;

      while (isRunning.get()) {
        bytesRead = micLine.read(buffer, 0, buffer.length);

        if (bytesRead > 0) {
          byte[] audioChunk = new byte[bytesRead];
          System.arraycopy(buffer, 0, audioChunk, 0, bytesRead);

          Blob audioBlob = Blob.builder().data(audioChunk).mimeType("audio/pcm").build();

          liveRequestQueue.realtime(audioBlob);
        }
      }
    } catch (LineUnavailableException e) {
      System.err.println("마이크 접근 오류: " + e.getMessage());
      e.printStackTrace();
    } finally {
      if (micLine != null) {
        micLine.stop();
        micLine.close();
      }
    }
  }

  private void processAudioOutput(
      Flowable<Event> eventStream, AtomicBoolean isRunning, AtomicBoolean conversationEnded) {
    SourceDataLine speakerLine = null;
    try {
      DataLine.Info info = new DataLine.Info(SourceDataLine.class, SPEAKER_AUDIO_FORMAT);
      if (!AudioSystem.isLineSupported(info)) {
        System.err.println("스피커 라인이 지원되지 않습니다!");
        return;
      }

      final SourceDataLine finalSpeakerLine = (SourceDataLine) AudioSystem.getLine(info);
      finalSpeakerLine.open(SPEAKER_AUDIO_FORMAT);
      finalSpeakerLine.start();

      System.out.println("스피커가 초기화되었습니다.");

      for (Event event : eventStream.blockingIterable()) {
        if (!isRunning.get()) {
          break;
        }
        event.content().ifPresent(content -> content.parts().ifPresent(parts -> parts.forEach(part -> playAudioData(part, finalSpeakerLine))));
      }

      speakerLine = finalSpeakerLine; // finally 블록에서 정리하기 위해 외부 변수에 할당
    } catch (LineUnavailableException e) {
      System.err.println("스피커 접근 오류: " + e.getMessage());
      e.printStackTrace();
    } finally {
      if (speakerLine != null) {
        speakerLine.drain();
        speakerLine.stop();
        speakerLine.close();
      }
      conversationEnded.set(true);
    }
  }

  private void playAudioData(Part part, SourceDataLine speakerLine) {
    part.inlineData()
        .ifPresent(
            inlineBlob ->
                inlineBlob
                    .data()
                    .ifPresent(
                        audioBytes -> {
                          if (audioBytes.length > 0) {
                            System.out.printf(
                                "오디오 재생 중 (%s): %d 바이트%n",
                                inlineBlob.mimeType(),
                                audioBytes.length);
                            speakerLine.write(audioBytes, 0, audioBytes.length);
                          }
                        }));
  }

  private void processEvent(Event event, java.util.concurrent.atomic.AtomicBoolean audioReceived) {
    event
        .content()
        .ifPresent(
            content ->
                content
                    .parts()
                    .ifPresent(parts -> parts.forEach(part -> logReceivedAudioData(part, audioReceived))));
  }

  private void logReceivedAudioData(Part part, AtomicBoolean audioReceived) {
    part.inlineData()
        .ifPresent(
            inlineBlob ->
                inlineBlob
                    .data()
                    .ifPresent(
                        audioBytes -> {
                          if (audioBytes.length > 0) {
                            System.out.printf(
                                "    오디오 (%s): %d 바이트 수신.%n",
                                inlineBlob.mimeType(),
                                audioBytes.length);
                            audioReceived.set(true);
                          } else {
                            System.out.printf(
                                "    오디오 (%s): 빈 오디오 데이터 수신.%n",
                                inlineBlob.mimeType());
                          }
                        }));
  }

  public static void main(String[] args) throws Exception {
    LiveAudioRun liveAudioRun = new LiveAudioRun();
    liveAudioRun.runConversation();
    System.out.println("라이브 오디오 실행 종료.");
  }
}
```

### **라이브 오디오 실행 도구 실행하기**

라이브 오디오 실행 도구를 실행하려면, `adk-agents` 디렉토리에서 다음 명령을 사용하세요:

```
mvn compile exec:java
```

그러면 다음 메시지가 표시됩니다:

```
$ mvn compile exec:java
...
마이크 입력 및 스피커 출력 초기화 중...
대화가 시작되었습니다. 중지하려면 Enter를 누르세요...
스피커가 초기화되었습니다.
마이크가 초기화되었습니다. 말씀하세요...
```

이 메시지가 표시되면 도구가 음성 입력을 받을 준비가 된 것입니다. `전자가 뭐야?`와 같은 질문으로 에이전트와 대화해보세요.

!!! Caution
    에이전트가 혼자 계속 말하고 멈추지 않는 현상이 관찰되면, 이어폰을 사용하여 에코를 억제해 보세요.

## **요약** {#summary}

ADK용 스트리밍은 개발자가 저지연, 양방향 음성 및 비디오 통신이 가능한 에이전트를 생성하여 대화형 경험을 향상시킬 수 있도록 합니다. 이 글은 텍스트 스트리밍이 추가적인 특정 코드 없이 ADK 에이전트의 내장 기능임을 보여주며, 동시에 에이전트와의 실시간 음성 상호작용을 위한 라이브 오디오 대화를 구현하는 방법을 보여줍니다. 이를 통해 사용자는 에이전트와 원활하게 말하고 들을 수 있으므로 더 자연스럽고 동적인 커뮤니케이션이 가능해집니다.