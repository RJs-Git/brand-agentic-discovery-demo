# Stage 4: Agent Search (AI Agent Queries & Results Delivery)

**User Story:** As a customer using the AI travel assistant, I want to **search for travel options by describing my needs** (e.g. “a family-friendly hotel in Hawaii” or “a flight with easy ground transport”), and have the AI agent fetch results that include the brand’s **latest offerings**, **so that** I discover the new amenity/service we added if it matches my intent. , 

*(This stage enables Claude, the AI agent, to query the backend. It covers building the search API and integrating it with the AI assistant interface. The result will be the agent presenting the user with options that highlight the new Kids’ Club or Ride App Pickup feature.)*

## Functional Requirements:
*   **Agent Query Interface:** There is a cloud API that the AI assistant can call whenever a user’s question relates to finding travel options. For example, if the user asks: “Find me a **family-friendly hotel** in Hawaii” or “I need a flight that offers a **ride service** from the airport,” the agent will invoke this backend service rather than relying only on its built-in knowledge. , 
*   **Intent Interpretation:** The query service or the agent itself will interpret the user’s request to identify key parameters:
    *   Determine the **intent category** (from Stage 3’s catalog) implied by the request. (E.g., “family-friendly” maps to the FamilyVacation intent; “ride service from airport” suggests an intent of seamless ground transportation, which we linked to our new flight service.) , 
    *   Extract any additional filters like location or dates if provided (e.g., destination “Hawaii”).
    *   *Note:* In this PoC, we can assume the agent or skill explicitly provides the intent tag and needed filters (to keep it simple, we don’t rely on a complex NLP here).
*   **Search on Knowledge Graph:** The backend service uses the above parameters to **find matching travel products**:
    *   It queries the **Neptune knowledge graph** for products (hotels, flights) that meet the criteria. Primarily, it will look up products that are tagged with the given **intent** (from the intent catalog data). For example, if intent = FamilyVacation and location = Hawaii, it will find all Hawaii hotels in Neptune that have a “FamilyVacation” tag or relevant amenity (like Kids’ Club). 
    *   Thanks to Stage 3, the Sunshine Resort hotel is now associated with FamilyVacation, so it should be found. Likewise, if the intent is BusinessTrip/SeamlessJourney for flights, our JFK–LAX flight with Ride App Pickup would be found.
*   **Real-Time Info Enrichment:** For each result, the service retrieves **real-time booking info**:
    *   It gets the current **price** (e.g., nightly rate for the hotel, airfare for the flight) and **availability** (dates or seat availability) from a live data source or cache. 
    *   In the PoC, this might be a simple lookup of a stored price (since we’re not hitting a real system). But the requirement is that the agent’s answer includes up-to-date pricing and availability, not stale or hard-coded values.
*   **Compose Results:** The service returns a **list of matching options** in a structured format. For example:
    *   For the hotel query: it might return **Sunshine Resort** – Hawaii, with features = \[“Kids’ Club”, “Pool”, “Free WiFi”], price = $250/night, availability = “Dec 1–7 available”. (If there were multiple hotels matching, it would list them.) , 
    *   For the flight query: it might return **JFK–LAX Premium Economy**, features = \[“Ride App Pickup”, “Lounge Access”], price = $450, next flight date/time, and seats left. 
*   **Results Presentation:** The AI agent (Claude) takes the response and presents it to the user in conversational form:
    *   For example, Claude might say: *“I found a family-friendly hotel: **Sunshine Resort in Hawaii** – it even has a **Kids’ Club** for children. It’s available for your dates at $250 per night.”* 
    *   Or for the flight: *“There’s a Premium Economy flight from JFK to LAX that includes a **Ride App Pickup** service at your destination, priced at $450.”* 
    *   The new inventory items (“Kids’ Club”, “Ride App Pickup”) should be explicitly mentioned or highlighted in the agent’s response, confirming that the agent “knows” about these features. 
*   The user can then ask follow-up questions or proceed to booking (Stage 5), but at this stage, the main outcome is the **user is informed** of relevant options that incorporate the newly added offering.

