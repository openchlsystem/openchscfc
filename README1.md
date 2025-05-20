
```markdown
# Unified Communication Gateway - Comprehensive Technical Documentation

## 1. Executive Overview

The Unified Communication Gateway (UCG) is an enterprise-grade middleware platform built on Django that standardizes and manages communication across diverse channels (webform, WhatsApp, SMS, etc.) and backend systems. The UCG handles message normalization, routing, media processing, authentication, and delivery while maintaining robust audit trails. It implements a modular, adapter-based architecture to facilitate clean separation of concerns and easy expansion to new platforms.

### 1.1 Design Philosophy

The UCG follows several core design principles:
- **Single Point of Integration**: Isolate backend systems from the specifics of multiple communication platforms.
- **Standardization**: Convert diverse message formats into a common internal representation.
- **Platform Independence**: Separate platform-specific code from core business logic.
- **Extensibility**: Enable new platforms to be added with minimal changes to existing code.
- **Auditability**: Maintain comprehensive logs of all communication passing through the system.
- **Security**: Implement robust authentication and authorization mechanisms.

### 1.2 Key Features

- **Platform-agnostic messaging**: Standardized message format across all platforms
- **Modular architecture**: Adapter pattern for platform-specific code
- **Media handling**: Process, store, and route various media types (images, audio, video)
- **Authentication**: JWT-based token system for secure API access
- **Conversation tracking**: Track messaging threads across sessions
- **Signal-based event system**: Trigger workflows based on message events
- **Database persistence**: Store all messages and media for audit and analysis
- **Token management**: Handle platform-specific authentication tokens
- **Error handling**: Robust error handling and recovery mechanisms
- **API endpoints**: RESTful API interface for integrations

## 2. System Architecture in Depth

### 2.1 Architectural Patterns

The UCG implements several design patterns:
- **Adapter Pattern**: For platform-specific code isolation
- **Factory Pattern**: For adapter instantiation
- **Strategy Pattern**: For message routing decisions
- **Repository Pattern**: For data access abstraction
- **Mediator Pattern**: For decoupling message producers from consumers
- **Observer Pattern**: Through the signal system for event handling

### 2.2 Core Components (Detailed)

#### 2.2.1 UnifiedWebhookView

The UnifiedWebhookView serves as the central entry point for all platform communications. It:
- Handles GET requests for verification challenges (WhatsApp, Facebook, etc.)
- Processes POST requests for incoming messages, outgoing messages, and token operations
- Routes requests to appropriate handlers based on platform and direction
- Manages error states and returns appropriate HTTP responses
- Performs initial request validation before platform-specific validation

```python
class UnifiedWebhookView(View):
    def get(self, request, platform, *args, **kwargs):
        """
        Handles GET requests typically used for platform verification.
        Args:
            request: The HTTP request object
            platform: The platform identifier from the URL
        Returns:
            HTTP response, typically for verification challenges
        """
        try:
            # Get the appropriate adapter for this platform
            adapter = AdapterFactory.get_adapter(platform)
            
            # Let the adapter handle verification
            response = adapter.handle_verification(request)
            if response:
                return response
                
            # If adapter didn't handle it, return a default response
            return HttpResponse("Verification not required or failed.")
        except Exception as e:
            logger.exception(f"Error handling verification: {str(e)}")
            return HttpResponse("Verification failed", status=500)
    
    def post(self, request, platform, *args, **kwargs):
        """
        Handles POST requests for message exchange and token operations.
        Args:
            request: The HTTP request object
            platform: The platform identifier from the URL
        Returns:
            HTTP response containing operation result
        """
        try:
            # Get the appropriate adapter for this platform
            adapter = AdapterFactory.get_adapter(platform)
            
            # Parse the request body
            try:
                payload = json.loads(request.body)
            except json.JSONDecodeError:
                # If the body isn't JSON, treat it as form data
                payload = request.POST.dict()
                
            # Determine the direction of the message flow
            direction = payload.get('direction', 'incoming')
            
            # Route based on direction
            if direction == 'outgoing':
                return self._handle_outgoing_message(adapter, platform, payload, request)
            elif direction == 'token':
                return self._handle_token_operation(adapter, platform, payload, request)
            else:
                return self._handle_incoming_message(adapter, platform, payload, request)
                
        except Exception as e:
            logger.exception(f"Error processing webhook: {str(e)}")
            return HttpResponse("Processing failed", status=500)
