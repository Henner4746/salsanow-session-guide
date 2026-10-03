# Sources

## Official upstream documentation

- [SalsaNOW source repository](https://github.com/dpadGuy/SalsaNOW) — upstream project and documentation entry point. Its source was not independently audited for all persistence claims in the supplied guide.
- [SalsaNOW documentation](https://documentation.salsanowfiles.work) — upstream documentation entry point, linked by the project's README; individual persistence claims have not been reverified here.
- [Cloudflare tunnel run parameters](https://developers.cloudflare.com/tunnel/reference/run-parameters/) — remotely managed token-file startup, including the 2025.4.0 minimum version; checked 2026-10-03.
- [Cloudflare tunnel permissions](https://developers.cloudflare.com/cloudflare-one/networks/connectors/cloudflare-tunnel/configure-tunnels/remote-tunnel-permissions/) — token handling for remotely managed connectors; checked 2026-10-03.
- [LM Studio Anthropic compatibility](https://lmstudio.ai/docs/developer/anthropic-compat) — `/v1/messages`, client base URL and authentication headers; checked 2026-10-03.
- [Python downloads](https://www.python.org/downloads/) — runtime prerequisite.

## Supplied source material

This repository adapts `SALSANOW-GFN-GUIDE.public.md`, `HANDOFF-MAIN-PC.md` and a supplied ignore file. The handoff is the newer account. Their original author reports actual session experiments, including successful API tests. Those reports are attributed as observations, not recast as independent measurements made while preparing this repository.

Personal hostnames and machine-specific model identifiers were removed from reusable examples. No upstream application source code, proprietary binaries, models or actual credentials are bundled.
