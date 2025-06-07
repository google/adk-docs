# アーティファクト

ADKにおける**アーティファクト**は、特定のユーザーインタラクションセッションに関連付けられるか、複数のセッションにわたってユーザーに永続的に関連付けられる、名前付きでバージョン管理されたバイナリデータを管理するための重要なメカニズムです。これにより、エージェントやツールが単純なテキスト文字列を超えたデータを扱うことが可能になり、ファイル、画像、音声、その他のバイナリ形式を含む、よりリッチなインタラクションが実現します。

!!! Note
    プリミティブの具体的なパラメータやメソッド名は、SDKの言語によって若干異なる場合があります（例：Pythonでは`save_artifact`、Javaでは`saveArtifact`）。詳細は各言語のAPIドキュメントを参照してください。

## アーティファクトとは？

*   **定義：** アーティファクトは、本質的には特定のスコープ（セッションまたはユーザー）内で一意の`filename`文字列によって識別されるバイナリデータ（ファイルの内容など）です。同じファイル名でアーティファクトを保存するたびに、新しいバージョンが作成されます。

*   **表現：** アーティファクトは、標準の`google.genai.types.Part`オブジェクトを使用して一貫して表現されます。中心となるデータは通常、`Part`のインラインデータ構造（`inline_data`を介してアクセス）に格納され、それ自体には以下が含まれます：
    *   `data`：生のバイナリコンテンツ（バイト列）。
    *   `mime_type`：データの種類を示す文字列（例：`"image/png"`、`"application/pdf"`）。これは後でデータを正しく解釈するために不可欠です。

=== "Python"

    ```py
    # アーティファクトがtypes.Partとしてどのように表現されるかの例
    import google.genai.types as types

    # 'image_bytes'がPNG画像のバイナリデータを含むと仮定
    image_bytes = b'\x89PNG\r\n\x1a\n...' # 実際の画像バイトのプレースホルダー

    image_artifact = types.Part(
        inline_data=types.Blob(
            mime_type="image/png",
            data=image_bytes
        )
    )

    # 便利なコンストラクタを使用することもできます：
    # image_artifact_alt = types.Part.from_bytes(data=image_bytes, mime_type="image/png")

    print(f"アーティファクトのMIMEタイプ: {image_artifact.inline_data.mime_type}")
    print(f"アーティファクトのデータ（最初の10バイト）: {image_artifact.inline_data.data[:10]}...")
    ```

=== "Java"

    ```java
    import com.google.genai.types.Part;
    import java.nio.charset.StandardCharsets;

    public class ArtifactExample {
        public static void main(String[] args) {
            // 'imageBytes'がPNG画像のバイナリデータを含むと仮定
            byte[] imageBytes = {(byte) 0x89, (byte) 0x50, (byte) 0x4E, (byte) 0x47, (byte) 0x0D, (byte) 0x0A, (byte) 0x1A, (byte) 0x0A, (byte) 0x01, (byte) 0x02}; // 実際の画像バイトのプレースホルダー

            // Part.fromBytesを使用して画像アーティファクトを作成
            Part imageArtifact = Part.fromBytes(imageBytes, "image/png");

            System.out.println("アーティファクトのMIMEタイプ: " + imageArtifact.inlineData().get().mimeType().get());
            System.out.println(
                "アーティファクトのデータ（最初の10バイト）: "
                    + new String(imageArtifact.inlineData().get().data().get(), 0, 10, StandardCharsets.UTF_8)
                    + "...");
        }
    }
    ```

*   **永続化と管理：** アーティファクトはエージェントやセッション状態に直接保存されるわけではありません。その保存と取得は、専用の**Artifact Service**（`google.adk.artifacts`で定義されている`BaseArtifactService`の実装）によって管理されます。ADKは、以下のような様々な実装を提供します：
    *   テストや一時的な保存のためのインメモリサービス（例：Pythonの`InMemoryArtifactService`、`google.adk.artifacts.in_memory_artifact_service.py`で定義）。
    *   Google Cloud Storage (GCS) を使用した永続的な保存のためのサービス（例：Pythonの`GcsArtifactService`、`google.adk.artifacts.gcs_artifact_service.py`で定義）。
    選択されたサービス実装は、データを保存する際に自動的にバージョニングを処理します。

## なぜアーティファクトを使用するのか？

セッションの`state`は、設定情報や会話の文脈（文字列、数値、ブール値、小さな辞書/リストなど）といった小さなデータを保存するのに適していますが、アーティファクトはバイナリデータや大規模なデータを含むシナリオ向けに設計されています：

