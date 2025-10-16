# Evaluation Criteria

This page outlines the evaluation criteria provided by ADK to assess agent
performance, including tool use trajectory, response quality, and safety.

Criterion                                | Description                                               | Reference-Based | Requires Rubrics | LLM-as-a-Judge
:--------------------------------------- | :-------------------------------------------------------- | :-------------- | :--------------- | :-------------
`tool_trajectory_avg_score`              | Exact match of tool call trajectory                       | Yes             | No               | No
`response_match_score`                   | ROUGE-1 similarity to reference response                  | Yes             | No               | No
`final_response_match_v2`                | LLM-judged semantic match to reference response           | Yes             | No               | Yes
`rubric_based_final_response_quality_v1` | LLM-judged final response quality based on custom rubrics | No              | Yes              | Yes
`rubric_based_tool_use_quality_v1`       | LLM-judged tool usage quality based on custom rubrics     | No              | Yes              | Yes
`hallucinations_v1`                      | LLM-judged groundedness of agent response against context | No              | No               | Yes
`safety_v1`                              | Safety/harmlessness of agent response                     | No              | No               | Yes

## tool_trajectory_avg_score

This criterion compares the sequence of tools called by the agent against a list
of expected calls and computes an average score based on exact match.

### When To Use This Criterion?

This criterion is ideal for scenarios where the correctness of an agent's
behavior is strictly dependent on following a precise sequence of tool calls
with exact arguments. Use it when you need to enforce a specific tool execution
path and consider any deviation—whether in tool name, arguments, or order—as a
failure. It is particularly valuable for:

*   **Regression testing:** Ensuring that agent updates do not unintentionally
    alter tool call behavior for established test cases.
*   **Workflow validation:** Verifying that agents correctly follow predefined
    workflows that require specific API calls in a specific order.
*   **High-precision tasks:** Evaluating tasks where slight deviations in tool
    parameters or call order can lead to significantly different or incorrect
    outcomes.

### Details

For each invocation that is being evaluated, this criterion compares the list
and order of tool calls produced by the agent against the list of expected tool
calls. The comparison is done by performing an exact match on the tool name and
tool arguments for each tool call in the list. If all tool calls in an
invocation match exactly in content and order, a score of 1.0 is awarded for
that invocation, otherwise the score is 0.0. The final value is the average of
these scores across all invocations in the eval case.

### How To Use This Criterion?

You can specify a threshold for this criterion in `EvalConfig` under the
`criteria` dictionary. The value should be a float between 0.0 and 1.0, which
represents the minimum acceptable score for the eval case to pass. If you expect
tool trajectories to match exactly in all invocations, you should set the
threshold to 1.0.

Example `EvalConfig` entry:

```json
{
  "criteria": {
    "tool_trajectory_avg_score": 1.0
  }
}
```

### Output And How To Interpret

The output is a score between 0.0 and 1.0, where 1.0 indicates a perfect match
between actual and expected tool trajectories for all invocations, and 0.0
indicates a complete mismatch for all invocations. Higher scores are better. A
score below 1.0 means that for at least one invocation, the agent's tool call
trajectory deviated from the expected one.

## response_match_score

This criterion evaluates if agent's final response matches a golden/expected
final response using Rouge-1.

### When To Use This Criterion?

Use this criterion when you need a quantitative measure of how closely the
agent's output matches the expected output in terms of content overlap.

### Details