```

It includes detailed private methods for handling each type of operation:
- `_handle_incoming_message`: Processes messages from platforms to the system
- `_handle_outgoing_message`: Processes messages from the system to platforms
- `_handle_token_operation`: Manages authentication tokens
- `_handle_webform_submission`: Handles the specific case of form submissions

#### 2.2.2 Platform Adapters System

The adapter system creates a clean separation between platform-specific code and the core system, allowing each platform to handle its unique requirements while conforming to a standard interface.

##### BaseAdapter

```python
class BaseAdapter(ABC):
    """
    Abstract base class that all platform adapters must implement.
    Defines the contract for platform-specific functionality.
    """
    
    @abstractmethod
    def handle_verification(self, request: HttpRequest) -> Optional[HttpResponse]:
        """
        Handle platform verification challenges.
        Args:
            request: The HTTP request containing verification data
        Returns:
            HttpResponse if verification was handled, None otherwise
        """
        pass
    
    @abstractmethod
    def validate_request(self, request: Any) -> bool:
        """
        Validate authenticity of an incoming request.
        Args:
            request: The request to validate
        Returns:
            True if request is valid, False otherwise
        Raises:
            ValidationError: If validation fails with specific issues
        """
        pass
    
    @abstractmethod
    def parse_messages(self, request: Any) -> List[Dict[str, Any]]:
        """
        Extract messages from platform-specific format.
        Args:
            request: The request containing message data
        Returns:
            List of parsed messages as dictionaries
        """
        pass
    
    @abstractmethod
    def send_message(self, recipient_id: str, message_content: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send a message to a recipient on this platform.
        Args:
            recipient_id: ID of the recipient on the platform
            message_content: Content to send in standardized format
        Returns:
            Response data from the platform
        """
        pass
    
    @abstractmethod
    def format_webhook_response(self, responses: List[Dict[str, Any]]) -> HttpResponse:
        """
        Format response to return to the platform's webhook.
        Args:
            responses: List of processed message responses
        Returns:
            HttpResponse in the format expected by the platform
        """
        pass
```

##### AdapterFactory

```python
class AdapterFactory:
    """
    Factory for creating and managing platform adapters.
    
    This class follows the Factory pattern to:
    1. Register adapters by platform
    2. Instantiate and cache adapter instances
    3. Provide a uniform interface for the system to access platform-specific adapters
    """
    
    # Registry of platform adapters
    _adapters: Dict[str, Type[BaseAdapter]] = {}
    
    # Cache of adapter instances (for singleton behavior)
    _adapter_instances: Dict[str, BaseAdapter] = {}
    
    @classmethod
    def register_adapter(cls, platform: str, adapter_class: Type[BaseAdapter]) -> None:
        """
        Register a new adapter for a platform.
        
        Args:
            platform: String identifier for the platform
            adapter_class: Class that implements BaseAdapter
        Raises:
            TypeError: If adapter_class doesn't inherit from BaseAdapter
        """
        platform = platform.lower()
        if not issubclass(adapter_class, BaseAdapter):
            raise TypeError(f"Adapter class must inherit from BaseAdapter: {adapter_class.__name__}")
        
        cls._adapters[platform] = adapter_class
    
    @classmethod
    def get_adapter(cls, platform: str) -> BaseAdapter:
        """
        Get an adapter instance for the specified platform.
        
        Args:
            platform: String identifier for the platform
            
        Returns:
            An instance of the appropriate adapter
            
        Raises:
            ValueError: If the platform is not supported
        """
        platform = platform.lower()
        
        # Check if we have an instance already
        if platform in cls._adapter_instances:
            return cls._adapter_instances[platform]
        
        # Get the adapter class
        if platform not in cls._adapters:
            raise ValueError(f"Unsupported platform: {platform}")
        
        adapter_class = cls._adapters[platform]
        
        # Create an instance
        adapter = adapter_class()
        
        # Cache the instance
        cls._adapter_instances[platform] = adapter
        
        return adapter
```

##### Platform-Specific Adapters

Each adapter implements platform-specific logic while adhering to the BaseAdapter interface:

1. **WebformAdapter**: Handles form submissions for case reporting
   - Processes structured form data
   - Handles media file uploads
   - Captures reporter, victim, and perpetrator information

2. **WhatsAppAdapter**: Handles WhatsApp messaging 
   - Verifies webhook challenges from Meta
   - Processes incoming messages (text and media)
   - Handles media uploads and downloads
   - Manages token refresh mechanisms

#### 2.2.3 StandardMessage in Detail

The StandardMessage class is the unified internal representation of all messages:

```python
@dataclass
class StandardMessage:
    """
    Standardized message format aligned with endpoint formats.
    
    This class provides:
    1. A consistent internal representation of messages
    2. Mapping between different platform formats
    3. Support for media and metadata
    4. Serialization to/from dictionary
    5. Timestamp utilities
    
    Attributes are carefully ordered to comply with Python's requirement
    that non-default parameters must come before parameters with defaults.
    """
    
    # Common fields that directly map to endpoint formats
    source: str               # 'whatsapp', 'webform', etc. (maps to 'channel'/'src')
    source_uid: str           # Sender identifier (maps to 'session_id'/'src_uid')
    source_address: str       # Sender address (maps to 'from'/'src_address')
    message_id: str           # Unique message identifier (maps to 'message_id'/'src_callid')
    source_timestamp: float   # Unix timestamp (maps to 'timestamp'/'src_ts')
    content: str              # The message content (will be encoded for messaging endpoint)
    platform: str             # Internal platform identifier (may be different from source)
    
    # Fields with default values
    content_type: str = "text/plain"  # MIME type for the content
    media_url: Optional[str] = None   # URL to any media content
    metadata: Dict[str, Any] = field(default_factory=dict)  # Platform-specific data
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the StandardMessage to a dictionary."""
        return {
            'source': self.source,
            'source_uid': self.source_uid,
            'source_address': self.source_address,
            'message_id': self.message_id,
            'source_timestamp': self.source_timestamp,
            'content': self.content,
            'content_type': self.content_type,
            'platform': self.platform,
            'media_url': self.media_url,
            'metadata': self.metadata
        }
    
    def get_iso_timestamp(self) -> str:
        """
        Convert the Unix timestamp to ISO format.
        Useful for the messaging endpoint format.
        """
        return datetime.fromtimestamp(self.source_timestamp).isoformat()
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'StandardMessage':
        """Create a StandardMessage from a dictionary."""
        return cls(
            source=data['source'],
            source_uid=data['source_uid'],
            source_address=data['source_address'],
            message_id=data['message_id'],
            source_timestamp=data['source_timestamp'],
            content=data['content'],
            platform=data['platform'],
            content_type=data.get('content_type', 'text/plain'),
            media_url=data.get('media_url'),
            metadata=data.get('metadata', {})
        )
```

The StandardMessage serves as the backbone of inter-component communication, providing a consistent format that abstracts away platform-specific details.

#### 2.2.4 MessageRouter Implementation

The MessageRouter directs messages to the appropriate endpoints based on message characteristics and system configuration:

```python
class MessageRouter:
    """
    Routes standardized messages to appropriate endpoints.
    
    This class is responsible for:
    1. Determining which endpoint should receive a message
    2. Formatting messages according to endpoint requirements
    3. Handling the HTTP communication with endpoints
    4. Processing and returning endpoint responses
    
    It maintains a conversation service to track message threads.
    """
    
    def __init__(self):
        """Initialize the MessageRouter with configuration and services."""
        self.conversation_service = ConversationService()
        self.endpoint_config = getattr(settings, 'ENDPOINT_CONFIG', {})
        
    def route_to_endpoint(self, message: StandardMessage) -> Dict[str, Any]:
        """
        Route a standardized message to an endpoint.
        
        For webform/complaint messages, the actual API submission may be
        handled by the post_save signal, not directly by this method.
        
        Args:
            message: A StandardMessage instance
            
        Returns:
            Response data from the endpoint
        """
        # Special case for webform complaints - handled by signal
        if message.platform == 'webform' and message.content_type.startswith('complaint'):
            return {
                'status': 'success',
                'message': 'Complaint will be processed by signal handler'
            }
            
        # Determine which endpoint to use
        endpoint = self._determine_endpoint(message)
        
        # Get or create a conversation
        conversation = self.conversation_service.get_or_create_conversation(
            message.source_uid, message.platform
        )
        
        # Get endpoint configuration
        if endpoint not in self.endpoint_config:
            error_msg = f"Endpoint not configured: {endpoint}"
            logger.error(error_msg)
            return {'status': 'error', 'error': error_msg}
        
        config = self.endpoint_config[endpoint]
        
        # Format the message for the endpoint
        formatted_message = self._format_for_endpoint(message, conversation, config, endpoint)
        
        # Send the formatted message to the endpoint
        response = self._send_to_endpoint(formatted_message, config)
        
        return response
```

It includes methods for:
- Endpoint determination based on message characteristics
- Message formatting specific to each endpoint
- HTTP communication with endpoints
- Response processing

### 2.3 Authentication System

#### 2.3.1 TokenManager

The TokenManager handles JWT token generation, validation, and management:

```python
class TokenManager:
    """
    Manages JWT token generation and verification for the gateway API.
    
    This class:
    1. Generates JWT tokens for organizations
    2. Verifies token validity and authenticity
    3. Handles token expiry and claims
    4. Maintains organization associations
    """
    
    @staticmethod
    def generate_token(organization_name, organization_email=None):
        """
        Generate a JWT token for an organization.
        Creates the organization if it doesn't exist.
        
        Args:
            organization_name: Name of the organization
            organization_email: Email of the organization (optional)
            
        Returns:
            Dict with token and expiry information
            
        Raises:
            Exception: If token generation fails
        """
        try:
            # Get or create organization
            org, created = Organization.objects.get_or_create(
                name=organization_name,
                defaults={
                    'email': organization_email or f"{organization_name.lower().replace(' ', '')}@example.com"
                }
            )
            
            # Create token payload
            payload = {
                'org_id': str(org.id),
                'org_name': org.name,
                'exp': datetime.datetime.utcnow() + datetime.timedelta(days=365),  # 1 year expiry
                'iat': datetime.datetime.utcnow(),
                'jti': str(uuid.uuid4())
            }
            
            # Generate token
            token = jwt.encode(
                payload,
                settings.SECRET_KEY,
                algorithm='HS256'
            )
            
            return {
                'token': token,
                'organization_id': str(org.id),
                'expires': payload['exp'].isoformat()
            }
            
        except Exception as e:
            raise Exception(f"Failed to generate token: {str(e)}")
    
    @staticmethod
    def verify_token(token):
        """
        Verify a JWT token.
        
        Args:
            token: JWT token to verify
            
        Returns:
            Dict with token payload if valid, None otherwise
        """
        try:
            # Decode and verify token
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=['HS256']
            )
            
            # Check if organization exists
            org_id = payload.get('org_id')
            if not org_id or not Organization.objects.filter(id=org_id).exists():
                return None
                
            return payload
            
        except jwt.ExpiredSignatureError:
            logger.error("Token validation failed: Token has expired")
            return None
        except jwt.InvalidTokenError:
            logger.error("Token validation failed: Invalid token")
            return None
        except Exception as e:
            logger.error(f"Token validation failed: {str(e)}")
            return None