1.  **非テキストデータの処理：** 画像、音声クリップ、ビデオ断片、PDF、スプレッドシートなど、エージェントの機能に関連するあらゆるファイル形式を簡単に保存・取得できます。
2.  **大規模データの永続化：** セッション状態は一般的に大量のデータを保存するために最適化されていません。アーティファクトは、セッション状態を煩雑にすることなく、より大きなBLOBを永続化するための専用メカニズムを提供します。
3.  **ユーザーファイル管理：** ユーザーがファイルをアップロード（アーティファクトとして保存可能）し、エージェントによって生成されたファイルを取得またはダウンロード（アーティファクトから読み込み）する機能を提供します。
4.  **出力の共有：** ツールやエージェントが生成したバイナリ出力（PDFレポートや生成画像など）を`save_artifact`を介して保存し、後でアプリケーションの他の部分や、さらには後続のセッション（ユーザー名前空間を使用している場合）でアクセスできるようにします。
5.  **バイナリデータのキャッシュ：** バイナリデータを生成する計算コストの高い操作（複雑なチャート画像のレンダリングなど）の結果をアーティファクトとして保存し、後続のリクエストで再生成するのを避けます。

要するに、エージェントが永続化、バージョニング、または共有が必要なファイルのようなバイナリデータを扱う必要がある場合、ADK内では`ArtifactService`によって管理されるアーティファクトが適切なメカニズムとなります。

## 一般的なユースケース

アーティファクトは、ADKアプリケーション内でバイナリデータを扱うための柔軟な方法を提供します。

以下は、それらが価値を発揮する典型的なシナリオです：

*   **生成されたレポート/ファイル：**
    *   ツールやエージェントがレポート（例：PDF分析、CSVデータエクスポート、画像チャート）を生成します。

*   **ユーザーアップロードの処理：**
    *   ユーザーがフロントエンドインターフェースを通じてファイル（例：分析用の画像、要約用のドキュメント）をアップロードします。

*   **中間バイナリ結果の保存：**
    *   エージェントが複雑な複数ステップのプロセスを実行し、あるステップで中間的なバイナリデータ（例：音声合成、シミュレーション結果）が生成されます。

*   **永続的なユーザーデータ：**
    *   単純なキーと値の状態ではない、ユーザー固有の設定やデータを保存します。

*   **生成されたバイナリコンテンツのキャッシュ：**
    *   エージェントが特定の入力に基づいて同じバイナリ出力（例：会社のロゴ画像、標準の音声挨拶）を頻繁に生成します。

## コアコンセプト

アーティファクトを理解するには、いくつかの主要なコンポーネントを把握する必要があります：それらを管理するサービス、それらを保持するために使用されるデータ構造、そしてそれらがどのように識別され、バージョン管理されるかです。

### Artifact Service (`BaseArtifactService`)

*   **役割：** アーティファクトの実際の保存と取得ロジックを担当する中心的なコンポーネント。アーティファクトが*どのように*、*どこに*永続化されるかを定義します。

*   **インターフェース：** 抽象基底クラス`BaseArtifactService`によって定義されます。具体的な実装は、以下のメソッドを提供する必要があります：

    *   `Save Artifact`: アーティファクトデータを保存し、割り当てられたバージョン番号を返します。
    *   `Load Artifact`: アーティファクトの特定のバージョン（または最新版）を取得します。
    *   `List Artifact keys`: 指定されたスコープ内のアーティファクトの一意なファイル名をリストします。
    *   `Delete Artifact`: アーティファクトを（実装によってはすべてのバージョンを）削除します。
    *   `List versions`: 特定のアーティファクトファイル名の利用可能なすべてのバージョン番号をリストします。

*   **設定：** `Runner`の初期化時に、アーティファクトサービスのインスタンス（例：`InMemoryArtifactService`, `GcsArtifactService`）を提供します。`Runner`は、このサービスを`InvocationContext`を介してエージェントやツールで利用可能にします。

=== "Python"

    ```py
    from google.adk.runners import Runner
    from google.adk.artifacts import InMemoryArtifactService # または GcsArtifactService
    from google.adk.agents import LlmAgent # 任意の agent
    from google.adk.sessions import InMemorySessionService

    # 例：RunnerをArtifact Serviceで設定する
    my_agent = LlmAgent(name="artifact_user_agent", model="gemini-2.0-flash")
    artifact_service = InMemoryArtifactService() # 実装を選択
    session_service = InMemorySessionService()

    runner = Runner(
        agent=my_agent,
        app_name="my_artifact_app",
        session_service=session_service,
        artifact_service=artifact_service # ここでサービスのインスタンスを提供する
    )
    # これで、このrunnerによって管理される実行内のコンテキストはアーティファクトメソッドを使用できます
    ```

=== "Java"
    
    ```java
    import com.google.adk.agents.LlmAgent;
    import com.google.adk.runner.Runner;
    import com.google.adk.sessions.InMemorySessionService;
    import com.google.adk.artifacts.InMemoryArtifactService;
    
    // 例：RunnerをArtifact Serviceで設定する
    LlmAgent myAgent =  LlmAgent.builder()
      .name("artifact_user_agent")
      .model("gemini-2.0-flash")
      .build();
    InMemoryArtifactService artifactService = new InMemoryArtifactService(); // 実装を選択
    InMemorySessionService sessionService = new InMemorySessionService();

    Runner runner = new Runner(myAgent, "my_artifact_app", artifactService, sessionService); // ここでサービスのインスタンスを提供する
    // これで、このrunnerによって管理される実行内のコンテキストはアーティファクトメソッドを使用できます
    ```

### アーティファクトデータ

