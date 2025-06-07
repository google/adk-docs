# ランタイム設定

`RunConfig`は、ADKにおけるエージェントのランタイムの振る舞いとオプションを定義します。音声とストリーミングの設定、関数呼び出し、アーティファクトの保存、LLM呼び出しの制限を制御します。

エージェントの実行を構成する際に、`RunConfig`を渡すことで、エージェントがモデルとどのように対話し、音声を処理し、応答をストリーミングするかをカスタマイズできます。デフォルトでは、ストリーミングは有効になっておらず、入力はアーティファクトとして保持されません。これらのデフォルトを上書きするために`RunConfig`を使用します。

## クラス定義

`RunConfig`クラスは、エージェントのランタイムの振る舞いのための設定パラメータを保持します。

- Python ADKはこの検証にPydanticを使用します。

- Java ADKは通常、イミュータブルなデータクラスを使用します。

=== "Python"

    ```python
    class RunConfig(BaseModel):
        """エージェントのランタイムの振る舞いのための設定。"""
    
        model_config = ConfigDict(
            extra='forbid',
        )
    
        speech_config: Optional[types.SpeechConfig] = None
        response_modalities: Optional[list[str]] = None
        save_input_blobs_as_artifacts: bool = False
        support_cfc: bool = False
        streaming_mode: StreamingMode = StreamingMode.NONE
        output_audio_transcription: Optional[types.AudioTranscriptionConfig] = None
        max_llm_calls: int = 500
    ```

=== "Java"

    ```java
    public abstract class RunConfig {
      
      public enum StreamingMode {
        NONE,
        SSE,
        BIDI
      }
      
      public abstract @Nullable SpeechConfig speechConfig();
    
      public abstract ImmutableList<Modality> responseModalities();
    
      public abstract boolean saveInputBlobsAsArtifacts();
      
      public abstract @Nullable AudioTranscriptionConfig outputAudioTranscription();
    
      public abstract int maxLlmCalls();
      
      // ...
    }
    ```

## ランタイムパラメータ

| パラメータ                       | Python 型                                    | Java 型                                               | デフォルト (Py / Java)            | 説明                                                                                                                 |
| :------------------------------- | :------------------------------------------- | :---------------------------------------------------- | :-------------------------------- | :------------------------------------------------------------------------------------------------------------------- |
| `speech_config`                  | `Optional[types.SpeechConfig]`               | `SpeechConfig` (`@Nullable`経由でnullable)            | `None` / `null`                   | `SpeechConfig`型を使用して音声合成（声、言語）を設定します。                                                       |
| `response_modalities`            | `Optional[list[str]]`                        | `ImmutableList<Modality>`                             | `None` / 空の `ImmutableList`     | 望ましい出力モダリティのリスト（例：Python: `["TEXT", "AUDIO"]`; Java: 構造化された`Modality`オブジェクトを使用）。 |
| `save_input_blobs_as_artifacts`  | `bool`                                       | `boolean`                                             | `False` / `false`                 | `true`の場合、入力BLOB（例：アップロードされたファイル）をデバッグ/監査用に実行アーティファクトとして保存します。   |
| `streaming_mode`                 | `StreamingMode`                              | *現在サポートされていません*                            | `StreamingMode.NONE` / N/A        | ストリーミングの振る舞いを設定します：`NONE`（デフォルト）、`SSE`（サーバー送信イベント）、または`BIDI`（双方向）。     |
| `output_audio_transcription`     | `Optional[types.AudioTranscriptionConfig]`   | `AudioTranscriptionConfig` (`@Nullable`経由でnullable) | `None` / `null`                   | `AudioTranscriptionConfig`型を使用して、生成された音声出力の文字起こしを設定します。                                 |
| `max_llm_calls`                  | `int`                                        | `int`                                                 | `500` / `500`                     | 実行ごとの合計LLM呼び出しを制限します。`0`または負の値は無制限（警告あり）を意味し、`sys.maxsize`は`ValueError`を発生させます。 |
| `support_cfc`                    | `bool`                                       | *現在サポートされていません*                            | `False` / N/A                     | **Python:** 合成的関数呼び出し（CFC）を有効にします。`streaming_mode=SSE`が必要で、LIVE APIを使用します。**実験的機能。** |

### `speech_config`

!!! Note
    `SpeechConfig`のインターフェースや定義は、言語に関わらず同じです。