ROUGE-1 specifically measures the overlap of unigrams (single words) between the
system-generated text (candidate summary) and the a reference text. It
essentially checks how many individual words from the reference text are present
in the candidate text. To learn more, see details on
[ROUGE-1](https://github.com/google-research/google-research/tree/master/rouge).

### How To Use This Criterion?

You can specify a threshold for this criterion in `EvalConfig` under the
`criteria` dictionary. The value should be a float between 0.0 and 1.0, which
represents the minimum acceptable score for the eval case to pass.

Example `EvalConfig` entry:

```json
{
  "criteria": {
    "response_match_score": 0.8
  }
}
```

### Output And How To Interpret

Value range for this criterion is [0,1], with values closer to 1 more desirable.

## final_response_match_v2

This criterion evaluates if the agent's final response matches a golden/expected
final response using LLM as a judge.

### When To Use This Criterion?

Use this criterion when you need to evaluate the correctness of an agent's final
response against a reference, but require flexibility in how the answer is
presented. It is suitable for cases where different phrasings or formats are
acceptable, as long as the core meaning and information match the reference.
This criterion is a good choice for evaluating question-answering,
summarization, or other generative tasks where semantic equivalence is more
important than exact lexical overlap, making it a more sophisticated alternative
to `response_match_score`.

### Details

This criterion uses a Large Language Model (LLM) as a judge to determine if the
agent's final response is semantically equivalent to the provided reference
response. It is designed to be more flexible than lexical matching metrics (like
`response_match_score`), as it focuses on whether the agent's response contains
the correct information, while tolerating differences in formatting, phrasing,
or the inclusion of additional correct details.

For each invocation, the criterion prompts a judge LLM to rate the agent's
response as "valid" or "invalid" compared to the reference. This is repeated
multiple times for robustness (configurable via `num_samples`), and a majority
vote determines if the invocation receives a score of 1.0 (valid) or 0.0
(invalid). The final criterion score is the fraction of invocations deemed valid
across the entire eval case.

### How To Use This Criterion?

This criterion uses `LlmAsAJudgeCriterion`, allowing you to configure the
evaluation threshold, the judge model, and the number of samples per invocation.

Example `EvalConfig` entry:

```json
{
  "criteria": {
    "final_response_match_v2": {
      "threshold": 0.8,
      "judge_model_options": {
            "judge_model": "gemini-2.5-flash",
            "num_samples": 5
          }
        }
    }
  }
}
```

### Output And How To Interpret

The criterion returns a score between 0.0 and 1.0. A score of 1.0 means the LLM
judge considered the agent's final response to be valid for all invocations,
while a score closer to 0.0 indicates that many responses were judged as invalid
when compared to the reference responses. Higher values are better.

## rubric_based_final_response_quality_v1

This criterion assesses the quality of an agent's final response against a
user-defined set of rubrics using LLM as a judge.

### When To Use This Criterion?

Use this criterion when you need to evaluate aspects of response quality that go
beyond simple correctness or semantic equivalence with a reference. It is ideal
for assessing nuanced attributes like tone, style, helpfulness, or adherence to
specific conversational guidelines defined in your rubrics. This criterion is
particularly useful when no single reference response exists, or when quality
depends on multiple subjective factors.

### Details

This criterion provides a flexible way to evaluate response quality based on
specific criteria that you define as rubrics. For example, you could define
rubrics to check if a response is concise, if it correctly infers user intent,
or if it avoids jargon.

The criterion uses an LLM-as-a-judge to evaluate the agent's final response
against each rubric, producing a `yes` (1.0) or `no` (0.0) verdict for each.
Like other LLM-based metrics, it samples the judge model multiple times per
invocation and uses a majority vote to determine the score for each rubric in
that invocation. The overall score for an invocation is the average of its
rubric scores. The final criterion score for the eval case is the average of
these overall scores across all invocations.

### How To Use This Criterion?

This criterion uses `RubricsBasedCriterion`, which requires a list of rubrics to
be provided in the `EvalConfig`. Each rubric should be defined with a unique ID
and its content.

Example `EvalConfig` entry:

```json
{
  "criteria": {
    "rubric_based_final_response_quality_v1": {
      "threshold": 0.8,
      "judge_model_options": {
        "judge_model": "gemini-2.5-flash",
        "num_samples": 5
      },
      "rubrics": [
        {
          "rubric_id": "conciseness",
          "rubric_content": {
            "text_property": "The agent's response is direct and to the point."
          }
        },
        {
          "rubric_id": "intent_inference",
          "rubric_content": {
            "text_property": "The agent's response accurately infers the user's underlying goal from ambiguous queries."
          }
        }
      ]
    }
  }
}
```

### Output And How To Interpret

The criterion outputs an overall score between 0.0 and 1.0, where 1.0 indicates
that the agent's responses satisfied all rubrics across all invocations, and 0.0
indicates that no rubrics were satisfied. The results also include detailed
per-rubric scores for each invocation. Higher values are better.

## rubric_based_tool_use_quality_v1

This criterion assesses the quality of an agent's tool usage against a
user-defined set of rubrics using LLM as a judge.

### When To Use This Criterion?

Use this criterion when you need to evaluate *how* an agent uses tools, rather
than just *if* the final response is correct. It is ideal for assessing whether
the agent selected the right tool, used the correct parameters, or followed a
specific sequence of tool calls. This is useful for validating agent reasoning
processes, debugging tool-use errors, and ensuring adherence to prescribed
workflows, especially in cases where multiple tool-use paths could lead to a
similar final answer but only one path is considered correct.

### Details

This criterion provides a flexible way to evaluate tool usage based on specific
rules that you define as rubrics. For example, you could define rubrics to check
if a specific tool was called, if its parameters were correct, or if tools were
called in a particular order.

The criterion uses an LLM-as-a-judge to evaluate the agent's tool calls and
responses against each rubric, producing a `yes` (1.0) or `no` (0.0) verdict for
each. Like other LLM-based metrics, it samples the judge model multiple times
per invocation and uses a majority vote to determine the score for each rubric
in that invocation. The overall score for an invocation is the average of its
rubric scores. The final criterion score for the eval case is the average of
these overall scores across all invocations.

### How To Use This Criterion?

This criterion uses `RubricsBasedCriterion`, which requires a list of rubrics to
be provided in the `EvalConfig`. Each rubric should be defined with a unique ID
and its content, describing a specific aspect of tool use to evaluate.

Example `EvalConfig` entry:

```json
{
  "criteria": {
    "rubric_based_tool_use_quality_v1": {
      "threshold": 1.0,
      "judge_model_options": {
        "judge_model": "gemini-2.5-flash",
        "num_samples": 5
      },
      "rubrics": [
        {
          "rubric_id": "geocoding_called",
          "rubric_content": {
            "text_property": "The agent calls the GeoCoding tool before calling the GetWeather tool."
          }
        },
        {
          "rubric_id": "getweather_called",
          "rubric_content": {
            "text_property": "The agent calls the GetWeather tool with coordinates derived from the user's location."
          }
        }
      ]
    }
  }
}
```

### Output And How To Interpret

The criterion outputs an overall score between 0.0 and 1.0, where 1.0 indicates
that the agent's tool usage satisfied all rubrics across all invocations, and
0.0 indicates that no rubrics were satisfied. The results also include detailed
per-rubric scores for each invocation. Higher values are better.

## hallucinations_v1

This criterion assesses whether a model response contains any false,
contradictory, or unsupported claims.

### When To Use This Criterion?

Use this criterion to ensure the agent's response is grounded in the provided
context (e.g., tool outputs, user query, instructions) and does not contain
hallucinations.

### Details

This criterion assesses whether a model response contains any false,
contradictory, or unsupported claims based on context that includes developer
instructions, user prompt, tool definitions, and tool invocations and their
results. It uses LLM-as-a-judge and follows a two-step process:

1.  **Segmenter**: Segments the agent response into individual sentences.
2.  **Sentence Validator**: Evaluates each segmented sentence against the
    provided context for grounding. Each sentence is labeled as `supported`,
    `unsupported`, `contradictory`, `disputed` or `not_applicable`.

The metric computes an Accuracy Score: the percentage of sentences that are
`supported` or `not_applicable`. By default, only the final response is
evaluated. If `evaluate_intermediate_nl_responses` is set to true in the
criterion, intermediate natural language responses from agents are also
evaluated.

### How To Use This Criterion?

This criterion uses `HallucinationsCriterion`, allowing you to configure the
evaluation threshold, the judge model, the number of samples per invocation and
whether to evaluate intermediate natural language responses.

Example `EvalConfig` entry:

```json
{
  "criteria": {
    "hallucinations_v1": {
      "threshold": 0.8,
      "judge_model_options": {
            "judge_model": "gemini-2.5-flash",
          },
      "evaluate_intermediate_nl_responses": true
    }
  }
}

```

### Output And How To Interpret

The criterion returns a score between 0.0 and 1.0. A score of 1.0 means all
sentences in agent's response are grounded in the context, while a score closer
to 0.0 indicates that many sentences are false, contradictory, or unsupported.
Higher values are better.

## safety_v1

This criterion evaluates the safety (harmlessness) of an Agent's Response.

### When To Use This Criterion?

This criterion should be used when you need to ensure that agent responses
comply with safety guidelines and do not produce harmful or inappropriate
content. It is essential for user-facing applications or any system where
response safety is a priority.

### Details

This criterion assesses whether the agent's response contains any harmful
content, such as hate speech, harassment, or dangerous information. Unlike other
metrics implemented natively within ADK, `safety_v1` delegates the evaluation to
the Vertex AI General AI Eval SDK.

### How To Use This Criterion?

Using this criterion requires a Google Cloud Project. You must have
`GOOGLE_CLOUD_PROJECT` and `GOOGLE_CLOUD_LOCATION` environment variables set,
typically in an `.env` file in your agent's directory, for the Vertex AI SDK to
function correctly.

You can specify a threshold for this criterion in `EvalConfig` under the
`criteria` dictionary. The value should be a float between 0.0 and 1.0,
representing the minimum safety score for a response to be considered passing.

Example `EvalConfig` entry:

```json
{
  "criteria": {
    "safety_v1": 0.8
  }
}
```

### Output And How To Interpret

The criterion returns a score between 0.0 and 1.0. Scores closer to 1.0 indicate
that the response is safe, while scores closer to 0.0 indicate potential safety
issues.