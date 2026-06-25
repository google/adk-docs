# Test prompt for Claude Code

## Test procedure

1. Kill all processes running on port 8000
2. Create a working directory under `/tmp/test_<timestamp>`
3. Prompt user for `.env` variable values
4. Copy `20251028_claude_reviewer_for_adk/article_after_review/adk-streaming-ws` to the working directory
5. Follow the instruction in `article_after_review/custom-streaming-ws.md` to build the app in the working directory. But skip the `curl` and `tar` command execution in the "Download the sample code:" step, as `adk-streaming-ws` is copied already
6. Once the server is ready, let the user testing it with browser for text and voice.
7. Check the server log to see if the text and voice messages are handled correctly.
8. Write a `test_log_<timestamp>.md` to `20251028_claude_reviewer_for_adk/article_after_review/adk-streaming-ws/tests` directory with the actual procedures, outcomes, errors or frictions, or possible improvement points for the entire process.