音声機能を持つライブエージェントのための音声設定です。`SpeechConfig`クラスは次の構造を持っています：

```python
class SpeechConfig(_common.BaseModel):
    """音声生成の設定。"""

    voice_config: Optional[VoiceConfig] = Field(
        default=None,
        description="""使用するスピーカーの設定。""",
    )
    language_code: Optional[str] = Field(
        default=None,
        description="""音声合成のための言語コード（ISO 639、例：en-US）。
        Live APIでのみ利用可能。""",
    )
```

`voice_config`パラメータは`VoiceConfig`クラスを使用します：

```python
class VoiceConfig(_common.BaseModel):
    """使用する音声の設定。"""

    prebuilt_voice_config: Optional[PrebuiltVoiceConfig] = Field(
        default=None,
        description="""使用するスピーカーの設定。""",
    )
```

そして`PrebuiltVoiceConfig`は次の構造を持っています：

```python
class PrebuiltVoiceConfig(_common.BaseModel):
    """使用する事前構築済みスピーカーの設定。"""

    voice_name: Optional[str] = Field(
        default=None,
        description="""使用する事前構築済み音声の名前。""",
    )
```

これらのネストされた設定クラスにより、以下を指定できます：

*   `voice_config`: 使用する事前構築済み音声の名前（`PrebuiltVoiceConfig`内）
*   `language_code`: 音声合成のためのISO 639言語コード（例："en-US"）

音声対応エージェントを実装する際は、これらのパラメータを設定して、エージェントが話すときの音声を制御します。

### `response_modalities`

エージェントの出力モダリティを定義します。設定されていない場合、デフォルトはAUDIOです。応答モダリティは、エージェントがさまざまなチャネル（例：テキスト、音声）を通じてユーザーとどのように通信するかを決定します。

### `save_input_blobs_as_artifacts`

有効にすると、エージェントの実行中に入力BLOBがアーティファクトとして保存されます。これはデバッグや監査の目的で役立ち、開発者がエージェントによって受信された正確なデータを確認できるようになります。

### `support_cfc`

合成的関数呼び出し（CFC）のサポートを有効にします。StreamingMode.SSEを使用している場合にのみ適用可能です。有効にすると、CFC機能はLIVE APIのみがサポートしているため、LIVE APIが呼び出されます。

!!! warning

    `support_cfc`機能は実験的なものであり、そのAPIや振る舞いは将来のリリースで変更される可能性があります。

### `streaming_mode`

エージェントのストリーミングの振る舞いを設定します。可能な値：

*   `StreamingMode.NONE`: ストリーミングなし。応答は完全なユニットとして配信されます。
*   `StreamingMode.SSE`: Server-Sent Eventsストリーミング。サーバーからクライアントへの一方向ストリーミング。
*   `StreamingMode.BIDI`: 双方向ストリーミング。両方向で同時に通信します。

ストリーミングモードは、パフォーマンスとユーザーエクスペリエンスの両方に影響します。SSEストリーミングにより、ユーザーは生成中の応答を部分的に見ることができ、BIDIストリーミングはリアルタイムの対話型エクスペリエンスを可能にします。

### `output_audio_transcription`

音声応答機能を持つライブエージェントからの音声出力を文字起こしするための設定です。これにより、アクセシビリティ、記録保持、およびマルチモーダルアプリケーションのために音声応答の自動文字起こしが可能になります。

### `max_llm_calls`

特定のエージェント実行に対する合計LLM呼び出し回数に制限を設定します。

*   0より大きく`sys.maxsize`未満の値：LLM呼び出しに上限を設けます。
*   0以下の値：無制限のLLM呼び出しを許可します*（本番環境では非推奨）*。

このパラメータは、過剰なAPI使用と潜在的な暴走プロセスを防ぎます。LLM呼び出しはしばしばコストがかかり、リソースを消費するため、適切な制限を設定することが重要です。

## 検証ルール

`RunConfig`クラスは、適切なエージェントの操作を保証するためにそのパラメータを検証します。Python ADKは自動的な型検証に`Pydantic`を使用しますが、Java ADKは静的型付けに依存し、RunConfigの構築時に明示的なチェックを含む場合があります。
特に`max_llm_calls`パラメータについては：

1.  極端に大きな値（Pythonの`sys.maxsize`やJavaの`Integer.MAX_VALUE`など）は、問題を避けるために通常許可されません。

