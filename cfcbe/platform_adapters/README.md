# Platform Adapters App

## Overview

The `platform_adapters` app is the heart of the gateway's modularity. It uses the Adapter design pattern to translate data from various external platforms into a standardized format that the rest of the application can understand. Each platform (e.g., WhatsApp, Webform, EEMIS) has its own adapter responsible for handling the specific data structure and communication protocol of that platform.

## Core Responsibilities

-   **Standardization**: To translate platform-specific data into a common `StandardMessage` format.
-   **Decoupling**: To decouple the core application logic from the specific details of each external platform.
-   **Extensibility**: To allow new platforms to be integrated easily by simply creating a new adapter.

## Key Components

### `base_adapter.py`

This file defines the `BaseAdapter`, an abstract base class that all platform adapters must inherit from. It enforces a common interface for all adapters, ensuring they can be used interchangeably by the `webhook_handler`.

The key methods that each adapter must implement are:

-   **`handle_verification(request)`**: Handles platform-specific verification challenges (e.g., WhatsApp's `hub.challenge`).
-   **`validate_request(request)`**: Validates the authenticity of an incoming request (e.g., by checking a signature).
-   **`parse_messages(payload)`**: Parses the incoming data payload and extracts one or more messages.
-   **`to_standard_message(message_data)`**: Converts a single message from the platform's format into a `StandardMessage` object.
-   **`send_message(recipient_id, message_content)`**: Sends a message back to the user on the platform.
-   **`format_webhook_response(responses)`**: Formats the HTTP response to be sent back to the platform's webhook, acknowledging receipt of the message.

### `adapter_factory.py`

The `AdapterFactory` is a central registry for all available adapters. It is responsible for creating and providing the correct adapter instance when requested.

-   **`register_adapter(platform, adapter_class)`**: This class method is used to register a new adapter in the factory.
-   **`get_adapter(platform)`**: This is the most important method. The `webhook_handler` calls this method with a platform string (e.g., `'whatsapp'`) to get an instance of the corresponding adapter.

### Individual Adapters

The app contains several subdirectories, each holding an adapter for a specific platform:

-   **`whatsApp/`**: Contains the adapter for handling messages from the WhatsApp Business API.
-   **`webform/`**: Contains the adapter for handling submissions from a web form. This adapter is also responsible for converting `Complaint` model instances into `StandardMessage` objects.
-   **`ceemis/` and `eemis/`**: Contain adapters for the CEEMIS and EEMIS platforms, respectively.
-   **`mamacare_chatbot/`**: Contains an adapter for the MamaCare chatbot, which is a specialized layer on top of the WhatsApp adapter.

## Workflow

1.  The `UnifiedWebhookView` in the `webhook_handler` receives a request.
2.  It calls `AdapterFactory.get_adapter()` with the platform name from the URL (e.g., `'whatsapp'`).
3.  The factory returns an instance of the appropriate adapter (e.g., `WhatsAppAdapter`).
4.  The view then uses this adapter instance to process the request:
    -   It calls `adapter.validate_request()` to ensure the request is authentic.
    -   It calls `adapter.parse_messages()` to extract the message data from the request payload.
    -   For each message, it calls `adapter.to_standard_message()` to convert the data into a `StandardMessage` object.
5.  This `StandardMessage` object is then passed to the `endpoint_integration` app for routing.
6.  If a response needs to be sent back to the user, the `adapter.send_message()` method is used.
