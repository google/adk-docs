---
catalog_title: TypeSafe
catalog_description: Classify inputs and route workflows with calibrated decision models
catalog_icon: /integrations/assets/adk.png
catalog_tags: ["connectors"]
---

# TypeSafe classifier for ADK

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python v2.13.0</span><span class="lst-go">Go v2.7.0</span><span class="lst-preview">Experimental</span>
</div>

The TypeSafe classifier connects Agent Development Kit (ADK) agents to
TypeSafe's Jev decision models. A Jev
model answers typed questions about an input, such as "Which team should handle
this ticket?", and returns a calibrated probability for each possible answer.
Jev computes the answer in a single forward pass instead of generating text.

The classifier implements the ADK classifier interface, so you can call it
directly or use it in a classifier node to route a graph workflow.

!!! example "Experimental"
    The TypeSafe classifier is an experimental release. It may have limitations
    and is not recommended for production use. Its interface, and the ADK
    classifier interface it implements, may change between releases.

## Use cases

-   **Triage:** Send a support ticket to the billing or technical team.
-   **Gating:** Check whether a request describes an outage before you page an
    on-call engineer.
-   **Rating:** Place a message on an ordered scale, such as urgency from low to
    high.

## Prerequisites

-   A TypeSafe API key, stored in the `TYPESAFE_API_KEY` environment variable:

    ```bash
    export TYPESAFE_API_KEY="YOUR_TYPESAFE_API_KEY"
    ```

-   ADK Python v2.13.0 or later, or ADK Go v2.7.0 or later. The classifier is
    part of the core ADK package in both languages, so you don't need to install
    anything else.

## Classify an input

The following example asks one `Choice` question about a support ticket and
reads the chosen label and the probability of each label:

=== "Python"

    ```python
    import asyncio

    from google.adk.integrations.typesafe import TypesafeClassifier
    from google.adk.labs.classifiers import Choice

    classifier = TypesafeClassifier()  # Reads TYPESAFE_API_KEY.

    async def main():
        response = await classifier.classify(
            input="My invoice was charged twice.",
            questions={
                "department": Choice(
                    instructions="Which team should handle this support ticket?",
                    criteria={
                        "billing": "Invoices, refunds, or subscription charges",
                        "technical": "Bugs, errors, outages, or API problems",
                    },
                ),
            },
        )
        answer = response.answers["department"]
        print(answer.choice)         # billing
        print(answer.probabilities)  # {'billing': 0.97, 'technical': 0.03}

    asyncio.run(main())
    ```

=== "Go"

    ```go
    import (
        "context"
        "fmt"

        "google.golang.org/adk/v2/exp/classifier"
        "google.golang.org/adk/v2/exp/classifier/typesafe"
    )

    func classifyTicket(ctx context.Context) error {
        // Classify reads TYPESAFE_API_KEY on each call.
        clf, err := typesafe.New(typesafe.Config{})
        if err != nil {
            return err
        }

        resp, err := clf.Classify(ctx, "My invoice was charged twice.",
            map[string]classifier.Question{
                "department": classifier.Choice{
                    Instructions: "Which team should handle this support ticket?",
                    Criteria: map[string]any{
                        "billing":   "Invoices, refunds, or subscription charges",
                        "technical": "Bugs, errors, outages, or API problems",
                    },
                },
            })
        if err != nil {
            return err
        }

        answer := resp.Answers["department"].(classifier.ChoiceAnswer)
        fmt.Println(answer.Choice)        // billing
        fmt.Println(answer.Probabilities) // map[billing:0.97 technical:0.03]
        return nil
    }
    ```

The probabilities in the comments are illustrative. The classifier sends every
question in one request and returns one answer per question, under the name you
gave it. To ask several questions about the same input, add them to the same
call instead of making one call per question.

## Use with agent

To branch a [graph workflow](/graphs/routes/) on a classification, pass the
TypeSafe classifier to a classifier node. The node asks one `Choice` or `Binary`
question about its input, and the answer becomes the route: the chosen label
for a `Choice`, or `true` or `false` for a `Binary`. The node outputs its
unchanged input, so the next node receives the same data the classifier saw.

=== "Python"

    ```python
    from google.adk import Workflow
    from google.adk.agents import Agent
    from google.adk.integrations.typesafe import TypesafeClassifier
    from google.adk.labs.classifiers import Choice, ClassifierNode

    triage = ClassifierNode(
        name="triage",
        classifier=TypesafeClassifier(),
        question=Choice(
            instructions="Which team should handle this support ticket?",
            criteria={
                "billing": "Invoices, refunds, or subscription charges",
                "technical": "Bugs, errors, outages, or API problems",
            },
        ),
    )

    billing_agent = Agent(
        model="gemini-flash-latest",
        name="billing_agent",
        instruction="You are a billing specialist.",
    )
    technical_agent = Agent(
        model="gemini-flash-latest",
        name="technical_agent",
        instruction="You are a support engineer.",
    )

    root_agent = Workflow(
        name="triage_workflow",
        edges=[
            ("START", triage),
            (triage, {"billing": billing_agent, "technical": technical_agent}),
        ],
    )
    ```

