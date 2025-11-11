# Stage 1: Inventory Addition (New Offerings Added to Catalog)

**User Story:** *As an internal product manager,* I want to **add a new product offering** (e.g. a hotel amenity or an airline service) to our travel catalog via an internal tool, **so that** the new feature is recorded in the system and becomes available for AI-agent discovery. (In the demo, the two scenarios are adding a **“Kids’ Club”** amenity to a hotel and a **“Ride App Pickup”** service to a flight route.), 

## Functional Requirements:
*   Provide an interface or API for an authorized employee to input a new inventory item with details:
    *   **Hotel scenario:** the staff can add a **“Kids’ Club”** amenity under a specific hotel property (e.g. *Sunshine Resort, Hawaii*). 
    *   **Airline scenario:** the staff can add a **“Ride App Pickup”** service option under a specific flight offering (e.g. a Premium Economy class for the *JFK–LAX* route). 
    *   The input includes the type of inventory (amenity vs. service), a name/description, and a reference to the parent entity (hotel ID or route ID).
*   Upon submission, the new inventory item is **persisted** in the travel product catalog (backed by a graph database). The new amenity/service should be immediately linked to the respective hotel or flight in the catalog data. 
*   The system emits a **notification/event** that a new inventory item was added, including context (e.g. item ID, type, parent hotel/route). This event will trigger downstream updates in subsequent stages. 
*   No actual customer-facing change occurs at this stage, but the data back-end now includes the new offering, making it “machine-visible” to queries and AI systems. 

## Technical Requirements:
*   **Internal Ingestion Interface:** Implement a lightweight front-end form or CLI, or simply use a script/GraphQL client, to allow internal users to add inventory. This will invoke an **AWS AppSync GraphQL mutation** to create the new item. 
    *   *Example:* Define a GraphQL schema with a mutation like `addInventory`. Calling `addInventory(type: "Amenity", name: "Kids' Club", propertyId: "...")` will insert a new **Amenity node** linked to the given hotel in the **Amazon Neptune** graph. Similarly, `addInventory(type: "Service", name: "Ride App Pickup", routeId: "...")` for the flight route scenario. 
*   **Data Storage:** Use **Amazon Neptune** (a managed graph DB) to store the travel catalog as a **knowledge graph** (digital twin of hotels, flights, and their attributes). The new node is added to Neptune with relationships to its parent node (e.g., hotel “Sunshine Resort” now has child amenity “Kids’ Club”). Ensure the mutation maintains the graph schema (e.g., an `Amenity` type node connected to a `Hotel` node). 
*   **API Layer:** Through **AWS AppSync**, automatically handle the GraphQL resolver to Neptune. This ensures the insertion is done in a structured, schema-valid way without custom backend code. 
*   **Metadata (Optional):** If needed, update **AWS Glue Data Catalog** with any schema or metadata changes for discovery (though the PoC does not heavily use Glue). 
*   **Event Emission:** Configure an **Amazon EventBridge** rule to listen for successful inventory additions. The GraphQL mutation (via AppSync) can post an event or trigger a Lambda that puts an `InventoryAdded` event onto EventBridge. This event contains details like `itemId`, `itemType` (amenity/service), and `parentId` (hotel or route) – enabling the next stage to know what was added. 
*   The entire addition process should be cloud-native and serverless. (AppSync and Neptune handle the core, eliminating the need for a custom server to process the addition.) 

## Mock Data & Testing:
*   Use a **synthetic dataset** to represent the travel catalog. Before testing the addition, pre-load Neptune with a small set of fictional entities:
    *   E.g. create a few **Hotel** nodes (like “OceanView Resort”, “Sunshine Resort”) with basic attributes and some pre-existing amenities (pool, Wi-Fi, etc.). 
    *   Create a few **Flight Route** nodes (like a “NYC to LA” route, with classes such as Economy, PremiumEconomy and some existing services like “In-flight meal”). 
*   With this baseline, test the mutation for each scenario:
    *   Add an amenity – for example, call the GraphQL mutation to add `"Kids' Club"` under the hotel node ID corresponding to Sunshine Resort. Verify that the mutation returns the new amenity’s ID and that it’s linked to the hotel (e.g., the response includes `property { name: "Sunshine Resort" }`). 
    *   Add a service – similarly, add `"Ride App Pickup"` under the flight route node (e.g., the route ID for JFK–LAX). 
*   Ensure the EventBridge event is firing. In a test, the Lambda or resolver can log an event message like “InventoryAdded: Kids' Club under Sunshine Resort (hotel123)” for inspection.
*   **Examples:** The demo document provides pseudo-code for the mutation. In practice, the GraphQL call payload would look like:

    ```graphql
    mutation {
        addInventory(type: "Amenity", name: "Kids' Club", propertyId: "hotel123") {
        id, name, property { name }
        }
    }
    ```

    and should return data confirming the new amenity node (with an ID and name, and the parent hotel’s name). Similar structure applies for adding the Ride App Pickup service with a `routeId`. Use placeholder IDs like “hotel123” and “route789” as referenced in the synthetic data. No real hotel/flight data is used – everything (names, IDs) is fictional.  , 