*   **標準表現：** アーティファクトのコンテンツは、LLMメッセージの一部に使用されるのと同じ構造である`google.genai.types.Part`オブジェクトを使用して普遍的に表現されます。

*   **主要な属性 (`inline_data`)：** アーティファクトにとって最も関連性の高い属性は`inline_data`で、これは以下の情報を含む`google.genai.types.Blob`オブジェクトです：

    *   `data` (`bytes`): アーティファクトの生のバイナリコンテンツ。
    *   `mime_type` (`str`): バイナリデータの性質を説明する標準のMIMEタイプ文字列（例：`'application/pdf'`, `'image/png'`, `'audio/mpeg'`）。**これはアーティファクトを読み込む際に正しく解釈するために非常に重要です。**

=== "Python"

    ```python
    import google.genai.types as types

    # 例：生のバイトからアーティファクトPartを作成する
    pdf_bytes = b'%PDF-1.4...' # あなたの生のPDFデータ
    pdf_mime_type = "application/pdf"

    # コンストラクタを使用
    pdf_artifact_py = types.Part(
        inline_data=types.Blob(data=pdf_bytes, mime_type=pdf_mime_type)
    )

    # 便利なクラスメソッドを使用（同等）
    pdf_artifact_alt_py = types.Part.from_bytes(data=pdf_bytes, mime_type=pdf_mime_type)

    print(f"作成されたPythonアーティファクトのMIMEタイプ: {pdf_artifact_py.inline_data.mime_type}")
    ```
    
=== "Java"

    ```java
    --8<-- "examples/java/snippets/src/main/java/artifacts/ArtifactDataExample.java:full_code"
    ```

### ファイル名

*   **識別子：** 特定の名前空間内でアーティファクトに名前を付け、取得するために使用される単純な文字列。
*   **一意性：** ファイル名は、そのスコープ（セッションまたはユーザー名前空間）内で一意でなければなりません。
*   **ベストプラクティス：** 説明的な名前を使用し、ファイル拡張子（例：`"monthly_report.pdf"`、`"user_avatar.jpg"`）を含めることが推奨されますが、拡張子自体が振る舞いを決定するわけではなく、`mime_type`が決定します。

### バージョニング

*   **自動バージョニング：** アーティファクトサービスが自動的にバージョニングを処理します。`save_artifact`を呼び出すと、サービスはその特定のファイル名とスコープに対して次に利用可能なバージョン番号（通常は0から始まりインクリメントされる）を決定します。
*   **`save_artifact`による返り値：** `save_artifact`メソッドは、新しく保存されたアーティファクトに割り当てられた整数のバージョン番号を返します。
*   **取得：**
    *   `load_artifact(..., version=None)` (デフォルト): アーティファクトの*最新*の利用可能なバージョンを取得します。
    *   `load_artifact(..., version=N)`: 特定のバージョン`N`を取得します。
*   **バージョンのリスト表示：** `list_versions`メソッド（コンテキストではなくサービス上）を使用して、アーティファクトの既存のすべてのバージョン番号を見つけることができます。

### 名前空間（セッション vs. ユーザー）

*   **概念：** アーティファクトは、特定のセッションにスコープを限定するか、アプリケーション内のすべてのセッションにわたってより広くユーザーにスコープを限定することができます。このスコープは`filename`の形式によって決定され、`ArtifactService`によって内部的に処理されます。

*   **デフォルト（セッションスコープ）：** `"report.pdf"`のようなプレーンなファイル名を使用すると、アーティファクトは特定の`app_name`、`user_id`、*および*`session_id`に関連付けられます。その正確なセッションコンテキスト内でのみアクセス可能です。

*   **ユーザースコープ（`"user:"`プレフィックス）：** ファイル名を`"user:profile.png"`のように`"user:"`で始めると、アーティファクトは`app_name`と`user_id`のみに関連付けられます。アプリ内のそのユーザーに属する*どの*セッションからでもアクセスまたは更新できます。

=== "Python"

    ```python
    # 名前空間の違いを示す概念的な例

    # セッション固有のアーティファクトファイル名
    session_report_filename = "summary.txt"

    # ユーザー固有のアーティファクトファイル名
    user_config_filename = "user:settings.json"

    # context.save_artifact経由で'summary.txt'を保存すると、
    # 現在のapp_name、user_id、session_idに紐付けられる。

    # context.save_artifact経由で'user:settings.json'を保存すると、
    # ArtifactService実装は"user:"プレフィックスを認識し、
    # app_nameとuser_idにスコープを限定し、そのユーザーのセッション間でアクセス可能にするべきである。
    ```

=== "Java"

    ```java
    // 名前空間の違いを示す概念的な例
    
    // セッション固有のアーティファクトファイル名
    String sessionReportFilename = "summary.txt";
    
    // ユーザー固有のアーティファクトファイル名
    String userConfigFilename = "user:settings.json"; // "user:"プレフィックスが鍵
    
    // context.save_artifact経由で'summary.txt'を保存すると、
    // 現在のapp_name、user_id、session_idに紐付けられる。
    // artifactService.saveArtifact(appName, userId, sessionId1, sessionReportFilename, someData);
    
    // context.save_artifact経由で'user:settings.json'を保存すると、
    // ArtifactService実装は"user:"プレフィックスを認識し、
    // app_nameとuser_idにスコープを限定し、そのユーザーのセッション間でアクセス可能にするべきである。
    // artifactService.saveArtifact(appName, userId, sessionId1, userConfigFilename, someData);
    ```

