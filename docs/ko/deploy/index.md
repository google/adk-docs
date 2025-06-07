# 에이전트 배포하기

ADK를 사용하여 에이전트를 구축하고 테스트한 후, 다음 단계는 프로덕션 환경에서 접근, 쿼리, 사용되거나 다른 애플리케이션과 통합될 수 있도록 배포하는 것입니다. 배포는 에이전트를 로컬 개발 머신에서 확장 가능하고 안정적인 환경으로 이동시킵니다.

<img src="../assets/deploy-agent.png" alt="에이전트 배포하기">

## 배포 옵션

ADK 에이전트는 프로덕션 준비 상태나 사용자 정의 유연성에 대한 필요에 따라 다양한 환경에 배포될 수 있습니다:

### Vertex AI의 Agent Engine

[Agent Engine](agent-engine.md)은 ADK와 같은 프레임워크로 구축된 AI 에이전트를 배포, 관리 및 확장하기 위해 특별히 설계된 Google Cloud의 완전 관리형 자동 확장 서비스입니다.

[Vertex AI Agent Engine에 에이전트 배포에 대해 더 알아보기](agent-engine.md).

### Cloud Run

[Cloud Run](https://cloud.google.com/run)은 에이전트를 컨테이너 기반 애플리케이션으로 실행할 수 있게 해주는 Google Cloud의 관리형 자동 확장 컴퓨팅 플랫폼입니다.

[Cloud Run에 에이전트 배포에 대해 더 알아보기](cloud-run.md).

### Google Kubernetes Engine (GKE)

[Google Kubernetes Engine (GKE)](https://cloud.google.com/kubernetes-engine)은 에이전트를 컨테이너화된 환경에서 실행할 수 있게 해주는 Google Cloud의 관리형 Kubernetes 서비스입니다. GKE는 배포에 대한 더 많은 제어가 필요하거나 오픈 모델을 실행하는 경우 좋은 옵션입니다.

[GKE에 에이전트 배포에 대해 더 알아보기](gke.md).