package tools;

// --8<-- [start:full_code]

import com.google.adk.agents.LlmAgent;
import com.google.adk.events.Event;
import com.google.adk.runner.InMemoryRunner;
import com.google.adk.sessions.Session;
import com.google.adk.tools.Annotations.Schema;
import com.google.adk.tools.FunctionTool;
import com.google.genai.types.Content;
import com.google.genai.types.Part;
import io.reactivex.rxjava3.core.Flowable;
import java.util.Map;
import yahoofinance.Stock;
import yahoofinance.YahooFinance;
import java.math.BigDecimal;

public class StockPriceAgent {

  private static final String APP_NAME = "stock_agent";
  private static final String USER_ID = "user1234";

  // No longer using mock stock data - we fetch it live!

  @Schema(description = "Retrieves the current stock price for a given symbol.")
  public static Map<String, Object> getStockPrice(
      @Schema(description = "The stock symbol (e.g., \"AAPL\", \"GOOG\")",
        name = "symbol")
      String symbol) {

    try {
      Stock stock = YahooFinance.get(symbol.toUpperCase());
      if (stock != null && stock.getQuote().getPrice() != null) {
        BigDecimal currentPrice = stock.getQuote().getPrice();
        System.out.println("Tool: Found live price for " + symbol + ": " + currentPrice);
        return Map.of("symbol", symbol, "price", currentPrice.doubleValue());
      } else {
        return Map.of("symbol", symbol, "error", "No data found for symbol");
      }
    } catch (Exception e) {
      return Map.of("symbol", symbol, "error", e.getMessage());
    }
  }

  public static void callAgent(String prompt) {
    // Create the FunctionTool from the Java method
    FunctionTool getStockPriceTool = FunctionTool.create(StockPriceAgent.class, "getStockPrice");

    LlmAgent stockPriceAgent =
        LlmAgent.builder()
            .model("gemini-2.0-flash")
            .name("stock_agent")
            .instruction(
                "You are an agent who retrieves stock prices. If a ticker symbol is provided, fetch the current price. If only a company name is given, first perform a Google search to find the correct ticker symbol before retrieving the stock price. If the provided ticker symbol is invalid or data cannot be retrieved, inform the user that the stock price could not be found.")
            .description(
                "This agent specializes in retrieving real-time stock prices. Given a stock ticker symbol (e.g., AAPL, GOOG, MSFT) or the stock name, use the tools and reliable data sources to provide the most up-to-date price.")
            .tools(getStockPriceTool) // Add the Java FunctionTool
            .build();

    // Create an InMemoryRunner
    InMemoryRunner runner = new InMemoryRunner(stockPriceAgent, APP_NAME);
    // InMemoryRunner automatically creates a session service. Create a session using the service
    Session session = runner.sessionService().createSession(APP_NAME, USER_ID).blockingGet();
    Content userMessage = Content.fromParts(Part.fromText(prompt));

    // Run the agent
    Flowable<Event> eventStream = runner.runAsync(USER_ID, session.id(), userMessage);

    // Stream event response
    eventStream.blockingForEach(
        event -> {
          if (event.finalResponse()) {
            System.out.println(event.stringifyContent());
          }
        });
  }

  public static void main(String[] args) {
    callAgent("stock price of GOOG");
    callAgent("What's the price of MSFT?");
    callAgent("Can you find the stock price for an unknown company XYZ?");
  }
}
// --8<-- [end:full_code]
