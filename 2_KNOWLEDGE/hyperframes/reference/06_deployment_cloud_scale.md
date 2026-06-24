# HyperFrames — Deployment & Cloud Scale

Source: https://hyperframes.heygen.com/packages/{aws-lambda,gcp-cloud-run}.md + https://hyperframes.heygen.com/deploy/{cloud,aws-lambda,gcp-cloud-run,templates-on-lambda}.md (fetched 2026-06-24)

Distributed/at-scale rendering: the `@hyperframes/aws-lambda` and `@hyperframes/gcp-cloud-run` packages, HeyGen-hosted cloud rendering, the AWS Lambda + GCP Cloud Run deploy guides, and the templates-at-scale (variables fan-out) pipeline.

**Chooser:**
- `hyperframes render` (local): fastest iteration loop; use while authoring.
- `hyperframes cloud render`: zero-infra; HeyGen runs the render, you pay per credit.
- `hyperframes lambda render`: bring-your-own-AWS distributed rendering, chunked parallelism.
- `hyperframes cloudrun render`: GCP equivalent of lambda.
- In-process vs distributed crossover: single render under ~30s → in-process wins (no S3 round-trip per chunk). Distributed wins for renders over ~60s or personalised batches.

---

# Cloud Rendering (HeyGen-hosted, zero infra)

> Render a composition on HeyGen's hosted cloud — no local Chrome, no FFmpeg, no AWS.

```bash
hyperframes auth login            # one-time sign-in
hyperframes cloud render          # zip → upload → render → download
```

## Authenticate
Credential stored in `~/.heygen/credentials` (mode `0600`), shared with the `heygen` CLI. Default flow opens browser for OAuth 2.0 + PKCE (loopback port). For CI: `hyperframes auth login --api-key` (prompt or `echo "$HEYGEN_API_KEY" | hyperframes auth login --api-key`). Confirm with `hyperframes auth status`.

Resolution order: `HEYGEN_API_KEY` env → `HYPERFRAMES_API_KEY` env → `~/.heygen/credentials`. Backend override: `HEYGEN_API_URL` (default `https://api.heygen.com`). `hyperframes auth refresh`, `hyperframes auth logout`.

## How a cloud render flows
1. Resolve the project (local dir default `.`, or skip upload with `--asset-id`/`--url`).
2. Auto-detect aspect ratio from entry HTML's `data-width`/`data-height`.
3. Zip project (excludes `.git`, `node_modules`, `dist`, `.next`, `coverage`, dotfiles).
4. Upload zip to `POST /v3/assets` → `asset_id`.
5. Submit render to `POST /v3/hyperframes/renders` → `render_id` (queued).
6. Poll `GET /v3/hyperframes/renders/{id}` until complete/failed (skip with `--no-wait`).
7. Download signed video URL to disk.

## Render options (`cloud render [<projectDir>]`)
Zips the project, uploads via `POST /v3/assets`, submits `POST /v3/hyperframes/renders`, polls, streams video to disk.
| Flag | Default | Meaning |
| --- | --- | --- |
| `--fps` | `30` | Frames per second, 1–240 |
| `--quality` | `standard` | `draft`, `standard`, `high` |
| `--format` | `mp4` | `mp4`, `webm`, `mov` (webm/mov carry alpha) |
| `--resolution` | `1080p` | `1080p` or `4k`. 4k billed 1.5×, can't combine with webm/mov |
| `--aspect-ratio` | auto | `16:9`, `9:16`, `1:1`. Auto from local `data-width`/`data-height`; defaults `16:9` for `--asset-id`/`--url` |
| `--composition` / `-c` | `index.html` | Entry HTML file inside the zip |
| `--variables` | — | Inline JSON object overriding `data-composition-variables` |
| `--variables-file` | — | Path to JSON file |
| `--strict-variables` | off | Fail when variables undeclared / wrong type |
| `--title` | — | Free-text label |
| `--output` / `-o` | `renders/<render_id>.<ext>` | Local download destination |

