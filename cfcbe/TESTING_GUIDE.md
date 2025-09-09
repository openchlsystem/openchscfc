# CPIMS Adapter Testing Guide

## Prerequisites

1. **Python Environment**: Ensure you have Python 3.8+ and Django installed
2. **Database**: Run migrations if needed
3. **Environment Variables**: Configure CPIMS settings in `.env` file

## Environment Configuration

### Required Environment Variables

Create/update your `.env` file with:

```bash
# CPIMS Configuration
CPIMS_ENDPOINT_URL=https://test.cpims.net/api/v1/crs/
CPIMS_AUTH_TOKEN=330764ede3eb59acca76b8f064b84eb477ff452e
DISABLE_SSL_VERIFICATION=False

# Optional: Geo endpoint (uses default if not set)
CPIMS_GEO_ENDPOINT_URL=https://test.cpims.net/api/v1/geo/
```

## Quick Start Commands

### 1. Start the Server
```bash
# Navigate to project directory
cd /path/to/your/cfcbe

# Check for any issues
python manage.py check

# Start development server
python manage.py runserver 8000
```

### 2. Test Endpoint Availability
```bash
# Test server is running
curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/admin/
# Should return: 302 (redirect - server is working)
```

## Testing the CPIMS Adapter

### Test Payload Structure

The CPIMS adapter expects helpline data in this array-based format:

```json
{
  "cases": [
    [
      "CASE_ID",           // [0] Case ID
      "TIMESTAMP",         // [1] Created timestamp
      "USER",              // [2] User
      // ... more fields up to index 52
      "NARRATIVE",         // [39] Case narrative
      "PLAN",              // [40] Case plan  
      "OB_NUMBER",         // [41] Police OB number
      // ... more fields
    ]
  ],
  "reporters": [
    [
      "REPORTER_ID",       // [0] Reporter ID
      "TIMESTAMP",         // [1] Timestamp
      "USER",              // [2] User
      // ... more fields
      "FULL_NAME",         // [6] Reporter full name
      // ... more fields
      "PHONE",             // [9] Reporter phone
      "EMAIL",             // [10] Reporter email
      // ... more fields up to index 48
      "RELATIONSHIP"       // [48] Relationship to case
    ]
  ],
  "clients": [
    [
      "CLIENT_ID",         // [0] Client ID
      "TIMESTAMP",         // [1] Timestamp
      "USER",              // [2] User
      // ... more fields
      "FULL_NAME",         // [7] Client full name
      "DATE_OF_BIRTH",     // [13] Date of birth
      "GENDER",            // [18] Gender (Male/Female)
      "TRIBE",             // [27] Tribe
      "RELIGION",          // [28] Religion
      "COUNTY",            // [33] County name
      "CONSTITUENCY",      // [34] Constituency name  
      "WARD",              // [35] Ward name
      // ... more fields
      "PHYSICAL_CONDITION", // [57] Physical condition
      "OTHER_CONDITION",   // [59] Other conditions
      "IN_SCHOOL",         // [63] In school (Yes/No)
      "SCHOOL_LEVEL",      // [67] School level/class
      "SCHOOL_NAME",       // [69] School name
      // ... more fields
      "ECONOMIC_STATUS"    // [86] Economic status
    ]
  ],
  "perpetrators": [
    [
      "PERP_ID",           // [0] Perpetrator ID
      "TIMESTAMP",         // [1] Timestamp
      "USER",              // [2] User
      // ... more fields
      "FULL_NAME",         // [7] Perpetrator full name
      "GENDER",            // [18] Gender
      // ... more fields
      "RELATIONSHIP"       // [49] Relationship to victim
    ]
  ]
}
```

### Sample Test Request

#### Option A: Using curl

Create a test file `test_case.json`:
```json
{
  "cases": [
    [
      "TEST001", "1703678400", "test_user", "", "", "", "", "", "", "", "", "", "", "", "",
      "Sexual Exploitation and abuse", "Online harassment", "Chronic/On-going event", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "",
      "High", "", "", "", "Child reported online harassment by stranger", "Provide counseling", "OB/001/2024", "Central Police", "", "", "", "", "", "", "", "", "", "", "Online platform", "1703678400"
    ]
  ],
  "reporters": [
    [
      "REP001", "1703678400", "test_user", "", "", "", "Jane Doe", "", "", "0700123456", "jane@email.com", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "Self"
    ]
  ],
  "clients": [
    [
      "CLIENT001", "1703678400", "test_user", "", "", "", "", "Mary Smith", "", "", "", "", "", "946684800", "", "", "", "", "Female", "", "", "", "", "", "", "", "", "Kikuyu", "Christian", "", "", "", "Nairobi Central", "Nairobi", "Starehe", "Central Ward", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "Appears Normal", "", "Appears Normal", "", "", "None", "Yes", "", "", "", "Grade 8", "", "Test School", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "Middle Income (apparent)"
    ]
  ],
  "perpetrators": [
    [
      "PERP001", "1703678400", "test_user", "", "", "", "", "Unknown Person", "", "", "", "", "", "", "", "", "", "", "Male", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "Strangers"
    ]
  ]
}
```

