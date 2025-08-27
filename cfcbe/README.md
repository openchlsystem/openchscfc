# CFCBE API Gateway

## Overview

This project is a Django-based API Gateway designed to handle and route requests from various platforms to their respective backend services. It acts as a central hub for incoming webhooks, standardizing the data and forwarding it to the appropriate endpoints. The system is built with a modular architecture, using an adapter pattern to easily integrate with different platforms.

## Core Technologies

- **Backend Framework**: Django
- **API Framework**: Django Rest Framework
- **Authentication**: JWT (JSON Web Tokens)
- **Database**: SQLite (default, configurable)
- **CORS Handling**: django-cors-headers

## Project Structure

The project is organized into several Django apps, each with a specific responsibility:

- **`cfcbe`**: The main project directory containing settings and root URL configuration.
- **`webhook_handler`**: The core of the API gateway. It receives all incoming webhook requests and uses the `AdapterFactory` to process them.
- **`platform_adapters`**: Contains the adapters for each integrated platform (e.g., WhatsApp, Webform, EEMIS, CEEMIS). Each adapter is responsible for parsing platform-specific data and converting it to a standard format.
- **`endpoint_integration`**: The `MessageRouter` in this app takes the standardized message and routes it to the correct internal or external service.
- **`authapp`**: Handles user authentication and authorization.
- **`feedback` & `emailfeedback`**: Apps for managing feedback from users.
- **`shared`**: Contains shared models and utilities used across the project.

## API Endpoints

All API endpoints are prefixed with `/api/`. The main endpoints are:

- **`POST /api/webhook/<str:platform>/`**: The unified webhook endpoint for receiving data from various platforms. The `<platform>` parameter determines which adapter is used.
- **`POST /api/webhook/eemis`**: A dedicated endpoint for handling webhooks from the EEMIS platform.
- **`POST /api/webhook/helpline/case/ceemis/`**: Creates a case in CEEMIS based on data from a helpline.
- **`PUT /api/webhook/helpline/case/ceemis/update/`**: Updates a case in CEEMIS.
- **`POST /api/webhook/ceemis/create/`**: Creates a case from CEEMIS data.
- **`GET /api/case/status/<str:case_reference>/`**: Checks the status of a case using its reference number.
- **`POST /api/webhook/webform/auth/request-verification/`**: Sends a verification email for webform authentication.
- **`POST /api/webhook/webform/auth/verify-otp/`**: Verifies the OTP and issues a JWT token for webform access.

## Setup and Installation

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
    Create a `.env` file in the project root and add the necessary configuration. You can use the `.env.example` file as a template.

5.  **Run database migrations:**
    ```bash
    python manage.py migrate
    ```

6.  **Run the development server:**
    ```bash
    python manage.py runserver
    ```
    The API will be available at `http://127.0.0.1:8000`.

## Running Tests

To run the test suite, use the following command:

```bash
python manage.py test
```

## Detailed Documentation

For more detailed information on the core apps, please see their individual `README.md` files:

-   **[`webhook_handler/README.md`](./webhook_handler/README.md)**: Detailed documentation for the app that handles all incoming webhook requests.
-   **[`platform_adapters/README.md`](./platform_adapters/README.md)**: A deep dive into the adapter pattern used for platform integration.
-   **[`endpoint_integration/README.md`](./endpoint_integration/README.md)**: Information on how standardized messages are routed to their final destinations.
