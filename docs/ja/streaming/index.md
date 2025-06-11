# ADKにおける双方向ストリーミング(live)

!!! info "情報"

    これは実験的な機能です。現在、Pythonで利用可能です。

!!! info "情報"

    これはサーバーサイドストリーミングやトークンレベルのストリーミングとは異なります。このセクションは、双方向ストリーミング(live)に関するものです。
    
ADKの双方向ストリーミング(live)は、[Gemini Live API](https://ai.google.dev/gemini-api/docs/live)が持つ、低遅延な双方向の音声・映像対話機能をAIエージェントに追加します。

双方向ストリーミング(live)モードを使用すると、エンドユーザーに対して、自然で人間のような音声会話体験を提供できます。これには、ユーザーが音声コマンドでエージェントの応答に割り込む機能も含まれます。ストリーミング機能を持つエージェントは、テキスト、オーディオ、ビデオの入力を処理し、テキストとオーディオの出力を提供できます。

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

    このクイックスタートでは、シンプルなエージェントを構築し、ADKのストリーミング機能を用いて、低遅延かつ双方向の音声・映像通信を実装します。

    [:octicons-arrow-right-24: 詳細はこちら](../get-started/streaming/quickstart-streaming.md)

-   :material-console-line: **ストリーミングツール**

    ---

    ストリーミングツールを使用すると、ツール（関数）が中間結果をエージェントにストリーミングで返し、エージェントはその中間結果に応答できます。例えば、ストリーミングツールで株価の変動を監視し、エージェントに反応させることが可能です。また、エージェントにビデオストリームを監視させ、変化があった場合にその内容を報告させることもできます。

    [:octicons-arrow-right-24: 詳細はこちら](streaming-tools.md)

-   :material-console-line: **カスタムオーディオストリーミングアプリのサンプル**

    ---

    この記事では、ADKストリーミングとFastAPIで構築されたカスタム非同期Webアプリのサーバーとクライアントのコードの概要を説明します。サーバー送信イベント（SSE）とWebSocketの両方を使用して、リアルタイムの双方向オーディオ・テキスト通信を可能にします。

    [:octicons-arrow-right-24: 詳細はこちら (SSE)](custom-streaming.md) および
    [:octicons-arrow-right-24: (WebSocket)](custom-streaming-ws.md)

-   :material-console-line: **ブログ記事: Google ADK + Vertex AI Live API**

    ---

    この記事では、ADKの双方向ストリーミング(live)をリアルタイムのオーディオ/ビデオストリーミングに使用する方法を解説します。カスタムの対話型AIエージェントを構築するために、`LiveRequestQueue`を使用したPythonサーバーの例を紹介します。

    [:octicons-arrow-right-24: 詳細はこちら](https://medium.com/google-cloud/google-adk-vertex-ai-live-api-125238982d5e)

-   :material-console-line: **Shopper's Conciergeデモ**

    ---

    ADKのストリーミング機能を使って、個人のスタイルを理解し、パーソナライズされた推薦を行うショッピングコンシェルジュを構築する方法を学びます。

    [:octicons-arrow-right-24: 詳細はこちら](https://youtu.be/LwHPYyw7u6U)

-   :material-console-line: **ストリーミング設定**

    ---

    live(ストリーミング)エージェント向けに設定できる構成オプションがいくつかあります。

    [:octicons-arrow-right-24: 詳細はこちら](configuration.md)
</div>