# Credential handling

The client prompts for a hidden LM Studio key or reads `API_KEY` from its process environment. It does not write keys to configuration files, shell profiles, the registry or logs. Connection exceptions do not print request headers or response bodies. HTTPS verification remains enabled, and redirects are refused to prevent forwarding the key to another endpoint.

Environment variables are not a password vault. Processes launched in the configured terminal can read the key. Close the terminal when done, and give each device its own revocable LM Studio key. Do not paste a key into shell commands, screenshots or issues.

The host's Cloudflare connection token is a separate credential. Keep any host-side private token file outside the repository. Ignore rules are only a convenience; Git can still include ignored files if forced, and old commits retain leaked secrets. If a credential leaks, revoke/rotate it before dealing with repository history.

For a repository security issue, use GitHub's private vulnerability reporting if the maintainer has enabled it. If no private route is available, open a minimal issue requesting a private contact channel without publishing exploit details or credentials. For an upstream vulnerability, contact the upstream maintainer.