Lifecycle / control flags:
| Flag | Meaning |
| --- | --- |
| `--no-wait` | Submit and exit; print `render_id` |
| `--callback-url` | HTTPS webhook fired when render terminates |
| `--callback-id` | Opaque tracking ID echoed in webhook payloads |
| `--asset-id` | Skip zip+upload; submit already-uploaded composition (mutually exclusive w/ project dir and `--url`) |
| `--url` | Submit a public HTTPS zip URL |
| `--poll-interval` | Poll cadence seconds (default `10`) |
| `--max-wait` | Max poll duration minutes (default `60`) |
| `--idempotency-key` | `Idempotency-Key` for safe retries (1-255 chars `[A-Za-z0-9_:.-]`) |
| `--json` | Machine-readable JSON |

> WARNING: `--resolution 4k` can't combine with `--format webm`/`mov` (4k supersampling runs through screenshot capture, no alpha).

## Templates and variables (cloud)
Declare `data-composition-variables`, fill at render time. For a local project the CLI validates `--variables` against the schema before uploading; for `--asset-id`/`--url` mismatches surface as `hyperframes_project_invalid`. Idiomatic workflow = upload once, re-render many:
```bash
hyperframes cloud render ./card-template            # note asset_id from upload
hyperframes cloud render --asset-id asst_abc123 --variables '{"name":"Ada"}'
```

## Safe retries
`POST /v3/assets` is NOT idempotent on its own — pass `--idempotency-key "$(uuidgen)"` so a 401-triggered retry doesn't duplicate the asset / double-bill. Key forwarded to both upload and submit; server scopes idempotency per-endpoint.

## Managing renders
```bash
hyperframes cloud list                 # --limit (1-100), --token, --all
hyperframes cloud get hfr_def456       # full detail + short-lived signed video_url
hyperframes cloud delete hfr_def456    # soft-delete (--no-confirm)
```
`video_url`/`thumbnail_url` are short-lived presigned URLs — re-fetch via `cloud get`, don't cache.

---

# AWS Lambda (`@hyperframes/aws-lambda` + deploy)

> Distributed rendering: one Lambda function fronts a Step Functions standard workflow that fans renders across many parallel chunk workers, S3 intermediate artifacts.

```bash
npm install @hyperframes/aws-lambda

hyperframes lambda deploy
hyperframes lambda render ./my-project --width 1920 --height 1080 --wait
hyperframes lambda destroy
```

## Architecture
Step Functions state machine: `Plan → Map(N) RenderChunk → Assemble`, dispatching by `event.Action` to one Lambda function (`handler.mjs`) calling `@hyperframes/producer/distributed`. S3 bucket holds plan tarball + per-chunk outputs + final mp4. Handler is thin dispatch: parse event, download inputs from S3 into `/tmp`, call OSS primitive, upload outputs back, return small JSON. Uses `@sparticuz/chromium` by default (build-time fallback to bundle `chrome-headless-shell`).

1. **Plan** — download project archive from S3, run producer planner, upload plan dir.
2. **Render chunks** — Step Functions fans out chunk jobs; each Lambda downloads plan assets, renders one chunk, uploads result.
3. **Assemble** — download all chunks + audio, assemble final output, write to S3.

## Package Exports
| Import | Description |
| --- | --- |
| `@hyperframes/aws-lambda` | Handler types, runtime helpers, S3 transport, client SDK exports |
| `@hyperframes/aws-lambda/handler` | Lambda handler entry point for Step Functions dispatch |
| `@hyperframes/aws-lambda/sdk` | Node SDK: deploy sites, start renders, poll progress, estimate cost |
| `@hyperframes/aws-lambda/cdk` | Optional CDK construct for provisioning the stack |