=== "Go"

    ```go
    import (
        "google.golang.org/adk/v2/agent"
        "google.golang.org/adk/v2/agent/workflowagent"
        "google.golang.org/adk/v2/exp/classifier"
        "google.golang.org/adk/v2/exp/classifier/typesafe"
        "google.golang.org/adk/v2/workflow"
    )

    func newTriageWorkflow() (agent.Agent, error) {
        clf, err := typesafe.New(typesafe.Config{})
        if err != nil {
            return nil, err
        }

        triage, err := classifier.NewNode(classifier.NodeConfig{
            Name:       "triage",
            Classifier: clf,
            Question: classifier.Choice{
                Instructions: "Which team should handle this support ticket?",
                Criteria: map[string]any{
                    "billing":   "Invoices, refunds, or subscription charges",
                    "technical": "Bugs, errors, outages, or API problems",
                },
            },
        })
        if err != nil {
            return nil, err
        }

        billing := workflow.NewFunctionNode("billing",
            func(_ agent.Context, ticket string) (string, error) {
                return "Sent to billing: " + ticket, nil
            }, workflow.NodeConfig{})
        technical := workflow.NewFunctionNode("technical",
            func(_ agent.Context, ticket string) (string, error) {
                return "Sent to engineering: " + ticket, nil
            }, workflow.NodeConfig{})

        return workflowagent.New(workflowagent.Config{
            Name: "triage_workflow",
            Edges: []workflow.Edge{
                {From: workflow.Start, To: triage},
                {From: triage, To: billing, Route: workflow.StringRoute("billing")},
                {From: triage, To: technical, Route: workflow.StringRoute("technical")},
            },
        })
    }
    ```

The labels in `criteria` are also the routes, so each edge after the classifier
node uses one of the labels. When ADK builds the workflow, it checks that every
route is a label in the question and that every label has an edge, unless a
default route or an unrouted edge catches the remaining labels.

For a `Binary` question, set a threshold to control when the node routes to
`true`. The default is 0.5, which routes to the more likely answer. Raise the
threshold when a wrong `true` costs more than a wrong `false`, such as paging an
on-call engineer. The node compares the threshold with the probability of
`true` that the classifier returns. To let later nodes read the probabilities,
set an answer key, and the node stores the full answer in session state under
that key.

=== "Python"

    ```python
    from google.adk.labs.classifiers import Binary, ClassifierNode

    is_urgent = ClassifierNode(
        name="is_urgent",
        classifier=TypesafeClassifier(),
        question=Binary(
            instructions="Does this ticket describe an outage?",
            criteria="The customer cannot use the product in production.",
        ),
        threshold=0.7,
        answer_key="urgency_answer",
    )
    ```

=== "Go"

    ```go
    threshold := 0.7
    isUrgent, err := classifier.NewNode(classifier.NodeConfig{
        Name:       "is_urgent",
        Classifier: clf,
        Question: classifier.Binary{
            Instructions: "Does this ticket describe an outage?",
            Criteria:     "The customer cannot use the product in production.",
        },
        Threshold: &threshold,
        AnswerKey: "urgency_answer",
    })
    ```

## Write questions for TypeSafe

The classifier supports the three ADK question types. Each question type
returns a different kind of answer:

| Question | What it asks | Answer |
| :--- | :--- | :--- |
| `Choice` | Which one of two or more labels applies | The chosen label and the probability of each label |
| `Binary` | Whether a statement is true | The probability that the statement is true |
| `Score` | Where the input falls on an ordered scale, with one description per level starting at level 0 | The expected level and the probability of each level |

A classifier node accepts only `Choice` and `Binary` questions, because a route
must be one of a fixed set of values. To route on a scale, use a `Choice` with
labels for the ranges you care about, such as `low` and `high`.

Follow these guidelines to get useful answers from Jev:

-   **Always set instructions.** Every question sent to TypeSafe needs
    instructions that state what to decide. The classifier rejects a question
    without instructions before it sends the request.
-   **Describe each label.** In a `Choice`, map each label to a description of
    when it applies. A description is optional, but it tells the model where
    the boundary between similar labels lies. In a `Binary`, the criteria
    describe what counts as true, and everything else counts as false.
-   **Include the context the decision needs.** The classifier is stateless and
    does not see the session history. If the decision depends on earlier turns,
    include them in the input, as text or as JSON such as a list of role and
    text objects.

## Configuration

You can configure the model, credentials, endpoint, timeout, and retries. Every
option has a default.

