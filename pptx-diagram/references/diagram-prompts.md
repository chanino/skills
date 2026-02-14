# Diagram Prompt Engineering Guide

## Choosing the Right Diagram Type

| If the user says... | Use this type |
|---|---|
| "how the system works operationally" | CONOPS |
| "who does what and when" | CONOPS (swim lane) |
| "phased rollout / operational phases" | CONOPS (phased timeline) |
| "system components and connections" | Architecture |
| "cloud infrastructure layout" | Architecture (cloud) |
| "system layers / tiers" | Architecture (layered) |
| "how systems integrate" | Architecture (integration) |
| "step-by-step process" | Flowchart |
| "network topology / devices" | Network |
| "message exchange between services" | Sequence |
| "database schema / data model" | ER Diagram |
| "where data flows through the system" | Data Flow |

## General Template

Every diagram prompt should include these elements:

```
Create a [DIAGRAM TYPE] diagram showing [SUBJECT].

Components: [LIST KEY COMPONENTS]
Relationships: [DESCRIBE CONNECTIONS/FLOW]

Style: Clean, flat, modern design. White background. 16:9 aspect ratio.
Use readable text labels on all components. No decorative elements.
Professional technical diagram style with clear hierarchy.
Limit to [N] major components for readability.
```

## Quality Tips

- **Component count**: Keep to 5-10 major components. More than 12 becomes unreadable at slide resolution.
- **Text labels**: Always specify "readable text labels" — without this, AI may generate illegible or blurry text.
- **White background**: Always specify for clean PPTX embedding.
- **16:9 ratio**: Always specify to match slide dimensions.
- **Flat modern design**: Avoids 3D effects, gradients, and skeuomorphic elements that look dated.
- **Color**: Specify a limited palette (2-3 colors) for cohesion. Blues and grays are safe defaults for technical diagrams.
- **Spacing**: Mention "well-spaced" or "generous whitespace" to avoid cramped layouts.
- **No watermarks**: Specify "no watermarks, no stock photo artifacts."

---

## Primary Diagram Types

### Architecture Diagram

Architecture diagrams show system components and their connections. Use for any "how is the system built" question.

#### Basic Architecture

```
Create a clean system architecture diagram showing [SYSTEM NAME].

Components:
- [Component 1] (e.g., "React frontend")
- [Component 2] (e.g., "API Gateway")
- [Component 3] (e.g., "PostgreSQL database")
[...]

Show data flow between components with labeled arrows.
Group related components in bounded boxes (e.g., "Cloud Infrastructure", "Client Side").

Style: Flat modern design, white background, 16:9 ratio.
Use a blue/gray color palette. Rounded rectangles for services, cylinders for databases.
All text must be crisp and readable. Maximum 10 components.
```

#### Cloud Architecture

For AWS/Azure/GCP-style diagrams with regions, VPCs, and subnets.

```
Create a clean cloud architecture diagram showing [SYSTEM NAME] deployed on [CLOUD PROVIDER].

Infrastructure:
- Region: [region name]
- VPC/VNet with [N] subnets (public and private)
- [List services: e.g., "ALB in public subnet", "ECS tasks in private subnet", "RDS in isolated subnet"]
- [External services: e.g., "CloudFront CDN", "Route 53 DNS", "S3 bucket"]

Show network flow from users through CDN → load balancer → compute → database.
Use nested bounded boxes for region → VPC → subnet hierarchy.
Label each subnet as public or private. Show security group boundaries with dashed lines.

Style: Flat modern design, white background, 16:9 ratio.
Use provider-appropriate color palette (e.g., orange for AWS, blue for Azure).
Rounded rectangles for services, cylinders for databases, cloud shape for CDN.
All text must be crisp and readable. Maximum 10-12 components.
```

#### Layered Architecture

Horizontal tiers showing presentation, business logic, and data layers.

```
Create a clean layered architecture diagram showing [SYSTEM NAME].

Layers (top to bottom):
- Presentation Layer: [e.g., "Web App", "Mobile App", "Admin Portal"]
- API Layer: [e.g., "REST API Gateway", "GraphQL Endpoint"]
- Business Logic Layer: [e.g., "Auth Service", "Order Processing", "Notification Engine"]
- Data Layer: [e.g., "PostgreSQL", "Redis Cache", "S3 Object Store"]

Show vertical arrows for request/response flow between layers.
Each layer is a full-width horizontal band with components inside.
Label the layer names on the left side.

Style: Flat modern design, white background, 16:9 ratio.
Use progressively deeper blue shading from top to bottom.
All text must be crisp and readable. Maximum 4 layers, 3-4 components per layer.
```