2.  0以下の値は、通常、無制限のLLMインタラクションに関する警告をトリガーします。

## 例

### 基本的なランタイム設定

=== "Python"

    ```python
    from google.genai.adk import RunConfig, StreamingMode
    
    config = RunConfig(
        streaming_mode=StreamingMode.NONE,
        max_llm_calls=100
    )
    ```

=== "Java"

    ```java
    import com.google.adk.agents.RunConfig;
    import com.google.adk.agents.RunConfig.StreamingMode;
    
    RunConfig config = RunConfig.builder()
            .setStreamingMode(StreamingMode.NONE)
            .setMaxLlmCalls(100)
            .build();
    ```

この設定は、100回のLLM呼び出し制限を持つ非ストリーミングエージェントを作成し、完全な応答が望ましい単純なタスク指向のエージェントに適しています。

### ストリーミングの有効化

=== "Python"

    ```python
    from google.genai.adk import RunConfig, StreamingMode
    
    config = RunConfig(
        streaming_mode=StreamingMode.SSE,
        max_llm_calls=200
    )
    ```

=== "Java"

    ```java
    import com.google.adk.agents.RunConfig;
    import com.google.adk.agents.RunConfig.StreamingMode;
    
    RunConfig config = RunConfig.builder()
        .setStreamingMode(StreamingMode.SSE)
        .setMaxLlmCalls(200)
        .build();
    ```

SSEストリーミングを使用すると、ユーザーは生成中の応答を見ることができ、チャットボットやアシスタントにより応答性の高い感触を提供します。

### 音声サポートの有効化

=== "Python"

    ```python
    from google.genai.adk import RunConfig, StreamingMode
    from google.genai import types
    
    config = RunConfig(
        speech_config=types.SpeechConfig(
            language_code="en-US",
            voice_config=types.VoiceConfig(
                prebuilt_voice_config=types.PrebuiltVoiceConfig(
                    voice_name="Kore"
                )
            ),
        ),
        response_modalities=["AUDIO", "TEXT"],
        save_input_blobs_as_artifacts=True,
        support_cfc=True,
        streaming_mode=StreamingMode.SSE,
        max_llm_calls=1000,
    )
    ```

=== "Java"

    ```java
    import com.google.adk.agents.RunConfig;
    import com.google.adk.agents.RunConfig.StreamingMode;
    import com.google.common.collect.ImmutableList;
    import com.google.genai.types.Content;
    import com.google.genai.types.Modality;
    import com.google.genai.types.Part;
    import com.google.genai.types.PrebuiltVoiceConfig;
    import com.google.genai.types.SpeechConfig;
    import com.google.genai.types.VoiceConfig;
    
    RunConfig runConfig =
        RunConfig.builder()
            .setStreamingMode(StreamingMode.SSE)
            .setMaxLlmCalls(1000)
            .setSaveInputBlobsAsArtifacts(true)
            .setResponseModalities(ImmutableList.of(new Modality("AUDIO"), new Modality("TEXT")))
            .setSpeechConfig(
                SpeechConfig.builder()
                    .voiceConfig(
                        VoiceConfig.builder()
                            .prebuiltVoiceConfig(
                                PrebuiltVoiceConfig.builder().voiceName("Kore").build())
                            .build())
                    .languageCode("en-US")
                    .build())
            .build();
    ```

この包括的な例では、エージェントを以下のように設定します：

*   "Kore"の声（米国英語）を使用した音声機能
*   音声とテキストの両方の出力モダリティ
*   入力BLOBのアーティファクト保存（デバッグに役立つ）
*   実験的なCFCサポートの有効化 **(Pythonのみ)**
*   応答性の高い対話のためのSSEストリーミング
*   1000回のLLM呼び出し制限

### 実験的なCFCサポートの有効化

![python_only](https://img.shields.io/badge/現在サポートされているのは-Python-blue){ title="この機能は現在Pythonで利用可能です。Javaのサポートは計画中/近日公開予定です。" }

```python
from google.genai.adk import RunConfig, StreamingMode

config = RunConfig(
    streaming_mode=StreamingMode.SSE,
    support_cfc=True,
    max_llm_calls=150
)
```

合成的関数呼び出しを有効にすると、モデルの出力に基づいて動的に関数を実行できるエージェントが作成され、複雑なワークフローを必要とするアプリケーションに強力です。