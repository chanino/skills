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

Style: Clean, sophisticated, consulting-grade design.
- Muted, desaturated color palette — navy blue (#2E5090), slate gray (#64748B),
  warm gold (#C4A35A). NO bright primary colors (#3B82F6, #EF4444, etc.).
- Generous whitespace between all elements (0.4" minimum gaps)
- Minimal borders — shapes defined by subtle drop shadows, not outlines
- Clear visual hierarchy: primary elements larger and darker, secondary lighter
- White background, 16:9 aspect ratio
Use readable text labels on all components. No decorative elements.
Limit to [N] major components for readability.
```

## Quality Tips

- **Component count**: Keep to 5-10 major components. More than 12 becomes unreadable at slide resolution.
- **Text labels**: Always specify "readable text labels" — without this, AI may generate illegible or blurry text.
- **White background**: Always specify for clean PPTX embedding.
- **16:9 ratio**: Always specify to match slide dimensions.
- **Muted palette**: Use desaturated, professional colors (navy, slate, gold, forest green). NEVER use bright saturated primaries (#3B82F6, #EF4444, #10B981). See `shape-spec.md` consulting palettes.
- **Borderless shapes**: Specify "shapes defined by shadows, not outlines" for a consulting look.
- **Generous spacing**: Mention "generous whitespace" and "well-spaced" — cramped layouts look amateur.
- **Visual hierarchy**: Specify that primary elements should be larger, darker, and have stronger shadows than secondary elements.
- **Shadow depth**: Use "subtle drop shadows for depth" rather than flat shapes or heavy borders.
- **Color**: Specify a limited palette (2-3 fill colors max) for cohesion. Pick from the consulting palettes in shape-spec.md.
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

Style: Consulting-grade design, muted desaturated palette, white background, 16:9 ratio. Shapes defined by shadows, not heavy borders.
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

Style: Consulting-grade design, muted desaturated palette, white background, 16:9 ratio. Shapes defined by shadows, not heavy borders.
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

Style: Consulting-grade design, muted desaturated palette, white background, 16:9 ratio. Shapes defined by shadows, not heavy borders.
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

Style: Consulting-grade design, muted desaturated palette, white background, 16:9 ratio. Shapes defined by shadows, not heavy borders.
Blue for internal systems, green for external/third-party systems, gray for middleware.
All text must be crisp and readable. Maximum 8 systems.
```

#### Architecture-Specific Tips

- **Bounded boxes** for trust boundaries, network zones, or organizational ownership
- **Solid arrows** for synchronous communication, **dashed arrows** for async
- **Cylinder shapes** for databases and data stores
- **Cloud shapes** for external/SaaS services
- **Color-code** by visual weight: Primary palette color for key compute, Secondary for data/supporting, Accent for external/decision points

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

Style: Consulting-grade design, muted desaturated palette, white background, 16:9 ratio. Shapes defined by shadows, not heavy borders.
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

Style: Consulting-grade design, muted desaturated palette, white background, 16:9 ratio. Shapes defined by shadows, not heavy borders.
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

Style: Consulting-grade design, muted desaturated palette, white background, 16:9 ratio. Shapes defined by shadows, not heavy borders.
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

Style: Consulting-grade design, muted desaturated palette, white background, 16:9 ratio. Shapes defined by shadows, not heavy borders.
Top-to-bottom or left-to-right flow. Readable text labels on all shapes.
Primary palette color for process steps, Accent for decisions, Primary for start/end.
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

Style: Consulting-grade design, muted palette, white background, 16:9 ratio.
Use standard network icons (simplified). Dashed lines for zone boundaries.
Shapes defined by subtle shadows, not heavy borders. Readable labels on all devices and connections.
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

Style: Consulting-grade design, muted palette, white background, 16:9 ratio.
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

Style: Consulting-grade design, muted palette, white background, 16:9 ratio.
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

Style: Consulting-grade design, muted palette, white background, 16:9 ratio.
Circles for processes, open rectangles for data stores, squares for external entities.
Labeled arrows for all data flows. Readable text.
```

---

## Example Prompts

**Simple architecture:**
> Create a clean system architecture diagram showing a web application. Components: React SPA frontend, Nginx reverse proxy, Node.js API server, Redis cache, PostgreSQL database. Show request flow from user through each layer. Consulting-grade design, muted navy/slate palette (#2E5090, #5B8DB8), white background, 16:9 ratio, shapes defined by subtle shadows, generous whitespace, readable text labels, no watermarks.

**Cloud architecture:**
> Create a clean AWS cloud architecture diagram showing a serverless web app. Region us-east-1, VPC with public and private subnets. CloudFront CDN → API Gateway → Lambda functions in private subnet → DynamoDB. S3 for static assets. Cognito for auth. Nested boxes for region and VPC. Consulting-grade design, muted professional palette, white background, 16:9 ratio, shapes defined by subtle shadows, generous whitespace, readable text labels, no watermarks.

**CI/CD pipeline:**
> Create a clean flowchart showing a CI/CD pipeline. Steps: Developer pushes code → GitHub triggers webhook → Jenkins runs tests → Decision: tests pass? Yes → Build Docker image → Push to registry → Deploy to staging → Decision: approval? Yes → Deploy to production. No paths loop back. Consulting-grade design, muted palette, white background, 16:9 ratio, subtle shadows, generous whitespace, readable text labels.

**Microservices:**
> Create a clean architecture diagram showing a microservices system. Services: API Gateway, User Service, Order Service, Payment Service, Notification Service. Each service has its own database. Services communicate via message queue. Show synchronous (solid arrows) and async (dashed arrows) communication. Consulting-grade design, muted navy/slate palette, white background, 16:9 ratio, shapes defined by subtle shadows, generous whitespace, readable text labels.

**CONOPS swim lane:**
> Create a clean swim lane CONOPS diagram showing an incident response operation. Lanes: Field Team, SOC Analyst, Automated SIEM, Incident Commander. Phases: Detection, Triage, Containment, Recovery. Field Team detects anomaly and reports to SOC. SIEM automatically correlates alerts. SOC Analyst triages and escalates. Incident Commander authorizes containment. Field Team executes containment, then recovery. Consulting-grade design, muted slate palette, white background, 16:9 ratio, shapes defined by subtle shadows, generous whitespace, readable text labels, no watermarks.

**Operational context CONOPS:**
> Create a clean operational context CONOPS diagram showing a drone surveillance system. Central system: "Mission Control Platform". Surrounding actors: Drone Operators (launch/control drones), Intelligence Analysts (review feeds), Field Commanders (request missions), Partner Agencies (receive reports). External systems: Weather API (provides conditions), Satellite Comms (relays data), Archive Database (stores imagery). Labeled arrows showing interactions. Consulting-grade design, muted professional palette, white background, 16:9 ratio, shapes defined by subtle shadows, generous whitespace, readable text labels, no watermarks.

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
2. **Map described positions to a grid**: use the grid templates below for common layouts
3. **Standard shape sizes**: boxes are typically 1.5"–2.5" wide × 0.5"–0.8" tall; cylinders are 1.5"–2.0" wide × 1.0"–1.2" tall
4. **Connectors**: always assign `id` fields to shapes that have connectors. Use `from`/`to` with side anchors instead of calculating x1,y1,x2,y2 manually. The build script auto-calculates edge midpoints at render time.

#### Grid Templates for Common Layouts

**3-column horizontal flow** (e.g., Frontend → API → Database):
```
Shape width: 2.0"  |  x positions: 1.0, 4.0, 7.0  |  y: 2.5 (centered)
```

**4-column horizontal flow**:
```
Shape width: 1.8"  |  x positions: 0.5, 2.8, 5.1, 7.4  |  y: 2.5
```

**2-row × 3-column grid** (e.g., layered architecture):
```
Shape width: 2.0"  |  x positions: 1.0, 4.0, 7.0
Row 1 y: 1.5  |  Row 2 y: 3.5
```

**Vertical flow** (e.g., top-to-bottom flowchart):
```
Shape width: 2.0", height: 0.6"  |  x: 4.0 (centered)
y positions: 1.0, 2.0, 3.0, 4.0 (0.4" gap between shapes)
```

#### Connector Best Practices

- **Always use shape-anchored connectors** (`from`/`to` with `fromSide`/`toSide`) instead of manually calculating absolute coordinates. This eliminates the #1 source of visual errors: arrows that don't touch shapes.
- For horizontal flows: `fromSide: "right"`, `toSide: "left"`
- For vertical flows: `fromSide: "bottom"`, `toSide: "top"`
- Use `"route": "elbow"` for connectors that need to go around shapes (L-shaped paths)
- For diagonal connections or non-adjacent shapes, elbow routing produces cleaner results than straight lines

### Spacing Conventions

- **0.2" minimum gap** between adjacent shapes
- **0.5"–1.0" gap** for typical horizontal spacing between related shapes
- **0.1"–0.2" padding** inside group backgrounds (from group border to contained shapes)
- **0.3"–0.5" vertical gap** between rows of shapes

### Icons in Diagrams

When the reference image or user request calls for icons (server icons, database icons, user icons, cloud logos, etc.), you can include them in the JSON spec as `"type": "icon"` elements. See `references/icon-catalog.md` for available icon names.

**In the image generation prompt:** You can request icons on shapes (e.g., "show a server icon on each compute node") to guide the reference layout. The image generator may or may not produce distinct icons, but they serve as placement hints.

**In the structural description (Step 3):** Call out any icons or iconographic elements: "a server icon appears above the 'API Server' label", "a database cylinder icon sits to the left of 'PostgreSQL'". This helps map them to `icon` elements in Step 4.

**In the JSON spec (Step 4):** Add `icon` elements positioned near their associated shapes. Icons are optional — if you're unsure which icon to use or the description doesn't clearly call for one, skip it. Shapes and labels alone produce clear diagrams.

### Color Strategy for Consulting Quality

When translating a reference image to a JSON shape spec, select one of the four consulting palettes from `references/shape-spec.md`:

1. **Choose a palette** that matches the diagram's domain:
   - Corporate Blue — enterprise IT, general architecture
   - Warm Professional — executive, reports, process
   - Modern Slate — cloud, DevOps, modern tech
   - Forest Green — healthcare, sustainability, environmental

2. **Assign colors by visual role**, not by element type:
   - **Primary fill** (palette Primary) → key components, main process shapes
   - **Secondary fill** (palette Secondary) → supporting components, sub-processes
   - **Accent fill** (palette Accent) → decision points, highlights, callouts
   - **Neutral** (palette Neutral) → connectors, borders, labels
   - **Light** (palette Light) → group backgrounds

3. **Max 3 fill colors** per diagram — Primary, Secondary, and at most one Accent

4. **Ban bright saturated primaries** — never use:
   - `3B82F6` → use `2E5090` or `334155` instead
   - `EF4444` → use `7C3A2D` instead
   - `10B981` → use `1B5E42` instead
   - `F59E0B` → use `C4A35A` or `D4A847` instead

5. **Text contrast rules:**
   - White text (`FFFFFF`) on Primary/Secondary/Accent fills
   - Dark text (`1E293B`) on Light fills and white backgrounds
   - Connector labels use Neutral color (`6B7280` or `94A3B8`)
