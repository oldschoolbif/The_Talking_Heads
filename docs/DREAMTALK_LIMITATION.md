# DreamTalk Limitation - Checkpoints Required

## ⚠️ Important Notice

**DreamTalk requires checkpoints that are NOT publicly available.**

This limitation was discovered during integration. DreamTalk checkpoints must be requested via email from the maintainers, which can take days to weeks.

## Current Status

- ✅ **Code Integration:** Complete
- ✅ **dlib Installation:** Complete (dlib-bin 20.0.0)
- ❌ **Checkpoints:** Required but not available
- ⏸️ **Status:** Disabled until checkpoints are obtained

## Impact

DreamTalk is **currently disabled** in the system:

- Default avatar engine changed from `dreamtalk` to `heygen`
- DreamTalk excluded from smoke tests
- DreamTalk provider code remains but is not used

## To Enable DreamTalk

1. **Obtain checkpoints** (see `docs/HOW_TO_GET_DREAMTALK_CHECKPOINTS.md`)
2. **Place checkpoints** in `dreamtalk/checkpoints/`:
   - `denoising_network.pth`
   - `renderer.pt`
3. **Update config** to set `avatar.engine: dreamtalk`
4. **Re-enable** in smoke tests

## Alternative Avatar Providers

While waiting for DreamTalk checkpoints, use:

- **HeyGen** (cloud API) - Currently set as default
- **D-ID** (cloud API) - Available as alternative

Both require API keys and subscriptions but work immediately.

## Lessons Learned

**For future integrations:**
- Check checkpoint/model availability BEFORE starting integration
- Verify all dependencies are publicly available
- Document limitations upfront in integration planning

## Files Modified

- `config/config.yaml` - Changed default engine to `heygen`
- `scripts/smoke_test_avatar_providers.py` - Disabled DreamTalk test
- `src/core/dreamtalk_provider.py` - Code remains but not used

## Re-enabling DreamTalk

Once checkpoints are available:

1. Place files in `dreamtalk/checkpoints/`
2. Update `config/config.yaml`: `avatar.engine: dreamtalk`
3. Uncomment DreamTalk test in `scripts/smoke_test_avatar_providers.py`
4. Run smoke test to verify

