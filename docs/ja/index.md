---
hide:
  - toc
---

!!! tip "Google I/O'25 - ADK アップデート"

    ビッグニュース！

    - **[Java ADK v0.1.0](https://github.com/google/adk-java/)** をご紹介します。これにより、エージェントの機能がJavaエコシステムに拡張されます。

    - **[Python ADK](https://github.com/google/adk-python/)** が正式にv1.0.0となり、本番環境に対応したエージェントのための安定性を提供します。

<div style="text-align: center;">
  <div class="centered-logo-text-group">
    <img src="assets/agent-development-kit.png" alt="Agent Development Kit ロゴ" width="100">
    <h1>Agent Development Kit</h1>
  </div>
</div>

## Agent Development Kitとは？

Agent Development Kit (ADK)は、**AIエージェントを開発・デプロイ**するための、柔軟でモジュール式のフレームワークです。ADKは、GeminiとGoogleエコシステムに最適化されていますが、**モデルに依存せず**、**デプロイ環境に依存せず**、**他のフレームワークとの互換性**を持つように構築されています。ADKは、エージェント開発をソフトウェア開発のようにより身近なものに感じられるように設計されており、開発者が単純なタスクから複雑なワークフローに至るまで、エージェントのアーキテクチャを容易に作成、デプロイ、オーケストレーションできるようにします。

<div id="centered-install-tabs" class="install-command-container" markdown="1">

<p class="get-started-text" style="text-align: center;">利用開始：</p>

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
  <a href="get-started/quickstart/" class="md-button" style="margin:3px">クイックスタート</a>
  <a href="tutorials/" class="md-button" style="margin:3px">チュートリアル</a>
  <a href="http://github.com/google/adk-samples" class="md-button" target="_blank" style="margin:3px">サンプルエージェント</a>
  <a href="api-reference/" class="md-button" style="margin:3px">APIリファレンス</a>
  <a href="contributing-guide/" class="md-button" style="margin:3px">貢献する ❤️</a>
</p>

---

## さらに詳しく

[:fontawesome-brands-youtube:{.youtube-red-icon} "Agent Development Kitの紹介"を視聴する！](https://www.youtube.com/watch?v=zgrOwow_uTQ target="_blank" rel="noopener noreferrer")

<div class="grid cards" markdown>

-   :material-transit-connection-variant: **柔軟なオーケストレーション**

    ---

    ワークフローエージェント（`Sequential`、`Parallel`、`Loop`）を使用して予測可能なパイプラインを定義するか、LLM駆動の動的ルーティング（`LlmAgent`転送）を活用して適応的な振る舞いを実現します。

    [**エージェントについて学ぶ**](agents/index.md)

-   :material-graph: **マルチエージェントアーキテクチャ**

    ---

    複数の特化したエージェントを階層的に構成することで、モジュール式でスケーラブルなアプリケーションを構築します。複雑な協調と委任を可能にします。

    [**マルチエージェントシステムを探る**](agents/multi-agents.md)

-   :material-toolbox-outline: **豊富なツールエコシステム**

    ---

    エージェントに多様な機能を持たせます。事前構築済みツール（検索、コード実行）の使用、カスタム関数の作成、サードパーティライブラリ（LangChain, CrewAI）の統合、あるいは他のエージェントをツールとして使用することも可能です。

    [**ツールを見る**](tools/index.md)

-   :material-rocket-launch-outline: **デプロイ対応**

    ---

    エージェントをコンテナ化し、どこにでもデプロイできます。ローカルで実行したり、Vertex AI Agent Engineでスケールさせたり、Cloud RunやDockerを使用してカスタムインフラに統合したりできます。

    [**エージェントをデプロイする**](deploy/index.md)

-   :material-clipboard-check-outline: **組み込みの評価機能**

    ---

    最終的なレスポンスの品質と、事前に定義されたテストケースに対するステップバイステップの実行軌跡の両方を評価することで、エージェントのパフォーマンスを体系的に評価します。

    [**エージェントを評価する**](evaluate/index.md)

-   :material-console-line: **安全でセキュアなエージェントの構築**

    ---

    エージェントの設計にセキュリティと安全性のパターンやベストプラクティスを実装することで、強力で信頼性の高いエージェントを構築する方法を学びます。

    [**安全性とセキュリティ**](safety/index.md)

</div> 