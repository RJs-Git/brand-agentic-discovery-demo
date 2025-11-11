# Stage 3: Intent Catalog Update (Mapping New Offering to Traveler Intents)

**Status:** :red_circle: Backlog

**User Story:** When a new product feature is added, the system should **automatically map it to relevant traveler intents** or use-cases. I want the platform to update its **Intent Catalog** (the mapping of customer intents to available offerings) to include the new item, **so that** if a customer searches by that intent, the new offering will be among the results. , 

## Functional Requirements:
*   **Trigger & Classification:** The addition of a new inventory item triggers a classification process:
    *   The system receives the event (from Stage 1) indicating a new item (e.g., `"Kids' Club"` amenity or `"Ride App Pickup"` service) was added. 
    *   It determines what **traveler intent category** this item relates to. For example:
        *   “Kids’ Club” is recognized as relevant to **family travel** intent – e.g., categorized under an intent like **FamilyVacation** (families with children). 
        *   “Ride App Pickup” is recognized as an intent related to convenient ground transportation, possibly aligning with a **BusinessTrip** intent (business travelers value door-to-door service) or a general **SeamlessJourney** intent. 
    *   The classification can be based on simple rules/keywords or a lookup table (since this is a PoC, a straightforward rule engine is sufficient).
*   **Update Intent Catalog:** After classification:
    *   The system **updates the intent catalog data store** to link the new offering (or its parent product) with the identified intent(s). For instance, it might add the Sunshine Resort’s ID to the list of products under the “FamilyVacation” intent. 
    *   If the intent was not previously in the catalog, it might create a new entry. (In our mock scenario, intents are predefined, so we’ll use existing ones.)
    *   This ensures that any search query targeting that intent will consider this new product.
*   **Business Rules Adjustments (Optional):** If there are any **bundles or business rules** that should change due to the new item, the system addresses those:
    *   E.g., if there’s a “Family Fun Package” that includes family-friendly amenities, adding a Kids’ Club might mean Sunshine Resort should now qualify for that package. The system could update that rule or at least flag it.
    *   In the PoC, this is an optional/logged action – we won’t fully implement bundle logic, but we note it as a step (it could simply log “Updated Package X to include Kids’ Club properties”). 
*   All of the above happens in the background without user intervention. By the end of this stage, the **intent→product mapping** is up-to-date, aligning the new offering with customer intents.

## Technical Requirements:
*   **Event-Driven Workflow:** Use **Amazon EventBridge** to feed the Stage 1 event into an **AWS Step Functions** state machine or directly trigger an **AWS Lambda** function. The choice can be: 
    *   A Step Functions workflow that orchestrates multiple steps (e.g., classification, then catalog update, then bundle update).
    *   Or a single Lambda (if the logic is simple enough) that handles classification and updating the data store. The demo suggests Step Functions for clarity, but either is acceptable.
*   **Classification Logic (Rules Engine):** Implement the logic to map new inventory to intent:
    *   For PoC simplicity, use a **hard-coded dictionary** or rule-set within a Lambda function. E.g., a Python dict like `{"Kids' Club": "FamilyVacation", "Ride App Pickup": "SeamlessJourney"}` based on keywords. This Lambda reads the `itemName` or `itemType` from the event and assigns one or more intent tags. 
    *   The Lambda could also consider the context: e.g., “Kids’ Club” appears under a hotel (so definitely a leisure amenity), “Ride App Pickup” under a flight (could imply business traveler convenience). But the simplest approach is direct string matching as above.
    *   (If desired, this could be extended to a ML model or Bedrock NLP call in the future, but not needed in the demo.)