#### Integration Architecture

System-of-systems with APIs, message queues, and ETL pipelines.

```
Create a clean integration architecture diagram showing how [SYSTEMS] connect.

Systems:
- [System A] (e.g., "CRM - Salesforce")
- [System B] (e.g., "ERP - SAP")
- [System C] (e.g., "Data Warehouse")
[...]

Integration points:
- [System A] → REST API → [Integration Hub]
- [Integration Hub] → Message Queue → [System B]
- [System B] → ETL batch job → [System C]
[...]

Show each system as a bounded box. Place the integration hub/middleware in the center.
Use solid arrows for synchronous (REST/SOAP) and dashed arrows for asynchronous (queues/events).
Label each arrow with the protocol or integration method.

Style: Flat modern design, white background, 16:9 ratio.
Blue for internal systems, green for external/third-party systems, gray for middleware.
All text must be crisp and readable. Maximum 8 systems.
```

#### Architecture-Specific Tips

- **Bounded boxes** for trust boundaries, network zones, or organizational ownership
- **Solid arrows** for synchronous communication, **dashed arrows** for async
- **Cylinder shapes** for databases and data stores
- **Cloud shapes** for external/SaaS services
- **Color-code** by concern: blue for compute, green for data, orange for external

---

### CONOPS (Concept of Operations) Diagram

CONOPS diagrams show how a system operates from the user/stakeholder perspective. They focus on *who does what, when, and how* rather than technical components. Use for operational workflows, mission threads, and stakeholder interaction models.

#### Swim Lane CONOPS

Horizontal lanes for each actor/organization, activities positioned by phase or time.

```
Create a clean swim lane concept of operations diagram showing [OPERATION NAME].

Actors (one lane each, top to bottom):
- [Actor 1] (e.g., "Field Operator")
- [Actor 2] (e.g., "Operations Center")
- [Actor 3] (e.g., "Automated System")
- [Actor 4] (e.g., "Decision Authority")

Phases (left to right): [e.g., "Detection", "Assessment", "Response", "Recovery"]

Activities:
- [Phase 1]: [Actor 1] performs [activity], passes to [Actor 2]
- [Phase 2]: [Actor 2] performs [activity], triggers [Actor 3]
- [Phase 3]: [Actor 3] performs [automated activity], notifies [Actor 4]
- [Phase 4]: [Actor 4] [decides/approves], [Actor 1] executes
[...]

Show handoffs between lanes with arrows. Mark decision points with diamonds.
Distinguish automated steps (dashed borders) from manual steps (solid borders).
Label phase boundaries with vertical divider lines.

Style: Flat modern design, white background, 16:9 ratio.
Blue for human activities, green for automated activities, orange for decision points.
All text must be crisp and readable. Maximum 4 lanes, 4 phases.
```

#### Phased Timeline CONOPS

Left-to-right phases with activities, decision gates, and handoffs.

```
Create a clean phased timeline concept of operations diagram showing [OPERATION NAME].

Phases (left to right):
- Phase 1: [Name] — [key activities]
- Phase 2: [Name] — [key activities]
- Phase 3: [Name] — [key activities]
- Phase 4: [Name] — [key activities]

Decision gates between phases:
- Gate 1 (between Phase 1-2): [criteria, e.g., "Threat confirmed?"]
- Gate 2 (between Phase 2-3): [criteria, e.g., "Resources available?"]
- Gate 3 (between Phase 3-4): [criteria, e.g., "Mission complete?"]

Show each phase as a large rounded rectangle containing its activities as bullet points.
Connect phases with thick arrows. Place diamond-shaped decision gates between phases.
Show the timeline arrow along the bottom. Label key inputs and outputs for each phase.

Style: Flat modern design, white background, 16:9 ratio.
Use a blue-to-green gradient progression across phases.
All text must be crisp and readable. Maximum 4-5 phases.
```

#### Operational Context CONOPS

Central system with surrounding actors, external systems, and interaction arrows.

```
Create a clean operational context diagram showing [SYSTEM NAME] concept of operations.

Central system: [System Name] in the center

Surrounding actors and systems:
- [Actor 1] (e.g., "End Users") — [interaction: e.g., "submits requests via web portal"]
- [Actor 2] (e.g., "Administrators") — [interaction: e.g., "configures and monitors"]
- [External System 1] (e.g., "Partner API") — [interaction: e.g., "sends/receives data feeds"]
- [External System 2] (e.g., "Legacy Database") — [interaction: e.g., "nightly data sync"]
[...]

Show the central system as a large bounded box. Arrange actors/systems around it.
Use labeled arrows showing the direction and nature of each interaction.
Use person icons for human actors, rectangles for systems.
Distinguish inbound vs. outbound data flows.

Style: Flat modern design, white background, 16:9 ratio.
Blue for the central system, gray for external systems, teal for human actors.
All text must be crisp and readable. Maximum 6-8 surrounding entities.
```

