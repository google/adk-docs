# ADKのインストール

=== "Python"

    ## 仮想環境の作成と有効化
    
    [venv](https://docs.python.org/3/library/venv.html) を使用してPythonの仮想環境を作成することをお勧めします：
    
    ```shell
    python -m venv .venv
    ```
    
    次に、お使いのオペレーティングシステムと環境に応じた適切なコマンドを使用して、仮想環境を有効化します：
    
    ```
    # Mac / Linux
    source .venv/bin/activate
    
    # Windows CMD:
    .venv\Scripts\activate.bat
    
    # Windows PowerShell:
    .venv\Scripts\Activate.ps1
    ```

    ### ADKのインストール
    
    ```bash
    pip install google-adk
    ```
    
    （オプション）インストールの確認：
    
    ```bash
    pip show google-adk
    ```

=== "Java"

    MavenまたはGradleのいずれかを使用して、`google-adk`および`google-adk-dev`パッケージを追加できます。

    `google-adk`はJava ADKのコアライブラリです。Java ADKには、エージェントをシームレスに実行するためのプラグイン可能なサンプルSpringBootサーバーも付属しています。このオプションのパッケージは`google-adk-dev`の一部として提供されています。
    
    Mavenを使用している場合は、`pom.xml`に以下を追加してください：

    ```xml title="pom.xml"
    <dependencies>
      <!-- ADKコアの依存関係 -->
      <dependency>
        <groupId>com.google.adk</groupId>
        <artifactId>google-adk</artifactId>
        <version>0.1.0</version>
      </dependency>
      
      <!-- エージェントをデバッグするためのADK Dev Web UI（オプション） -->
      <dependency>
        <groupId>com.google.adk</groupId>
        <artifactId>google-adk-dev</artifactId>
        <version>0.1.0</version>
      </dependency>
    </dependencies>
    ```

    参考として、[完全なpom.xml](https://github.com/google/adk-docs/tree/main/examples/java/cloud-run/pom.xml)ファイルはこちらです。

    Gradleを使用している場合は、`build.gradle`に依存関係を追加してください：

    ```title="build.gradle"
    dependencies {
        implementation 'com.google.adk:google-adk:0.1.0'
        implementation 'com.google.adk:google-adk-dev:0.1.0'
    }
    ```

## 次のステップ

*   [**クイックスタート**](quickstart.md)で初めてのエージェントを作成してみましょう。