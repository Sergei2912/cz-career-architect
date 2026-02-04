# OpenClaw Documentation Extraction Plan

## Reconnaissance Summary

### Sources Discovered

#### 1. GitHub Repository (Primary Source)
- **URL**: https://github.com/openclaw/openclaw/tree/main/docs
- **Access**: Open, raw files accessible via `raw.githubusercontent.com`
- **Format**: Markdown (.md) and MDX (.mdx)
- **Structure**: 25+ directories, 31+ files in root

**Directory Structure:**
```
docs/
├── .i18n/              # Internationalization
├── _layouts/           # Jekyll layouts
├── assets/             # Static assets
├── automation/         # Webhooks, cron, scripts
├── channels/           # WhatsApp, Telegram, Discord, Signal, etc.
├── cli/                # CLI command reference
├── concepts/           # Core concepts (memory, sessions, routing)
├── debug/              # Debugging guides
├── diagnostics/        # Health checks
├── experiments/        # Experimental features
├── gateway/            # Gateway architecture & config
├── help/               # FAQ, troubleshooting
├── hooks/              # Hook system
├── images/             # Documentation images
├── install/            # Installation (Docker, Ansible, npm)
├── nodes/              # iOS/Android companion apps
├── platforms/          # macOS, Linux, Windows, Cloud (Fly.io, DO, etc.)
├── plugins/            # Plugin development
├── providers/          # Model providers (Anthropic, OpenAI)
├── refactor/           # Internal refactoring docs
├── reference/          # Templates (AGENTS.md, SOUL.md, etc.)
├── security/           # Security configuration
├── start/              # Getting started guides
├── tools/              # Skills, Chrome extension, exec
├── web/                # WebChat, Control UI
└── zh-CN/              # Chinese translations
```

#### 2. docs.openclaw.ai (Official Documentation)
- **URL**: https://docs.openclaw.ai/
- **Access**: Returns 403 on direct fetch (Cloudflare protection)
- **Framework**: Appears to be static site (likely VitePress/Jekyll based on _config.yml)
- **Workaround**: Content accessible via:
  - Web search indexing (Google)
  - GitHub raw files (source of truth)

**Key Pages Discovered:**
| Category | URLs |
|----------|------|
| Getting Started | `/start/getting-started`, `/start/wizard`, `/start/openclaw`, `/start/setup`, `/start/pairing` |
| Channels | `/channels`, `/channels/whatsapp`, `/channels/telegram`, `/channels/signal`, `/channels/msteams` |
| Gateway | `/gateway/configuration`, `/gateway/security`, `/gateway/troubleshooting`, `/gateway/cli-backends` |
| Tools | `/tools`, `/tools/skills`, `/tools/skills-config`, `/tools/clawhub`, `/tools/chrome-extension`, `/tools/exec` |
| CLI | `/cli`, `/cli/agent`, `/cli/gateway`, `/cli/browser`, `/cli/message` |
| Concepts | `/concepts/memory`, `/concepts/session`, `/concepts/agent`, `/concepts/groups`, `/concepts/messages`, `/concepts/model-providers`, `/concepts/channel-routing`, `/concepts/multi-agent` |
| Plugins | `/plugins/manifest`, `/plugins/agent-tools` |
| Install | `/install`, `/install/docker`, `/install/ansible`, `/install/development-channels` |
| Platforms | `/platforms/windows`, `/platforms/linux`, `/platforms/fly`, `/platforms/digitalocean`, `/platforms/macos-vm` |
| Automation | `/automation/webhook` |
| Reference | `/reference/session-management-compaction`, `/reference/templates/AGENTS` |
| VPS | `/vps`, `/northflank.mdx`, `/railway.mdx`, `/render.mdx` |
| Help | `/help/faq` |

#### 3. DeepWiki (Architecture Deep Dive)
- **URL**: https://deepwiki.com/openclaw/openclaw
- **Access**: Returns 403 on direct fetch
- **Content**: AI-generated documentation from source code analysis

