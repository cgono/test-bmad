# Deferred Work

## Deferred from: code review of 6-2-add-per-line-pronunciation-playback-controls (2026-03-30)

- `cancelPlaybackIfActiveRef.current` reassigned on every render (stable-ref-callback pattern) — works correctly but any future non-ref closure dependency will silently break cleanup without a linter warning
- No `:active` CSS press state on `.pinyin-playback-button` — touch users see no press feedback while holding
- No test for `voiceschanged` event firing during active playback — unlikely but untested state transition
- `lineKey` includes `groupIndex` alongside `line_id` — could mismatch if group order shifts; unlikely in practice given deterministic `groupSegmentsByLine` output
- Fallback message not shown before first successful result — `speechFallbackMessage` is set on mount but the `<p>` is gated inside `pinyinSegments.length > 0`; acceptable for current story scope

## Deferred from: code review of 6-3-add-full-page-sequential-pronunciation-playback (2026-03-30)

- `onSequenceEnd` closes over render-scope `lineGroups` — safe via session guard but fragile; future weakening of session guard would silently break sequence advancement
- `buildLineKey` still embeds `groupIndex` — violates Story 6.2 "stable identifiers" deferred note; not worsened but not resolved
- Cancel/`onend` race on Safari — simultaneous `onend` + stop click can cause spurious extra `speak` call before cancel runs; session guard ultimately recovers
- Backend regression unverified — pre-existing local `pytest` environment failure; story makes no backend changes
- `handlePagePlayback` skips `!speechSynthesis` guard — benign since `startUtterance` catches it, but `cancelPlayback` fires unnecessarily in unsupported browsers
