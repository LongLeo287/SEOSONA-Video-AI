# Source: https://developers.heygen.com/reference/create-avatar

Create Avatar

cURL

```
curl --request POST \
  --url https://api.heygen.com/v3/avatars \
  --header 'Content-Type: application/json' \
  --header 'x-api-key: <api-key>' \
  --data '
{
  "type": "<string>",
  "name": "<string>",
  "prompt": "<string>",
  "reference_images": [
    {
      "type": "<string>",
      "url": "<string>"
    }
  ],
  "avatar_group_id": "<string>"
}
'
```

200

400

401

409

429

```
{
  "data": {
    "avatar_item": {
      "id": "<string>",
      "name": "<string>",
      "group_id": "ag_abc123",
      "preview_image_url": "https://files.heygen.ai/look/business_preview.jpg",
      "preview_video_url": "https://files.heygen.ai/look/business_preview.mp4",
      "gender": "female",
      "tags": [
        "<string>"
      ],
      "default_voice_id": "1bd001e7e50f421d891986aad5c8bbd2",
      "supported_api_engines": [
        "<string>"
      ],
      "image_width": 1920,
      "image_height": 1080,
      "status": "completed",
      "error": {
        "code": "<string>",
        "message": "<string>"
      }
    },
    "avatar_group": {
      "id": "<string>",
      "name": "<string>",
      "created_at": 123,
      "looks_count": 123,
      "preview_image_url": "https://files.heygen.ai/avatar/anna_preview.jpg",
      "preview_video_url": "https://files.heygen.ai/avatar/anna_preview.mp4",
      "gender": "female",
      "default_voice_id": "1bd001e7e50f421d891986aad5c8bbd2",
      "consent_status": "approved",
      "status": "completed",
      "error": {
        "code": "<string>",
        "message": "<string>"
      }
    }
  }
}
```

POST

/

v3

/

avatars

Try it

Create Avatar

cURL

```
curl --request POST \
  --url https://api.heygen.com/v3/avatars \
  --header 'Content-Type: application/json' \
  --header 'x-api-key: <api-key>' \
  --data '
{
  "type": "<string>",
  "name": "<string>",
  "prompt": "<string>",
  "reference_images": [
    {
      "type": "<string>",
      "url": "<string>"
    }
  ],
  "avatar_group_id": "<string>"
}
'
```

200

400

401

409

429

```
{
  "data": {
    "avatar_item": {
      "id": "<string>",
      "name": "<string>",
      "group_id": "ag_abc123",
      "preview_image_url": "https://files.heygen.ai/look/business_preview.jpg",
      "preview_video_url": "https://files.heygen.ai/look/business_preview.mp4",
      "gender": "female",
      "tags": [
        "<string>"
      ],
      "default_voice_id": "1bd001e7e50f421d891986aad5c8bbd2",
      "supported_api_engines": [
        "<string>"
      ],
      "image_width": 1920,
      "image_height": 1080,
      "status": "completed",
      "error": {
        "code": "<string>",
        "message": "<string>"
      }
    },
    "avatar_group": {
      "id": "<string>",
      "name": "<string>",
      "created_at": 123,
      "looks_count": 123,
      "preview_image_url": "https://files.heygen.ai/avatar/anna_preview.jpg",
      "preview_video_url": "https://files.heygen.ai/avatar/anna_preview.mp4",
      "gender": "female",
      "default_voice_id": "1bd001e7e50f421d891986aad5c8bbd2",
      "consent_status": "approved",
      "status": "completed",
      "error": {
        "code": "<string>",
        "message": "<string>"
      }
    }
  }
}
```

#### Authorizations

ApiKeyAuthBearerAuthApiKeyAuthBearerAuth

​

x-api-key

string

header

required

HeyGen API key. Obtain from your HeyGen dashboard.

#### Headers

​

Idempotency-Key

string

Optional client-supplied key for safely retrying mutations. Subsequent calls within 24 hours that share this key replay the original response — even if the request body differs slightly (a warning is logged). A retry that arrives while the original is still in flight gets a 409 `request_in_progress`. Keys must be 1–255 characters from `[A-Za-z0-9_:.-]`; a UUID is a safe default. Scope is per-endpoint and per-resource: the same key on a different route or path parameter is independent.

Required string length: `1 - 255`

Pattern: `^[A-Za-z0-9_\-:.]{1,255}$`

#### Body

application/json

* CreatePromptAvatarRequest
* CreateDigitalTwinRequest
* CreatePhotoAvatarRequest

Discriminated union for POST /v3/avatars request body.

​

type

string

required

Must be 'prompt' for AI-generated avatars.

Allowed value: `"prompt"`

​

name

string

required

Name of the avatar.

​

prompt

string

required

Prompt for avatar generation.

Maximum string length: `1000`

​

reference\_images

(AssetUrl · object | AssetId · object | AssetBase64 · object)[] | null

Reference images — each as {"type": "url", "url": "https://..."} or {"type": "asset\_id", "asset\_id": "..."}. Max 3. Will only work with an avatar\_group\_id.

Maximum array length: `3`

Asset input via publicly accessible HTTPS URL.

* AssetUrl
* AssetId
* AssetBase64

Show child attributes

​

avatar\_group\_id

string | null

Optional identity you would like to attach the prompted avatar to. By default it will create a new identity.

#### Response

200

application/json

Successful response

​

data

CreateAvatarResponse · object

Show child attributes

List avatar groupsGet avatar group

⌘I