**Sections Discovered:**
```
1. Overview
2. Architecture
3. Gateway System
4. Configuration
   4.1 Configuration File Structure
5. Agent System
6. Tools and Skills
   6.1 Built-in Tools
   6.2 Tool Security and Sandboxing
7. Memory System
8. Channel Integrations
   8.4 Discord Integration
   8.5 Signal Integration
9. Web Interfaces
10. Extensions and Plugins
11. Companion Applications
12. CLI Reference
    12.4 Model Commands
    12.5 Configuration Commands
13. Deployment
14. Operations and Troubleshooting
```

---

## Technical Analysis

### Extraction Methods

#### Method 1: GitHub Raw Files (Recommended)
```
Base URL: https://raw.githubusercontent.com/openclaw/openclaw/main/docs/
Example:  https://raw.githubusercontent.com/openclaw/openclaw/main/docs/start/getting-started.md
```
- **Pros**: Direct access, no rate limiting, source of truth
- **Cons**: Need to discover file paths

#### Method 2: GitHub API
```bash
# List directory contents
curl -H "Accept: application/vnd.github.v3+json" \
  https://api.github.com/repos/openclaw/openclaw/contents/docs

# Recursive tree
curl https://api.github.com/repos/openclaw/openclaw/git/trees/main?recursive=1
```
- **Pros**: Structured data, can enumerate all files
- **Cons**: Rate limited (60/hour unauthenticated)

#### Method 3: Clone Repository
```bash
git clone --depth 1 --filter=blob:none --sparse https://github.com/openclaw/openclaw.git
cd openclaw
git sparse-checkout set docs
```
- **Pros**: Fast, complete, offline access
- **Cons**: Requires git

### Content Processing

1. **MDX → Markdown**: Strip JSX components, keep prose
2. **Code blocks**: Preserve with language hints
3. **Internal links**: Convert to relative paths
4. **Images**: Download and store locally

---

## Extraction Plan

### Phase 1: Core Documentation (Priority 1)

#### 1.1 Getting Started
| Source File | Target File | Priority |
|-------------|-------------|----------|
| `docs/start/getting-started.md` | `01-core/getting-started.md` | P1 |
| `docs/start/wizard.md` | `01-core/onboarding-wizard.md` | P1 |
| `docs/start/openclaw.md` | `01-core/personal-assistant-setup.md` | P1 |
| `docs/start/setup.md` | `01-core/setup.md` | P1 |
| `docs/start/pairing.md` | `01-core/pairing.md` | P1 |

#### 1.2 Configuration
| Source File | Target File | Priority |
|-------------|-------------|----------|
| `docs/gateway/configuration.md` | `02-configuration/gateway-config.md` | P1 |
| `docs/gateway/configuration-examples.md` | `02-configuration/config-examples.md` | P1 |
| `docs/environment.md` | `02-configuration/environment.md` | P1 |

#### 1.3 CLI Reference
| Source File | Target File | Priority |
|-------------|-------------|----------|
| `docs/cli/index.md` (or cli.md) | `03-cli/cli-overview.md` | P1 |
| `docs/cli/agent.md` | `03-cli/agent-command.md` | P1 |
| `docs/cli/gateway.md` | `03-cli/gateway-command.md` | P1 |
| `docs/cli/browser.md` | `03-cli/browser-command.md` | P2 |
| `docs/cli/message.md` | `03-cli/message-command.md` | P2 |

### Phase 2: Skills & Tools (Priority 1)

| Source File | Target File | Priority |
|-------------|-------------|----------|
| `docs/tools/skills.md` | `04-skills/skills-overview.md` | P1 |
| `docs/tools/skills-config.md` | `04-skills/skills-config.md` | P1 |
| `docs/tools/clawhub.md` | `04-skills/clawhub-registry.md` | P1 |
| `docs/tools/exec.md` | `04-skills/exec-tool.md` | P2 |
| `docs/tools/chrome-extension.md` | `04-skills/chrome-extension.md` | P2 |

