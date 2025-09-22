Cloud function alows to enrich descriptions directly in SQL, keep track of which shows are processed, and scale for batch processing while maintaining alignment between inputs and outputs.

Definition:
- Remote function is defined in BigQuery.
- When you call this function in SQL, BigQuery sends the input parameters as a JSON array of calls to the associated Cloud Function endpoint.

Batching:
- BigQuery can send multiple rows in one HTTP request, controlled by max_batching_rows.
- Each row in the request corresponds to one call, and the Cloud Function must return a JSON array (replies) with the same number of elements, in the same order.
- BigQuery takes each element of replies and maps it to the corresponding row in the SQL result.

Cloud Function

Receives Requests:
- The Cloud Function receives a POST request from BigQuery containing an array of show metadata (show_id, show_title, show_description, director, etc.).

Processing Logic:
- For each row, the function calls the LLM (via Google GenAI) to generate an enhanced, English description following the narrative structure.
- Cleans citations, asterisks, and quotes from the description.
- Wraps the output in a JSON object containing show_id, show_title, and show_description.

Returns Response:
- Returns a JSON object with a replies array, each element corresponding to a row in the original request.
- BigQuery receives this response and assigns each show_description to the respective row in the query result.

End-to-End Flow
- SQL query in BigQuery calls the remote function.
- BigQuery batches rows and sends JSON request to Cloud Function.
- Cloud Function processes each row: enriches description, translates if needed, cleans formatting.
- Cloud Function returns a JSON array of enhanced descriptions.
- BigQuery maps the array back to the SQL query result.
