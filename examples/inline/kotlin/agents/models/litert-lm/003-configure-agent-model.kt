 object HelloTimeAgent {

    // Get model path from environment variable.
    private val modelPath: String by lazy {
        System.getenv("LITERT_LM_MODEL_PATH")
            ?: throw IllegalStateException(
                "LITERT_LM_MODEL_PATH environment variable must be set pointing to a .litertlm file."
            )
    }

    @JvmField
    val rootAgent =
        LlmAgent(
            name = "hello_time_agent",
            description = "Tells the current time in a specified city.",
            model =
                LiteRtLmModel.create(
                    EngineConfig(modelPath = modelPath, backend = Backend.CPU())
                ),
            instruction =
                Instruction(
                    "You are a helpful assistant that tells the current time in a city. " +
                        "Use the 'getCurrentTime' tool for this purpose."
                ),
            tools = TimeService().generatedTools(),
        )
}