### Phase 3: Channels (Priority 2)

| Source File | Target File | Priority |
|-------------|-------------|----------|
| `docs/channels/index.md` | `05-channels/channels-overview.md` | P1 |
| `docs/channels/whatsapp.md` | `05-channels/whatsapp.md` | P1 |
| `docs/channels/telegram.md` | `05-channels/telegram.md` | P1 |
| `docs/channels/discord.md` | `05-channels/discord.md` | P2 |
| `docs/channels/slack.md` | `05-channels/slack.md` | P2 |
| `docs/channels/signal.md` | `05-channels/signal.md` | P2 |
| `docs/channels/imessage.md` | `05-channels/imessage.md` | P3 |
| `docs/channels/msteams.md` | `05-channels/msteams.md` | P3 |

### Phase 4: Architecture & Concepts (Priority 2)

| Source File | Target File | Priority |
|-------------|-------------|----------|
| `docs/gateway/*.md` | `06-architecture/gateway-*.md` | P1 |
| `docs/concepts/agent.md` | `06-architecture/agent-runtime.md` | P1 |
| `docs/concepts/memory.md` | `06-architecture/memory-system.md` | P1 |
| `docs/concepts/session.md` | `06-architecture/session-management.md` | P2 |
| `docs/concepts/multi-agent.md` | `06-architecture/multi-agent-routing.md` | P2 |
| `docs/concepts/model-providers.md` | `06-architecture/model-providers.md` | P2 |

### Phase 5: Plugins & Extensions (Priority 2)

| Source File | Target File | Priority |
|-------------|-------------|----------|
| `docs/plugins/manifest.md` | `07-plugins/plugin-manifest.md` | P1 |
| `docs/plugins/agent-tools.md` | `07-plugins/agent-tools.md` | P1 |
| `docs/plugin.md` | `07-plugins/plugin-overview.md` | P2 |

### Phase 6: Deployment (Priority 2)

| Source File | Target File | Priority |
|-------------|-------------|----------|
| `docs/install/docker.md` | `08-deployment/docker.md` | P1 |
| `docs/install/ansible.md` | `08-deployment/ansible.md` | P1 |
| `docs/vps.md` | `08-deployment/vps-overview.md` | P1 |
| `docs/platforms/fly.md` | `08-deployment/fly-io.md` | P2 |
| `docs/platforms/digitalocean.md` | `08-deployment/digitalocean.md` | P2 |
| `docs/platforms/linux.md` | `08-deployment/linux.md` | P2 |
| `docs/platforms/windows.md` | `08-deployment/windows-wsl2.md` | P2 |

### Phase 7: DeepWiki Content (Priority 3)

Extract via web search summaries (since direct access blocked):
| Topic | Target File |
|-------|-------------|
| Architecture Overview | `09-deepwiki/architecture.md` |
| Agent System Internals | `09-deepwiki/agent-system.md` |
| Tool Security & Sandboxing | `09-deepwiki/tool-security.md` |
| Gateway Operations | `09-deepwiki/gateway-operations.md` |

---

## Output Structure