```

#### 2.3.2 TokenAuthMiddleware

```python
class TokenAuthMiddleware:
    """
    Middleware to authenticate requests using JWT tokens.
    
    This middleware:
    1. Intercepts incoming requests
    2. Extracts and validates bearer tokens
    3. Attaches organization information to authenticated requests
    4. Rejects unauthorized requests
    5. Bypasses authentication for specific paths or methods
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        # Skip authentication for token generation endpoint
        if request.path.endswith('/api/webhook/webform/auth/token/'):
            return self.get_response(request)
        
        # Skip authentication for non-webform endpoints
        if '/api/webhook/webform/' not in request.path:
            return self.get_response(request)
        
        # Skip authentication for GET requests (like categories)
        if request.method == 'GET':
            return self.get_response(request)
        
        # Get authorization header
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        
        # Check if header exists and has correct format
        if not auth_header.startswith('Bearer '):
            return JsonResponse({
                'status': 'error',
                'message': 'Authentication required. Please provide a valid bearer token.'
            }, status=401)
            
        # Extract token
        token = auth_header.split(' ')[1]
        
        # Verify token
        payload = TokenManager.verify_token(token)
        if not payload:
            return JsonResponse({
                'status': 'error',
                'message': 'Invalid or expired token.'
            }, status=401)
            
        # Add organization info to request
        request.organization_id = payload.get('org_id')
        request.organization_name = payload.get('org_name')
        
        # Continue with request
        return self.get_response(request)
```

### 2.4 Data Model in Detail

#### 2.4.1 Core Gateway Models

```python
class Conversation(models.Model):
    """
    Tracks conversations across platforms.
    
    This model:
    1. Links messages in a conversation thread
    2. Maintains conversation state
    3. Tracks the platform of the conversation
    4. Stores metadata for platform-specific details
    """
    
    conversation_id = models.CharField(max_length=255, unique=True)
    sender_id = models.CharField(max_length=255)
    platform = models.CharField(max_length=50)
    is_active = models.BooleanField(default=True)
    last_activity = models.DateTimeField(default=timezone.now)
    metadata = models.JSONField(default=dict, blank=True)
    
    def __str__(self):
        return f"{self.platform} conversation with {self.sender_id}"


class WebhookMessage(models.Model):
    """
    Stores incoming webhook messages for auditing and processing.
    
    This model:
    1. Records all messages passing through the system
    2. Links messages to conversations
    3. Tracks message metadata and content
    4. Supports different message types
    """
    
    message_id = models.CharField(max_length=255, unique=True)
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    sender_id = models.CharField(max_length=255)
    platform = models.CharField(max_length=50)
    content = models.TextField(blank=True)
    media_url = models.URLField(blank=True, null=True)
    message_type = models.CharField(max_length=50, default='text')
    timestamp = models.DateTimeField(default=timezone.now)
    metadata = models.JSONField(default=dict, blank=True)
    
    def __str__(self):
        return f"Message from {self.sender_id} on {self.platform}"
```

#### 2.4.2 Webform (Complaint) Models

```python
class Person(models.Model):
    """
    Stores information about individuals (victims or perpetrators).
    
    This model:
    1. Records identifying information about a person
    2. Can be linked to either victim or perpetrator roles
    3. Maintains demographic information
    """
    
    name = models.CharField(max_length=255)
    age = models.PositiveIntegerField(null=True, blank=True)
    gender = models.CharField(max_length=50, null=True, blank=True)
    additional_info = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

class Complaint(models.Model):
    """
    Represents a case or complaint submitted through webform.
    
    This model:
    1. Stores details about a reported incident
    2. Links victims and perpetrators
    3. Tracks conversation context
    4. Maintains media attachments
    5. Records timestamps and reference IDs
    """
    
    complaint_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    session_id = models.UUIDField(default=uuid.uuid4, null=True, blank=True) 
    conversation = models.ForeignKey(Conversation, on_delete=models.SET_NULL, null=True, blank=True, related_name='complaints')
    timestamp = models.DateTimeField(auto_now_add=True)
    reporter_nickname = models.CharField(max_length=100, null=True, blank=True)
    case_category = models.CharField(max_length=255, default="Not Specified", null=True, blank=True)
    complaint_text = models.TextField(blank=True, null=True)
    complaint_image = models.ImageField(upload_to="complaints/images/", blank=True, null=True)
    complaint_audio = models.FileField(upload_to="complaints/audio/", blank=True, null=True)
    complaint_video = models.FileField(upload_to="complaints/videos/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    message_id_ref = models.CharField(max_length=255, null=True, blank=True)
    
    victim = models.ForeignKey(Person, related_name='victims', on_delete=models.CASCADE, null=True, blank=True)
    perpetrator = models.ForeignKey(Person, related_name='perpetrators', on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"Complaint {self.complaint_id} by {self.reporter_nickname}"
```

#### 2.4.3 WhatsApp Models

```python
class Contact(models.Model):
    """
    Stores WhatsApp contacts.
    
    This model:
    1. Records WhatsApp user information
    2. Links users to conversations
    3. Maintains display information
    """
    
    wa_id = models.CharField(max_length=15, unique=True)  # WhatsApp ID
    name = models.CharField(max_length=255, blank=True, null=True)  # Optional name
    display_phone_number = models.CharField(max_length=15, blank=True, null=True)
    conversation = models.ForeignKey(Conversation, on_delete=models.SET_NULL, null=True, blank=True, related_name='contacts')

    def __str__(self):
        return self.name if self.name else self.wa_id

class WhatsAppMedia(models.Model):
    """
    Stores media files linked to WhatsApp messages.
    
    This model:
    1. Records media information and content
    2. Supports different media types
    3. Stores both URLs and local files
    """
    
    MEDIA_TYPES = [
        ("image", "Image"),
        ("video", "Video"),
        ("audio", "Audio"),
        ("document", "Document"),
    ]

    media_type = models.CharField(max_length=50, choices=MEDIA_TYPES, help_text="Type of the media file")
    media_url = models.URLField(blank=True, null=True, help_text="URL of the media file, if applicable")
    media_file = models.FileField(upload_to='whatsapp_media/', blank=True, null=True, help_text="Uploaded media file")
    media_mime_type = models.CharField(max_length=100, blank=True, null=True, help_text="MIME type of the media file")

    def __str__(self):
        return f"Media ({self.media_type}) - {self.media_url or self.media_file}"

class WhatsAppMessage(models.Model):
    """
    Handles different types of WhatsApp messages.
    
    This model:
    1. Records message content and metadata
    2. Tracks message status
    3. Links messages to media content
    4. Maintains sender and recipient information
    """
    
    MESSAGE_TYPES = [
        ("text", "Text"),
        ("image", "Image"),
        ("video", "Video"),
        ("audio", "Audio"),
        ("document", "Document"),
        ("sticker", "Sticker"),
        ("location", "Location"),
        ("contact", "Contact"),
    ]

    MESSAGE_STATUS = [
        ("pending", "Pending"),
        ("sent", "Sent"),
        ("failed", "Failed"),
        ("delivered", "Delivered"),
        ("read", "Read"),
    ]

    sender = models.ForeignKey(Contact, on_delete=models.CASCADE, related_name="sent_messages", null=True, blank=True)
    recipient = models.ForeignKey(Contact, on_delete=models.CASCADE, related_name="received_messages", blank=True, null=True)
    conversation = models.ForeignKey(Conversation, on_delete=models.SET_NULL, null=True, blank=True, related_name='whatsapp_messages')
    webhook_message = models.OneToOneField(WebhookMessage, on_delete=models.SET_NULL, null=True, blank=True, related_name='whatsapp_message')
    message_type = models.CharField(max_length=50, choices=MESSAGE_TYPES, default="text", help_text="Type of the message")
    content = models.TextField(blank=True, null=True, help_text="Text content of the message, if applicable")
    caption = models.TextField(blank=True, null=True, help_text="Caption for media messages, if applicable")
    media = models.ForeignKey(WhatsAppMedia, on_delete=models.SET_NULL, blank=True, null=True, help_text="Linked media file")
    timestamp = models.DateTimeField(auto_now_add=True, help_text="Timestamp of when the message was sent/received")
    status = models.CharField(max_length=20, choices=MESSAGE_STATUS, default="pending", help_text="Current status of the message")
    is_forwarded_to_main_system = models.BooleanField(default=False, help_text="Flag to track if the message was forwarded to the main system")

    class Meta:
        ordering = ['-timestamp']
```

### 2.5 Directory Structure Detailed

The file structure follows Django conventions with additions for the adapter pattern:

```
gateway_project/
│
├── gateway/                       # Main Django project
│   ├── settings.py                # Project settings with configurations
│   ├── urls.py                    # Main URL configuration
│   ├── asgi.py                    # ASGI configuration
│   └── wsgi.py                    # WSGI configuration
│
├── webhook_handler/               # Core webhook handling app
│   ├── __init__.py
│   ├── models.py                  # Consolidated models for all platforms
│   ├── urls.py                    # URL routing for webhooks
│   ├── views.py                   # UnifiedWebhookView
│   ├── middleware.py              # Authentication middleware
│   ├── token_manager.py           # JWT token management
│   ├── signals.py                 # Signal handlers
│   ├── admin.py                   # Admin configuration
│   ├── apps.py                    # AppConfig
│   ├── migrations/                # Database migrations
│   │   └── __init__.py
│   ├── tests/                     # Test suite
│   │   ├── __init__.py
│   │   ├── test_models.py
│   │   ├── test_views.py
│   │   └── test_serializers.py
│   └── services/
│       ├── __init__.py
│       └── conversation_service.py # Conversation management
│
├── platform_adapters/             # Platform-specific adapters
│   ├── __init__.py
│   ├── adapter_factory.py         # Factory for creating adapters
│   ├── base_adapter.py            # Abstract base class for adapters
│   ├── apps.py                    # AppConfig for adapters
│   ├── migrations/                # Database migrations
│   │   └── __init__.py
│   ├── webform/                   # Webform platform adapter
│   │   ├── __init__.py
│   │   ├── webform_adapter.py     # Adapter for webform
│   │   └── serializers.py         # Serializers for webform models
│   └── whatsapp/                  # WhatsApp platform adapter
│       ├── __init__.py
│       ├── whatsapp_adapter.py    # Adapter for WhatsApp
│       ├── serializers.py         # Serializers for WhatsApp models
│       └── token_manager.py       # WhatsApp token management
│
├── endpoint_integration/          # External API integration
│   ├── __init__.py
│   ├── message_router.py          # Routes messages to endpoints
│   ├── formatters/                # Message formatting utilities
│   │   ├── __init__.py
│   │   ├── cases_formatter.py     # Cases endpoint formatter
│   │   └── messaging_formatter.py # Messaging endpoint formatter
│   └── tests/                     # Test suite
│       ├── __init__.py
│       └── test_router.py
│
├── shared/                        # Shared utilities and models
│   ├── __init__.py
│   ├── models/                    # Shared models
│   │