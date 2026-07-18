# HeyGen API Error Handling

## Overview

The HeyGen provider includes comprehensive error handling for all external API interactions. This document outlines the error handling strategy and common error scenarios.

## Error Handling Principles

1. **Always create robust error handling for external APIs** - This is a core principle for all API integrations
2. **Provide detailed, actionable error messages** - Help users understand what went wrong and how to fix it
3. **Implement retry logic for transient errors** - Network issues, rate limits, and server errors should be retried
4. **Validate inputs before API calls** - Catch configuration errors early
5. **Handle all HTTP status codes** - Each status code has specific handling logic

## Error Categories

### Input Validation Errors

- **Missing API Key**: `ValueError` with instructions to set `HEYGEN_API_KEY`
- **Missing Text**: `ValueError` explaining that text is required for HeyGen v2
- **Invalid Avatar ID**: `ValueError` with guidance on using valid HeyGen avatar IDs
- **Missing Audio File**: `ValueError` with file path information

### Network Errors

- **Timeout**: Retries with exponential backoff (3 attempts)
- **Connection Error**: Retries with exponential backoff (3 attempts)
- **Request Exception**: Wrapped with context about network/API issues

### HTTP Status Code Handling

- **401 Unauthorized**: Authentication failed - check API key
- **403 Forbidden**: Access denied - check permissions/subscription
- **404 Not Found**: Endpoint not found - API may have changed
- **429 Too Many Requests**: Rate limited - retries with `Retry-After` header
- **500 Internal Server Error**: Server error - retries with exponential backoff
- **400 Bad Request**: Detailed error message with common causes listed

### API Response Errors

- **Invalid JSON**: Error message includes response text snippet
- **API-Level Errors**: Extracts error code and message from response
- **Missing video_id**: Shows response structure for debugging
- **Missing video_url**: Provides video_id for manual retrieval

### Polling Errors

- **404 During Polling**: Normal initially - continues polling (videos take time to appear)
- **Timeout**: Detailed message with video_id for manual retrieval
- **Status Errors**: Extracts error details from API response
- **Network Errors During Polling**: Continues polling, logs warnings

## Retry Logic

- **Max Retries**: 3 attempts for transient errors
- **Exponential Backoff**: Starts at 2 seconds, doubles each retry
- **Rate Limit Handling**: Respects `Retry-After` header when provided
- **Server Error Retries**: 500 errors are retried automatically

## Error Messages

All error messages include:
- **What went wrong**: Clear description of the error
- **Why it might have happened**: Common causes or context
- **How to fix it**: Actionable steps or suggestions
- **Relevant IDs**: API keys (masked), video IDs, avatar IDs for debugging

## Example Error Messages

### Authentication Error
```
HeyGen API authentication failed (401 Unauthorized). 
Check that your API key is correct. Key starts with: abc123xyz...
```

### Rate Limit Error
```
HeyGen API rate limit exceeded (429 Too Many Requests). 
Wait before making more requests or upgrade your subscription plan.
```

### Invalid Input Error
```
HeyGen API error (400): video_inputs.0.voice.text.input_text is invalid: Field required

Common causes:
- Invalid avatar_id: 'Abigail_expressive_2024112501'
- Invalid voice_id: 'e0cc82c22f414c95b1f25696c732f058'
- Text too long or contains invalid characters
- Missing required fields in payload
```

### Timeout Error
```
HeyGen video generation timed out after 300 seconds (video_id: abc123...). 
Last error: Connection error polling https://api.heygen.com/v2/videos/abc123...
The video may still be processing. 
You can check its status manually using the HeyGen API with video_id: abc123...
```

## Best Practices

1. **Always wrap API calls in try/except blocks**
2. **Provide context in error messages** (IDs, parameters, etc.)
3. **Log warnings for retries** so users know what's happening
4. **Continue polling on 404s** - videos take time to appear
5. **Extract detailed error info** from API responses when available
6. **Handle edge cases** - missing fields, null values, unexpected formats

## Testing Error Handling

To test error handling:
1. Use invalid API keys
2. Use invalid avatar/voice IDs
3. Simulate network timeouts
4. Test with rate-limited responses
5. Test with malformed API responses

