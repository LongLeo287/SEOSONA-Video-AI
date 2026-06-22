# Source: https://developers.heygen.com/reference/create-video

Create Video

cURL

```
curl --request POST \
  --url https://api.heygen.com/v3/videos \
  --header 'Content-Type: application/json' \
  --header 'x-api-key: <api-key>' \
  --data '
{
  "type": "<string>",
  "avatar_id": "<string>",
  "title": "<string>",
  "aspect_ratio": "16:9",
  "background": {
    "value": "<string>",
    "url": "<string>",
    "asset_id": "<string>"
  },
  "remove_background": true,
  "callback_url": "<string>",
  "callback_id": "<string>",
  "watermark": {
    "image": {
      "type": "<string>",
      "url": "<string>"
    },
    "scale": 1,
    "opacity": 1,
    "placement": {
      "position": "bottom_right",
      "offset_x": 0,
      "offset_y": 0
    }
  },
  "caption": {
    "file_format": "srt",
    "style": "default"
  },
  "output_format": "mp4",
  "script": "<string>",
  "voice_id": "<string>",
  "audio_url": "<string>",
  "audio_asset_id": "<string>",
  "voice_settings": {
    "speed": 1,
    "pitch": 0,
    "volume": 1,
    "locale": "<string>",
    "engine_settings": {
      "engine_type": "<string>",
      "similarity_boost": 0.5,
      "stability": 0.5,
      "style": 0.5,
      "use_speaker_boost": true
    }
  },
  "motion_prompt": "<string>",
  "engine": {
    "type": "<string>"
  }
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
    "video_id": "<string>",
    "status": "<string>",
    "output_format": "mp4"
  }
}
```

POST

/

v3

/

videos

Try it

Create Video

cURL

```
curl --request POST \
  --url https://api.heygen.com/v3/videos \
  --header 'Content-Type: application/json' \
  --header 'x-api-key: <api-key>' \
  --data '
{
  "type": "<string>",
  "avatar_id": "<string>",
  "title": "<string>",
  "aspect_ratio": "16:9",
  "background": {
    "value": "<string>",
    "url": "<string>",
    "asset_id": "<string>"
  },
  "remove_background": true,
  "callback_url": "<string>",
  "callback_id": "<string>",
  "watermark": {
    "image": {
      "type": "<string>",
      "url": "<string>"
    },
    "scale": 1,
    "opacity": 1,
    "placement": {
      "position": "bottom_right",
      "offset_x": 0,
      "offset_y": 0
    }
  },
  "caption": {
    "file_format": "srt",
    "style": "default"
  },
  "output_format": "mp4",
  "script": "<string>",
  "voice_id": "<string>",
  "audio_url": "<string>",
  "audio_asset_id": "<string>",
  "voice_settings": {
    "speed": 1,
    "pitch": 0,
    "volume": 1,
    "locale": "<string>",
    "engine_settings": {
      "engine_type": "<string>",
      "similarity_boost": 0.5,
      "stability": 0.5,
      "style": 0.5,
      "use_speaker_boost": true
    }
  },
  "motion_prompt": "<string>",
  "engine": {
    "type": "<string>"
  }
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
    "video_id": "<string>",
    "status": "<string>",
    "output_format": "mp4"
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

* CreateVideoFromAvatar
* CreateVideoFromImage
* CreateVideoFromCinematicAvatar

Create a video from a HeyGen avatar (video or photo avatar).

Provide an avatar\_id to use a previously created avatar. Supports all
avatar types: studio\_avatar, digital\_twin, and photo\_avatar. Optionally
set `engine` to select Avatar V for eligible avatars; when omitted, the
server defaults to Avatar IV.

​

type

string

required

Must be 'avatar' for avatar-based video creation.

Allowed value: `"avatar"`

​

avatar\_id

string

required

HeyGen avatar ID (video avatar or photo avatar look ID).

​

title

string | null

Display title for the video in the HeyGen dashboard.

​

resolution

enum<string> | null

Output video resolution.

Available options:

`4k`,

`1080p`,

`720p`

​

aspect\_ratio

enum<string> | null

default:16:9

Output video aspect ratio. Supported values: '16:9', '9:16', '4:5', '5:4', '1:1', 'auto'. Defaults to '16:9'. 'auto' preserves the source's aspect ratio (avatar source frames or uploaded image), short-edge anchored to the requested resolution and capped at the tier's long edge. Falls back to '16:9' when source dimensions can't be read.

Available options:

`16:9`,

`9:16`,

`4:5`,

`5:4`,

`1:1`,

`auto`

​

fit

enum<string> | null

How the subject is fitted to the output canvas. 'cover' scales to fill the frame (may crop edges). 'contain' scales to fit entirely within the frame (may show background). When omitted, the server picks the best option based on the source and canvas orientations.

Available options:

`contain`,

`cover`

​

background

BackgroundSetting · object

Background settings for the video.

Show child attributes

​

remove\_background

boolean | null

Remove the avatar background. Video avatars must be trained with matting enabled.

​

callback\_url

string | null

Webhook URL to receive a POST notification when the video is ready.

​

callback\_id

string | null

Caller-defined identifier echoed back in the webhook payload.

​

watermark

WatermarkInput · object

Custom watermark image to overlay on the video (PNG or JPEG). Available as a premium option for select Enterprise customers. To request access, please contact our support team.

Show child attributes

​

caption

CaptionSetting · object

Caption generation settings. A sidecar subtitle file is always returned via subtitle\_url; set 'style' to additionally burn captions into the rendered video.

Show child attributes

​

output\_format

enum<string>

default:mp4

Output container. 'webm' returns a video with a transparent background (alpha channel); 'mp4' (default) returns a standard video. 'webm' requires an avatar that supports matting. When 'webm' is selected, any 'background' value is rejected and background removal is applied automatically — the caller does not need to set 'remove\_background'.

Available options:

`mp4`,

`webm`

​

script

string | null

Text script for the avatar to speak. Pair with voice\_id, or omit voice\_id when using avatar\_id to use the avatar's default voice. Mutually exclusive with audio\_url/audio\_asset\_id.

Minimum string length: `1`

​

voice\_id

string | null

Voice ID for text-to-speech. Required when script is provided, unless avatar\_id is set (the avatar's default voice is used as fallback).

​

audio\_url

string | null

Public URL of an audio file to lip-sync. Mutually exclusive with script.

​

audio\_asset\_id

string | null

HeyGen asset ID of an uploaded audio file. Mutually exclusive with script.

​

voice\_settings

VoiceSettingsInput · object

Voice tuning parameters (speed, pitch, locale).

Show child attributes

​

motion\_prompt

string | null

Natural-language prompt controlling avatar body motion and hand gestures. Supported for photo avatars on either engine, and for video avatars when engine.type is 'avatar\_v'. Rejected for video avatars on the default Avatar IV engine.

​

expressiveness

enum<string> | null

Avatar expressiveness level. Photo avatars only. Defaults to 'low' when omitted. Avatar IV only; rejected when engine.type is 'avatar\_v'.

Available options:

`high`,

`medium`,

`low`

​

engine

AvatarVEngineConfig · object

Avatar V engine configuration with cross-reference-driven animation.

* AvatarVEngineConfig
* AvatarIVEngineConfig

Show child attributes

#### Response

200

application/json

Successful response

​

data

CreateAvatarVideoResponse · object

Show child attributes

List videosGet video

⌘I