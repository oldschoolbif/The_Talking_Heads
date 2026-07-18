# API Version Policy

## Principle

**Always check for and use the newest stable version of any APIs used in the project. We want all of the latest features that we can reliably use.**

## Implementation Checklist

When integrating or updating APIs:

1. ✅ **Check Official Documentation** - Visit the provider's official docs for latest API version
2. ✅ **Verify Endpoint URLs** - Ensure base URLs point to the latest stable version
3. ✅ **Test API Connectivity** - Verify endpoints are accessible and functional
4. ✅ **Review Changelog** - Check for breaking changes or new features
5. ✅ **Update Configuration** - Set base URLs and endpoints to latest versions
6. ✅ **Test Integration** - Verify the integration works with new version
7. ✅ **Document Version** - Note the API version in code comments and config

## Current API Versions

### ElevenLabs
- **Version**: v1 (latest stable)
- **Base URL**: `https://api.elevenlabs.io/v1`
- **Status**: ✅ Working
- **Last Checked**: 2024

### D-ID
- **Version**: Latest (no version in URL)
- **Base URL**: `https://api.d-id.com`
- **Status**: ⚠️ Request format issue - may not support direct audio uploads
- **Last Checked**: 2024
- **Issue**: API expects `audio_url` (public URL) or `script` (TTS), not direct file uploads

### HeyGen
- **Version**: v1 (decommissioned), v2 (status unknown)
- **Base URL**: `https://api.heygen.com/v2` (updated)
- **Status**: ❌ v1 decommissioned, v2 needs testing
- **Last Checked**: 2024

### Azure Speech
- **Version**: Latest
- **Base URL**: Region-specific
- **Status**: ✅ Configured
- **Last Checked**: 2024

## Maintenance

- Review API versions quarterly
- Monitor provider announcements for version updates
- Update immediately when new stable versions are released
- Test thoroughly after version updates

