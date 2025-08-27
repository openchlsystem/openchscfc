# Handover Document: CFCBE API Gateway

## 1. Project Overview

This document provides a comprehensive handover for the CFCBE API Gateway. The project is a Django-based API Gateway designed to handle and route requests from various platforms to their respective backend services. It acts as a central hub for incoming webhooks, standardizing the data and forwarding it to the appropriate endpoints. The system is built with a modular architecture, using an adapter pattern to easily integrate with different platforms.

## 2. Core Technologies

The project is built with the following technologies:

*   **Backend Framework**: Django
*   **API Framework**: Django Rest Framework
*   **Authentication**: JWT (JSON Web Tokens)
*   **Database**: SQLite (default, configurable)
*   **CORS Handling**: django-cors-headers

## 3. Project Structure

The project is organized into several Django apps, each with a specific responsibility:

*   **`cfcbe`**: The main project directory containing settings and root URL configuration.
*   **`webhook_handler`**: The core of the API gateway. It receives all incoming webhook requests and uses the `AdapterFactory` to process them.
*   **`platform_adapters`**: Contains the adapters for each integrated platform (e.g., WhatsApp, Webform, EEMIS, CEEMIS). Each adapter is responsible for parsing platform-specific data and converting it to a standard format.
*   **`endpoint_integration`**: The `MessageRouter` in this app takes the standardized message and routes it to the correct internal or external service.
*   **`authapp`**: Handles user authentication and authorization.
*   **`feedback` & `emailfeedback`**: Apps for managing feedback from users.
*   **`shared`**: Contains shared models and utilities used across the project.

## 4. Setup and Installation

To set up a local development environment, follow these steps:

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd cfcbe
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Set up environment variables:**
    Create a `.env` file in the project root and add the necessary configuration. See the `5.1. Environment Configuration` section for a list of required environment variables.

5.  **Run database migrations:**
    ```bash
    python manage.py migrate
    ```

6.  **Run the development server:**
    ```bash
    python manage.py runserver
    ```
    The API will be available at `http://127.0.0.1:8000`.

## 5. Environment & Deployment

### 5.1. Environment Configuration

The project uses a `.env` file to manage environment variables. The following keys are used in the `.env` file:

*   `SECRET_KEY`
*   `DEBUG`
*   `ALLOWED_HOSTS`
*   `LOG_LEVEL`
*   `DB_ENGINE`
*   `DB_NAME`
*   `MEDIA_URL`
*   `MEDIA_ROOT`
*   `CORS_ALLOW_ALL_ORIGINS`
*   `CORS_ALLOW_CREDENTIALS`
*   `CORS_ALLOWED_ORIGINS`
*   `WHATSAPP_VERIFY_TOKEN`
*   `WHATSAPP_CLIENT_ID`
*   `WHATSAPP_CLIENT_SECRET`
*   `WHATSAPP_BUSINESS_ID`
*   `WHATSAPP_PHONE_NUMBER_ID`
*   `WHATSAPP_ACCESS_TOKEN`
*   `WHATSAPP_API_URL`
*   `PLATFORM_WEBFORM_API_TOKEN`
*   `ENDPOINT_AUTH_TOKEN`
*   `MISTRAL_API_ENDPOINT`
*   `ENDPOINT_CASES_URL`
*   `ENDPOINT_MESSAGING_URL`
*   `ENDPOINT_CEEMIS_URL`
*   `ENDPOINT_CEEMIS_UPDATE_URL`
*   `EMAIL_BACKEND`
*   `EMAIL_HOST`
*   `EMAIL_PORT`
*   `EMAIL_HOST_USER`
*   `EMAIL_HOST_PASSWORD`
*   `EMAIL_USE_TLS`
*   `EMAIL_USE_SSL`
*   `DEFAULT_FROM_EMAIL`

**Switching between environments:**

To switch between development, staging, and production environments, you can maintain separate `.env` files (e.g., `.env.dev`, `.env.prod`) and load the appropriate one based on an environment variable (e.g., `ENV=production`). The `python-dotenv` library is used to load these variables.

### 5.2. Deployment

The project can be deployed using Docker and Gunicorn.

*   **Docker**: A `Dockerfile` is provided in the project root. You can build and run the Docker container with the following commands:
    ```bash
    docker build -t cfcbe .
    docker run -p 8000:8000 cfcbe
    ```