#### CONOPS-Specific Tips

- **Show human actors** — CONOPS is about people and operations, not just boxes
- **Label phases clearly** — readers should immediately see temporal progression
- **Distinguish automated vs. manual** — use dashed borders or different colors for automated steps
- **Include decision points** — operations always involve go/no-go gates
- **Keep it operational** — focus on *what happens* and *who does it*, not implementation details
- **Show handoffs explicitly** — arrows between actors should be labeled with what's passed

---

## Other Diagram Types

### Flowchart

```
Create a clean flowchart diagram showing [PROCESS NAME].

Steps:
1. [Start condition]
2. [Decision point]: Yes → [path A], No → [path B]
3. [Process step]
[...]

Use standard flowchart shapes: rounded rectangles for start/end, diamonds for decisions,
rectangles for process steps. Arrows showing flow direction with labels on decision branches.

Style: Flat modern design, white background, 16:9 ratio.
Top-to-bottom or left-to-right flow. Readable text labels on all shapes.
Blue for process steps, orange for decisions, green for start/end.
```

### Network Diagram

```
Create a clean network topology diagram showing [NETWORK NAME].

Devices:
- [Device 1] (e.g., "Load Balancer")
- [Device 2] (e.g., "Web Server Cluster")
- [Device 3] (e.g., "Firewall")
[...]

Show connections between devices with protocol labels (e.g., HTTPS, TCP/443).
Group devices by network zone (e.g., DMZ, Internal, External).

Style: Flat modern design, white background, 16:9 ratio.
Use standard network icons (simplified). Dashed lines for zone boundaries.
Readable labels on all devices and connections.
```

### Sequence Diagram

```
Create a clean sequence diagram showing [INTERACTION NAME].

Participants (left to right):
- [Actor 1] (e.g., "User")
- [Actor 2] (e.g., "Frontend")
- [Actor 3] (e.g., "API Server")
- [Actor 4] (e.g., "Database")

Messages:
1. [Actor 1] → [Actor 2]: [message] (e.g., "Login request")
2. [Actor 2] → [Actor 3]: [message]
3. [Actor 3] → [Actor 4]: [message]
4. [Actor 4] → [Actor 3]: [response]
[...]

Style: Flat modern design, white background, 16:9 ratio.
Vertical lifelines, horizontal arrows with message labels.
Readable text. Maximum 5-6 participants, 10-12 messages.
```

### ER Diagram

```
Create a clean entity-relationship diagram showing [DOMAIN NAME] data model.

Entities:
- [Entity 1] with attributes: [attr1 (PK), attr2, attr3]
- [Entity 2] with attributes: [attr1 (PK), attr2, attr3 (FK)]
[...]

Relationships:
- [Entity 1] one-to-many [Entity 2]
- [Entity 2] many-to-many [Entity 3]
[...]

Style: Flat modern design, white background, 16:9 ratio.
Rectangles for entities, crow's foot notation for relationships.
Primary keys underlined. Readable text labels. Maximum 8 entities.
```

### Data Flow Diagram

```
Create a clean data flow diagram showing [SYSTEM/PROCESS NAME].

External entities: [list sources/sinks]
Processes: [list processing steps]
Data stores: [list storage]
Data flows: [list what data moves where]

Style: Flat modern design, white background, 16:9 ratio.
Circles for processes, open rectangles for data stores, squares for external entities.
Labeled arrows for all data flows. Readable text.
```

---

## Example Prompts

**Simple architecture:**
> Create a clean system architecture diagram showing a web application. Components: React SPA frontend, Nginx reverse proxy, Node.js API server, Redis cache, PostgreSQL database. Show request flow from user through each layer. Flat modern design, white background, 16:9 ratio, blue/gray palette, readable text labels, no watermarks.

**Cloud architecture:**
> Create a clean AWS cloud architecture diagram showing a serverless web app. Region us-east-1, VPC with public and private subnets. CloudFront CDN → API Gateway → Lambda functions in private subnet → DynamoDB. S3 for static assets. Cognito for auth. Nested boxes for region and VPC. Flat modern design, white background, 16:9 ratio, orange/gray AWS palette, readable text labels, no watermarks.

