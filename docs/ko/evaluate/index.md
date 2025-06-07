# 에이전트를 평가하는 이유

![python_only](https://img.shields.io/badge/현재_지원되는_언어-Python-blue){ title="이 기능은 현재 Python에서만 사용할 수 있습니다. Java 지원은 계획 중이거나 곧 제공될 예정입니다."}

전통적인 소프트웨어 개발에서 단위 테스트와 통합 테스트는 코드가 예상대로 작동하고 변경 사항에도 안정적으로 유지된다는 확신을 줍니다. 이러한 테스트는 명확한 "통과/실패" 신호를 제공하여 추가 개발을 안내합니다. 그러나 LLM 에이전트는 전통적인 테스트 접근 방식을 불충분하게 만드는 수준의 가변성을 도입합니다.

모델의 확률적 특성으로 인해 결정론적인 "통과/실패" 주장은 종종 에이전트 성능 평가에 부적합합니다. 대신, 최종 출력과 에이전트의 궤적(해결책에 도달하기 위해 취한 단계의 순서) 모두에 대한 정성적 평가가 필요합니다. 이는 에이전트의 결정 품질, 추론 과정 및 최종 결과를 평가하는 것을 포함합니다.

이는 설정하는 데 많은 추가 작업처럼 보일 수 있지만, 평가 자동화에 대한 투자는 빠르게 성과를 거두게 됩니다. 프로토타입을 넘어서고자 한다면, 이는 강력히 권장되는 모범 사례입니다.

![인트로 컴포넌트](../assets/evaluate_agent.png)

## 에이전트 평가 준비

에이전트 평가를 자동화하기 전에 명확한 목표와 성공 기준을 정의하세요:

*   **성공 정의:** 에이전트에게 성공적인 결과는 무엇인가요?
*   **중요 작업 식별:** 에이전트가 반드시 수행해야 하는 필수 작업은 무엇인가요?
*   **관련 지표 선택:** 성능 측정을 위해 어떤 지표를 추적할 것인가요?

이러한 고려 사항은 평가 시나리오 생성을 안내하고 실제 배포에서 에이전트 행동을 효과적으로 모니터링하는 데 도움이 됩니다.

## 무엇을 평가해야 할까요?

개념 증명과 프로덕션 준비가 된 AI 에이전트 사이의 간극을 메우기 위해서는 견고하고 자동화된 평가 프레임워크가 필수적입니다. 주로 최종 출력에 초점을 맞추는 생성 모델 평가와 달리, 에이전트 평가는 의사 결정 과정에 대한 더 깊은 이해를 필요로 합니다. 에이전트 평가는 두 가지 구성 요소로 나눌 수 있습니다:

1.  **궤적 및 도구 사용 평가:** 도구 선택, 전략, 접근 방식의 효율성을 포함하여 에이전트가 해결책에 도달하기 위해 취하는 단계를 분석합니다.
2.  **최종 응답 평가:** 에이전트의 최종 출력의 품질, 관련성 및 정확성을 평가합니다.

궤적은 에이전트가 사용자에게 응답하기 전에 취한 단계의 목록일 뿐입니다. 이를 우리가 에이전트가 취했을 것으로 예상하는 단계 목록과 비교할 수 있습니다.

### 궤적 및 도구 사용 평가

사용자에게 응답하기 전에 에이전트는 일반적으로 일련의 작업을 수행하며, 이를 '궤적'이라고 합니다. 용어를 명확히 하기 위해 사용자 입력을 세션 기록과 비교하거나, 정책 문서를 조회하거나, 지식 기반을 검색하거나, 티켓을 저장하기 위해 API를 호출할 수 있습니다. 이를 '작업의 궤적'이라고 합니다. 에이전트의 성능을 평가하려면 실제 궤적을 예상되는, 또는 이상적인 궤적과 비교해야 합니다. 이 비교는 에이전트 프로세스의 오류와 비효율성을 드러낼 수 있습니다. 예상 궤적은 우리가 에이전트가 취해야 할 것으로 예상하는 단계 목록인 정답을 나타냅니다.

예를 들어:

```py
// 궤적 평가는 다음을 비교합니다
expected_steps = ["determine_intent", "use_tool", "review_results", "report_generation"]
actual_steps = ["determine_intent", "use_tool", "review_results", "report_generation"]
```

몇 가지 정답 기반 궤적 평가가 있습니다:

1.  **정확한 일치:** 이상적인 궤적과 완벽하게 일치해야 합니다.
2.  **순서대로 일치:** 올바른 순서로 올바른 작업이 필요하며, 추가 작업은 허용됩니다.
3.  **순서 무관 일치:** 순서에 상관없이 올바른 작업이 필요하며, 추가 작업은 허용됩니다.
4.  **정밀도:** 예측된 작업의 관련성/정확성을 측정합니다.
5.  **재현율:** 예측에서 필수적인 작업이 얼마나 많이 캡처되었는지 측정합니다.
6.  **단일 도구 사용:** 특정 작업의 포함 여부를 확인합니다.

올바른 평가 지표를 선택하는 것은 에이전트의 특정 요구 사항과 목표에 따라 다릅니다. 예를 들어, 위험도가 높은 시나리오에서는 정확한 일치가 중요할 수 있지만, 더 유연한 상황에서는 순서대로 또는 순서 무관 일치로 충분할 수 있습니다.

## ADK에서 평가는 어떻게 작동하나요?

ADK는 미리 정의된 데이터 세트 및 평가 기준에 대해 에이전트 성능을 평가하는 두 가지 방법을 제공합니다. 개념적으로 유사하지만, 처리할 수 있는 데이터 양에서 차이가 나며, 이는 일반적으로 각각의 적절한 사용 사례를 결정합니다.

### 첫 번째 접근 방식: 테스트 파일 사용

이 접근 방식은 각각 단일하고 간단한 에이전트-모델 상호 작용(세션)을 나타내는 개별 테스트 파일을 만드는 것을 포함합니다. 활발한 에이전트 개발 중에 가장 효과적이며, 단위 테스트의 한 형태로 사용됩니다. 이러한 테스트는 빠른 실행을 위해 설계되었으며 간단한 세션 복잡성에 초점을 맞춰야 합니다. 각 테스트 파일에는 하나의 세션이 포함되며, 이는 여러 턴으로 구성될 수 있습니다. 턴은 사용자와 에이전트 간의 단일 상호 작용을 나타냅니다. 각 턴에는 다음이 포함됩니다

-   `사용자 콘텐츠`: 사용자가 발행한 쿼리입니다.
-   `예상 중간 도구 사용 궤적`: 에이전트가 사용자 쿼리에 올바르게 응답하기 위해 수행할 것으로 예상되는 도구 호출입니다.
-   `예상 중간 에이전트 응답`: 에이전트(또는 하위 에이전트)가 최종 답변을 생성하기 위해 이동하면서 생성하는 자연어 응답입니다. 이러한 자연어 응답은 일반적으로 루트 에이전트가 목표를 달성하기 위해 하위 에이전트에 의존하는 다중 에이전트 시스템의 산물입니다. 이러한 중간 응답은 최종 사용자에게는 중요하지 않을 수 있지만, 시스템 개발자/소유자에게는 에이전트가 최종 응답을 생성하기 위해 올바른 경로를 거쳤다는 확신을 주기 때문에 매우 중요합니다.
-   `최종 응답`: 에이전트의 예상 최종 응답입니다.

파일에 `evaluation.test.json`과 같은 이름을 지정할 수 있습니다. 프레임워크는 `.test.json` 접미사만 확인하며, 파일 이름의 앞부분은 제한되지 않습니다. 다음은 몇 가지 예제가 포함된 테스트 파일입니다:

참고: 테스트 파일은 이제 공식 Pydantic 데이터 모델에 의해 지원됩니다. 두 가지 주요 스키마 파일은 [Eval Set](https://github.com/google/adk-python/blob/main/src/google/adk/evaluation/eval_set.py)와 [Eval Case](https://github.com/google/adk-python/blob/main/src/google/adk/evaluation/eval_case.py)입니다.

```json
# 이 문서를 읽기 쉽게 하기 위해 일부 필드가 제거되었습니다.
{
  "eval_set_id": "home_automation_agent_light_on_off_set",
  "name": "",
  "description": "이것은 에이전트의 `x` 동작을 단위 테스트하는 데 사용되는 평가 세트입니다.",
  "eval_cases": [
    {
      "eval_id": "eval_case_id",
      "conversation": [
        {
          "invocation_id": "b7982664-0ab6-47cc-ab13-326656afdf75", # 호출에 대한 고유 식별자.
          "user_content": { # 이 호출에서 사용자가 제공한 콘텐츠. 이것이 쿼리입니다.
            "parts": [
              {
                "text": "침실의 device_2를 끄세요."
              }
            ],
            "role": "user"
          },
          "final_response": { # 벤치마크의 참조 역할을 하는 에이전트의 최종 응답.
            "parts": [
              {
                "text": "device_2의 상태를 off로 설정했습니다."
              }
            ],
            "role": "model"
          },
          "intermediate_data": {
            "tool_uses": [ # 시간순으로 정렬된 도구 사용 궤적.
              {
                "args": {
                  "location": "Bedroom",
                  "device_id": "device_2",
                  "status": "OFF"
                },
                "name": "set_device_info"
              }
            ],
            "intermediate_responses": [] # 모든 중간 하위 에이전트 응답.
          },
        }
      ],
      "session_input": { # 초기 세션 입력.
        "app_name": "home_automation_agent",
        "user_id": "test_user",
        "state": {}
      },
    }
  ],
}
```

테스트 파일은 폴더로 구성할 수 있습니다. 선택적으로 폴더에는 평가 기준을 지정하는 `test_config.json` 파일을 포함할 수도 있습니다.

#### Pydantic 스키마로 지원되지 않는 테스트 파일을 마이그레이션하는 방법은 무엇인가요?

참고: 테스트 파일이 [EvalSet](https://github.com/google/adk-python/blob/main/src/google/adk/evaluation/eval_set.py) 스키마 파일을 준수하지 않는 경우 이 섹션이 관련 있습니다.

기존 `*.test.json` 파일을 Pydantic 지원 스키마로 마이그레이션하려면 `AgentEvaluator.migrate_eval_data_to_new_schema`를 사용하세요.

이 유틸리티는 현재 테스트 데이터 파일과 선택적 초기 세션 파일을 가져와 새 형식으로 직렬화된 데이터가 포함된 단일 출력 json 파일을 생성합니다. 새 스키마가 더 응집력이 있으므로 이전 테스트 데이터 파일과 초기 세션 파일은 모두 무시하거나 제거할 수 있습니다.

### 두 번째 접근 방식: Evalset 파일 사용

evalset 접근 방식은 에이전트-모델 상호 작용을 평가하기 위해 "evalset"이라는 전용 데이터 세트를 활용합니다. 테스트 파일과 유사하게 evalset에는 예제 상호 작용이 포함되어 있습니다. 그러나 evalset은 여러 개의 잠재적으로 긴 세션을 포함할 수 있으므로 복잡한 다중 턴 대화를 시뮬레이션하는 데 이상적입니다. 복잡한 세션을 나타낼 수 있는 능력으로 인해 evalset은 통합 테스트에 매우 적합합니다. 이러한 테스트는 더 광범위한 특성으로 인해 일반적으로 단위 테스트보다 덜 자주 실행됩니다.

evalset 파일에는 각각 고유한 세션을 나타내는 여러 "eval"이 포함되어 있습니다. 각 eval은 사용자 쿼리, 예상 도구 사용, 예상 중간 에이전트 응답 및 참조 응답을 포함하는 하나 이상의 "턴"으로 구성됩니다. 이러한 필드는 테스트 파일 접근 방식과 동일한 의미를 갖습니다. 각 eval은 고유한 이름으로 식별됩니다. 또한 각 eval에는 관련 초기 세션 상태가 포함됩니다.

evalset을 수동으로 만드는 것은 복잡할 수 있으므로 관련 세션을 캡처하고 evalset 내에서 eval로 쉽게 변환하는 데 도움이 되는 UI 도구가 제공됩니다. 아래에서 평가를 위해 웹 UI를 사용하는 방법에 대해 자세히 알아보세요. 다음은 두 개의 세션을 포함하는 예제 evalset입니다.

참고: eval set 파일은 이제 공식 Pydantic 데이터 모델에 의해 지원됩니다. 두 가지 주요 스키마 파일은 [Eval Set](https://github.com/google/adk-python/blob/main/src/google/adk/evaluation/eval_set.py)와 [Eval Case](https://github.com/google/adk-python/blob/main/src/google/adk/evaluation/eval_case.py)입니다.

```json
# 이 문서를 읽기 쉽게 하기 위해 일부 필드가 제거되었습니다.
{
  "eval_set_id": "eval_set_example_with_multiple_sessions",
  "name": "여러 세션을 포함하는 평가 세트",
  "description": "이 평가 세트는 평가 세트에 두 개 이상의 세션이 포함될 수 있음을 보여주는 예제입니다.",
  "eval_cases": [
    {
      "eval_id": "session_01",
      "conversation": [
        {
          "invocation_id": "e-0067f6c4-ac27-4f24-81d7-3ab994c28768",
          "user_content": {
            "parts": [
              {
                "text": "무엇을 할 수 있나요?"
              }
            ],
            "role": "user"
          },
          "final_response": {
            "parts": [
              {

                "text": "다른 크기의 주사위를 굴리고 숫자가 소수인지 확인할 수 있습니다."
              }
            ],
            "role": null
          },
          "intermediate_data": {
            "tool_uses": [],
            "intermediate_responses": []
          },
        },
      ],
      "session_input": {
        "app_name": "hello_world",
        "user_id": "user",
        "state": {}
      },
    },
    {
      "eval_id": "session_02",
      "conversation": [
        {
          "invocation_id": "e-92d34c6d-0a1b-452a-ba90-33af2838647a",
          "user_content": {
            "parts": [
              {
                "text": "19면체 주사위를 굴리세요"
              }
            ],
            "role": "user"
          },
          "final_response": {
            "parts": [
              {
                "text": "17이 나왔습니다."
              }
            ],
            "role": null
          },
          "intermediate_data": {
            "tool_uses": [],
            "intermediate_responses": []
          },
        },
        {
          "invocation_id": "e-bf8549a1-2a61-4ecc-a4ee-4efbbf25a8ea",
          "user_content": {
            "parts": [
              {
                "text": "10면체 주사위를 두 번 굴린 다음 9가 소수인지 확인하세요"
              }
            ],
            "role": "user"
          },
          "final_response": {
            "parts": [
              {
                "text": "주사위 굴리기에서 4와 7이 나왔고, 9는 소수가 아닙니다.\n"
              }
            ],
            "role": null
          },
          "intermediate_data": {
            "tool_uses": [
              {
                "id": "adk-1a3f5a01-1782-4530-949f-07cf53fc6f05",
                "args": {
                  "sides": 10
                },
                "name": "roll_die"
              },
              {
                "id": "adk-52fc3269-caaf-41c3-833d-511e454c7058",
                "args": {
                  "sides": 10
                },
                "name": "roll_die"
              },
              {
                "id": "adk-5274768e-9ec5-4915-b6cf-f5d7f0387056",
                "args": {
                  "nums": [
                    9
                  ]
                },
                "name": "check_prime"
              }
            ],
            "intermediate_responses": [
              [
                "data_processing_agent",
                [
                  {
                    "text": "10면체 주사위를 두 번 굴렸습니다. 첫 번째 굴리기는 5이고 두 번째 굴리기는 3입니다.\n"
                  }
                ]
              ]
            ]
          },
        }
      ],
      "session_input": {
        "app_name": "hello_world",
        "user_id": "user",
        "state": {}
      },
    }
  ],
}
```

#### Pydantic 스키마로 지원되지 않는 eval set 파일을 마이그레이션하는 방법은 무엇인가요?

참고: eval set 파일이 [EvalSet](https://github.com/google/adk-python/blob/main/src/google/adk/evaluation/eval_set.py) 스키마 파일을 준수하지 않는 경우 이 섹션이 관련 있습니다.

eval set 데이터를 누가 유지 관리하는지에 따라 두 가지 경로가 있습니다:

1.  **ADK UI에서 유지 관리되는 Eval set 데이터** ADK UI를 사용하여 Eval set 데이터를 유지 관리하는 경우 *아무 조치도 필요하지 않습니다*.

2.  **수동으로 개발 및 유지 관리되고 ADK eval Cli에서 사용되는 Eval set 데이터** 마이그레이션 도구가 개발 중이며, 그때까지 ADK eval cli 명령은 이전 형식의 데이터를 계속 지원합니다.

### 평가 기준

평가 기준은 evalset에 대해 에이전트의 성능이 어떻게 측정되는지를 정의합니다. 다음 지표가 지원됩니다:

*   `tool_trajectory_avg_score`: 이 지표는 평가 중 에이전트의 실제 도구 사용을 `expected_tool_use` 필드에 정의된 예상 도구 사용과 비교합니다. 각 일치하는 도구 사용 단계는 1점을 받고, 불일치는 0점을 받습니다. 최종 점수는 이러한 일치의 평균이며, 도구 사용 궤적의 정확도를 나타냅니다.
*   `response_match_score`: 이 지표는 에이전트의 최종 자연어 응답을 `reference` 필드에 저장된 예상 최종 응답과 비교합니다. 두 응답 간의 유사성을 계산하기 위해 [ROUGE](https://en.wikipedia.org/wiki/ROUGE_\(metric\)) 지표를 사용합니다.

평가 기준이 제공되지 않으면 다음 기본 구성이 사용됩니다:

*   `tool_trajectory_avg_score`: 기본값은 1.0이며, 도구 사용 궤적에서 100% 일치가 필요합니다.
*   `response_match_score`: 기본값은 0.8이며, 에이전트의 자연어 응답에서 약간의 오차를 허용합니다.

다음은 사용자 지정 평가 기준을 지정하는 `test_config.json` 파일의 예입니다:

```json
{
  "criteria": {
    "tool_trajectory_avg_score": 1.0,
    "response_match_score": 0.8
  }
}
```

## ADK로 평가를 실행하는 방법

개발자는 ADK를 사용하여 다음 방법으로 에이전트를 평가할 수 있습니다:

1.  **웹 기반 UI (**`adk web`**):** 웹 기반 인터페이스를 통해 대화형으로 에이전트를 평가합니다.
2.  **프로그래밍 방식 (**`pytest`**):** `pytest` 및 테스트 파일을 사용하여 평가를 테스트 파이프라인에 통합합니다.
3.  **명령줄 인터페이스 (**`adk eval`**):** 명령줄에서 직접 기존 평가 세트 파일에 대한 평가를 실행합니다.

### 1. `adk web` - 웹 UI를 통해 평가 실행

웹 UI는 에이전트를 평가하고 평가 데이터 세트를 생성하는 대화형 방법을 제공합니다.

웹 UI를 통해 평가를 실행하는 단계:

1.  `bash adk web samples_for_testing`을 실행하여 웹 서버를 시작합니다.
2.  웹 인터페이스에서:
    *   에이전트(예: `hello_world`)를 선택합니다.
    *   테스트 사례로 저장하려는 세션을 만들기 위해 에이전트와 상호 작용합니다.
    *   인터페이스 오른쪽의 **“평가 탭”**을 클릭합니다.
    *   기존 평가 세트가 있는 경우 해당 세트를 선택하거나 **"새 평가 세트 만들기"** 버튼을 클릭하여 새 세트를 만듭니다. 평가 세트에 문맥에 맞는 이름을 지정합니다. 새로 만든 평가 세트를 선택합니다.
    *   **"현재 세션 추가"**를 클릭하여 현재 세션을 평가 세트 파일에 평가로 저장합니다. 이 평가에 대한 이름을 입력하라는 메시지가 표시됩니다. 다시 문맥에 맞는 이름을 지정합니다.
    *   생성되면 새로 만든 평가는 평가 세트 파일의 사용 가능한 평가 목록에 표시됩니다. 전체를 실행하거나 특정 평가를 선택하여 평가를 실행할 수 있습니다.
    *   각 평가의 상태가 UI에 표시됩니다.

### 2. `pytest` - 프로그래밍 방식으로 테스트 실행

**`pytest`**를 사용하여 통합 테스트의 일부로 테스트 파일을 실행할 수도 있습니다.

#### 예제 명령어

```shell
pytest tests/integration/
```

#### 예제 테스트 코드

다음은 단일 테스트 파일을 실행하는 `pytest` 테스트 사례의 예입니다:

```py
from google.adk.evaluation.agent_evaluator import AgentEvaluator

def test_with_single_test_file():
    """세션 파일을 통해 에이전트의 기본 능력을 테스트합니다."""
    AgentEvaluator.evaluate(
        agent_module="home_automation_agent",
        eval_dataset_file_path_or_dir="tests/integration/fixture/home_automation_agent/simple_test.test.json",
    )
```

이 접근 방식을 사용하면 에이전트 평가를 CI/CD 파이프라인이나 더 큰 테스트 스위트에 통합할 수 있습니다. 테스트에 대한 초기 세션 상태를 지정하려면 세션 세부 정보를 파일에 저장하고 해당 파일을 `AgentEvaluator.evaluate` 메서드에 전달하면 됩니다.

### 3. `adk eval` - cli를 통해 평가 실행

명령줄 인터페이스(CLI)를 통해 eval set 파일의 평가를 실행할 수도 있습니다. 이것은 UI에서 실행되는 것과 동일한 평가를 실행하지만 자동화에 도움이 됩니다. 즉, 이 명령을 정기적인 빌드 생성 및 검증 프로세스의 일부로 추가할 수 있습니다.

명령어는 다음과 같습니다:

```shell
adk eval \
    <AGENT_MODULE_FILE_PATH> \
    <EVAL_SET_FILE_PATH> \
    [--config_file_path=<PATH_TO_TEST_JSON_CONFIG_FILE>] \
    [--print_detailed_results]
```

예를 들어:

```shell
adk eval \
    samples_for_testing/hello_world \
    samples_for_testing/hello_world/hello_world_eval_set_001.evalset.json
```

각 명령줄 인수에 대한 세부 정보는 다음과 같습니다:

*   `AGENT_MODULE_FILE_PATH`: "agent"라는 이름의 모듈을 포함하는 `__init__.py` 파일의 경로입니다. "agent" 모듈에는 `root_agent`가 포함되어 있습니다.
*   `EVAL_SET_FILE_PATH`: 평가 파일의 경로입니다. 하나 이상의 eval set 파일 경로를 지정할 수 있습니다. 각 파일에 대해 기본적으로 모든 eval이 실행됩니다. eval set에서 특정 eval만 실행하려면 먼저 쉼표로 구분된 eval 이름 목록을 만든 다음, 콜론 `:`으로 구분하여 eval set 파일 이름에 접미사로 추가합니다.
*   예: `sample_eval_set_file.json:eval_1,eval_2,eval_3`
  `이것은 sample_eval_set_file.json에서 eval_1, eval_2, eval_3만 실행합니다`
*   `CONFIG_FILE_PATH`: 구성 파일의 경로입니다.
*   `PRINT_DETAILED_RESULTS`: 콘솔에 자세한 결과를 출력합니다.