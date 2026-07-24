# Paste-ready update for the V2 Blueprint (Google Doc) + Tracker (Google Sheet)

> Evidence for every line: `8_WORKSPACE/benchmarks/asr_tts_20260714/REPORT.md` + memory
> `vi-asr-tts-benchmark`. The Drive connector is read-only, so paste these blocks manually.

## A. Google Doc — amend §12.2 (Engine mặc định theo boundary)

**Voice (thay đoạn cũ):**
> Voice: OmniVoice (k2-fsa) là engine TTS DUY NHẤT — quyết định chủ dự án 14/07/2026 sau benchmark
> Phase 0 (chất lượng thắng; KHÔNG có backup engine, synth hỏng trả None trung thực). LƯU Ý LICENSE:
> code Apache-2.0 nhưng weights CC-BY-NC (dữ liệu Emilia) — chủ dự án chấp nhận rủi ro, ghi tại
> voice_router.py + 0_SETUP/MODELS.md. VieNeu-TTS (Apache-2.0 toàn phần, engine VN duy nhất còn lại
> có clone) là phương án thay thế sạch license NẾU lập trường NC thay đổi — đã gỡ khỏi legacy,
> chỉ ghi nhận trong hồ sơ. Voice clone vẫn cần consent_id.

**ASR (thay đoạn cũ):**
> ASR: MỘT engine, MỘT model — PhoWhisper-large (CT2 float16, kiendt/PhoWhisper-large-ct2) trên
> runtime faster-whisper/CTranslate2, cuda auto-detect. Căn cứ: benchmark Phase 0 (bản
> medium-ct2 int8 bị lỗi lặp câu đã bị loại; large đạt WER 0.041 gold-set) + khảo sát ngành
> (pipeline chuyên ngữ chọn fine-tune: FunClip→Paraformer-zh, dự án VN→PhoWhisper).
> BỎ khỏi blueprint: (1) whisper.cpp làm runtime — DTW word-timestamp không hỗ trợ fine-tune
> PhoWhisper, CT2 là runtime đã chứng minh; (2) WhisperX alignment — aligner tiếng Việt của nó
> (wav2vec2-base-vi-vlsp2020) là CC-BY-NC, không được vào pipeline thương mại; word-timestamp
> của faster-whisper là đường sạch.

**GenVideo (bổ sung §10):**
> Tuyến local (LTX-Video) đã gỡ 14/07/2026 (nặng tài nguyên, xung VRAM với render — mục tiêu tốc độ
> thắng). Engine #6 ở chế độ PROMPT-ONLY (prompt-director + shotlist); nhà cung cấp trả phí
> (fal/Replicate/BytePlus) kích hoạt khi có key chính chủ. Kế hoạch khi bật API: 6_SOP/LTX_BROLL_PLAN.md.

**Lipsync/avatar (xác nhận §14.4 RETIRE):**
> Toàn tuyến lipsync/avatar (MuseTalk/SadTalker/LivePortrait/Rhubarb/mascot engines) đã XÓA khỏi
> legacy 14/07/2026 (~22,6GB). KHÔNG rebuild trong legacy; V2 chỉ xem xét lại ở Phase 6 nếu có nhu cầu thật.

## B. Google Sheet — tab 00 Điều hành (cập nhật dòng "Điểm gate gần nhất")

| Trường | Giá trị mới |
|---|---|
| Trạng thái | **Phase 0 GATE PASS (14/07/2026)** → Phase 1 đang code |
| Ghi chú | Đủ 4 hạng mục gate, evidence trong legacy repo `docs/v2_phase0/`: LEGACY_CAPABILITY_MATRIX.md + fixtures.json (10/10, sha256) + ADR.md (001–005) + GATE_REVIEW.md; benchmark đã có từ trước. Monorepo V2 khởi tạo tại `D:\SEOSONA AI\seosona-video-os` (TypeScript+zod+vitest: contracts, timeline-ir, control-plane state machine fail-closed, event ledger, artifact store content-addressed). Gate P1 = fixture fx01 chạy hết typed contracts + invalid transition fail-closed. LƯU Ý: gate P4 (8/10 reviewer duyệt) và P5 (publish receipt thật) cần CHỦ DỰ ÁN — không tự hoàn thành được. |

## C. Google Sheet — tab 17 Nhật ký thay đổi (thêm các dòng)

| Ngày | Thay đổi | Evidence |
|---|---|---|
| 2026-07-14 | Benchmark Phase 0 ASR/TTS tiếng Việt: 4 TTS × 4 ASR × 12 câu gold + 6 clip giọng thật | 8_WORKSPACE/benchmarks/asr_tts_20260714/REPORT.md |
| 2026-07-14 | QUYẾT ĐỊNH: OmniVoice = voice duy nhất (chấp nhận CC-BY-NC); gỡ VieNeu + mọi engine TTS khác | voice_router.py, MODELS.md |
| 2026-07-14 | QUYẾT ĐỊNH: PhoWhisper-large-ct2 = ASR duy nhất; loại medium-ct2 lỗi; ct2 4.8.1 + omnivoice 0.2.0 | asr_router.py, benchmark REPORT |
| 2026-07-14 | Gỡ toàn tuyến lipsync/avatar (~22,6GB) + LTX local (~23,7GB → prompt-only) + clone tham khảo | MODELS.md mục Deleted |
| 2026-07-14 | Sửa bẫy tái sinh: requirements.txt gốc → pointer 0_SETUP; quy tắc vị trí output vào STRUCTURE.md | requirements.txt, STRUCTURE.md §Output placement |
| 2026-07-14 | Sửa blueprint §12.2: bỏ whisper.cpp runtime + WhisperX vi-aligner (NC) | mục A ở trên |
