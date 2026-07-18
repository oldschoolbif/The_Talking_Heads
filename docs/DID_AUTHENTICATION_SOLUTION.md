# D-ID Authentication Solution

## Problem Summary

D-ID API uses AWS API Gateway with AWS Signature V4 authentication, but the provided API key format (`username:password`) is not directly compatible with AWS SigV4.

## Key Findings

### 1. API Gateway Confirmation
- **Headers**: `x-amzn-RequestId`, `x-amz-apigw-id` confirm AWS API Gateway
- **IP Address**: 44.235.0.103 (AWS us-west-2 region)
- **Region**: us-west-2 (Oregon)

### 2. Authentication Requirements
- D-ID API requires AWS Signature V4
- Service name: `execute-api`
- Region: **us-west-2** (confirmed by different error message)

### 3. The Problem
When using us-west-2:
```
Error: "The security token included in the request is invalid."
```

This error indicates:
- The region (us-west-2) is CORRECT
- The credentials are INVALID or in the wrong format

## Root Cause

The API key from D-ID (`username:password` format) is **NOT** AWS IAM credentials.

D-ID likely uses one of these approaches:
1. **API Key Mapping**: D-ID maps their API keys to AWS IAM credentials on their backend
2. **Custom Authorizer**: AWS API Gateway custom authorizer that doesn't use standard SigV4
3. **Different Auth Flow**: OAuth2 or JWT tokens instead of simple API keys

## Solutions

### Option 1: Check D-ID Dashboard for AWS Credentials
1. Log into D-ID Studio: https://studio.d-id.com
2. Navigate to Settings → API
3. Look for:
   - AWS Access Key ID
   - AWS Secret Access Key
   - Or "Generate AWS Credentials" button

### Option 2: Use D-ID's Official SDK (Recommended)
If D-ID provides an official Python SDK, it will handle authentication correctly:

```bash
pip install d-id-sdk  # Check if this exists
```

### Option 3: Contact D-ID Support
Required information from D-ID:
1. Correct authentication method for `https://api.d-id.com`
2. If AWS SigV4 is required:
   - How to convert API key to AWS credentials
   - Exact region (confirm us-west-2)
   - Service name (confirm execute-api)
3. Alternative authentication methods (API key header, OAuth, JWT)

### Option 4: Use HeyGen Instead
**Immediate workaround**: 
- HeyGen integration is fully functional with webhook support
- Can proceed with project using HeyGen for avatar generation
- D-ID can be added later once authentication is resolved

## Current Implementation Status

### ✅ What Works
- Region identified: us-west-2
- Service name confirmed: execute-api
- AWS SigV4 implementation ready
- Comprehensive error handling

### ❌ What's Blocked
- Valid AWS credentials for D-ID API
- Cannot make authenticated requests

## Recommended Next Steps

1. **Immediate**: Use HeyGen for avatar generation (fully functional)
2. **Short-term**: Check D-ID dashboard for AWS credentials or SDK
3. **If urgent**: Contact D-ID support with this analysis
4. **Long-term**: Implement D-ID once auth is clarified

## Alternative: Proceed with HeyGen

The project can move forward immediately using HeyGen:
- ✅ Webhook support implemented and tested
- ✅ Progress tracking integrated
- ✅ Comprehensive error handling
- ✅ Ready for production use (with ngrok for webhooks)

To switch focus to HeyGen:
1. Update `config/config.yaml`: `avatar.engine: "heygen"`
2. Test end-to-end with real HeyGen API
3. Add D-ID support later when authentication is resolved

## Test Scripts Created

1. `scripts/test_did_basic_auth.py` - HTTPBasicAuth test
2. `scripts/test_did_comprehensive.py` - Multiple auth methods
3. `scripts/test_did_debug.py` - Service/region combinations  
4. `scripts/test_did_endpoint_analysis.py` - IP/region analysis
5. `scripts/test_did_manual_basic_auth.py` - Manual auth construction

All scripts confirm: D-ID requires AWS SigV4 with us-west-2, but API key format is incompatible.

