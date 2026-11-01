# Level 1 synthetic design

This is a design-only RevenueLab 0.3 example. It uses reserved example publisher and service names, not live APIs.

The data query requests authorised fleet summaries for the host's selected locations. Display fields are location, class, rentable units and committed units. No implied full-rental-period availability or pricing recommendation is made.

The view reads data only.

Input bindings supply location IDs from authorised host context and, where applicable, a fixed task title. They do not substitute for server-side validation. The task does not conditionally select high-pressure rows: that requires a separately defined filter/calculation contract.

Validate using the kit checker. No renderer, live task service, workflow engine or scheduler is included. Sample support URLs are placeholders. Licence: Apache-2.0; complete terms are included in LICENSE.txt. The design does not grant data access or production authority.