*   **Gunicorn**: Gunicorn is used as the WSGI HTTP server. The `gunicorn` command in the `Dockerfile` is used to run the application.

*   **CI/CD**: There is no CI/CD pipeline configured in this project.

## 6. Configuration & Settings

### 6.1. `settings.py`

The main settings for the Django project are in `cfcbe/settings.py`. Here are some of the key settings:

*   **`SECRET_KEY`**: A secret key for a particular Django installation. This is used to provide cryptographic signing, and should be set to a unique, unpredictable value.
*   **`DEBUG`**: A boolean that turns on/off debug mode. In debug mode, Django will show detailed error pages.
*   **`ALLOWED_HOSTS`**: A list of strings representing the host/domain names that this Django site can serve.
*   **`INSTALLED_APPS`**: A list of all Django applications that are activated in this Django instance.
*   **`MIDDLEWARE`**: A list of middleware to be used.
*   **`DATABASES`**: A dictionary containing the settings for all databases to be used with this project.
*   **`REST_FRAMEWORK`**: A dictionary containing settings for the Django Rest Framework.
*   **`CORS_...`**: A set of variables to configure Cross-Origin Resource Sharing (CORS).
*   **`LOGGING`**: A dictionary containing the logging configuration.
*   **`PLATFORM_CONFIGS`**: A dictionary containing platform-specific configurations.
*   **`ENDPOINT_CONFIG`**: A dictionary containing the configuration for the different endpoints the application can route to.
*   **`EMAIL_...`**: A set of variables to configure email sending.

### 6.2. Environment Variables

The project uses a `.env` file to manage environment variables. See the `5.1. Environment Configuration` section for a list of required environment variables.

## 7. Data Models & Database

### 7.1. Data Models

The following are the key Django models used in the project:

**`authapp/models.py`**

*   **`User`**: Represents a user with a WhatsApp number and an OTP secret for authentication.

**`emailfeedback/models.py`**

*   **`Email`**: Stores email details, including sender, recipient, subject, body, and raw message.

**`feedback/models.py`**

*   **`Person`**: Represents a victim or perpetrator with name, age, gender, and additional info.
*   **`Complaint`**: The main model for storing complaint details, including reporter, category, text, media, and related victim/perpetrator.
*   **`CaseNote`**: Stores notes related to a complaint.
*   **`ComplaintStatus`**: Stores the status of a complaint.
*   **`Notification`**: Stores notifications related to a complaint.
*   **`Voicenotes`**: Stores voice notes related to a complaint.

**`webhook_handler/models.py`**

*   **`Conversation`**: Tracks conversations across different platforms.
*   **`WebhookMessage`**: Stores incoming webhook messages.
*   **`Organization`**: Represents an organization using the API.
*   **`EmailVerification`**: Tracks email verification attempts with OTP.
*   **`Person`**: (Duplicate of `feedback/models.py`)
*   **`Complaint`**: (Duplicate of `feedback/models.py`)
*   **`CaseNote`**: (Duplicate of `feedback/models.py`)
*   **`ComplaintStatus`**: (Duplicate of `feedback/models.py`)
*   **`Notification`**: (Duplicate of `feedback/models.py`)
*   **`Voicenote`**: (Duplicate of `feedback/models.py`)
*   **`Contact`**: Stores WhatsApp contacts.
*   **`WhatsAppMedia`**: Stores media files linked to WhatsApp messages.
*   **`WhatsAppMessage`**: Handles different types of WhatsApp messages.
*   **`WhatsAppResponse`**: Represents responses to WhatsApp messages.
*   **`WhatsAppCredential`**: Stores WhatsApp API credentials for an organization.

### 7.2. Database

The project uses SQLite as the default database. The database configuration is defined in the `DATABASES` setting in `cfcbe/settings.py`.

### 7.3. Migration Strategy

The project uses Django's built-in migration system to manage database schema changes. To create and apply migrations, use the following commands:

```bash
python manage.py makemigrations
python manage.py migrate
```

## 8. Authentication & Authorization

### 8.1. JWT Authentication

The project uses JSON Web Tokens (JWT) for authentication. The `webhook_handler/token_manager.py` file contains the `TokenManager` class, which is responsible for generating and verifying JWT tokens.