## Technical Requirements:
*   **Answers API (MCP):** Develop an **agent-facing search API** (sometimes referred to as an “Answers” service or MCP – Master Control Program) that the AI agent can call. Key technical components: 
    *   **Amazon API Gateway** to expose a RESTful endpoint, e.g. `GET /searchTravel` or `POST /search`. This endpoint will accept parameters like intent, location, dates, etc. (For simplicity, a GET with query params or a fixed JSON payload structure can be used.) 
    *   **AWS Lambda** as the backend for this API. The Lambda function will contain the logic to handle the search request: 
        *   Parse the input (e.g., intent = “FamilyVacation”, location = “Hawaii”).
        *   **Query Neptune**: The Lambda can query Neptune in one of two ways:
            1.  Through **AppSync** – by invoking a GraphQL query that fetches products by intent and filter. This would require AppSync resolvers and possibly a pre-built GraphQL query (similar to Stage 2’s verification query, but filtering by intent). 
            2.  Or using Neptune’s query language (Gremlin or SPARQL) via an SDK within the Lambda. Given the PoC scale, using AppSync’s GraphQL for Neptune may be easier and consistent.
        *   **Query Intent Catalog**: Alternatively, the Lambda could first look up the intent in the DynamoDB intent catalog to get a list of product IDs, then fetch details for those IDs from Neptune. E.g., DynamoDB might tell it “FamilyVacation => \[hotel123]”, then it queries Neptune for those specific IDs (and checks the location property = Hawaii).
        *   **Query Pricing DB**: The Lambda then queries a small **database for pricing and availability**. This could be:
            *   **Amazon Aurora Serverless** (MySQL/Postgres) with a table of sample prices. For instance, a `Prices` table keyed by product ID (hotel or flight) that has a price and maybe inventory count. Aurora might be overkill for a couple of entries, but it simulates a real pricing engine. 
            *   Or **Amazon DynamoDB** as a simple key-value store for prices (which might be easier since we already use DynamoDB for intents). , 
            *   The Lambda can also hold a hardcoded dictionary for prices if we want to avoid another service – but using a service shows the principle of separation.
        *   **Construct Response**: The Lambda combines the data into a JSON response. It should include fields such as product name, location, features (including the new ones), price, availability, etc., as shown in the example formats. , 
    *   Security: since this is a demo, we can assume the API Gateway is either secured by an API key or not publicly exposed except to the agent. In a real scenario, we’d enforce authentication (so only the agent or authorized clients call it).
*   **Claude Integration (Skill/Plugin):** To connect Claude (the AI front-end) with our Answers API:
    *   **Claude Skill**: Write a skill file (or configure via Claude’s interface) such that when certain triggers or intents are detected in conversation, Claude calls our API. For example, the skill might detect the user asking for “find hotel” or “family trip” and then call `/searchTravel?intent=FamilyVacation&location=Hawaii`. 
        *   The skill will provide Claude with instructions on how to format the API call and how to parse the JSON response.
    *   **Direct API Call**: If the AI platform supports function calling (like OpenAI’s system), we could register our API as a tool. Claude (or a similar LLM) would then decide to invoke the API when needed. For the PoC, we assume a skill or manual triggering since we may not have an actual Claude instance accessible. 
    *   We ensure that **Claude’s response template** highlights the new features. The skill can instruct: “If the JSON contains a special feature like ‘Kids’ Club’, mention it in the response.” This way, the user clearly hears about the new amenity or service. (In demo terms, we saw the responses emphasizing those terms with formatting.) 
    *   Because we cannot use private Claude data, we **simulate the integration** in the PoC: for example, by calling the API directly with a test query and then manually formatting a dummy Claude-like answer. This shows the end-to-end flow without needing actual AI agent hookup. , 
*   **Result Handling:** The system should handle cases where no results are found or multiple results:
    *   In our small dataset, likely exactly one result matches each scenario (by design). But ensure the code could handle an array of results (as the JSON is structured). 
    *   If no results, the API could return an empty list, and Claude would say something like “I didn’t find any options for that.” (We might not showcase this in the demo, but we can note it in the implementation.)
*   **Performance:** The search and data fetch should be reasonably quick (Neptune and DynamoDB/Aurora calls are low-latency for this scale). This ensures the agent’s response is fast. We can use CloudWatch to monitor the Lambda execution time, and Neptune’s performance with such small data should be near-instant.
*   **Optional NLP enhancement:** The design allows plugging in more advanced query interpretation if needed. For instance, integrating **Amazon Bedrock** for natural language parsing or vector-based retrieval if queries get complex. In this demo scope, we skip this – using straightforward intent keys – but we note that the architecture is extensible to handle, say, a question like *“Which Hawaii resorts have amenities for kids under 5?”* by using LLM or embeddings to map that to our intent and data. 

