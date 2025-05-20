# Patent Search Agent

Using ADK Java SDK to perform the popular Patent Search (Contextual Search)  use case.

1. Get API KEY from Google AI Studio for your active GCP project
   
2. Set env variables:
```
export GOOGLE_GENAI_USE_VERTEXAI=FALSE
export GOOGLE_API_KEY="<your-api-key>"
```
3. Update the placeholders in the code with values from your project (like PROJECT_ID etc.)

4. Set up AlloyDB for Patents Data by following the codelab below:
   https://codelabs.developers.google.com/patent-search-java-adk
   
5. Create Cloud Run Function (CRF) to access AlloyDB for patents data (code in this repo)
   Follow codelab for this step: https://codelabs.developers.google.com/patent-search-java-adk

6. Deploy and get the CRF endpoint
  
7. In cloud Shell Terminal, navigate into the project folder
   
8. Run the following command to kickoff agent interaction:
```
   mvn compile exec:java -Dexec.mainClass="agents.App"
```

9. Deploy in Cloud Run:
    Navigate to your root folder & run the following command:
```
    gcloud run deploy --source . --set-env-vars GOOGLE_API_KEY=<<YOUR_API_KEY>>
```

10. Navigate to the deployed CR Endpoint for your agent so you can see the web UI.
    
TEST:

**Start interacting with the agent with inputs like:**

    Hi.
    >>
    I want to search about NLP related patents.
    >>
    Can you give more details about this patent #*****
   

   