*   **Token Generation**: The `TokenManager.generate_token()` method creates a new JWT for a given organization. The token includes the organization's ID and an expiration date (currently set to 1 year).
*   **Token Verification**: The `TokenManager.verify_token()` method decodes and validates a JWT to ensure it's authentic and has not expired.

### 8.2. Authentication Flow

The authentication flow for the webform is handled by the `webhook_handler/auth_views.py` file.

1.  **Request Verification**: The `request_email_verification` view handles the initial request for authentication. It takes an email address and organization name, generates a one-time password (OTP), and sends it to the provided email.
2.  **Verify OTP and Issue Token**: The `verify_otp_and_issue_token` view receives the OTP submitted by the user. If the OTP is valid, it generates a JWT token using the `TokenManager` and returns it to the user.

### 8.3. Token Refresh

There is no automatic token refresh logic implemented. The tokens are valid for one year, and a new token must be generated after that.

### 8.4. Role-Based Access Control (RBAC)

There is no role-based access control implemented in the project. Once a user is authenticated, they have access to all the resources.

## 9. API Documentation

### 9.1. API Endpoints

The following are the key API endpoints in the project:

*   **`POST /api/webhook/<str:platform>/`**: The unified webhook endpoint for receiving data from various platforms. The `<platform>` parameter determines which adapter is used.
*   **`POST /api/webhook/eemis`**: A dedicated endpoint for handling webhooks from the EEMIS platform.
*   **`POST /api/webhook/helpline/case/ceemis/`**: Creates a case in CEEMIS based on data from a helpline.
*   **`PUT /api/webhook/helpline/case/ceemis/update/`**: Updates a case in CEEMIS.
*   **`POST /api/webhook/ceemis/create/`**: Creates a case from CEEMIS data.
*   **`GET /api/case/status/<str:case_reference>/`**: Checks the status of a case using its reference number.
*   **`POST /api/webhook/webform/auth/request-verification/`**: Sends a verification email for webform authentication.
*   **`POST /api/webhook/webform/auth/verify-otp/`**: Verifies the OTP and issues a JWT token for webform access.

### 9.2. Sample Payloads

There are no sample payloads available in the codebase. It is recommended to add sample payloads for each webhook endpoint to facilitate testing and development.

## 10. Core Workflow

The following steps describe the end-to-end workflow of a request through the API Gateway:

1.  **Request Reception**: An external platform sends an HTTP request to one of the URLs defined in `webhook_handler/urls.py`.

2.  **Routing to View**: Django routes the request to the appropriate view in `webhook_handler/views.py`. For most platforms, this will be the `UnifiedWebhookView`.

3.  **Adapter Selection**: The `UnifiedWebhookView` identifies the platform from the URL (e.g., 'whatsapp') and calls `AdapterFactory.get_adapter(platform)` to get the correct adapter from the `platform_adapters` app.

4.  **Request Processing**: The view then uses the adapter to process the request:
    *   It calls `adapter.validate_request()` to ensure the request is authentic.
    *   It calls `adapter.parse_messages()` to extract the message data from the request payload.
    *   For each message, it calls `adapter.to_standard_message()` to convert the data into a `StandardMessage` object.

5.  **Conversation Management**: For each `StandardMessage`, the view calls `ConversationService.get_or_create_conversation()` to manage the session, ensuring that messages from the same user are grouped into a single conversation.

6.  **Endpoint Routing**: The `StandardMessage` is then passed to the `MessageRouter` in the `endpoint_integration` app.

7.  **Message Formatting and Dispatch**: The `MessageRouter` determines the correct destination endpoint for the message, formats the message into the specific format required by the destination, and sends it via an HTTP POST request.

8.  **Response Handling**: The response from the destination endpoint is captured and returned up the call stack to the `UnifiedWebhookView`.

## 11. Error Handling & Logging

### 11.1. Logging

The project uses Python's built-in `logging` module. The logging configuration is defined in `cfcbe/settings.py` and allows for different logging levels (e.g., `INFO`, `DEBUG`). By default, logs are printed to the console.

### 11.2. Error Handling

Errors are handled in the view functions and a `JsonResponse` with an appropriate status code and error message is returned.

### 11.3. Common Error Codes

The following are some of the common error codes and their meanings:

