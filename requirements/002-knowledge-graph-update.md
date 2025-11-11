# Stage 2: Knowledge Graph Update (Real-time Graph Sync & Verification)

**User Story:** Once a new offering is added, the system’s **knowledge graph is immediately updated** with that item and its relationships. We need to **confirm** that the Neptune graph now contains the new node linked to the correct product, **so that** any service querying the graph (search, recommendations, etc.) can see the new offering in real-time. 

## Functional Requirements:
*   The travel **Product Graph** (Neptune) should now reflect the newly added inventory item under its parent entity:
    *   For example, the hotel “Sunshine Resort” node should now have an amenity child node “Kids’ Club” (with relevant attributes like type, name, etc.) in the graph structure. 
    *   The flight route “JFK–LAX (Premium Economy)” node should now have a service child node “Ride App Pickup” attached to it. 
*   The system can perform a **graph query to verify** the update. For instance, querying the hotel’s amenities list should include “Kids’ Club” after the addition. This verification ensures our mock data remains consistent and the addition truly succeeded. 
*   This update occurs **instantly (real-time)** as part of the transaction in Stage 1. There should be **no lag** between the item being added and it being queryable in Neptune. 
*   Downstream systems or services that rely on the graph (for example, a search service or a recommendation engine) would now automatically have access to the new information. (In the context of the PoC, we simply note this, since the next stages will explicitly query the graph.)

## Technical Requirements:
*   **Neptune Graph Update:** The insertion from Stage 1 is handled by Neptune’s graph database commit. No additional write steps are needed in this stage; instead, we focus on **reading** the graph to confirm the presence of the new data.
*   **GraphQL Query Verification:** Use **AWS AppSync** (or a direct Neptune query) to retrieve the parent entity and its linked items. For example, execute a GraphQL query such as:
    ```graphql
    query {
        getProperty(id: "hotel123") {
            name
            amenities { name, type }
        }
    }
    ```
    This query should return the “Sunshine Resort” hotel with a list of amenities that now includes an entry for “Kids’ Club”. Similarly, a query on the flight route should list “Ride App Pickup” as an available service. Implement this query in a test to programmatically verify the update (the AppSync schema should have types and connections set up to support this). 
*   **Real-time Graph Sync:** Ensure that Neptune’s configuration (which is ACID compliant for graph transactions) is such that once the `addInventory` mutation returns success, any subsequent query sees the data. In the PoC, this is naturally handled by Neptune; no special config needed beyond using the same graph instance.
*   **EventBridge Trigger Continuation:** The **EventBridge** event emitted in Stage 1 should be configured to invoke the Stage 3 processing (via Step Functions or Lambda) without delay. Technically, this is part of Stage 1’s output, but it’s critical to mention here: verify that the event with the new inventory details is indeed in the bus and will trigger the intent classification workflow next. (In testing, we might check EventBridge or the Step Functions execution logs to ensure the chain continues.) 

## Mock Data & Testing:
*   The Neptune graph was pre-seeded with a minimal dataset and then augmented in Stage 1. To test Stage 2:
    *   Query the Neptune dataset (via AppSync or Neptune APIs) after adding **Kids’ Club**. For example, run the `getProperty` query for “Sunshine Resort” and inspect the returned JSON or GraphQL response. It should contain something like `"amenities": [ { "name": "Kids' Club", "type": "Amenity" }, ... ]` among other amenities. This confirms our synthetic hotel node now links to the new amenity node. 
    *   Similarly, query the flight route (if accessible via a query, e.g., `getRoute(id: "route789") { services { name } }`) to ensure “Ride App Pickup” appears.
*   The **mock data** for hotels and routes must include identifiable IDs that were used during insertion. For example, if “hotel123” was used as the Sunshine Resort’s ID in the mutation, the same ID should be present in the Neptune dataset for that hotel node. Our pre-loaded data should have a hotel node with `id="hotel123"` representing Sunshine Resort (with pre-existing fields), so that the new amenity attaches to it meaningfully. , 
*   No external or live data is needed; this is purely an internal consistency check. We can log the output of the verification query to the console or include it in a test result. In a real scenario, this might correspond to a unit test ensuring that the `addInventory` mutation works correctly.
*   After verification, confirm that the **InventoryAdded event** was indeed published. In a test environment, one might capture the EventBridge event (using a dummy Lambda subscriber) to verify its content (e.g., it contains an `"itemName": "Kids' Club"` field or similar). This ensures the pipeline to Stage 3 is intact.