# Built-in Gemini Safety Features

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span><span class="lst-typescript">TypeScript</span><span class="lst-go">Go</span><span class="lst-java">Java</span>
</div>

Gemini models come with in-built safety mechanisms that can be leveraged to improve content and brand safety.

* **Content safety filters**:  [Content filters](https://cloud.google.com/vertex-ai/generative-ai/docs/multimodal/configure-safety-attributes) can help block the output of harmful content. They function independently from Gemini models as part of a layered defense against threat actors who attempt to jailbreak the model. Gemini models on Vertex AI use two types of content filters:
* **Non-configurable safety filters** automatically block outputs containing prohibited content, such as child sexual abuse material (CSAM) and personally identifiable information (PII).
* **Configurable content filters** allow you to define blocking thresholds in four harm categories (hate speech, harassment, sexually explicit, and dangerous content,) based on probability and severity scores. These filters are default off but you can configure them according to your needs.
* **System instructions for safety**: [System instructions](https://cloud.google.com/vertex-ai/generative-ai/docs/multimodal/safety-system-instructions) for Gemini models in Vertex AI provide direct guidance to the model on how to behave and what type of content to generate. By providing specific instructions, you can proactively steer the model away from generating undesirable content to meet your organization’s unique needs. You can craft system instructions to define content safety guidelines, such as prohibited and sensitive topics, and disclaimer language, as well as brand safety guidelines to ensure the model's outputs align with your brand's voice, tone, values, and target audience.

While these measures are robust against content safety, you need additional checks to reduce agent misalignment, unsafe actions, and brand safety risks.