*   **400 Bad Request**: The request is missing required parameters or the parameters are invalid.
*   **404 Not Found**: The requested resource could not be found.
*   **500 Internal Server Error**: An unexpected error occurred on the server.

Here are some specific error messages from the `webhook_handler/auth_views.py` file:

*   `Email and organization name are required` (status 400)
*   `Failed to send verification email` (status 500)
*   `Email, OTP, and organization name are required` (status 400)
*   `No pending verification found for this email` (status 404)
*   `Verification has expired, please request a new code` (status 400)
*   `Invalid verification code` (status 400)

## 12. Testing & QA

### 12.1. Test Coverage

The project has a `tests.py` file in each Django app, but most of them are empty. It is recommended to add unit and integration tests to ensure the quality of the code.

### 12.2. Running Tests

To run the test suite, use the following command:

```bash
python manage.py test
```

## 13. Extensibility

### 13.1. Adding a New Platform Adapter

To add a new platform adapter, follow these steps:

1.  Create a new directory for your platform in the `platform_adapters/` directory (e.g., `platform_adapters/myplatform/`).
2.  Inside the new directory, create a new file for your adapter (e.g., `myplatform_adapter.py`).
3.  In the new file, create a new class that inherits from `platform_adapters.base_adapter.BaseAdapter` and implement the required methods (`handle_verification`, `validate_request`, `parse_messages`, `to_standard_message`, `send_message`, `format_webhook_response`).
4.  In `platform_adapters/adapter_factory.py`, import your new adapter and register it in the `AdapterFactory`'s `adapters` dictionary.

### 13.2. Extending the MessageRouter

To extend the `MessageRouter` with a new endpoint, follow these steps:

1.  In `cfcbe/settings.py`, add a new entry to the `ENDPOINT_CONFIG` dictionary with the URL and authentication token for the new endpoint.
2.  In `endpoint_integration/message_router.py`, add a new private method to the `MessageRouter` class to format the message for the new endpoint.
3.  In the `MessageRouter._determine_endpoint()` method, add a new condition to route messages to the new endpoint based on the message's platform or content type.

## 14. Security & Privacy Considerations

### 14.1. Sensitive Data

The project handles sensitive data, such as user information and complaint details. The following measures are in place to protect this data:

*   **Secrets Management**: The `SECRET_KEY` and other sensitive information are stored in a `.env` file and loaded into the environment.
*   **Data Encryption**: The `webhook_handler/models.py` file suggests that the `client_secret` and `access_token` in the `WhatsAppCredential` model could be encrypted, but this is not implemented.

### 14.2. Data Privacy

The project has a basic data privacy statement in the `cfcbe/settings.py` file: `"*To stop messages:* Reply STOP\nData privacy: We never share your number."`. However, there is no formal privacy policy or GDPR/child-safety/data protection measures implemented.

It is recommended to:

*   Implement encryption for sensitive data at rest and in transit.
*   Create a formal privacy policy and ensure the project is compliant with relevant data protection regulations.

## 15. Known Issues & Future Improvements

### 15.1. Known Issues

*   **Duplicate Models**: The `Person`, `Complaint`, `CaseNote`, `ComplaintStatus`, `Notification`, and `Voicenote` models are defined in both `feedback/models.py` and `webhook_handler/models.py`. This is a code smell and should be refactored to have a single source of truth.
*   **Lack of Tests**: The test coverage is very low. Most of the `tests.py` files are empty. This makes it difficult to refactor the code or add new features without introducing bugs.
*   **Incomplete Security Measures**: As mentioned in the "Security & Privacy Considerations" section, the encryption of sensitive data is not fully implemented.

### 15.2. Future Improvements

*   **Refactor Duplicate Models**: Refactor the duplicate models to have a single source of truth.
*   **Improve Test Coverage**: Add unit and integration tests to ensure the quality of the code.
*   **Implement Encryption**: Implement encryption for sensitive data at rest and in transit.
*   **Add Role-Based Access Control (RBAC)**: Implement RBAC to control access to resources based on user roles.
*   **Add API Throttling**: Implement API throttling to prevent abuse of the API.
*   **Add Caching**: Implement caching to improve the performance of the API.
*   **Improve Logging**: Improve the logging to include more context and make it easier to debug issues.
*   **Add CI/CD Pipeline**: Add a CI/CD pipeline to automate the testing and deployment process.