=== "Python"

    Set these options as `TypesafeClassifier` constructor arguments.

    | Option | Type | Default | Description |
    | :--- | :--- | :--- | :--- |
    | `model` | `str` | `"jev-latest"` | The Jev model, such as `"jev-latest"` or a pinned version like `"jev-1.13"`. |
    | `api_key` | `str` | `TYPESAFE_API_KEY` | The TypeSafe API key. |
    | `base_url` | `str` | See description | The API base URL. Defaults to the base URL of `http_client`, then the `TYPESAFE_BASE_URL` environment variable, then `https://api.typesafe.ai`. |
    | `timeout` | `float` | `30.0` | Seconds to wait for each request. With `http_client` set, defaults to the client's timeout. |
    | `max_attempts` | `int` | `3` | Attempts per call, including the first. Must be at least 1. |
    | `http_client` | `httpx.AsyncClient` | `None` | A client to send requests with, such as one configured with a proxy. When unset, each call opens and closes its own client. |

=== "Go"

    Set these options as `typesafe.Config` fields passed to `typesafe.New`.

    | Option | Type | Default | Description |
    | :--- | :--- | :--- | :--- |
    | `Model` | `string` | `"jev-latest"` | The Jev model, such as `"jev-latest"` or a pinned version like `"jev-1.13"`. |
    | `APIKey` | `string` | `TYPESAFE_API_KEY` | The TypeSafe API key. When empty, the classifier reads `TYPESAFE_API_KEY` on each call. |
    | `BaseURL` | `string` | See description | The API base URL. Defaults to the `TYPESAFE_BASE_URL` environment variable, then `https://api.typesafe.ai`. |
    | `Timeout` | `time.Duration` | `30s` | The timeout for each attempt, not for the whole call. With `HTTPClient` set, defaults to the client's timeout. |
    | `MaxAttempts` | `int` | `3` | Attempts per call, including the first. Set `1` to turn off retries. |
    | `HTTPClient` | `*http.Client` | Shared client | The client to send requests with. The default client doesn't follow redirects. |

Pin a model version, such as `jev-1.13`, to control which model answers your
questions. The response includes the model version that produced the answers
when TypeSafe reports it.

If you point the base URL at an endpoint other than TypeSafe, such as a proxy,
set the API key explicitly so that the classifier doesn't send the key in
`TYPESAFE_API_KEY` to that endpoint.

## Handle errors

The classifier retries rate-limited responses with HTTP status 429, overloaded
responses with HTTP status 529, timeouts, and dropped connections. It waits
with exponential backoff between attempts, up to the maximum number of
attempts. It does not retry other errors.

=== "Python"

    -   A `ValueError` reports a problem the classifier finds itself: a missing
        API key, a question without instructions, input with non-text parts, or
        a response that doesn't match the questions.
    -   A `RuntimeError` reports an HTTP error from TypeSafe, including a 429 or
        529 response that persists after the last attempt. The message includes
        the status code and the start of the response body.
    -   An `httpx` timeout or network exception reports a transport failure
        that persists after the last attempt.

=== "Go"

    The `Classify` method returns errors that wrap sentinel values, so you can
    check them with `errors.Is`. A non-2xx response from TypeSafe is a `*typesafe.APIError`
    that carries the status code and request ID, without the response body.

    ```go
    _, err := clf.Classify(ctx, input, questions)
    var apiErr *typesafe.APIError
    switch {
    case errors.Is(err, typesafe.ErrMissingAPIKey):
        log.Fatal("set TYPESAFE_API_KEY")
    case errors.Is(err, typesafe.ErrRateLimited), errors.Is(err, typesafe.ErrOverloaded):
        // Retries are exhausted. Fall back or try again later.
    case errors.As(err, &apiErr):
        log.Printf("TypeSafe returned %d (request %s)", apiErr.StatusCode, apiErr.RequestID)
    }
    ```

    The `typesafe` package also defines `ErrInvalidConfig`, `ErrAuthentication`,
    `ErrBadRequest`, `ErrMalformedResponse`, and `ErrAPIStatus`. An invalid
    question or input wraps `classifier.ErrInvalidQuestion` or
    `classifier.ErrInvalidInput`.

## Limitations

-   **Text and JSON input only.** The classifier rejects images, files, and other
    non-text content.
-   **Instructions required.** Every question needs instructions, even though
    the ADK question types make them optional.
-   **One question per classifier node.** A node emits one route, so branching
    on two independent questions takes two nodes.
-   **Experimental.** The TypeSafe classifier and the ADK classifier interface
    may change between releases. ADK Python issues a warning that the
    experimental `CLASSIFIER` feature is enabled.

## Additional resources

-   [Build graph routes for agent workflows](/graphs/routes/)
-   [`ClassifierNode` unit guide (Python)](https://github.com/google/adk-python/blob/v2.13.0/docs/guides/labs/classifiers/classifier_node/index.md)
-   [Classifier routing sample (Python)](https://github.com/google/adk-python/tree/v2.13.0/contributing/samples/workflows/classifier_node)
-   [`TypesafeClassifier` source (Python)](https://github.com/google/adk-python/tree/v2.13.0/src/google/adk/integrations/typesafe)
-   [`typesafe` package source (Go)](https://github.com/google/adk-go/tree/v2.7.0/exp/classifier/typesafe)
