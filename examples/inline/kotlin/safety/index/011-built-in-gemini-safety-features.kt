import com.google.adk.kt.agents.LlmAgent
import com.google.adk.kt.types.GenerateContentConfig
import com.google.adk.kt.types.HarmBlockThreshold
import com.google.adk.kt.types.HarmCategory
import com.google.adk.kt.types.SafetySetting

val agent =
    LlmAgent(
        // ...
        generateContentConfig =
            GenerateContentConfig(
                safetySettings =
                    listOf(
                        SafetySetting(
                            category = HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
                            threshold = HarmBlockThreshold.OFF,
                        ),
                    ),
            ),
    )