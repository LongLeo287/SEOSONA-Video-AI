# Source: https://developers.heygen.com/reference/create-video-translation

Create Video Translation

cURL

```
curl --request POST \
  --url https://api.heygen.com/v3/video-translations \
  --header 'Content-Type: application/json' \
  --header 'x-api-key: <api-key>' \
  --data '
{
  "video": {
    "type": "<string>",
    "url": "<string>"
  },
  "output_languages": [
    "<string>"
  ],
  "title": "<string>",
  "audio": {
    "type": "<string>",
    "url": "<string>"
  },
  "input_language": "<string>",
  "translate_audio_only": false,
  "speaker_num": 123,
  "mode": "speed",
  "callback_url": "<string>",
  "callback_id": "<string>",
  "enable_caption": false,
  "keep_the_same_format": true,
  "enable_dynamic_duration": true,
  "disable_music_track": false,
  "enable_speech_enhancement": false,
  "enable_watermark": false,
  "start_time": 123,
  "end_time": 123,
  "brand_voice_id": "<string>",
  "brand_glossary_id": "<string>",
  "stock_voice_config": {
    "use_stock_voice": false,
    "preferred_stock_voice_ids": [
      "<string>"
    ]
  },
  "srt": {
    "type": "<string>",
    "url": "<string>"
  },
  "folder_id": "<string>"
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
    "video_translation_ids": [
      "<string>"
    ]
  }
}
```

POST

/

v3

/

video-translations

Try it

Create Video Translation

cURL

```
curl --request POST \
  --url https://api.heygen.com/v3/video-translations \
  --header 'Content-Type: application/json' \
  --header 'x-api-key: <api-key>' \
  --data '
{
  "video": {
    "type": "<string>",
    "url": "<string>"
  },
  "output_languages": [
    "<string>"
  ],
  "title": "<string>",
  "audio": {
    "type": "<string>",
    "url": "<string>"
  },
  "input_language": "<string>",
  "translate_audio_only": false,
  "speaker_num": 123,
  "mode": "speed",
  "callback_url": "<string>",
  "callback_id": "<string>",
  "enable_caption": false,
  "keep_the_same_format": true,
  "enable_dynamic_duration": true,
  "disable_music_track": false,
  "enable_speech_enhancement": false,
  "enable_watermark": false,
  "start_time": 123,
  "end_time": 123,
  "brand_voice_id": "<string>",
  "brand_glossary_id": "<string>",
  "stock_voice_config": {
    "use_stock_voice": false,
    "preferred_stock_voice_ids": [
      "<string>"
    ]
  },
  "srt": {
    "type": "<string>",
    "url": "<string>"
  },
  "folder_id": "<string>"
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
    "video_translation_ids": [
      "<string>"
    ]
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

Request body for POST /v3/video-translations.

​

video

AssetUrl · object

required

Asset input via publicly accessible HTTPS URL.

* AssetUrl
* AssetId

Show child attributes

​

output\_languages

string[]

required

Target language names (e.g. 'Chinese (Cantonese, Traditional)', 'Spanish (Spain)', 'English'). Use GET /v3/video-translations/languages for valid values. Use one for single translation, multiple for batch.

Minimum array length: `1`

​

title

string | null

Title for the translation job

​

audio

AssetUrl · object

Asset input via publicly accessible HTTPS URL.

* AssetUrl
* AssetId

Show child attributes

​

input\_language

string | null

Source language code (auto-detected if omitted)

​

translate\_audio\_only

boolean

default:false

Only translate audio, keep original video

​

speaker\_num

integer | null

Number of speakers (improves speaker separation)

​

mode

enum<string>

default:speed

Translation quality mode: 'speed' (faster) or 'precision' (higher quality, uses avatar inference)

Available options:

`speed`,

`precision`

​

callback\_url

string | null

Webhook URL for completion notifications

​

callback\_id

string | null

ID included in webhook payload

​

enable\_caption

boolean

default:false

Generate captions for translated video

​

keep\_the\_same\_format

boolean | null

Preserve the source video's encoding specs (resolution, bitrate).

​

enable\_dynamic\_duration

boolean

default:true

Allow dynamic duration adjustment

​

disable\_music\_track

boolean

default:false

Remove background music

​

enable\_speech\_enhancement

boolean

default:false

Enhance speech quality

​

enable\_watermark

boolean

default:false

Add watermark to output

​

start\_time

number | null

Start time in seconds for partial translation

​

end\_time

number | null

End time in seconds for partial translation

​

brand\_voice\_id

string | null

Brand glossary ID for custom term translations. Legacy field name for `brand_glossary_id` — both are accepted and resolve to the same workspace record. Discover IDs via GET /v3/brand-glossaries.

​

brand\_glossary\_id

string | null

Brand glossary ID for custom term translations (e.g. translate 'Reformer' as the Pilates equipment, not 'political activist'). Alias for the legacy `brand_voice_id` field. Discover IDs via GET /v3/brand-glossaries.

​

stock\_voice\_config

StockVoiceConfig · object

Opt into Stock TTS instead of Voice Clone. Set use\_stock\_voice=true to route the request to a stock voice; optionally pin specific voices via preferred\_stock\_voice\_ids. Gated by per-space and per-locale Nacos allowlists.

Show child attributes

​

srt

AssetUrl · object

Asset input via publicly accessible HTTPS URL.

* AssetUrl
* AssetId

Show child attributes

​

srt\_role

enum<string> | null

Which video the subtitle applies to: 'input' (source) or 'output' (translated). Enterprise plan only.

Available options:

`input`,

`output`

​

fps\_mode

enum<string> | null

Frame rate mode for the output video. 'vfr' = variable frame rate, 'cfr' = constant frame rate, 'passthrough' = match the source. Only takes effect when a custom 'audio' track is provided.

Available options:

`vfr`,

`cfr`,

`passthrough`

​

folder\_id

string | null

Project/folder ID to organize translation into

#### Response

200

application/json

Successful response

​

data

VideoTranslationCreateResponse · object

Response for POST /v3/video-translations.

Show child attributes

List video translationsGet video translation

⌘I