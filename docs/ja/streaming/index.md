# ADKにおける双方向ストリーミング（ライブ）

!!! info

    これは実験的な機能です。現在、Pythonで利用可能です。

!!! info

    これはサーバーサイドストリーミングやトークンレベルストリーミングとは異なります。このセクションは双方向ストリーミング（ライブ）に関するものです。

ADKにおける双方向ストリーミング（ライブ）は、[Gemini Live API](https://ai.google.dev/gemini-api/docs/live)の低遅延な双方向音声・ビデオ対話機能をAIエージェントに追加します。

双方向ストリーミング（ライブ）モードを使用すると、エンドユーザーに自然で人間らしい音声会話の体験を提供できます。これには、ユーザーが音声コマンドでエージェントの応答を中断する機能も含まれます。ストリーミング対応のエージェントは、テキスト、音声、およびビデオ入力を処理でき、テキストと音声の出力を提供できます。

<div class="video-grid">
  <div class="video-item">
    <div class="video-container">
      <iframe src="https://www.youtube-nocookie.com/embed/Tu7-voU7nnw?si=RKs7EWKjx0bL96i5" title="Shopper's Concierge" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>
    </div>
  </div>

  <div class="video-item">
    <div class="video-container">
      <iframe src="https://www.youtube-nocookie.com/embed/LwHPYyw7u6U?si=xxIEhnKBapzQA6VV" title="Shopper's Concierge" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>
    </div>
  </div>
</div>

<div class="grid cards" markdown>

-   :material-console-line: **クイックスタート（ストリーミング）**

    ---

    このクイックスタートでは、簡単なエージェントを構築し、ADKのストリーミングを使用して低遅延で双方向の音声・ビデオ通信を実装します。

    [:octicons-arrow-right-24: 詳細はこちら](../get-started/streaming/quickstart-streaming.md)

-   :material-console-line: **ストリーミングツール**

    ---

    ストリーミングツールを使用すると、ツール（関数）が中間結果をエージェントにストリーミングで送り返し、エージェントがそれらの中間結果に応答できます。例えば、ストリーミングツールを使用して株価の変動を監視し、エージェントにそれに反応させることができます。別の例として、エージェントにビデオストリームを監視させ、ビデオストリームに変化があった場合にエージェントがその変化を報告させることができます。

    [:octicons-arrow-right-24: 詳細はこちら](streaming-tools.md)

-   :material-console-line: **カスタムオーディオストリーミングアプリのサンプル**

    ---

    この記事では、ADKストリーミングとFastAPIで構築されたカスタム非同期Webアプリのサーバーとクライアントのコードを概観し、サーバー送信イベント（SSE）とWebSocketの両方でリアルタイムの双方向音声・テキスト通信を可能にします。

    [:octicons-arrow-right-24: 詳細はこちら (SSE)](custom-streaming.md)
    [:octicons-arrow-right-24: 詳細はこちら (WebSockets)](custom-streaming-ws.md)

-   :material-console-line: **ショッパーズ・コンシェルジュのデモ**

    ---

    ADKのストリーミングが、個人のスタイルを理解し、カスタマイズされた推薦を提供するパーソナルショッピングコンシェルジュの構築にどのように使用できるかを学びます。

    [:octicons-arrow-right-24: 詳細はこちら](https://youtu.be/LwHPYyw7u6U)

-   :material-console-line: **ストリーミング設定**

    ---

    ライブ（ストリーミング）エージェントには、設定可能な項目がいくつかあります。

    [:octicons-arrow-right-24: 詳細はこちら](configuration.md)
</div>