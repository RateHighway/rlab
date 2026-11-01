# RevenueLab host compatibility and certification

**Official host admission:** apply [RLAB-CENTRAL-ADMISSION-1](../../../docs/central-registration.md) in addition to this profile. Centrally retain every page package and source, record its host placements, and verify current central admission before display. The existing closed manifest grammar is unchanged; design-only content remains non-executable.

**Programme design | Draft Standard | 2026-10-02**

## Badge recommendation

Use a host compatibility badge with a verifiable certification record, rather than an award for general quality. Its purpose is practical: tell a builder that this system can accept a RevenueLab Page, then let the builder see the supported capabilities and installation process.

Primary badge copy:

> THIS SYSTEM HOSTS<br>
> **RevenueLab Pages**<br>
> Build pages. Make it yours.<br>
> READ-ONLY HOST · .rlab

The delivered image is a **certification design concept**. Its concept caption is intentional. It does not certify RateMonitor Elite, a partner or any existing system. No certification has been issued through this work.

## Three different claims

| Claim | Evidence | Permitted presentation |
|---|---|---|
| Developer preview | Implementation in progress; synthetic tests only | Plain text: RevenueLab page hosting in development |
| Supports RevenueLab Pages | Vendor's published conformance declaration and passed mandatory tests | Compatibility wording plus visible “Vendor tested” label and evidence link; never “Certified” |
| Certified RevenueLab Host | Reviewed evidence, named issuing authority and active certificate | Authorised badge linked to verification record, plus “Certified” and tested profile/version |

The programme issuer is recommended to be RateHighway RevenueLab, with documented criteria applied equally to RateHighway and other companies. This issuer/governance arrangement is a design recommendation, not an operating certification body. Fees, renewal periods, legal terms and commercial benefits are not set here.

Host certification does not certify all pages installed there, their calculations, profitability, data accuracy or security against every threat. It does not promise that every page works in every host. Certification is scoped to a product, runtime release range, profile, delivery mode and tested capability set. A company-wide badge with no product scope is insufficient.

## Mandatory test and evidence matrix

| ID | Test | Required result/evidence |
|---|---|---|
| H01 | Import valid bundle; reject malformed, oversized and unsafe archives | Exact validator version, test fixtures, results and artifact hashes |
| H02 | Missing required scope/context/service or incompatible protocol | Install/launch blocked with useful explanation |
| H03 | Optional service/scope unavailable | Clearly disclosed fallback, without fabricated data |
| H04 | Forged publisher or silently changed approved bytes | Identity review or digest check blocks activation |
| H05 | Wrong origin, sibling frame, null origin, replayed sequence/init | Message rejected; no data/token delivered |
| H06 | Parent DOM access, popup, navigation, worker, unapproved executable | Browser policy blocks prohibited capability; unexpected frame navigation revokes session |
| H07 | Tenant A token requests tenant B object; location/field escalation | Gateway denies every request, including cache paths |
| H08 | General login token leakage; wrong audience/expiry/version | No general token exposed; invalid credentials rejected |
| H09 | Revoke permission or suspend a noncooperating page | Next gateway request denied; no reliance on iframe cooperation |
| H10 | Context change during request; tenant switch | Stale result discarded; tenant switch creates new isolated session |
| H11 | Update, rollback, uninstall | Immutable releases, current grants preserved correctly, access revoked, audit retained |
| H12 | API timeout, quota and outage | Bounded retry, usable failure state, no stale result represented as current |
| H13 | Keyboard, focus, title, contrast, narrow layout, zoom | Documented accessibility review with defects resolved |
| H14 | Secret/dependency review and logs | No exposed secrets; support evidence redacted and correctly scoped |
| H15 | Support, vulnerability handling, restore and incident exercise | Named responsible teams and successful operational exercise |
| H16 | Two pages built independently using the published contract | Both run without host-specific hidden permissions or schema reinterpretation |
| H17 | Certificate/badge link and claims | Product/version/profile/status visible; no unsupported integration claims |
| R01 | Remote hosting, headers, origin/config and deployment drift | Required only for remote endorsement; changed deployments suspended/reviewed |
| R02 | External processing and retention | Required only when supported; administrator disclosure and rights reviewed |

Critical isolation, authorisation or integrity failures block certification. A missing optional feature narrows the certification scope; it must not be silently waived into a pass. The reference offline validator covers only part of H01/H02/H04 and is not the H01-H17 test suite.

## Issuance and maintenance

1. Vendor submits identity, product/version, supported profiles, capability document and test evidence.
2. Reviewer independently reproduces mandatory negative tests and inspects threat model/operations.
3. Issuer records certificate ID, issuer, vendor, product, approved runtime range, profiles, modes, capabilities, evidence digest, assessed date, expiry/review date and current status.
4. Vendor receives authorised artwork and installation copy only after the record becomes active.
5. Material changes to isolation, identity, gateway, package handling, protocol or deployment trigger re-review. Unchanged compatible patches use the documented change-control process.
6. Suspected loss of conformance can suspend the certificate. A revoked, expired or suspended record cannot support an active badge; vendor removes it and the verification page retains truthful history.

Before launch, approve reviewer authority/independence, assessment fee policy if any, trademark licence, review/renewal periods, appeal process, incident response and revocation process. Until then, use the concept only in design reviews.

## Badge placement and behaviour

Place near “Custom Pages”, “Extensions” or developer settings, and on the host's developer page. The badge links to the actual verification record, not a sales homepage. Below it, provide “Build a page” and “Install a page” links only when those destinations work and the user is authorised.

Suggested accompanying product copy after conformance is established:

> Build a RevenueLab Page for this system using your preferred AI or development tool. Your administrator reviews the page and its requested access before installation. Supported data and features depend on this host and your account permissions.

Tooltip/accessible name: “This system hosts RevenueLab Pages. View supported capabilities and verification status.” Do not convey status through colour alone. At small sizes use the principal words with accessible supporting text beside it rather than shrinking every line until unreadable. Keep high contrast and a visible keyboard focus outline on the linked badge. Do not animate the check mark.

Visual direction: neutral gray surface, charcoal badge, warm white text, restrained `#ff6500` accents, original browser/code/check icon. No gradients, glow, gold medals or implied security guarantee. RevenueLab is a programme label. The artwork contains no recreated RateHighway logo. Where ownership is needed, use ordinary ownership copy or place an approved official logo separately and unchanged.

The sample verification URL shape `/hosts/{certificate-id}` is a routing design only. Do not create an active-looking link until a real record is published. A downloadable badge cannot be secured by appearance alone; the linked status record is the authority.
