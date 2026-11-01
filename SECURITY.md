# Security and vulnerability reporting

These are draft specifications and offline reference tools. There is no
production host or supported production service in this repository. The
browser example requires a separately implemented isolated HTTPS host.
The declarative examples are design-only.

For a suspected vulnerability, use the repository's private vulnerability
reporting option in the Security tab when it is enabled. If it is unavailable,
ask the repository owner for a private reporting channel without including
exploit details. Never post customer data, credentials or personal records.

Include the affected commit, profile, reproduction using synthetic fixtures,
expected behavior and impact. An offline checker does not establish browser
isolation, tenant isolation, connector authorization or malware safety.

Maintainers must distinguish affected versions from tested fixes. Publish
security corrections under new release identities; never silently replace a
released schema or package. No response-time guarantee or bug bounty is
offered by this document.
