# Error Message Policy

## Principle: Don't Blame the User's Network

**NEVER** blame the user's internet connection, VPN, or network in error messages unless we've actually verified that:
1. We can't reach Google.com or other major sites
2. We've confirmed it's a local network issue

## Correct Error Messages

### ✅ GOOD - Service-Side Issue
```
"HeyGen API request timed out after 3 attempts. 
This may indicate the HeyGen API service is slow or unavailable. 
Check HeyGen API status at https://status.heygen.com or try again later."
```

### ✅ GOOD - API Issue
```
"HeyGen API connection failed after 3 attempts: Connection refused. 
This may indicate the HeyGen API service is unavailable or experiencing issues. 
Check HeyGen API status at https://status.heygen.com or try again later."
```

### ❌ BAD - Blaming User's Network
```
"Check your network connection and HeyGen API status."
"Check your internet connection and HeyGen API availability."
```

## Why This Matters

Connection errors can be caused by:
1. **Service-side issues** (most common) - API is down, slow, or overloaded
2. **API endpoint changes** - Service changed their endpoints
3. **Rate limiting** - Too many requests
4. **Authentication issues** - Invalid API key or expired token
5. **Service maintenance** - Planned or unplanned downtime
6. **Local network issues** (rare) - Only if we can verify by testing other sites

## Error Message Template

When a connection/network error occurs:

```python
raise RuntimeError(
    f"[Service Name] API [operation] failed: {error_details}. "
    f"This may indicate the [Service Name] API service is [slow/unavailable/experiencing issues]. "
    f"Check [Service Name] API status at [status_url] or try again later."
)
```

## Files Updated

- ✅ `src/core/avatar_generator.py` - Fixed HeyGen error messages
- ✅ All error messages now focus on service-side issues, not user's network

## Testing

To verify error messages are correct:
1. Test with invalid API keys (should mention API key, not network)
2. Test with service down (should mention service status, not user network)
3. Test with rate limiting (should mention rate limits, not network)

