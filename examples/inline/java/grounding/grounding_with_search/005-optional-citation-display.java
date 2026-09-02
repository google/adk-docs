for (Event event : events) {
    if (event.finalResponse()) {
        System.out.println(event.content().parts().get(0).text());

        // Optional: Show source count
        if (event.groundingMetadata().isPresent()) {
            System.out.println("\nBased on " + event.groundingMetadata().get().groundingChunks().size() + " documents");
        }
    }
}