`aws-cdk-lib` and `constructs` are optional peer dependencies (SDK-only consumers don't need them).

## Prerequisites
| Tool | Why | Install |
| --- | --- | --- |
| AWS credentials | CLI + deploy call AWS APIs | env, `~/.aws/credentials`, SSO, IMDS |
| AWS SAM CLI | `lambda deploy/destroy` shells out to `sam deploy/delete` | AWS SAM install guide |
| `bun` | Builds `packages/aws-lambda/dist/handler.zip` | `npm i -g bun` |
| HyperFrames repo checkout | `lambda deploy` builds handler ZIP from source | set `HYPERFRAMES_REPO_ROOT` if outside checkout |

## Using the SDK
```typescript
import { deploySite, getRenderProgress, renderToLambda } from "@hyperframes/aws-lambda/sdk";

const site = await deploySite({
  projectDir: "./my-composition",
  bucketName: "hyperframes-render-bucket",
});

const handle = await renderToLambda({
  siteHandle: site,
  bucketName: site.bucketName,
  stateMachineArn: "arn:aws:states:us-east-1:123456789012:stateMachine:hyperframes-render",
  config: {
    fps: 30, width: 1920, height: 1080, format: "mp4",
    chunkSize: 240, maxParallelChunks: 16, runtimeCap: "lambda",
  },
});

const progress = await getRenderProgress({ executionArn: handle.executionArn });
console.log(progress.status, progress.overallProgress, progress.costs.displayCost);
```
`renderToLambda()` validates the distributed render config before starting (invalid dimensions/formats/chunk sizes/payload sizes fail synchronously).

## Using the CDK Construct
```typescript
import { App, CfnOutput, Stack } from "aws-cdk-lib";
import { HyperframesRenderStack } from "@hyperframes/aws-lambda/cdk";

const app = new App();
const stack = new Stack(app, "MyApp");
const render = new HyperframesRenderStack(stack, "Render", {
  projectName: "hyperframes",
  lambdaMemoryMb: 10240,
  reservedConcurrency: 8,
  chromeSource: "sparticuz",
});

new CfnOutput(stack, "RenderBucketName", { value: render.bucket.bucketName });
new CfnOutput(stack, "StateMachineArn", { value: render.stateMachine.stateMachineArn });
```
Construct exposes `.bucket`, `.renderFunction`, `.stateMachine`.

## Three deployment paths

### Path 1 — `hyperframes lambda` CLI (recommended)
```bash
hyperframes lambda deploy --stack-name=hyperframes-prod --region=us-east-1 --concurrency=8 --memory=10240
hyperframes lambda render ./my-project --width 1920 --height 1080 --wait
```
Default `--concurrency=8` is conservative (caps worst-case runaway spend at ~`8 × (15 min × 10 GB × $0.0000167/GB-s) ≈ $1.20`). `--wait` streams per-chunk progress + cost; drop it then poll `hyperframes lambda progress <renderId>`.

**Pre-stage with `sites create`** (content-addressed SHA-256, skips re-upload on unchanged tree):
```bash
hyperframes lambda sites create ./my-project   # → Site ID: a1b2c3d4e5f6g7h8
hyperframes lambda render ./my-project --site-id=a1b2c3d4e5f6g7h8 --width 1920 --height 1080 --wait
```

### Path 2 — Direct SAM deploy
Template at `examples/aws-lambda/template.yaml`:
```bash
cd packages/aws-lambda && bun run build:zip   # produces dist/handler.zip
cd ../../examples/aws-lambda
sam deploy --stack-name=hyperframes-prod --region=us-east-1 --resolve-s3 \
  --capabilities CAPABILITY_IAM --no-confirm-changeset \
  --parameter-overrides ChromeSource=sparticuz ReservedConcurrency=8
```
CloudFormation outputs: `RenderBucketName`, `RenderStateMachineArn`, `RenderFunctionArn`.
> WARNING: SAM template default `ReservedConcurrency` is `-1` (unreserved, account-default). The CLI overrides to `8`. Set explicitly here unless you've sized your fan-out.

### Path 3 — CDK construct (see above)

## Lambda CLI subcommands (full)
- `lambda deploy` — builds `dist/handler.zip`, SAM-deploys `examples/aws-lambda/template.yaml`. Writes `<cwd>/.hyperframes/lambda-stack-<stackName>.json`. Idempotent.
- `lambda sites create <projectDir>` — tars+uploads to S3 with content-addressed key, returns reusable `siteId`.
- `lambda render <projectDir>` — starts a Step Functions execution. Returns `renderId` immediately (poll with `lambda progress`) unless `--wait`. `--json`. Variables via `--variables`/`--variables-file` flow into execution input → every chunk worker as `window.__hfVariables`. `--strict-variables` to fail on mismatch.
- `lambda render-batch <projectDir>` — fans out N personalised renders from a JSONL batch file. Deploys site once (or `--site-id`), invokes `renderToLambda` per row. `--max-concurrent` (default 50) caps simultaneous `StartExecution` calls. `--dry-run` prints manifest with `status: "would-invoke"`. `--json`.
  JSONL format:
  ```jsonl
  {"outputKey": "renders/alice.mp4", "variables": {"name": "Alice", "accent": "#ff0000"}}
  {"outputKey": "renders/bob.mp4",   "variables": {"name": "Bob",   "accent": "#0000ff"}}
  {"outputKey": "renders/carol.mp4", "variables": {"name": "Carol"}, "executionName": "hf-carol-001"}
  ```
- `lambda progress <renderId | executionArn>` — one progress snapshot (percent, frames, invocations, cost, errors).
- `lambda destroy` — `sam delete --no-prompts`, drops local state file. Render bucket has CloudFormation `Retain` (survives — empty/delete manually to reclaim storage).
- `lambda policies role | user | validate` — print/validate minimum IAM policy. `validate` checks a checked-in policy still covers required actions (exit non-zero on missing); wire into CI.

State files: `<cwd>/.hyperframes/lambda-stack-<name>.json` (bucket name, state-machine ARN, region).

## IAM permissions
```bash
hyperframes lambda policies user                       # inline policy doc for IAM user
hyperframes lambda policies role --principal=cloudformation
hyperframes lambda policies validate ./infra/iam/hyperframes-deploy.json
```
Generated docs grant `Resource: "*"`; narrow to deployed ARNs after first deploy.

## Cost shape
Billed by GB-seconds (Lambda billed duration × memory) + tiny per-state-transition Step Functions fee. `hyperframes lambda progress` shows running tally (Lambda + SFN). Math in `packages/aws-lambda/src/sdk/costAccounting.ts`.

## Variables size cap (Step Functions)
Variables travel inside the Step Functions Standard execution input, capped at **256 KiB for the entire payload** (Express caps at 32 KiB; HyperFrames uses Standard for history visibility). SDK validates size client-side and rejects oversize inputs before any AWS call. **Convention: variables are typed data; media assets are URL references the composition resolves at render time, never inlined base64.**

## Troubleshooting (AWS)
- `sam deploy` "Stack already exists" — reuse same `--stack-name` (SAM idempotent).
- `iam:CreateRole` not authorized — run `hyperframes lambda policies user`, attach printed policy.
- `PLAN_HASH_MISMATCH` — producer version differs between local `plan()` and deployed ZIP. Re-run `lambda deploy`.
- `BROWSER_GPU_NOT_SOFTWARE` — runtime found non-SwiftShader GL backend. Rebuild ZIP (`bun run --cwd packages/aws-lambda build:zip`), redeploy. Build pins `@sparticuz/chromium` + `--use-gl=swiftshader --use-angle=swiftshader`.
- Stuck at `RUNNING` — usually Lambda cold-start chain on many-chunk renders; reserved concurrency caps parallelism. Check Step Functions execution for typed error names (`FONT_FETCH_FAILED`, `FFMPEG_VERSION_MISMATCH`, etc.).
- Teardown doesn't reclaim S3 — bucket created with `Retain`; empty+delete via console/`aws s3 rb`.

## NOT in v1 surface
- Webhooks on completion (poll instead; `--webhook` on backlog).
- `compositions` discovery verb (point `lambda render` at project dir).
- Multi-region (each `--region` is an independent stack).
- HDR (distributed mode is SDR-only).

## Building the Handler ZIP
```bash
bun install
bun run --cwd packages/aws-lambda build:zip
bun run --cwd packages/aws-lambda verify:zip-size
```
Stages Chromium, Puppeteer, FFmpeg, and the handler bundle into `dist/handler.zip`; size verifier keeps unzipped artifact below Lambda's deployment limit.

---

# Google Cloud Run (`@hyperframes/gcp-cloud-run` + deploy)

> GCP counterpart to AWS Lambda: a single Cloud Run service fronts a Cloud Workflows definition fanning across parallel chunk workers, GCS intermediate artifacts.

```bash
npm install @hyperframes/gcp-cloud-run

hyperframes cloudrun deploy --project my-gcp-project
hyperframes cloudrun render ./my-project --width 1920 --height 1080 --wait
hyperframes cloudrun destroy --project my-gcp-project
```

## Architecture
Cloud Workflows: `Plan → parallel(for chunk) RenderChunk → Assemble`, OIDC-authenticated `http.post` per step to one Cloud Run service (`dist/server.js`) dispatching by `Action` to `@hyperframes/producer/distributed`. GCS bucket for download/upload. Workflow accumulates step results → `{ Plan, Chunks, Assemble }`.

Cloud Run runs a container image → Chrome story collapses to a Dockerfile line (no 250MB ZIP ceiling, no `@sparticuz/chromium` decompression). Gen2 gives up to 60-min request timeout and 32 GiB memory.

## Package Exports
| Import | Description |
| --- | --- |
| `@hyperframes/gcp-cloud-run` | Server handler, event types, GCS transport, client SDK |
| `@hyperframes/gcp-cloud-run/server` | Cloud Run HTTP service entry point |
| `@hyperframes/gcp-cloud-run/sdk` | Node SDK: deploy sites, start renders, poll progress, estimate cost |

Package also includes `terraform/` and a `Dockerfile`.

## Deploying
Terraform module at `packages/gcp-cloud-run/terraform` provisions GCS bucket, Cloud Run service, Cloud Workflows definition, two least-privilege service accounts, runaway-request alert.
```bash
# 1. Build + push render image
gcloud builds submit . --tag us-central1-docker.pkg.dev/PROJECT/hyperframes/hyperframes-render:v1

# 2. Apply the module
cd node_modules/@hyperframes/gcp-cloud-run/terraform
terraform init
terraform apply \
  -var project_id=PROJECT -var region=us-central1 \
  -var image=us-central1-docker.pkg.dev/PROJECT/hyperframes/hyperframes-render:v1
```
Terraform outputs `render_bucket_name`, `service_url`, `workflow_name`, `region`.
> NOTE: target GCP project must have billing enabled (Cloud Run, Cloud Workflows, Artifact Registry, Cloud Build are billed).

## Using the SDK
```typescript
import { getRenderProgress, renderToCloudRun } from "@hyperframes/gcp-cloud-run/sdk";

const handle = await renderToCloudRun({
  projectDir: "./my-composition",
  config: { fps: 30, width: 1920, height: 1080, format: "mp4" },
  bucketName: "hyperframes-render-my-project",
  projectId: "my-project",
  location: "us-central1",
  workflowId: "hyperframes-render",
  serviceUrl: "https://hyperframes-render-abc.us-central1.run.app",
});

let progress = await getRenderProgress({ executionName: handle.executionName });
while (progress.status === "running") {
  await new Promise((r) => setTimeout(r, 5000));
  progress = await getRenderProgress({ executionName: handle.executionName });
}
console.log(progress.status, progress.outputFile, progress.costs.displayCost);
```
Pass `projectDir` for one-shot uploads, or call `deploySite()` separately and reuse the handle. Templates with variables: declare `data-composition-variables`, pass `config.variables`. Cloud Workflows execution argument capped at **512 KiB** — pass media as URL references.

## cloudrun CLI subcommands
- `cloudrun deploy` — enables APIs, builds+pushes image via Cloud Build (unless `--image`), `terraform apply`s the module. Flags: `--project` (required), `--region` (default `us-central1`), `--image`, `--repo` (default `hyperframes`). Sizing: `--cpu` (1/2/4/8, default 4), `--memory` (e.g. `32Gi`, default `16Gi`), `--max-instances` (default 100), `--timeout` (per-request seconds, max 3600).
- `cloudrun sites create <projectDir>` — tar+upload to GCS once, reuse across renders. `--site-id` overrides content hash. Prints `gs://` URI.
- `cloudrun render <projectDir>` — `--width`/`--height` required; `--fps` (24/30/60), `--format`, `--codec`, `--quality`, `--chunk-size`, `--max-parallel-chunks`, `--target-chunk-frames`, `--output-resolution` (deviceScaleFactor supersampling, e.g. `4k`). Variables via `--variables`/`--variables-file`, `--strict-variables`. `--wait` polls until done + prints output URI + cost.
- `cloudrun render-batch <projectDir>` — fan out N renders from JSONL (`--batch users.jsonl`), capped at `--max-concurrent` (default 50). `--dry-run`.
- `cloudrun progress <executionName>` — progress + cost.
- `cloudrun destroy` — `terraform destroy` (force-destroys render bucket).

State file: `~/.hyperframes/cloudrun-state.json` (project id, region, bucket, service URL, workflow id).

## End-to-end smoke
`examples/gcp-cloud-run/scripts/smoke.sh --project my-project --region us-central1` — builds image, applies module, renders fixture at one or more chunk sizes, PSNR-compares against in-process baseline, tears down.

## Supported formats
`mp4` (H.264/H.265), `mov` (ProRes), `webm` (VP9), `png-sequence`. HDR mp4 not supported in distributed mode.

---

# Templates on Lambda (personalised video at scale)

> Render personalised template videos at scale on AWS Lambda using `--variables` and `lambda render-batch`.

```bash
hyperframes lambda render-batch ./my-template --batch ./users.jsonl --width 1920 --height 1080
```
Full loop: declare variables → iterate locally (`hyperframes render`) → deploy once → fan out N renders.

## What's a template
A composition whose top-level HTML declares `data-composition-variables`; reads runtime values via `window.__hyperframes.getVariables()`.
```html
<!doctype html>
<html data-composition-variables='[
  {"id":"title","type":"string","label":"Headline","default":"Welcome"},
  {"id":"accentColor","type":"string","label":"Accent","default":"#0a0a0a"},
  {"id":"avatarUrl","type":"string","label":"Avatar image","default":"/avatars/default.png"}
]'>
<head><meta charset="utf-8"><title>Welcome template</title></head>
<body style="margin:0;background:#f6f5f1">
  <div data-composition-id="root" data-width="1920" data-height="1080" data-duration="5">
    <h1 id="title" style="font:80px Inter,sans-serif">Welcome</h1>
    <div id="accent" style="width:100%;height:8px"></div>
    <img id="avatar" alt="" style="width:240px;height:240px;border-radius:50%" />
  </div>
  <script>
    (function () {
      var v = window.__hyperframes.getVariables();
      document.getElementById("title").textContent = v.title;
      document.getElementById("accent").style.background = v.accentColor;
      document.getElementById("avatar").src = v.avatarUrl;
    })();
  </script>
</body>
</html>
```
`window.__hyperframes.getVariables()` is a global, not a fetchable module. Use a plain `<script>` (not `type="module"`) so the runtime is initialized when the script executes.

## Declaring variables
| Field | Required | Example |
| --- | --- | --- |
| `id` | yes | `"title"` |
| `type` | yes | `"string"`, `"number"`, `"color"`, `"boolean"`, `"enum"` |
| `label` | recommended | `"Headline"` |
| `default` | recommended | `"Welcome"` |

Variables are typed primitives; for structured data, serialise on the caller side and parse back inside the composition:
```html
<html data-composition-variables='[
  {"id":"heroJson","type":"string","label":"Hero copy (JSON)","default":"{\"title\":\"Hi\"}"}
]'>
```
The runtime rejects declaration `type: "object"` (only the five canonical types); it silently drops the declaration, so `--strict-variables` then flags every key as undeclared.

## Local iteration loop
```bash
hyperframes render --variables '{"title":"Hello Alice","accentColor":"#ff0000"}' --output renders/alice-preview.mp4
hyperframes render --variables-file ./alice.json --strict-variables --output renders/alice-preview.mp4
```

## Deploy + pre-stage
```bash
hyperframes lambda deploy                    # once per account/region
hyperframes lambda sites create ./my-template   # → Site ID: abc1234deadbeef0
```

## Single personalised render
```bash
hyperframes lambda render ./my-template \
  --site-id abc1234deadbeef0 --width 1920 --height 1080 \
  --variables '{"title":"Hello Alice","accentColor":"#ff0000"}' \
  --output-key renders/alice.mp4 --wait
```

## Batch pipeline (the headline)
JSONL (one entry per recipient):
```jsonl
{"outputKey": "renders/alice.mp4", "variables": {"title": "Hi Alice", "accentColor": "#ff0000"}}
{"outputKey": "renders/bob.mp4",   "variables": {"title": "Hi Bob",   "accentColor": "#00aa00"}}
```
```bash
hyperframes lambda render-batch ./my-template --batch ./users.jsonl --width 1920 --height 1080 --max-concurrent 5
```
Deploys site once (or `--site-id`), calls `renderToLambda` per row. Variables travel inline per JSONL entry (no `--variables-file`). `--max-concurrent` (default 50) caps simultaneous Step Functions starts. `--json` for machine-readable output; `--dry-run` lints (status `would-invoke`). Poll each `executionArn`/`renderId` with `lambda progress`.

## Programmatic via SDK
```typescript
import { deploySite, renderToLambda } from "@hyperframes/aws-lambda/sdk";

const users = [
  { name: "Alice", accentColor: "#ff0000" },
  { name: "Bob",   accentColor: "#00aa00" },
];

const siteHandle = await deploySite({
  projectDir: "./my-template",
  bucketName: process.env.HYPERFRAMES_BUCKET!,
});

const handles = await Promise.all(
  users.map((user) =>
    renderToLambda({
      siteHandle,
      bucketName: process.env.HYPERFRAMES_BUCKET!,
      stateMachineArn: process.env.HYPERFRAMES_SFN_ARN!,
      config: {
        fps: 30, width: 1920, height: 1080, format: "mp4",
        variables: { title: `Hello ${user.name}`, accentColor: user.accentColor },
      },
      outputKey: `renders/${user.name.toLowerCase()}.mp4`,
    }),
  ),
);
```
`HYPERFRAMES_BUCKET` and `HYPERFRAMES_SFN_ARN` come from the deployed stack (`RenderBucketName`, `RenderStateMachineArn`). Wrap large batches in a semaphore to avoid tripping the Lambda concurrent-execution quota.

## Working with large variables
Step Functions Standard execution input cap = **256 KiB for the entire input**. SDK rejects oversize client-side. Convention: variables = typed data; media = URL references.

Right: `{ "title": "Hello Alice", "accentColor": "#ff0000", "avatarUrl": "https://cdn.example.com/avatars/alice.png" }`
Wrong (explodes): `{ "avatarBase64": "data:image/png;base64,iVBOR..." }`

The composition script assigns the URL to the DOM element; the Lambda chunk worker fetches the asset over the file server during capture (same as local). Same constraint applies to Remotion's `inputProps`.

## Cost and scale knobs
- **`--max-parallel-chunks`** (per render, default 16). Smaller comps don't fan out beyond `ceil(totalFrames / chunkSize)`.
- **`--target-chunk-frames`** (optional per-chunk frame ceiling). Planner uses `clamp(ceil(totalFrames / targetChunkFrames), 1, maxParallelChunks)` chunks; a ceiling, not fixed size; ignored when `--chunk-size` set. Keeps chunks under Lambda's 15-min cap on long videos.
- **Lambda reserved concurrency** (`lambda deploy --concurrency=<N>`): caps parallel invocations of the render function.
- **`render-batch --max-concurrent`**: orchestrator-side cap on simultaneous `StartExecution` calls (distinct from Lambda concurrency).
- **Lambda memory** (`lambda deploy --memory`): default 10 240 MB (max).

Each Step Functions execution fans out to ~`maxParallelChunks` Lambda invocations. If reserved concurrency = 8 and `maxParallelChunks` = 16 default, even a single render throttles — bump deploy concurrency before large batches. For large batches (>1 000), starting point `--max-concurrent ≈ floor(reservedConcurrency / maxParallelChunks)`. Default settings (`chunkSize: 240`, `maxParallelChunks: 16`): a 5s 30fps comp = 1 chunk; 60s ≈ 8 chunks.

## Migrating from @remotion/lambda inputProps
| Remotion | HyperFrames |
| --- | --- |
| `Composition.defaultProps` | `data-composition-variables` declaration on root HTML |
| `useCurrentFrame()` + `props.<x>` | `window.__hyperframes.getVariables().<x>` (read once on DOMContentLoaded) |
| `renderMediaOnLambda({ inputProps })` | `renderToLambda({ config: { variables } })` |
| Lambda inputProps 256 KiB cap | Step Functions execution-input 256 KiB cap |
| inputProps URL'ing pattern for large media | Same convention — URL references, not inlined bytes |
