# Shared Rehearsal App Security Preflight

## Learner Goal
- Understand the tradeoff between access security and low-friction use before choosing implementation scope.

## Current Level
- Status: mastered
- Last updated: 2026-08-16
- Confidence: decisions complete; implementation evidence pending

## Evidence
- 2026-08-15: Selected Vainglory as the analogy, depth 2, and Chat Markdown; prioritized understanding security and friction over immediate implementation.
- 2026-08-15: Chose device-bound nickname claims: normal visits use a cached device credential, while a new device must complete a separate recovery check.
- 2026-08-15: Chose administrator-assisted recovery when all enrolled devices are unavailable, avoiding permanent per-person recovery secrets.
- 2026-08-16: Chose self-enrollment behind the shared entry gate until the roster reaches ten nicknames; the first device claims the new nickname and an administrator may clean up mistakes or revoke devices.
- 2026-08-16: Chose a team-wide music library: all enrolled members may play every track, while only the uploader and administrators may rename, replace, or remove it.
- 2026-08-16: Chose immutable audio versions for replacement so existing timestamp-based loops remain attached to the exact bytes they were created against.
- 2026-08-16: Chose bounded browser-ready uploads without server-side transcoding.
- 2026-08-16: Chose OpenAI Sites as the sole canonical deployment rather than maintaining synchronized Vercel and Sites production targets; this makes platform authentication available and reopens the earlier custom device-credential design.
- 2026-08-16: Chose Sites platform identity plus one-time shared-secret roster enrollment and a stored nickname mapping. This supersedes the earlier custom device credential, recovery code, and administrator device-reset mechanism.
- 2026-08-16: Chose two explicit loop surfaces per audio version: a personal section that remembers the user's recent loops and a team section for shared loops.
- 2026-08-16: Chose separate actions: personal pinning keeps a loop beyond the recent-four list, while Share to Team publishes a stable snapshot that remains visible in the team section without silently tracking later personal edits.
- 2026-08-16: Specified one active team-visible music slot per enrolled user, limiting the live library to ten active tracks.
- 2026-08-16: Specified named loops on the audio timeline; when visible loop ranges overlap, the most recently created loop is shown and every older overlapping loop is hidden as a whole.
- 2026-08-16: Chose a maximum of ten active tracks; superseded audio versions remain hidden only while loops reference them and become eligible for cleanup once unreferenced.
- 2026-08-16: Reframed the user story around Netflix-like, freely switchable profiles that act as Kubernetes-like namespaces after one real platform sign-in. The authenticated actor and selected namespace are therefore separate concepts.
- 2026-08-16: Chose simple authorization: all enrolled members may enter any profile namespace to browse and play; only that profile's authenticated owner or the site administrator may upload, replace, rename, or remove its active track.
- 2026-08-16: Chose collaborative loop permissions: any enrolled member may create personal loops on any active track and publish their own stable snapshot to that profile's team section; the creator, profile owner, or administrator may remove it.
- 2026-08-16: Required every loop to show both a user-defined name and creator attribution. Deferred approval, reporting, blocking, and advanced moderation until actual misuse appears.
- 2026-08-16: Chose layered storage guardrails: enforce both per-file and whole-site byte budgets before upload, include referenced archives in usage, expose usage to the administrator, and clean only unreferenced superseded versions. Numeric thresholds must follow the current Sites quota and representative real audio sizes.
- 2026-08-16: Chose to import the current static audio into the initial administrator-owned profile and convert the six legacy sections into team loops attributed to a system import actor.
- 2026-08-16: Refined archive safety: automatic cleanup may delete only unreferenced versions, while an administrator or explicitly administrator-authorized maintenance agent may force-delete a referenced version after reviewing the affected loops.
- 2026-08-16: Chose the production gate: Sites becomes canonical and the frozen Vercel deployment is retired only after automated verification, a two-real-account cross-profile acceptance test, and one real rehearsal session.

## Known Gaps
- Numeric storage budgets still require the current Sites quota and representative real audio sizes.
- Real-account and rehearsal acceptance remain implementation-stage evidence, not preflight assumptions.

## Teaching Notes
- Use a Vainglory team-lobby frame and one shotcall per turn.
- Keep implementation details behind product decisions until the relevant boundary is confirmed.

## Next Suggested Levels
- Implement the confirmed Sites-only product contract and synthetic verification suite.
- Run a post-implementation debrief before public cutover.
- Complete the two-account and rehearsal acceptance gate before retiring Vercel.
