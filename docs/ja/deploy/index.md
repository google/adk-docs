# エージェントのデプロイ

ADKを使用してエージェントを構築・テストしたら、次のステップはそれをデプロイすることです。デプロイすることで、エージェントは本番環境でアクセス、クエリ、使用されたり、他のアプリケーションと統合されたりできるようになります。デプロイによって、エージェントはローカルの開発マシンから、スケーラブルで信頼性の高い環境に移行します。

<img src="../assets/deploy-agent.png" alt="エージェントのデプロイ">

## デプロイオプション

ADKエージェントは、本番環境への対応やカスタムの柔軟性に関するニーズに応じて、さまざまな環境にデプロイできます。

### Vertex AIのAgent Engine

[Agent Engine](agent-engine.md)は、ADKなどのフレームワークで構築されたAIエージェントのデプロイ、管理、スケーリングのために特別に設計された、Google Cloud上のフルマネージド自動スケーリングサービスです。

[Vertex AI Agent Engineへのエージェントのデプロイについて詳しくはこちら](agent-engine.md)。

### Cloud Run

[Cloud Run](https://cloud.google.com/run)は、Google Cloud上のマネージド自動スケーリングコンピューティングプラットフォームで、エージェントをコンテナベースのアプリケーションとして実行できます。

[Cloud Runへのエージェントのデプロイについて詳しくはこちら](cloud-run.md)。

### Google Kubernetes Engine (GKE)

[Google Kubernetes Engine (GKE)](https://cloud.google.com/kubernetes-engine)は、Google CloudのマネージドKubernetesサービスで、コンテナ化された環境でエージェントを実行できます。GKEは、デプロイに対するより多くの制御が必要な場合や、オープンモデルを実行する場合に適したオプションです。

[GKEへのエージェントのデプロイについて詳しくはこちら](gke.md)。