## Mock Data & Testing:
*   **Test Dataset Query:** With our mock Neptune graph and intent catalog ready (from previous stages), test the Answers API Lambda in isolation:
    *   Invoke it with a sample event representing a search. For example:
        ```json
        { "intent": "FamilyVacation", "location": "Hawaii" }
        ```
        (If using API Gateway, you’d actually hit the /searchTravel endpoint with these as parameters.)
    *   The expected behavior: The Lambda should find the Sunshine Resort in Neptune via the intent tag. Since we know Sunshine Resort is tagged as FamilyVacation and has `location = Hawaii` in our mock data, it qualifies. 
        *   Neptune query simulation: In lieu of a real Neptune query, our Lambda could just filter a hardcoded list. But better is to actually query Neptune if possible. We might, for instance, have a Gremlin query like `g.V().has('Hotel','location','Hawaii').out('hasAmenity').has('name','Kids\' Club')` to find hotels in Hawaii with Kids’ Club – which would return Sunshine Resort node.
        *   For simplicity, one could also have stored the direct mapping in Dynamo (FamilyVacation -> \[hotel123]) and then query Neptune for those IDs to get details (name, features). This two-step approach is easier to test: Dynamo returns “hotel123”, Neptune query `getProperty(id:"hotel123")` returns the hotel details with amenities (like done in Stage 2).
    *   Ensure the Lambda then looks up pricing. Prepare a **Pricing table**:
        *   For example, a DynamoDB table `Prices` with an item: `PK="hotel123", price=250, currency="USD", availability="Dec 1-7 Available"`.
        *   Another item `PK="route789", price=450, next_flight="2025-12-15 08:00", seats_left=5` for the flight.
        *   If using Aurora, create a simple table `Pricing(product_id, price, availability)` and put those values. (The exact method doesn’t matter for the PoC, but mimic real data sources.)
    *   The Lambda should retrieve these and construct a JSON like the examples given in the design doc. Verify that the JSON output matches expectations. , 
    *   **Example output (for FamilyVacation Hawaii):**
        ```json
        {
            "intent": "FamilyVacation",
            "results": [
            {
                "type": "hotel",
                "name": "Sunshine Resort",
                "location": "Hawaii",
                "features": ["Kids' Club", "Pool", "Free WiFi"],
                "price_per_night": "$250",
                "availability": "Dec 1-7: Available"
            }
            ]
        }
        ```
        Ensure “Kids’ Club” is in the features list and the price/availability reflect the mock data seed. 
    *   **Example output (for Ride App Pickup query):** If testing the flight case similarly:
        ```json
        {
            "intent": "BusinessTrip",
            "results": [
            {
                "type": "flight",
                "route": "JFK-LAX",
                "class": "PremiumEconomy",
                "features": ["Ride App Pickup", "Lounge Access"],
                "price": "$450",
                "next_flight": "2025-12-15 08:00",
                "seats_left": 5
            }
            ]
        }
        ```
        This includes “Ride App Pickup” in features and the dummy availability data. 
    *   If our Neptune data for the flight includes “Lounge Access” as a feature of that class, we list it too to show multiple features.
*   **Integration Test:** Since we might not have an actual Claude environment, simulate the end-to-end:
    *   Take the JSON output from the Lambda and feed it into a simple formatting function that produces a sentence like Claude would. Check that the sentence indeed mentions the new features:
        *   For the hotel: does it mention “Kids’ Club”? (It should, as per our plan.)
        *   For the flight: does it mention “Ride App Pickup”?
    *   We can create a **mock chatbot** in code or a small script that given an English question will call the Lambda and then print a formatted English answer. This would mimic Claude’s behavior in the demo. 
    *   Optionally, test the Claude Skill (if we have the environment): One could imagine configuring a rule like “when user message contains ‘family’ and ‘hotel’, call /searchTravel with intent=FamilyVacation…”.
    *   Make sure to test edge cases with the mock data – e.g., ask for something for which we didn’t set up data to ensure the system handles it gracefully (this is more for robustness; the demo itself sticks to the known scenarios).
*   Throughout, no actual external APIs (besides AWS services) and no private user data are used. All search results and inputs are from our synthetic dataset. This means we have full control to ensure the new features appear in results, demonstrating the value clearly.