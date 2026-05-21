# Project Guide for Claude

## Stack

- **Language:** TypeScript (ESM, `"type": "module"`)
- **Runtime:** Node.js 20+
- **Test runner:** Vitest
- **Lint:** ESLint (flat config)
- **Format:** Prettier
- **Dev runner:** tsx

## Layout

```
src/         Source code
tests/       Vitest tests (*.test.ts)
dist/        Build output (gitignored)
.github/     CI workflows
.claude/     Claude Code settings + hooks
```

## Commands

| Task        | Command            |
| ----------- | ------------------ |
| Install     | `npm ci`           |
| Dev (watch) | `npm run dev`      |
| Build       | `npm run build`    |
| Run         | `npm start`        |
| Test        | `npm test`         |
| Typecheck   | `npm run typecheck`|
| Lint        | `npm run lint`     |
| Format      | `npm run format`   |

## Conventions

- ESM imports use `.js` extensions even for `.ts` sources (TS bundler mode).
- Tests live in `tests/` and import from `../src/*.js`.
- `strict` + `noUncheckedIndexedAccess` are on — check optional access.
- Don't add comments that just restate the code.
- New deps: justify before adding. Prefer the standard library.

## CI

GitHub Actions runs `typecheck`, `lint`, `test`, `build` on Node 20 and 22 for every PR to `main`.