Test the endpoint:
```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -d @test_case.json \
  http://localhost:8000/api/webhook/helpline/cpims/abuse/ \
  -v
```

#### Option B: Using Python requests

```python
import requests
import json

# Test payload
payload = {
    "cases": [["TEST001", "1703678400", "test_user", "", "", "", "", "", "", "", "", "", "", "", "", "Sexual Exploitation and abuse", "Online harassment", "Chronic/On-going event", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "High", "", "", "", "Child reported online harassment", "Provide counseling", "OB/001/2024", "", "", "", "", "", "", "", "", "", "", "", "", "Online", "1703678400"]],
    "reporters": [["REP001", "1703678400", "test_user", "", "", "", "Jane Doe", "", "", "0700123456", "jane@email.com", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "Self"]],
    "clients": [["CLIENT001", "1703678400", "test_user", "", "", "", "", "Mary Smith", "", "", "", "", "", "946684800", "", "", "", "", "Female", "", "", "", "", "", "", "", "", "Kikuyu", "Christian", "", "", "", "Nairobi Central", "Nairobi", "Starehe", "Central Ward", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "Appears Normal", "", "Appears Normal", "", "", "None", "Yes", "", "", "", "Grade 8", "", "Test School", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "Middle Income (apparent)"]],
    "perpetrators": [["PERP001", "1703678400", "test_user", "", "", "", "", "Unknown Person", "", "", "", "", "", "", "", "", "", "", "Male", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "Strangers"]]
}

# Send request
response = requests.post(
    'http://localhost:8000/api/webhook/helpline/cpims/abuse/',
    json=payload,
    headers={'Content-Type': 'application/json'}
)

print(f"Status Code: {response.status_code}")
print(f"Response: {response.json()}")
```

## Expected Responses

### Success Response
```json
{
  "status": "success",
  "message": "Case successfully sent to CPIMS",
  "cpims_response": {
    "case_id": "335bc1c1-8a41-11f0-8c80-22a3499bfe31",
    "case_serial": "XXXX",
    "county": "GPR",
    "constituency": "GDI",
    // ... more CPIMS response data
  }
}
```

### Error Response  
```json
{
  "status": "error",
  "message": "CPIMS API error: 400",
  "details": "Field validation errors from CPIMS"
}
```

## Key Features Being Tested

1. **Data Validation**: Required fields (cases, reporters, clients)
2. **Geographic Lookup**: County/constituency names → CPIMS codes
3. **Category Mapping**: Case categories → CPIMS item_ids  
4. **Field Mapping**: All helpline values → CPIMS codes
5. **Authentication**: CPIMS API token validation
6. **Error Handling**: Proper error responses

## Common Issues & Solutions

### Issue: "Missing required field"
**Solution**: Ensure your payload has `cases`, `reporters`, and `clients` arrays

### Issue: "CPIMS API error: 401"  
**Solution**: Check your `CPIMS_AUTH_TOKEN` in environment variables

### Issue: "CPIMS API error: 400" with field validation
**Solution**: Check the `details` field for specific validation errors

### Issue: Server not responding
**Solution**: 
```bash
# Check if server is running
curl http://localhost:8000/admin/

# Restart server if needed
python manage.py runserver 8000
```

## Debugging

### Enable Detailed Logging
Add this to your Django settings:
```python
LOGGING = {
    'version': 1,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'platform_adapters.cpims': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    },
}
```

### Check Server Logs
The adapter provides detailed logging:
- 🌍 Location extraction and mapping
- 🔍 Geo lookup results  
- 📂 Category mapping results
- 📤 Payload being sent to CPIMS
- ✅/❌ CPIMS response status

## Testing Checklist

- [ ] Server starts without errors
- [ ] Endpoint responds (not 404)
- [ ] Sample payload validates  
- [ ] Geographic lookup works
- [ ] Category mapping works
- [ ] CPIMS API accepts payload
- [ ] Success response received
- [ ] Error handling works for bad data

## Production Considerations

1. **Environment Variables**: Set production CPIMS URL and token
2. **SSL Verification**: Set `DISABLE_SSL_VERIFICATION=False` for production
3. **Error Monitoring**: Monitor logs for failed CPIMS submissions
4. **Rate Limiting**: Consider CPIMS API rate limits
5. **Authentication**: Ensure CPIMS token is kept secure

## Support

If you encounter issues:
1. Check server logs for detailed error messages
2. Verify environment variables are set correctly  
3. Test with the sample payload first
4. Check CPIMS API documentation for field requirements