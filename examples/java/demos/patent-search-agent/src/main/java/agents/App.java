/*
 * Copyright 2025 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

package agents;


import com.google.adk.agents.LlmAgent;
import com.google.adk.agents.BaseAgent;
import com.google.adk.agents.InvocationContext;
import com.google.adk.events.Event;
import com.google.adk.runner.InMemoryRunner;
import com.google.adk.sessions.Session;
import com.google.adk.tools.Annotations.Schema;
import com.google.adk.tools.FunctionTool;
import com.google.genai.types.Content;
import com.google.genai.types.Part;
import io.reactivex.rxjava3.core.Flowable;
import java.nio.charset.StandardCharsets;
import java.net.HttpURLConnection;
import java.net.URL;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import com.google.gson.Gson;
import java.util.Scanner;
import java.io.OutputStream;
import java.io.BufferedReader;
import java.io.InputStreamReader;

import java.util.logging.Level;
import java.util.logging.Logger;

import java.util.ArrayList;
import java.util.Optional;

/** Patent Search agent that seraches contextually matching patents for user search request. */
public class App {


  static FunctionTool searchTool = FunctionTool.create(App.class, "getPatents");
  static FunctionTool explainTool = FunctionTool.create(App.class, "explainPatent");
  
  private static final String APP_NAME = "story_app";
  private static final String USER_ID = "user_12345";
  private static final String SESSION_ID = "session_1234567";
  private static final Logger logger = Logger.getLogger(App.class.getName());
  public static BaseAgent ROOT_AGENT = initAgent();

  public static BaseAgent initAgent() {
    return LlmAgent.builder()
              .name("patent-search-agent")
              .description("Patent Search agent")
              .model("gemini-2.0-flash-001")
              .instruction(
                  """
                  You are a helpful patent search assistant capable of 2 things:
                  1. Fetch 5 highly contextually relevant patents based on user search text.
                  For this you should use the tool "searchTool" and pass the search text as the input to the variable searchText.
                  If there is no matching patent, ask if the user wants to see matches from your own search outside the database.

                  2. Explain the patent in detail, abstract and concepts in it to the user for their selected patent id.
                  If the user does not provide the id for the patent they want you to explain, ask them to provide the id.
                  If they provide a title or description instead insist that they provide the id correctly.
                  For this you must use the tool "explainTool", pass the id of the patent that the user asks for
                  in the variable patentId as input and use the string value provided in session state with key 'patents' 
                  to get the corresponding abstract from the list of patents in the string. 
                  Get the abstract response from the tool for the searched patent and understand the abstract from it and summarize it in simple words in a concise way. 
                  If there is no matching patent for the id that the user entered, ask if the user wants to do a contextual search by search text instead of id.
                  Then offer to answer more questions for the user. 
                  """)
              .tools(searchTool, explainTool)
              .outputKey("patents")
              .build();
}

  
  static String VECTOR_SEARCH_ENDPOINT = "https://us-central1-*****.cloudfunctions.net/patent-search";
    public static void main(String[] args) throws Exception  {
      InMemoryRunner runner = new InMemoryRunner(ROOT_AGENT);
      Map<String, Object> initialState = new HashMap<>();
      initialState.put("patents", "");
      Session session =
          runner
              .sessionService()
              .createSession(runner.appName(), USER_ID )
              .blockingGet();
      logger.log(Level.INFO, () -> String.format("Initial session state: %s", session.state()));
 
      try (Scanner scanner = new Scanner(System.in, StandardCharsets.UTF_8)) {
        while (true) {
          System.out.print("\nYou > ");
          String userInput = scanner.nextLine();

          if ("quit".equalsIgnoreCase(userInput)) {
            break;
          }
          
          Content userMsg = Content.fromParts(Part.fromText(userInput));
          Flowable<Event> events = 
                  runner.runAsync(session.userId(), session.id(), userMsg);

          System.out.print("\nAgent > ");
          events.blockingForEach(event -> 
                  System.out.print(event.stringifyContent()));
      }
    }
  }

  

  // --- Define the Tool ---
  // Retrieves the contextually matching patents for user's search text
  public static Map<String, String> getPatents(
    @Schema(name="searchText",description = "The search text for which the user wants to find matching patents from the database") 
    String searchText) {
      try{
        String patents = "";
        patents = vectorSearch(searchText);
        return Map.of(
          "status", "success",
          "report", patents
        );
      }catch(Exception e){
        return Map.of(
          "status", "error",
          "report", "None matched your search!!"
        );
      }
}

// --- Define the Tool ---
  // Retrieves the explanation for the patent the user's interested in
  public static Map<String, String> explainPatent(
    @Schema(name="patentId",description = "The patent id for which the user wants to get more explanation for, from the database") 
    String patentId, 
    @Schema(name="ctx",description = "The list of patent abstracts from the database from which the user can pick the one to get more explanation for") 
    InvocationContext ctx) {
    String patent = "";
    try{
     String previousResults = (String) ctx.session().state().get("patents");
    
     System.out.println(previousResults);
      if(!(previousResults.isEmpty())) {
        String patents = previousResults;
        String[] patentIds = patents.split("\n\n\n\n");
        for(String pId : patentIds){
          if(pId.contains(patentId)){
            patent = pId;
          }
        }
        if(patent.isEmpty() || patent.equals("")){
          return Map.of(
                        "status", "error",
                        "report", "Patent ID not found in the previous search results. Please provide a valid patent ID."
                );
        }
      }
     //patent = fetchPatentAbstract(patentId);
     return Map.of(
      "status", "success",
      "report", patent
    );
    } catch(Exception e){
      return Map.of(
        "status", "error",
        "report", "None matched your search!!"
      );
    }
}


public static String vectorSearch(String searchText) throws Exception{
  String patents = "";
  String endpoint = VECTOR_SEARCH_ENDPOINT;
   try{
      URL url = new URL(endpoint);
      HttpURLConnection conn = (HttpURLConnection) url.openConnection();
      conn.setRequestMethod("POST");
      conn.setRequestProperty("Content-Type", "application/json");
      conn.setDoOutput(true);

      // Create JSON payload
      Gson gson = new Gson();
      Map<String, String> data = new HashMap<>();
      data.put("search", searchText);
      String jsonInputString = gson.toJson(data);
      
      try (OutputStream os = conn.getOutputStream()) {
        byte[] input = jsonInputString.getBytes("utf-8");
        os.write(input, 0, input.length);
      }
      int responseCode = conn.getResponseCode();

      if (responseCode == HttpURLConnection.HTTP_OK) {
        BufferedReader in = new BufferedReader(new InputStreamReader(conn.getInputStream()));
        String inputLine;
        StringBuilder response = new StringBuilder();

        while ((inputLine = in.readLine()) != null) {
          response.append(inputLine);
        }
        in.close();
        patents = response.toString();
        System.out.println("POST request worked! " + patents);
      } else {
        System.out.println("POST request did not work!");
      }
   } catch (Exception e) {
    System.out.println(e);
  }
  return patents;
}


}

