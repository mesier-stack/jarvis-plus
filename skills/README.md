# ULTRON Skills

Each skill lives in its own folder and may include a `manifest.json` describing its name, version, permissions and status.

ULTRON currently treats external skills as registered metadata only. It does not auto-execute arbitrary plugin code. Future skill execution should remain permission-gated and explicitly enabled.

Example manifest:

```json
{
  "name": "Example Skill",
  "version": "1.0.0",
  "status": "disabled",
  "permissions": ["read_local_context"]
}
```
