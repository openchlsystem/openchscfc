# Endpoint Integration App

## Overview

The `endpoint_integration` app is the final stage in the inbound message processing pipeline. Its primary role is to take the `StandardMessage` object produced by a platform adapter and route it to the correct destination, which could be an internal service or an external API. It is responsible for formatting the message into the specific format required by the destination endpoint and handling the final HTTP request.

## Core Responsibilities

-   **Routing**: Determining the correct destination endpoint for a message based on its platform or content.
-   **Formatting**: Transforming the `StandardMessage` into the precise JSON format expected by the destination API.
-   **Dispatching**: Making the final HTTP `POST` request to the destination endpoint, including handling authentication headers.
-   **Response Handling**: Processing the response from the endpoint and returning it to the `webhook_handler`.

## Key Components

### `message_router.py`

This file contains the `MessageRouter` class, which is the central component of this app.

-   **`__init__()`**: The constructor loads the endpoint configurations from the Django `settings.ENDPOINT_CONFIG` dictionary. This dictionary should define the URLs and authentication tokens for all possible destination services.

-   **`route_to_endpoint(message)`**: This is the main method of the class. It orchestrates the entire routing process:
    1.  It calls `_determine_endpoint()` to decide which destination to send the message to.
    2.  It calls `_format_for_endpoint()` to get the message payload in the correct format.
    3.  It calls `_send_to_endpoint()` to make the actual HTTP request.

-   **`_determine_endpoint(message)`**: This private method contains the routing logic. It inspects the `message.platform` and `message.content_type` to decide which endpoint configuration to use (e.g., `cases_endpoint` for webform submissions, `messaging_endpoint` for WhatsApp messages).

-   **`_format_for_endpoint(message, ...)`**: This method acts as a dispatcher, calling a more specific formatting method based on the endpoint determined previously.
    -   **`_format_cases_endpoint()`**: Formats the message for submission to a case management system. It builds a complex JSON object with details about the case, client, perpetrator, and narrative.
    -   **`_format_messaging_endpoint()`**: Formats the message for a generic messaging service. It typically encodes the message content in Base64 and includes metadata like channel, session ID, and timestamp.

-   **`_send_to_endpoint(formatted_message, config)`**: This method handles the final step of sending the data. It uses the `requests` library to make a `POST` request to the URL specified in the endpoint's configuration, adding an `Authorization` header if an auth token is provided.

## Workflow

1.  The `UnifiedWebhookView` in the `webhook_handler` successfully creates a `StandardMessage` object from an incoming request.
2.  The view calls `router.route_to_endpoint(standard_message)`, where `router` is an instance of the `MessageRouter`.
3.  The `MessageRouter` determines the destination (e.g., `'cases_endpoint'`).
4.  It then formats the `StandardMessage` into the JSON structure required by the cases endpoint.
5.  Finally, it sends this JSON payload as an HTTP `POST` request to the URL configured for the `cases_endpoint`.
6.  The response from the external service is captured and returned up the call stack to the `UnifiedWebhookView`.

## Configuration

The behavior of the `MessageRouter` is entirely dependent on the `ENDPOINT_CONFIG` dictionary in your `settings.py` file. This dictionary must contain the configuration for each possible destination.

**Example `settings.py`:**

```python
ENDPOINT_CONFIG = {
    'cases_endpoint': {
        'url': 'https://api.example.com/cases',
        'auth_token': 'your-secret-auth-token'
    },
    'messaging_endpoint': {
        'url': 'https://api.example.com/messages',
        'auth_token': 'your-other-secret-token'
    }
}
```
