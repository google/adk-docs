for event in events:
    if event.is_final_response() and event.content and event.content.parts:
        print(event.content.parts[0].text)

        # Optional: Show source count
        if event.grounding_metadata and event.grounding_metadata.grounding_chunks:
            print(f"\nBased on {len(event.grounding_metadata.grounding_chunks)} documents")