これらのコアコンセプトが連携して、ADKフレームワーク内でバイナリデータを管理するための柔軟なシステムを提供します。

## アーティファクトとの対話（コンテキストオブジェクト経由）

エージェントのロジック内（特にコールバックやツール内）でアーティファクトと対話する主要な方法は、`CallbackContext`および`ToolContext`オブジェクトによって提供されるメソッドを使用することです。これらのメソッドは、`ArtifactService`によって管理される基盤となるストレージの詳細を抽象化します。

### 前提条件：`ArtifactService`の設定

コンテキストオブジェクトを介してアーティファクトメソッドを使用する前に、`Runner`を初期化する際に**必ず** [`BaseArtifactService`の実装](#available-implementations)（[`InMemoryArtifactService`](#inmemoryartifactservice) や [`GcsArtifactService`](#gcsartifactservice) など）のインスタンスを提供する必要があります。

=== "Python"

    Pythonでは、`Runner`を初期化する際にこのインスタンスを提供します。

    ```python
    from google.adk.runners import Runner
    from google.adk.artifacts import InMemoryArtifactService # または GcsArtifactService
    from google.adk.agents import LlmAgent
    from google.adk.sessions import InMemorySessionService

    # エージェントの定義
    agent = LlmAgent(name="my_agent", model="gemini-2.0-flash")

    # 目的のアーティファクトサービスをインスタンス化
    artifact_service = InMemoryArtifactService()

    # それをRunnerに提供する
    runner = Runner(
        agent=agent,
        app_name="artifact_app",
        session_service=InMemorySessionService(),
        artifact_service=artifact_service # ここでサービスを提供する必要がある
    )
    ```
    `InvocationContext`に`artifact_service`が設定されていない場合（`Runner`に渡されなかった場合）、コンテキストオブジェクトで`save_artifact`、`load_artifact`、または`list_artifacts`を呼び出すと`ValueError`が発生します。

=== "Java"

    Javaでは、`BaseArtifactService`の実装をインスタンス化し、アーティファクトを管理するアプリケーションの部分からアクセスできるようにします。これは多くの場合、依存性注入を使用するか、サービスインスタンスを明示的に渡すことによって行われます。

    ```java
    import com.google.adk.agents.LlmAgent;
    import com.google.adk.artifacts.InMemoryArtifactService; // または GcsArtifactService
    import com.google.adk.runner.Runner;
    import com.google.adk.sessions.InMemorySessionService;
    
    public class SampleArtifactAgent {
    
      public static void main(String[] args) {
    
        // エージェントの定義
        LlmAgent agent = LlmAgent.builder()
            .name("my_agent")
            .model("gemini-2.0-flash")
            .build();
    
        // 目的のアーティファクトサービスをインスタンス化
        InMemoryArtifactService artifactService = new InMemoryArtifactService();
    
        // それをRunnerに提供する
        Runner runner = new Runner(agent,
            "APP_NAME",
            artifactService, // ここでサービスを提供する必要がある
            new InMemorySessionService());
    
      }
    }
    ```
    Javaでは、アーティファクト操作が試みられたときに`ArtifactService`インスタンスが利用できない場合（例：`null`）、通常は`NullPointerException`またはカスタムエラーが発生します。堅牢なアプリケーションでは、サービスのライフサイクルを管理し、可用性を確保するために依存性注入フレームワークをよく使用します。

### メソッドへのアクセス

アーティファクトとの対話メソッドは、`CallbackContext`（エージェントおよびモデルのコールバックに渡される）および`ToolContext`（ツールのコールバックに渡される）のインスタンスで直接利用できます。`ToolContext`は`CallbackContext`を継承していることを覚えておいてください。

*   **コード例：**

    === "Python"

        ```python
        import google.genai.types as types
        from google.adk.agents.callback_context import CallbackContext # または ToolContext

        async def save_generated_report_py(context: CallbackContext, report_bytes: bytes):
            """生成されたPDFレポートのバイトをアーティファクトとして保存します。"""
            report_artifact = types.Part.from_data(
                data=report_bytes,
                mime_type="application/pdf"
            )
            filename = "generated_report.pdf"

            try:
                version = await context.save_artifact(filename=filename, artifact=report_artifact)
                print(f"Pythonアーティファクト'{filename}'をバージョン{version}として正常に保存しました。")
                # このコールバックの後に生成されるイベントには以下が含まれます：
                # event.actions.artifact_delta == {"generated_report.pdf": version}
            except ValueError as e:
                print(f"Pythonアーティファクトの保存エラー: {e}。RunnerにArtifactServiceが設定されていますか？")
            except Exception as e:
                # 潜在的なストレージエラー（例：GCSの権限）を処理
                print(f"Pythonアーティファクトの保存中に予期しないエラーが発生しました: {e}")

        # --- 使用例の概念（Python） ---
        # async def main_py():
        #   callback_context: CallbackContext = ... # contextを取得
        #   report_data = b'...' # PDFのバイトデータを保持すると仮定
        #   await save_generated_report_py(callback_context, report_data)
        ```

    === "Java"
    
        ```java
        import com.google.adk.agents.CallbackContext;
        import com.google.adk.artifacts.BaseArtifactService;
        import com.google.adk.artifacts.InMemoryArtifactService;
        import com.google.genai.types.Part;
        import java.nio.charset.StandardCharsets;

        public class SaveArtifactExample {

        public void saveGeneratedReport(CallbackContext callbackContext, byte[] reportBytes) {
        // 生成されたPDFレポートのバイトをアーティファクトとして保存します。
        Part reportArtifact = Part.fromBytes(reportBytes, "application/pdf");
        String filename = "generatedReport.pdf";

            callbackContext.saveArtifact(filename, reportArtifact);
            System.out.println("Javaアーティファクト'" + filename + "'を正常に保存しました。");
            // このコールバックの後に生成されるイベントには以下が含まれます：
            // event().actions().artifactDelta == {"generated_report.pdf": version}
        }

        // --- 使用例の概念（Java） ---
        public static void main(String[] args) {
            BaseArtifactService service = new InMemoryArtifactService(); // または GcsArtifactService
            SaveArtifactExample myTool = new SaveArtifactExample();
            byte[] reportData = "...".getBytes(StandardCharsets.UTF_8); // PDFのバイトデータ
            CallbackContext callbackContext; // ... アプリからコールバックコンテキストを取得
            myTool.saveGeneratedReport(callbackContext, reportData);
            // 非同期の性質のため、実際のアプリではプログラムが待機するか完了を処理することを確認してください。
          }
        }
        ```

#### アーティファクトの読み込み

*   **コード例：**

    === "Python"

        ```python
        import google.genai.types as types
        from google.adk.agents.callback_context import CallbackContext # または ToolContext

        async def process_latest_report_py(context: CallbackContext):
            """最新のレポートアーティファクトを読み込み、そのデータを処理します。"""
            filename = "generated_report.pdf"
            try:
                # 最新バージョンを読み込む
                report_artifact = await context.load_artifact(filename=filename)

                if report_artifact and report_artifact.inline_data:
                    print(f"最新のPythonアーティファクト'{filename}'を正常に読み込みました。")
                    print(f"MIMEタイプ: {report_artifact.inline_data.mime_type}")
                    # report_artifact.inline_data.data (bytes) を処理する
                    pdf_bytes = report_artifact.inline_data.data
                    print(f"レポートサイズ: {len(pdf_bytes)} バイト。")
                    # ... さらなる処理 ...
                else:
                    print(f"Pythonアーティファクト'{filename}'が見つかりませんでした。")

                # 例：特定のバージョンを読み込む（バージョン0が存在する場合）
                # specific_version_artifact = await context.load_artifact(filename=filename, version=0)
                # if specific_version_artifact:
                #     print(f"'{filename}'のバージョン0を読み込みました。")

            except ValueError as e:
                print(f"Pythonアーティファクトの読み込みエラー: {e}。ArtifactServiceは設定されていますか？")
            except Exception as e:
                # 潜在的なストレージエラーを処理
                print(f"Pythonアーティファクトの読み込み中に予期しないエラーが発生しました: {e}")

        # --- 使用例の概念（Python） ---
        # async def main_py():
        #   callback_context: CallbackContext = ... # contextを取得
        #   await process_latest_report_py(callback_context)
        ```

    === "Java"

        ```java
        import com.google.adk.artifacts.BaseArtifactService;
        import com.google.genai.types.Part;
        import io.reactivex.rxjava3.core.MaybeObserver;
        import io.reactivex.rxjava3.disposables.Disposable;
        import java.util.Optional;

        public class MyArtifactLoaderService {

            private final BaseArtifactService artifactService;
            private final String appName;

            public MyArtifactLoaderService(BaseArtifactService artifactService, String appName) {
                this.artifactService = artifactService;
                this.appName = appName;
            }

            public void processLatestReportJava(String userId, String sessionId, String filename) {
                // バージョンにOptional.empty()を渡して最新バージョンを読み込む
                artifactService
                        .loadArtifact(appName, userId, sessionId, filename, Optional.empty())
                        .subscribe(
                                new MaybeObserver<Part>() {
                                    @Override
                                    public void onSubscribe(Disposable d) {
                                        // オプション：サブスクリプションを処理
                                    }

                                    @Override
                                    public void onSuccess(Part reportArtifact) {
                                        System.out.println(
                                                "最新のJavaアーティファクト'" + filename + "'を正常に読み込みました。");
                                        reportArtifact
                                                .inlineData()
                                                .ifPresent(
                                                        blob -> {
                                                            System.out.println(
                                                                    "MIMEタイプ: " + blob.mimeType().orElse("N/A"));
                                                            byte[] pdfBytes = blob.data().orElse(new byte);
                                                            System.out.println("レポートサイズ: " + pdfBytes.length + " バイト。");
                                                            // ... pdfBytesのさらなる処理 ...
                                                        });
                                    }

                                    @Override
                                    public void onError(Throwable e) {
                                        // 潜在的なストレージエラーやその他の例外を処理
                                        System.err.println(
                                                "Javaアーティファクト'"
                                                        + filename
                                                        + "'の読み込み中にエラーが発生しました: "
                                                        + e.getMessage());
                                    }

                                    @Override
                                    public void onComplete() {
                                        // アーティファクト（最新版）が見つからなかった場合に呼び出される
                                        System.out.println("Javaアーティファクト'" + filename + "'が見つかりませんでした。");
                                    }
                                });

                // 例：特定のバージョン（例：バージョン0）を読み込む
                /*
                artifactService.loadArtifact(appName, userId, sessionId, filename, Optional.of(0))
                    .subscribe(part -> {
                        System.out.println("Javaアーティファクト'" + filename + "'のバージョン0を読み込みました。");
                    }, throwable -> {
                        System.err.println("'" + filename + "'のバージョン0の読み込みエラー: " + throwable.getMessage());
                    }, () -> {
                        System.out.println("Javaアーティファクト'" + filename + "'のバージョン0が見つかりませんでした。");
                    });
                */
            }

            // --- 使用例の概念（Java） ---
            public static void main(String[] args) {
                // BaseArtifactService service = new InMemoryArtifactService(); // または GcsArtifactService
                // MyArtifactLoaderService loader = new MyArtifactLoaderService(service, "myJavaApp");
                // loader.processLatestReportJava("user123", "sessionABC", "java_report.pdf");
                // 非同期の性質のため、実際のアプリではプログラムが待機するか完了を処理することを確認してください。
            }
        }
        ```

#### アーティファクトファイル名のリスト表示

*   **コード例：**

    === "Python"

        ```python
        from google.adk.tools.tool_context import ToolContext

        async def list_user_files_py(tool_context: ToolContext) -> str:
            """ユーザーが利用可能なアーティファクトをリストするツール。"""
            try:
                available_files = await tool_context.list_artifacts()
                if not available_files:
                    return "保存されたアーティファクトはありません。"
                else:
                    # ユーザー/LLM用にリストをフォーマットする
                    file_list_str = "\n".join([f"- {fname}" for fname in available_files])
                    return f"利用可能なPythonアーティファクトは次のとおりです:\n{file_list_str}"
            except ValueError as e:
                print(f"Pythonアーティファクトのリスト表示エラー: {e}。ArtifactServiceは設定されていますか？")
                return "エラー：Pythonアーティファクトをリストできませんでした。"
            except Exception as e:
                print(f"Pythonアーティファクトのリスト表示中に予期しないエラーが発生しました: {e}")
                return "エラー：Pythonアーティファクトのリスト表示中に予期しないエラーが発生しました。"

        # この関数は通常、FunctionToolでラップされます
        # from google.adk.tools import FunctionTool
        # list_files_tool = FunctionTool(func=list_user_files_py)
        ```

    === "Java"

        ```java
        import com.google.adk.artifacts.BaseArtifactService;
        import com.google.adk.artifacts.ListArtifactsResponse;
        import com.google.common.collect.ImmutableList;
        import io.reactivex.rxjava3.core.SingleObserver;
        import io.reactivex.rxjava3.disposables.Disposable;

        public class MyArtifactListerService {

            private final BaseArtifactService artifactService;
            private final String appName;

            public MyArtifactListerService(BaseArtifactService artifactService, String appName) {
                this.artifactService = artifactService;
                this.appName = appName;
            }

            // ツールやエージェントのロジックから呼び出される可能性のあるメソッドの例
            public void listUserFilesJava(String userId, String sessionId) {
                artifactService
                        .listArtifactKeys(appName, userId, sessionId)
                        .subscribe(
                                new SingleObserver<ListArtifactsResponse>() {
                                    @Override
                                    public void onSubscribe(Disposable d) {
                                        // オプション：サブスクリプションを処理
                                    }

                                    @Override
                                    public void onSuccess(ListArtifactsResponse response) {
                                        ImmutableList<String> availableFiles = response.filenames();
                                        if (availableFiles.isEmpty()) {
                                            System.out.println(
                                                    "ユーザー "
                                                            + userId
                                                            + " のセッション "
                                                            + sessionId
                                                            + " には保存されたJavaアーティファクトはありません。");
                                        } else {
                                            StringBuilder fileListStr =
                                                    new StringBuilder(
                                                            "ユーザー "
                                                                    + userId
                                                                    + " のセッション "
                                                                    + sessionId
                                                                    + " で利用可能なJavaアーティファクトは次のとおりです:\n");
                                            for (String fname : availableFiles) {
                                                fileListStr.append("- ").append(fname).append("\n");
                                            }
                                            System.out.println(fileListStr.toString());
                                        }
                                    }

                                    @Override
                                    public void onError(Throwable e) {
                                        System.err.println(
                                                "ユーザー "
                                                        + userId
                                                        + " のセッション "
                                                        + sessionId
                                                        + " のJavaアーティファクトのリスト表示エラー: "
                                                        + e.getMessage());
                                        // 実際のアプリケーションでは、ユーザー/LLMにエラーメッセージを返すかもしれません
                                    }
                                });
            }

            // --- 使用例の概念（Java） ---
            public static void main(String[] args) {
                // BaseArtifactService service = new InMemoryArtifactService(); // または GcsArtifactService
                // MyArtifactListerService lister = new MyArtifactListerService(service, "myJavaApp");
                // lister.listUserFilesJava("user123", "sessionABC");
                // 非同期の性質のため、実際のアプリではプログラムが待機するか完了を処理することを確認してください。
            }
        }
        ```

これらの保存、読み込み、リスト表示のメソッドは、選択したバックエンドストレージの実装に関わらず、Pythonのコンテキストオブジェクトを使用する場合でも、Javaで`BaseArtifactService`と直接対話する場合でも、ADK内でバイナリデータの永続性を管理するための一貫した便利な方法を提供します。

## 利用可能な実装

ADKは`BaseArtifactService`インターフェースの具体的な実装を提供し、さまざまな開発段階やデプロイニーズに適した異なるストレージバックエンドを提供します。これらの実装は、`app_name`、`user_id`、`session_id`、および`filename`（`user:`名前空間プレフィックスを含む）に基づいて、アーティファクトデータの保存、バージョニング、取得の詳細を処理します。

### InMemoryArtifactService

*   **ストレージメカニズム：**
    *   Python：アプリケーションのメモリに保持されるPython辞書（`self.artifacts`）を使用します。辞書のキーはアーティファクトのパスを表し、値は`types.Part`のリストで、各リスト要素がバージョンです。
    *   Java：メモリに保持されるネストされた`HashMap`インスタンス（`private final Map<String, Map<String, Map<String, Map<String, List<Part>>>>> artifacts;`）を使用します。各レベルのキーはそれぞれ`appName`、`userId`、`sessionId`、`filename`です。最も内側の`List<Part>`がアーティファクトのバージョンを保存し、リストのインデックスがバージョン番号に対応します。
*   **主な特徴：**
    *   **単純さ：** コアADKライブラリ以外の外部セットアップや依存関係は不要です。
    *   **速度：** 操作は通常、メモリ内のマップ/辞書のルックアップとリスト操作を伴うため非常に高速です。
    *   **一時的：** 保存されたすべてのアーティファクトは、アプリケーションプロセスが終了すると**失われます**。データはアプリケーションの再起動間で永続しません。
*   **ユースケース：**
    *   永続性が不要なローカル開発やテストに最適です。
    *   短期間のデモンストレーションや、アーティファクトデータがアプリケーションの単一実行内で純粋に一時的なシナリオに適しています。
*   **インスタンス化：**

    === "Python"

        ```python
        from google.adk.artifacts import InMemoryArtifactService

        # クラスをインスタンス化するだけ
        in_memory_service_py = InMemoryArtifactService()

        # そしてそれをRunnerに渡す
        # runner = Runner(..., artifact_service=in_memory_service_py)
        ```

    === "Java"

        ```java
        import com.google.adk.artifacts.BaseArtifactService;
        import com.google.adk.artifacts.InMemoryArtifactService;

        public class InMemoryServiceSetup {
            public static void main(String[] args) {
                // クラスをインスタンス化するだけ
                BaseArtifactService inMemoryServiceJava = new InMemoryArtifactService();

                System.out.println("InMemoryArtifactService (Java) がインスタンス化されました: " + inMemoryServiceJava.getClass().getName());

                // このインスタンスはRunnerに提供されます。
                // Runner runner = new Runner(
                //     /* 他のサービス */,
                //     inMemoryServiceJava
                // );
            }
        }
        ```

### GcsArtifactService

*   **ストレージメカニズム：** 永続的なアーティファクトストレージのためにGoogle Cloud Storage (GCS) を活用します。アーティファクトの各バージョンは、指定されたGCSバケット内に個別のオブジェクト（BLOB）として保存されます。
*   **オブジェクトの命名規則：** 階層的なパス構造を使用してGCSオブジェクト名（BLOB名）を構築します。
*   **主な特徴：**
    *   **永続性：** GCSに保存されたアーティファクトは、アプリケーションの再起動やデプロイを越えて永続します。
    *   **スケーラビリティ：** Google Cloud Storageのスケーラビリティと耐久性を活用します。
    *   **バージョニング：** 各バージョンを個別のGCSオブジェクトとして明示的に保存します。`GcsArtifactService`の`saveArtifact`メソッド。
    *   **必要な権限：** アプリケーション環境には、指定されたGCSバケットからの読み取りと書き込みのための適切な認証情報（例：Application Default Credentials）とIAM権限が必要です。
*   **ユースケース：**
    *   永続的なアーティファクトストレージを必要とする本番環境。
    *   同じGCSバケットにアクセスすることで、異なるアプリケーションインスタンスやサービス間でアーティファクトを共有する必要があるシナリオ。
    *   ユーザーまたはセッションデータの長期的な保存と取得が必要なアプリケーション。
*   **インスタンス化：**

    === "Python"

        ```python
        from google.adk.artifacts import GcsArtifactService

        # GCSバケット名を指定
        gcs_bucket_name_py = "your-gcs-bucket-for-adk-artifacts" # あなたのバケット名に置き換えてください

        try:
            gcs_service_py = GcsArtifactService(bucket_name=gcs_bucket_name_py)
            print(f"Python GcsArtifactServiceがバケット: {gcs_bucket_name_py} のために初期化されました")
            # 環境がこのバケットにアクセスするための認証情報を持っていることを確認してください。
            # 例：Application Default Credentials (ADC)経由

            # そしてそれをRunnerに渡す
            # runner = Runner(..., artifact_service=gcs_service_py)

        except Exception as e:
            # GCSクライアントの初期化中の潜在的なエラー（例：認証問題）をキャッチ
            print(f"Python GcsArtifactServiceの初期化エラー: {e}")
            # エラーを適切に処理する - InMemoryにフォールバックするか、例外を発生させるなど
        ```

    === "Java"

        ```java
        --8<-- "examples/java/snippets/src/main/java/artifacts/GcsServiceSetup.java:full_code"
        ```

適切な`ArtifactService`実装の選択は、アプリケーションのデータ永続性、スケーラビリティ、および運用環境の要件に依存します。

## ベストプラクティス

アーティファクトを効果的かつ保守可能に使用するために：

*   **適切なサービスを選択する：** 迅速なプロトタイピング、テスト、および永続性が不要なシナリオでは`InMemoryArtifactService`を使用します。データの永続性とスケーラビリティが必要な本番環境では`GcsArtifactService`（または他のバックエンド用に独自の`BaseArtifactService`を実装）を使用します。
*   **意味のあるファイル名を使用する：** 明確で説明的なファイル名を使用します。関連する拡張子（`.pdf`、`.png`、`.wav`）を含めると、人間が内容を理解しやすくなりますが、プログラム的な処理は`mime_type`が決定します。一時的なアーティファクト名と永続的なアーティファクト名の規約を確立します。
*   **正しいMIMEタイプを指定する：** `save_artifact`のために`types.Part`を作成する際は、常に正確な`mime_type`を提供します。これは、後で`load_artifact`するアプリケーションやツールが`bytes`データを正しく解釈するために非常に重要です。可能な場合は標準のIANA MIMEタイプを使用します。
*   **バージョニングを理解する：** 特定の`version`引数なしで`load_artifact()`を呼び出すと、*最新*バージョンが取得されることを覚えておいてください。ロジックがアーティファクトの特定の過去のバージョンに依存する場合は、読み込み時に整数のバージョン番号を必ず提供してください。
*   **名前空間（`user:`）を意図的に使用する：** データが真にユーザーに属し、すべてのセッションでアクセス可能であるべき場合にのみ、ファイル名に`"user:"`プレフィックスを使用します。単一の会話やセッションに固有のデータの場合は、プレフィックスなしの通常のファイル名を使用します。
*   **エラーハンドリング：**
    *   コンテキストメソッド（`save_artifact`, `load_artifact`, `list_artifacts`）を呼び出す前に、`artifact_service`が実際に設定されているかを常に確認します。サービスが`None`の場合、`ValueError`が発生します。
    *   `load_artifact`の戻り値を確認します。アーティファクトやバージョンが存在しない場合、`None`になります。常に`Part`が返されると仮定しないでください。
    *   特に`GcsArtifactService`では、基盤となるストレージサービスからの例外（例：権限問題に対する`google.api_core.exceptions.Forbidden`、バケットが存在しない場合の`NotFound`、ネットワークエラー）を処理する準備をしてください。
*   **サイズの考慮事項：** アーティファクトは一般的なファイルサイズに適していますが、特にクラウドストレージを使用する場合、非常に大きなファイルによる潜在的なコストとパフォーマンスへの影響に注意してください。`InMemoryArtifactService`は、多くの大きなアーティファクトを保存すると、大量のメモリを消費する可能性があります。非常に大きなデータは、バイト配列全体をメモリ内で渡すのではなく、直接GCSリンクや他の専用ストレージソリューションを介して処理する方が良いか評価してください。
*   **クリーンアップ戦略：** `GcsArtifactService`のような永続ストレージでは、アーティファ-   **クリーンアップ戦略：** `GcsArtifactService`のような永続ストレージでは、アーティファクトは明示的に削除されるまで残ります。アーティファクトが一時的なデータを表すか、寿命が限られている場合は、クリーンアップ戦略を実装します。これには以下が含まれる場合があります：
    *   バケットに対するGCSライフサイクルポリシーの使用。
    *   `artifact_service.delete_artifact`メソッドを利用する特定のツールや管理機能の構築（注意：安全のため、deleteはコンテキストオブジェクト経由では公開されていません）。
    *   必要に応じてパターンベースの削除を可能にするために、ファイル名を慎重に管理する。
