/* How the framework provides context */
InMemoryRunner runner = new InMemoryRunner(agent);
Session session = runner
    .sessionService()
    .createSession(runner.appName(), USER_ID, initialState, SESSION_ID )
    .blockingGet();

try (Scanner scanner = new Scanner(System.in, StandardCharsets.UTF_8)) {
  while (true) {
    System.out.print("\nYou > ");
    String userInput = scanner.nextLine();
    if ("quit".equalsIgnoreCase(userInput)) {
      break;
    }
    Content userMsg = Content.fromParts(Part.fromText(userInput));
    Flowable<Event> events = runner.runAsync(session.userId(), session.id(), userMsg);
    System.out.print("\nAgent > ");
    events.blockingForEach(event -> System.out.print(event.stringifyContent()));
  }
}