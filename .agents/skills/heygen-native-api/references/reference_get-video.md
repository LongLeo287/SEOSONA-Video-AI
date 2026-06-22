# Source: https://developers.heygen.com/reference/get-video

Get Video

cURL

```
curl --request GET \
  --url https://api.heygen.com/v3/videos/{video_id} \
  --header 'x-api-key: <api-key>'
```

200

400

401

404

429

```
{
  "data": {
    "id": "<string>",
    "title": "My Generated Video",
    "created_at": 1711929600,
    "completed_at": 1711930200,
    "video_url": "https://files.heygen.ai/video/abc123.mp4",
    "thumbnail_url": "https://files.heygen.ai/thumb/abc123.jpg",
    "gif_url": "https://files.heygen.ai/gif/abc123.gif",
    "captioned_video_url": "https://files.heygen.ai/video/abc123_captioned.mp4",
    "subtitle_url": "https://files.heygen.ai/srt/abc123.srt",
    "duration": 30.5,
    "folder_id": "folder_abc123",
    "output_language": "en-US",
    "failure_code": "rendering_failed",
    "failure_message": "Avatar rendering timed out",
    "video_page_url": "https://app.heygen.com/video/abc123"
  }
}
```

GET

/

v3

/

videos

/

{video\_id}

Try it

Get Video

cURL

```
curl --request GET \
  --url https://api.heygen.com/v3/videos/{video_id} \
  --header 'x-api-key: <api-key>'
```

200

400

401

404

429

```
{
  "data": {
    "id": "<string>",
    "title": "My Generated Video",
    "created_at": 1711929600,
    "completed_at": 1711930200,
    "video_url": "https://files.heygen.ai/video/abc123.mp4",
    "thumbnail_url": "https://files.heygen.ai/thumb/abc123.jpg",
    "gif_url": "https://files.heygen.ai/gif/abc123.gif",
    "captioned_video_url": "https://files.heygen.ai/video/abc123_captioned.mp4",
    "subtitle_url": "https://files.heygen.ai/srt/abc123.srt",
    "duration": 30.5,
    "folder_id": "folder_abc123",
    "output_language": "en-US",
    "failure_code": "rendering_failed",
    "failure_message": "Avatar rendering timed out",
    "video_page_url": "https://app.heygen.com/video/abc123"
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

#### Path Parameters

​

video\_id

string

required

Unique video identifier

#### Response

200

application/json

Successful response

​

data

VideoDetail · object

Video resource returned by list and detail endpoints.

If `output_language` is present the video is a translated video;
otherwise it is a generated video.

Show child attributes

Create videoDelete video

⌘I