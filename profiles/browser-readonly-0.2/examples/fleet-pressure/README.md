# Fleet Pressure Summary

Sample 0.1.1 for RevenueLab Draft Standard 0.2. Publisher and URLs are fictional fixtures.

Purpose: explain committed fleet as a percentage of rentable fleet. Input: fixed synthetic 40 committed units and 50 rentable units. Output: 80%, with assumptions and single-day coverage visible. This is not a pricing recommendation or a live utilisation feed.

Runtime dependency: a conforming 0.2 host, `context.read`, `environment` context and reviewed deployment configuration at `/__rlab/host-config.json`. No third-party JavaScript dependencies. The host must retry non-sensitive init during config loading and send no auth token to this context-only sample.

Setup: pack with the kit tool, validate and import into a development host. The host configuration is outside this archive, controlled by the deployer, and lists the approved HTTPS parent origin, `com.example.fleet-pressure` and version `0.1.1`.

Tests: kit contains offline package/profile negative tests. Browser execution, accessibility and actual host integration must be tested separately. The JavaScript is a teaching example, not a full SDK; it uses no gateway, refresh or persistent storage. Host enforcement remains mandatory even if a page does not cooperate.

Limitations: fixed data, no location filtering, no rental-period availability calculation, no market prices and no backend. The sample intentionally states that host filter changes do not change the data.

Support: no live support service is created. Replace the example publisher/support values before a real submission. Licence: Apache-2.0; the complete terms are included in LICENSE.txt. This does not grant data access, host approval or certification.
