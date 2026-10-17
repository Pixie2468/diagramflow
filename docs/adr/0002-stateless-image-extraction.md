# ADR 0002: Process images statelessly in v1

## Status

Accepted — 2026-10-17

## Decision

Accept PNG, JPEG, and WebP uploads up to 10 MB, validate and enhance them in memory, send only the prepared image to the selected provider, then return the extraction. The application saves neither image nor graph.

## Consequences

This avoids accounts, retention policy, object storage, and project persistence. The configured Gemini provider may have its own API retention behavior; production deployment must review it before handling sensitive images.
