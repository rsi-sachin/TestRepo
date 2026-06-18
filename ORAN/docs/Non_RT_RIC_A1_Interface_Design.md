# Non-RT RIC A1 Interface Design

Source:
- ETSI TS 103 987 V4.3.0 (2025-05)
- File: `ORAN/docs/ts_103987v040300p.pdf`
- Inputs used: Section 5.1 and Figure 5.1-1

## Section 5.1 (Extracted and Normalized)

The A1 Application Protocol defines APIs for these A1 services:
- A1-P: A1 policy management service
- A1-EI: A1 enrichment information service

Notes from Section 5.1:
- Service definition and API for A1-ML are not defined in this document.
- The A1 application protocol is based on signalling between an A1 service consumer and an A1 service producer.
- The consumer and producer can reside in either the Non-RT RIC or Near-RT RIC, depending on service role.

Interaction model statement in the same subsection area (around Figure 5.1-1):
- Requests are sent from Service Consumer to Service Producer.
- Responses and notifications are sent from Service Producer to Service Consumer.
- The Service Producer handles resources on which the Consumer performs operations.
- Consumer/Producer terms indicate service roles, not raw data-flow direction over A1.

## Figure 5.1-1 Converted to Text

Figure title:
- Service framework for the A1 services

### Node placement by domain

Non-RT RIC contains:
- A1-P Consumer
- A1-ML Consumer
- A1-EI Producer

Near-RT RIC contains:
- A1-P Producer
- A1-ML Producer
- A1-EI Consumer

### Service role pairings across the A1 interface

- A1-P service:
  - Consumer: Non-RT RIC
  - Producer: Near-RT RIC

- A1-EI service:
  - Producer: Non-RT RIC
  - Consumer: Near-RT RIC

- A1-ML service (framework role shown, API not specified in this document):
  - Consumer: Non-RT RIC
  - Producer: Near-RT RIC

### Textual architecture view

A1 services are modeled as role-based consumer/producer pairs between Non-RT RIC and Near-RT RIC:
- For policy management (A1-P), Non-RT RIC acts as client-side service consumer and Near-RT RIC acts as service producer.
- For enrichment information (A1-EI), roles are inverted: Near-RT RIC consumes EI exposed by Non-RT RIC.
- A1-ML appears in the same framework as a logical service pair, but no API/service definition is provided here.

### ASCII relationship sketch

```text
Non-RT RIC                                  Near-RT RIC
-----------                                 ------------
A1-P Consumer  --------------------------->  A1-P Producer
A1-ML Consumer --------------------------->  A1-ML Producer
A1-EI Producer  <-------------------------  A1-EI Consumer

Legend:
- Arrow direction indicates request initiation from Consumer to Producer.
- Producer returns responses/notifications.
```

## Consolidated Design Summary (From Section 5.1 + Figure 5.1-1)

The A1 interface design is a service-oriented, role-based framework linking Non-RT RIC and Near-RT RIC. Each A1 service is realized as a Consumer-Producer pair with clear request/response responsibilities:
- Consumer initiates operations toward producer-managed resources.
- Producer owns resource handling and returns responses and notifications.

Service responsibilities in this specification:
- A1-P is fully defined as Non-RT RIC consumer to Near-RT RIC producer.
- A1-EI is fully defined as Near-RT RIC consumer to Non-RT RIC producer.
- A1-ML role placement is shown in framework view, but API details are out of scope for this document.
