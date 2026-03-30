# Deferred Work

## Deferred from: code review of 6-2-add-per-line-pronunciation-playback-controls (2026-03-30)

- `cancelPlaybackIfActiveRef.current` reassigned on every render (stable-ref-callback pattern) — works correctly but any future non-ref closure dependency will silently break cleanup without a linter warning
- No `:active` CSS press state on `.pinyin-playback-button` — touch users see no press feedback while holding
- No test for `voiceschanged` event firing during active playback — unlikely but untested state transition
- `lineKey` includes `groupIndex` alongside `line_id` — could mismatch if group order shifts; unlikely in practice given deterministic `groupSegmentsByLine` output
- Fallback message not shown before first successful result — `speechFallbackMessage` is set on mount but the `<p>` is gated inside `pinyinSegments.length > 0`; acceptable for current story scope