```
/openclaw-docs/
├── 01-core/
│   ├── getting-started.md
│   ├── onboarding-wizard.md
│   ├── personal-assistant-setup.md
│   ├── setup.md
│   └── pairing.md
├── 02-configuration/
│   ├── gateway-config.md
│   ├── config-examples.md
│   └── environment.md
├── 03-cli/
│   ├── cli-overview.md
│   ├── agent-command.md
│   ├── gateway-command.md
│   ├── browser-command.md
│   └── message-command.md
├── 04-skills/
│   ├── skills-overview.md
│   ├── skills-config.md
│   ├── clawhub-registry.md
│   ├── exec-tool.md
│   └── chrome-extension.md
├── 05-channels/
│   ├── channels-overview.md
│   ├── whatsapp.md
│   ├── telegram.md
│   ├── discord.md
│   ├── slack.md
│   ├── signal.md
│   ├── imessage.md
│   └── msteams.md
├── 06-architecture/
│   ├── gateway-overview.md
│   ├── gateway-security.md
│   ├── agent-runtime.md
│   ├── memory-system.md
│   ├── session-management.md
│   ├── multi-agent-routing.md
│   └── model-providers.md
├── 07-plugins/
│   ├── plugin-overview.md
│   ├── plugin-manifest.md
│   └── agent-tools.md
├── 08-deployment/
│   ├── docker.md
│   ├── ansible.md
│   ├── vps-overview.md
│   ├── fly-io.md
│   ├── digitalocean.md
│   ├── linux.md
│   └── windows-wsl2.md
├── 09-deepwiki/
│   ├── architecture.md
│   ├── agent-system.md
│   ├── tool-security.md
│   └── gateway-operations.md
├── assets/
│   └── images/
└── metadata.json
```

---

## Implementation Strategy

### Option A: Git Clone + Script (Recommended)
```bash
# Clone docs only
git clone --depth 1 --filter=blob:none --sparse \
  https://github.com/openclaw/openclaw.git /tmp/openclaw-source
cd /tmp/openclaw-source
git sparse-checkout set docs

# Run extraction script
node extract-docs.js
```

**Advantages:**
- Complete access to all files
- No rate limits
- Preserves directory structure
- Can process MDX files

### Option B: GitHub API + WebFetch
```javascript
// Enumerate files via API
const tree = await fetch('https://api.github.com/repos/openclaw/openclaw/git/trees/main?recursive=1');
// Fetch each .md file via raw.githubusercontent.com
```

**Advantages:**
- No git required
- More control over processing

### Option C: Hybrid (Web Search + Raw Files)
- Use web search to discover pages
- Fetch content from raw.githubusercontent.com

---

## Metadata Schema

```json
{
  "name": "openclaw-docs",
  "version": "1.0.0",
  "source": "https://github.com/openclaw/openclaw",
  "extracted_at": "2026-02-04T00:00:00Z",
  "documents": [
    {
      "id": "getting-started",
      "title": "Getting Started",
      "path": "01-core/getting-started.md",
      "source_url": "https://docs.openclaw.ai/start/getting-started",
      "github_url": "https://github.com/openclaw/openclaw/blob/main/docs/start/getting-started.md",
      "category": "core",
      "tags": ["installation", "setup", "quickstart"],
      "priority": 1
    }
  ],
  "categories": {
    "core": { "name": "Core", "description": "Getting started and basic setup" },
    "configuration": { "name": "Configuration", "description": "Configuration options and examples" },
    "cli": { "name": "CLI Reference", "description": "Command-line interface documentation" },
    "skills": { "name": "Skills & Tools", "description": "Skills system and built-in tools" },
    "channels": { "name": "Channels", "description": "Messaging platform integrations" },
    "architecture": { "name": "Architecture", "description": "System design and concepts" },
    "plugins": { "name": "Plugins", "description": "Plugin development" },
    "deployment": { "name": "Deployment", "description": "Installation and hosting" }
  }
}
```

---

## Next Steps

1. **Approve plan** - Confirm structure and priorities
2. **Clone repository** - Get docs source
3. **Create extraction script** - Process and organize files
4. **Generate metadata** - Create RAG index
5. **Validate output** - Check completeness

---

## Sources

- [GitHub - openclaw/openclaw](https://github.com/openclaw/openclaw)
- [GitHub - docs folder](https://github.com/openclaw/openclaw/tree/main/docs)
- [docs.openclaw.ai](https://docs.openclaw.ai/)
- [DeepWiki - openclaw](https://deepwiki.com/openclaw/openclaw)
- [Vultr - OpenClaw Deployment](https://docs.vultr.com/how-to-deploy-openclaw-autonomous-ai-agent-platform)
- [DigitalOcean - What is OpenClaw](https://www.digitalocean.com/resources/articles/what-is-openclaw)