**CI/CD pipeline:**
> Create a clean flowchart showing a CI/CD pipeline. Steps: Developer pushes code → GitHub triggers webhook → Jenkins runs tests → Decision: tests pass? Yes → Build Docker image → Push to registry → Deploy to staging → Decision: approval? Yes → Deploy to production. No paths loop back. Flat modern design, white background, 16:9 ratio, readable text labels.

**Microservices:**
> Create a clean architecture diagram showing a microservices system. Services: API Gateway, User Service, Order Service, Payment Service, Notification Service. Each service has its own database. Services communicate via message queue. Show synchronous (solid arrows) and async (dashed arrows) communication. Flat modern design, white background, 16:9 ratio, limited to blue/teal palette, readable text labels.

**CONOPS swim lane:**
> Create a clean swim lane CONOPS diagram showing an incident response operation. Lanes: Field Team, SOC Analyst, Automated SIEM, Incident Commander. Phases: Detection, Triage, Containment, Recovery. Field Team detects anomaly and reports to SOC. SIEM automatically correlates alerts. SOC Analyst triages and escalates. Incident Commander authorizes containment. Field Team executes containment, then recovery. Flat modern design, white background, 16:9 ratio, blue for human steps, green for automated, readable text labels, no watermarks.

**Operational context CONOPS:**
> Create a clean operational context CONOPS diagram showing a drone surveillance system. Central system: "Mission Control Platform". Surrounding actors: Drone Operators (launch/control drones), Intelligence Analysts (review feeds), Field Commanders (request missions), Partner Agencies (receive reports). External systems: Weather API (provides conditions), Satellite Comms (relays data), Archive Database (stores imagery). Labeled arrows showing interactions. Flat modern design, white background, 16:9 ratio, blue center, gray externals, readable text labels, no watermarks.

---

## JSON Shape Spec Guidelines

After generating the reference image (Step 2) and extracting a structural description via `image_to_text.py` (Step 3), you translate that **text description** into a JSON shape specification (Step 4). See `references/shape-spec.md` for the full schema. Here is guidance on the translation process.

### Mapping Described Elements to Shape Types

| What the description says | JSON element type | shapeType |
|---|---|---|
| Rounded boxes / rounded rectangles | `shape` | `roundedRect` |
| Sharp-cornered boxes / rectangles | `shape` | `rect` |
| Diamond / decision nodes | `shape` | `diamond` |
| Database cylinders | `shape` | `cylinder` |
| Cloud shapes | `shape` | `cloud` |
| Ovals / ellipses | `shape` | `oval` |
| Arrows / connectors between elements | `connector` | — |
| Background grouping boxes / regions | `group` | — |
| Standalone labels / headers | `text` | — |
| Separator / divider lines | `divider` | — |

### Translating the Structural Description to Coordinates

The structural description from Step 3 gives you positions (left/center/right, top/middle/bottom), relative sizes, and layout grid info. Map these to inch coordinates:

1. **Slide is 10" wide × 5.625" tall** — the title bar uses the top 0.75", so your diagram area is roughly 0.85" to 5.35" vertically
2. **Map described positions to a grid**: for a 3-column layout, shapes at x ≈ 1.0, 4.0, 7.0; for 4 columns: x ≈ 0.5, 2.8, 5.2, 7.5. Use the description's spatial terms ("left third", "center", "right side") to assign columns
3. **Standard shape sizes**: boxes are typically 1.5"–2.5" wide × 0.5"–0.8" tall; cylinders are 1.5"–2.0" wide × 1.0"–1.2" tall
4. **Connectors**: start at the right edge of one shape (x + w) and end at the left edge of the next (x); for vertical arrows, use the bottom (y + h) and top (y) of shapes. Use the description's start/end element names to identify which shapes to connect

### Spacing Conventions

- **0.2" minimum gap** between adjacent shapes
- **0.5"–1.0" gap** for typical horizontal spacing between related shapes
- **0.1"–0.2" padding** inside group backgrounds (from group border to contained shapes)
- **0.3"–0.5" vertical gap** between rows of shapes

### Color Extraction Tips

- Match the reference image's color palette — pick 2-3 primary fill colors
- Use darker variants of fill colors for borders (e.g., fill `4A90E2`, border `2C5F8A`)
- White text (`FFFFFF`) on dark fills, dark text (`1E293B`) on light fills
- Group backgrounds should be very light tints of their theme color (e.g., `EFF6FF` for blue groups)
