# Icon Catalog for Technical Diagrams

Curated list of react-icons for use with `"type": "icon"` elements. Each entry shows the export name, library, and when to use it.

Install: `npm install -g react react-dom react-icons sharp`

## Infrastructure

| Icon | Library | Name | Use for |
|------|---------|------|---------|
| Server | `fa` | `FaServer` | Application servers, compute instances |
| Database | `fa` | `FaDatabase` | Databases, data stores |
| Hard Drive | `fa` | `FaHdd` | Storage, disk, volumes |
| Microchip | `fa` | `FaMicrochip` | Processing units, embedded systems |
| Network | `fa` | `FaNetworkWired` | Network infrastructure, LAN |
| Desktop | `fa` | `FaDesktop` | Workstations, client machines |
| Memory | `fa` | `FaMemory` | RAM, caching layers |

## Cloud

| Icon | Library | Name | Use for |
|------|---------|------|---------|
| Cloud | `fa` | `FaCloud` | Generic cloud services |
| Cloud Upload | `fa` | `FaCloudUploadAlt` | Upload, ingestion, push to cloud |
| Cloud Download | `fa` | `FaCloudDownloadAlt` | Download, retrieval from cloud |
| AWS | `si` | `SiAmazonaws` | Amazon Web Services |
| Google Cloud | `si` | `SiGooglecloud` | Google Cloud Platform |
| Azure | `si` | `SiMicrosoftazure` | Microsoft Azure |
| Docker | `fa` | `FaDocker` | Containers, Docker |
| Kubernetes | `si` | `SiKubernetes` | Kubernetes orchestration |

## Security

| Icon | Library | Name | Use for |
|------|---------|------|---------|
| Shield | `fa` | `FaShieldAlt` | Security boundary, protection |
| Lock | `fa` | `FaLock` | Encryption, authentication |
| Key | `fa` | `FaKey` | API keys, credentials, secrets |
| User Shield | `fa` | `FaUserShield` | Identity protection, IAM |
| Fingerprint | `fa` | `FaFingerprint` | Biometrics, identity verification |

## People & Organizations

| Icon | Library | Name | Use for |
|------|---------|------|---------|
| User | `fa` | `FaUser` | Single user, actor |
| Users | `fa` | `FaUsers` | User groups, teams |
| User Cog | `fa` | `FaUserCog` | Admin user, operator |
| User Group | `hi` | `HiUserGroup` | Teams, organizations |
| Building | `fa` | `FaBuilding` | Organization, enterprise |

## Data & Files

| Icon | Library | Name | Use for |
|------|---------|------|---------|
| File | `fa` | `FaFileAlt` | Documents, files |
| Folder | `fa` | `FaFolder` | Directories, file systems |
| Bar Chart | `fa` | `FaChartBar` | Analytics, reporting |
| Table | `fa` | `FaTable` | Tabular data, spreadsheets |
| File Export | `fa` | `FaFileExport` | Data export, ETL output |
| File Import | `fa` | `FaFileImport` | Data import, ingestion |

## Network & Communication

| Icon | Library | Name | Use for |
|------|---------|------|---------|
| WiFi | `fa` | `FaWifi` | Wireless, connectivity |
| Globe | `fa` | `FaGlobe` | Internet, web, global |
| Sitemap | `fa` | `FaSitemap` | Hierarchy, org chart, topology |
| Route | `fa` | `FaRoute` | Routing, paths, pipelines |
| Exchange | `fa` | `FaExchangeAlt` | Data exchange, sync, bidirectional |
| Envelope | `fa` | `FaEnvelope` | Email, messaging |
| Broadcast Tower | `fa` | `FaBroadcastTower` | Broadcasting, pub/sub, events |

## Development & CI/CD

| Icon | Library | Name | Use for |
|------|---------|------|---------|
| Code | `fa` | `FaCode` | Source code, development |
| Git | `fa` | `FaGitAlt` | Version control, Git |
| Cogs | `fa` | `FaCogs` | Settings, configuration, processing |
| Terminal | `fa` | `FaTerminal` | CLI, command line, shell |
| Code Branch | `fa` | `FaCodeBranch` | Branching, version control |
| Bug | `fa` | `FaBug` | Debugging, issues, testing |
| Rocket | `fa` | `FaRocket` | Deployment, launch |

## Status & Indicators

| Icon | Library | Name | Use for |
|------|---------|------|---------|
| Check Circle | `fa` | `FaCheckCircle` | Success, approved, complete |
| Warning | `fa` | `FaExclamationTriangle` | Warning, caution |
| Error | `fa` | `FaTimesCircle` | Error, failure, blocked |
| Bell | `fa` | `FaBell` | Notifications, alerts |
| Info Circle | `fa` | `FaInfoCircle` | Information, help |
| Sync | `fa` | `FaSync` | Refresh, synchronization |

## Usage Example

```json
{
  "type": "icon",
  "name": "FaServer",
  "library": "fa",
  "x": 2.3,
  "y": 1.3,
  "w": 0.4,
  "h": 0.4,
  "color": "4A90E2"
}
```

**Tips:**
- Place icons above or beside their associated shape for visual reinforcement
- Use 0.3"–0.5" size for icons next to shapes, 0.5"–0.8" for standalone icons
- Match icon color to the shape's fill color for cohesion
- Don't overuse icons — 3-5 per diagram is typically enough
- Stick to the `fa` (Font Awesome) library unless you need specific brand icons from `si` (Simple Icons)
