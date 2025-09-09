# Webhook Handler App

The `webhook_handler` app is the primary entry point for all incoming data to the API Gateway. It is responsible for receiving requests, authenticating them where necessary, and passing them to the appropriate platform adapter for processing.

## Core Responsibilities

-   **Request Ingestion**: Receives all incoming HTTP requests from external platforms.
-   **URL Routing**: Maps incoming URLs to the correct view for processing.
-   **Authentication**: Handles authentication and authorization, particularly for the webform via an OTP email flow.
-   **Session Management**: Manages conversation sessions to track interactions with users.
-   **Request Dispatching**: Forwards the request to the `platform_adapters` layer to be translated into a standard format.

## Key Components

### `views.py`

This file contains the main logic for handling webhook requests.

-   **`UnifiedWebhookView`**: This is the most important view in the app. It's a class-based view that handles requests for multiple platforms.
    -   `get()`: Handles `GET` requests, which are typically used by platforms for webhook verification (e.g., WhatsApp's challenge verification).
    -   `post()`: Handles `POST` requests, which contain the actual message data. It determines the platform from the URL and uses the `AdapterFactory` to get the correct adapter. It then calls the adapter to parse and process the message.
-   **Platform-Specific Views**:
    -   `EEMISWebhookView`: A dedicated view for handling requests from the EEMIS platform.
    -   `HelplineCEEMISView` & `HelplineCEEMISUpdateView`: Views for creating and updating cases in CEEMIS from a helpline.
    -   `CEEMISHelplineView`: A view for creating cases in the helpline from CEEMIS data.
-   **`CaseStatusCheckView`**: A view that allows users to check the status of a case using a case reference number.

### `urls.py`

This file defines the URL patterns for the app. All URLs are prefixed with `/api/`.

-   **`webhook/<str:platform>/`**: The main endpoint for the `UnifiedWebhookView`. The `platform` argument tells the view which adapter to use.
-   **`webhook/eemis`**: The endpoint for the `EEMISWebhookView`.
-   **`webhook/helpline/case/ceemis/`**: The endpoint for creating CEEMIS cases.
-   **`webhook/helpline/case/ceemis/update/`**: The endpoint for updating CEEMIS cases.
-   **`webhook/ceemis/create/`**: The endpoint for creating cases from CEEMIS.
-   **`case/status/<str:case_reference>/`**: The endpoint for checking case status.
-   **`webhook/webform/auth/...`**: A group of endpoints for handling webform authentication.

### `auth_views.py`

This module manages the authentication flow for the webform.

-   **`request_email_verification`**: This view handles the initial request for authentication. It takes an email address and organization name, generates a one-time password (OTP), and sends it to the provided email.
-   **`verify_otp_and_issue_token`**: This view receives the OTP submitted by the user. If the OTP is valid, it generates a JWT token using the `TokenManager` and returns it to the user.

### `token_manager.py`

This module is responsible for creating and verifying JSON Web Tokens (JWT).

-   **`TokenManager.generate_token()`**: Creates a new JWT for a given organization. The token includes the organization's ID and an expiration date.
-   **`TokenManager.verify_token()`**: Decodes and validates a JWT to ensure it's authentic and has not expired.

### `services/conversation_service.py`

This service helps in managing the state of conversations.

-   **`ConversationService.get_or_create_conversation()`**: This method ensures that messages from the same user on the same platform are grouped into a single, continuous conversation. It creates a new conversation record if one doesn't already exist.
-   **`ConversationService.get_conversation_history()`**: Retrieves the message history for a given conversation.

## Workflow

1.  An external platform sends an HTTP request to one of the URLs defined in `urls.py`.
2.  Django routes the request to the appropriate view in `views.py`.
3.  For the `UnifiedWebhookView`, the view identifies the platform from the URL.
4.  The view calls `AdapterFactory.get_adapter(platform)` to get the correct adapter from the `platform_adapters` app.
5.  The view then uses the adapter's methods to:
    -   Validate the request.
    -   Parse the platform-specific payload into a list of messages.
    -   Convert each message into a `StandardMessage` object.
6.  For each `StandardMessage`, the view calls `ConversationService.get_or_create_conversation()` to manage the session.
7.  Finally, the `StandardMessage` is passed to the `MessageRouter` in the `endpoint_integration` app to be sent to its final destination.