*   **Intent Catalog Storage:** Use a simple **data store** to save the intent mappings:
    *   An **Amazon DynamoDB table** is a good choice, where each item is an Intent category, and contains a list (set) of Product IDs associated with that intent. For example, a DynamoDB item with `PK="FamilyVacation"` might have an attribute `ProductIDs=["hotel123", ...]` and after this process “hotel123” (Sunshine Resort’s ID) is added to that array. 
    *   Alternatively, a JSON file in **Amazon S3** could hold a dictionary of intents to products, which the Lambda updates (though DynamoDB is more straightforward for updates). 
    *   If using DynamoDB, configure it so that updates either append to a list or use a set data type to naturally avoid duplicates.
*   **Update Logic:** After classification, the Lambda will perform an **upsert** into the intent catalog:
    *   If the intent key exists, it appends the new product reference; if not, it creates it. Use DynamoDB UpdateItem (with `ADD` if using a set, or list append logic).
    *   The entry could store either the product’s unique ID or a human-readable name plus ID. E.g., store `"Sunshine Resort (hotel123)"` under FamilyVacation, for clarity in the demo.
*   **Logging/Optional Steps:** If including business rule updates, implement an additional Lambda or Step Functions step:
    *   For instance, a step that checks “does intent FamilyVacation correspond to any package definitions?” If yes, update that config. In the PoC, rather than a real update, just log that it would have been done (to show awareness).
    *   Ensure the Step Functions workflow catches and logs errors, as mapping intents is critical for the agent to find the product later.
*   **Confirmation:** Once updated, the system could output a log or metric (e.g., “IntentCatalog updated: FamilyVacation now has 5 items”). This helps in verifying the step during the demo.

## Mock Data & Testing:
*   Prepare a **small set of intent categories** to use in the demo. For example:
    *   **FamilyVacation** – meant to capture things like child-friendly amenities (kids’ meals, adjoining rooms, and our new **Kids’ Club** feature). 
    *   **BusinessTrip** – meant for business-traveler-focused services (e.g., airport lounge access, priority boarding, and our **Ride App Pickup** service). (The document also mentions “SeamlessJourney” or “DoorToDoor” as possible labels for this intent; we can use one of these or stick to BusinessTrip for simplicity.) 
    *   Possibly an **EcoTravel** or other category as a placeholder (though not used in this specific flow, included just to show extensibility). 
*   **Intent Catalog stub:** Create a DynamoDB table (or a Python dict if not actually using AWS services in a test) with these intent keys. Initially, they might map to a couple of dummy products (or be empty).
    *   Example initial state (pseudo-JSON):
        ```json
        {
            "FamilyVacation": ["hotel999 (Beachside Resort)"],
            "BusinessTrip": ["flight555 (Sample Airlines VIP Lounge Access)"]
        }
        ```
        This gives something to update. (These initial entries are optional; the main point is to have the structure ready.)
*   **Testing classification:** Simulate the EventBridge event for **Kids’ Club** addition. Run the classification Lambda with an input like `{"detail": {"itemName": "Kids' Club", "itemType": "Amenity", "parentType": "Hotel", "parentId": "hotel123"}}`. Check that the Lambda would output an intent “FamilyVacation”.
    *   Verify that after the Lambda executes, the DynamoDB table’s FamilyVacation entry now contains `hotel123` (Sunshine Resort). In a dry run, this could just be printed. 
*   Simulate the event for **Ride App Pickup** similarly. Expect the intent “BusinessTrip” (or “SeamlessJourney”) to be updated with the flight/route ID.
*   **Verify data:** Query the DynamoDB table (or print the JSON) to ensure:
    *   FamilyVacation -> includes Sunshine Resort/Kids’ Club.
    *   BusinessTrip (or chosen intent) -> includes the JFK–LAX route’s service.
*   Since we have no real user data, all inputs are synthetic strings and IDs. The dictionary in Lambda should account for the exact phrasing used in Stage 1. (Our example uses exact matches like `"Kids' Club"`; ensure the quotes/apostrophe are handled correctly in the code or normalized.)
*   This step is crucial for Stage 4: If Sunshine Resort isn’t in the FamilyVacation list, the agent’s search won’t find it. So, double-check that the mapping is successful using the dummy data.
