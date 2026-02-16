# Icon Catalog

Pre-generated icons in `assets/icons/`. Use via the `path` field in icon elements — no npm dependencies needed.

## Infrastructure

| Icon | File | Use for |
|------|------|---------|
| Server | `assets/icons/server_rack.png` | App servers, compute instances |
| Database | `assets/icons/database_cylinder.png` | Databases, data stores |
| Cloud | `assets/icons/cloud.png` | Generic cloud services |
| Storage Disk | `assets/icons/storage_disk.png` | Storage, disk, volumes |
| Lambda Function | `assets/icons/lambda_function.png` | Serverless functions, FaaS |
| CPU Microchip | `assets/icons/cpu_microchip.png` | Processing units, CPUs |
| Desktop Computer | `assets/icons/desktop_computer.png` | Workstations, client machines |
| Network Switch | `assets/icons/network_switch.png` | Network infrastructure, switches |

## Security

| Icon | File | Use for |
|------|------|---------|
| Shield | `assets/icons/shield.png` | Security boundary, protection |
| Padlock | `assets/icons/padlock.png` | Encryption, authentication |
| Key | `assets/icons/key.png` | API keys, credentials, secrets |

## People

| Icon | File | Use for |
|------|------|---------|
| Person | `assets/icons/person_silhouette.png` | Single user, actor |
| Group of People | `assets/icons/group_of_people.png` | User groups, teams |

## Network

| Icon | File | Use for |
|------|------|---------|
| Globe | `assets/icons/globe_internet.png` | Internet, web, global |
| Router | `assets/icons/network_router.png` | Routing, network paths |
| Data Exchange | `assets/icons/data_exchange_arrows.png` | Data sync, bidirectional flow |
| Broadcast Tower | `assets/icons/broadcast_tower.png` | Broadcasting, pub/sub, events |

## Operations

| Icon | File | Use for |
|------|------|---------|
| Gear Settings | `assets/icons/gear_settings.png` | Settings, configuration |
| Rocket Launch | `assets/icons/rocket_launch.png` | Deployment, launch |
| Sync Refresh | `assets/icons/sync_refresh_arrows.png` | Refresh, synchronization |

## Status

| Icon | File | Use for |
|------|------|---------|
| Checkmark | `assets/icons/checkmark_circle.png` | Success, approved, complete |
| Warning | `assets/icons/warning_triangle.png` | Warning, caution |
| Error X | `assets/icons/error_x_circle.png` | Error, failure, blocked |

## Data

| Icon | File | Use for |
|------|------|---------|
| Document | `assets/icons/document_file.png` | Documents, files |
| Bar Chart | `assets/icons/bar_chart_analytics.png` | Analytics, reporting |

---

## Usage

Use path-based icons in JSON specs — no npm install needed:

```json
{ "type": "icon", "path": "assets/icons/server_rack.png", "x": 2.5, "y": 1.5, "w": 0.4, "h": 0.4 }
```

Paths starting with `assets/icons/` are resolved relative to the skill root automatically by `build_slide.js`.

**Tips:**
- Place icons above or beside their associated shape for visual reinforcement
- Use 0.3"--0.5" size for icons next to shapes, 0.5"--0.8" for standalone icons
- Don't overuse icons — 3-5 per diagram is typically enough
- All 25 icons use a consistent dark navy blue style for visual coherence

---

## Custom Icons via Gemini

For concepts not in the catalog above, generate custom icons using `scripts/generate_icon.py`:

```bash
# Single icon
python3 scripts/generate_icon.py "API gateway" --color "dark navy blue" -o /tmp/icons/api_gateway.png

# Batch of custom icons
python3 scripts/generate_icon.py \
  --batch "API gateway,data lake,IoT sensor,message queue" \
  --color "dark navy blue" \
  --output-dir /tmp/icons/
```

Use the generated icons with the `path` field:
```json
{ "type": "icon", "path": "/tmp/icons/api_gateway.png", "x": 2.5, "y": 1.5, "w": 0.4, "h": 0.4 }
```

See **Step 1b** in `SKILL.md` for the full workflow and CLI options.

---

## Deprecated: react-icons (fallback)

The `name`/`library` fields still work for backward compatibility but require 4 npm packages (react, react-dom, react-icons, sharp). Prefer `path`-based icons from `assets/icons/`.

```json
{ "type": "icon", "name": "FaServer", "library": "fa", "x": 2.5, "y": 1.5, "w": 0.4, "h": 0.4, "color": "4A90E2" }
```
