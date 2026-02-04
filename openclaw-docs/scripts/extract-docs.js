#!/usr/bin/env node
/**
 * OpenClaw Documentation Extractor
 * Extracts and organizes documentation from the OpenClaw repository
 */

const fs = require('fs');
const path = require('path');

// Configuration
const SOURCE_DIR = '/tmp/openclaw-source/docs';
const OUTPUT_DIR = '/home/user/cz-career-architect/openclaw-docs/extracted';

// Target structure mapping
const CATEGORY_MAP = {
  // Core / Getting Started
  'index': { category: '01-core', name: 'overview' },
  'start/getting-started': { category: '01-core', name: 'getting-started' },
  'start/wizard': { category: '01-core', name: 'onboarding-wizard' },
  'start/setup': { category: '01-core', name: 'setup' },
  'start/onboarding': { category: '01-core', name: 'onboarding' },
  'start/pairing': { category: '01-core', name: 'pairing' },
  'start/openclaw': { category: '01-core', name: 'personal-assistant' },
  'start/hubs': { category: '01-core', name: 'hubs' },
  'start/showcase': { category: '01-core', name: 'showcase' },
  'start/lore': { category: '01-core', name: 'lore' },

  // Installation
  'install/index': { category: '02-installation', name: 'overview' },
  'install/installer': { category: '02-installation', name: 'installer' },
  'install/docker': { category: '02-installation', name: 'docker' },
  'install/bun': { category: '02-installation', name: 'bun' },
  'install/nix': { category: '02-installation', name: 'nix' },
  'install/ansible': { category: '02-installation', name: 'ansible' },
  'install/development-channels': { category: '02-installation', name: 'development-channels' },
  'install/updating': { category: '02-installation', name: 'updating' },
  'install/uninstall': { category: '02-installation', name: 'uninstall' },

  // Configuration
  'gateway/configuration': { category: '03-configuration', name: 'gateway-config' },
  'gateway/configuration-examples': { category: '03-configuration', name: 'config-examples' },
  'environment': { category: '03-configuration', name: 'environment' },

  // CLI Reference
  'cli/index': { category: '04-cli', name: 'overview' },
  'cli/agent': { category: '04-cli', name: 'agent' },
  'cli/agents': { category: '04-cli', name: 'agents' },
  'cli/gateway': { category: '04-cli', name: 'gateway' },
  'cli/browser': { category: '04-cli', name: 'browser' },
  'cli/message': { category: '04-cli', name: 'message' },
  'cli/channels': { category: '04-cli', name: 'channels' },
  'cli/configure': { category: '04-cli', name: 'configure' },
  'cli/cron': { category: '04-cli', name: 'cron' },
  'cli/dashboard': { category: '04-cli', name: 'dashboard' },
  'cli/doctor': { category: '04-cli', name: 'doctor' },
  'cli/health': { category: '04-cli', name: 'health' },
  'cli/hooks': { category: '04-cli', name: 'hooks' },
  'cli/logs': { category: '04-cli', name: 'logs' },
  'cli/memory': { category: '04-cli', name: 'memory' },
  'cli/models': { category: '04-cli', name: 'models' },
  'cli/nodes': { category: '04-cli', name: 'nodes' },
  'cli/onboard': { category: '04-cli', name: 'onboard' },
  'cli/pairing': { category: '04-cli', name: 'pairing' },
  'cli/plugins': { category: '04-cli', name: 'plugins' },
  'cli/reset': { category: '04-cli', name: 'reset' },
  'cli/sandbox': { category: '04-cli', name: 'sandbox' },
  'cli/security': { category: '04-cli', name: 'security' },
  'cli/sessions': { category: '04-cli', name: 'sessions' },
  'cli/setup': { category: '04-cli', name: 'setup' },
  'cli/skills': { category: '04-cli', name: 'skills' },
  'cli/status': { category: '04-cli', name: 'status' },
  'cli/system': { category: '04-cli', name: 'system' },
  'cli/tui': { category: '04-cli', name: 'tui' },
  'cli/uninstall': { category: '04-cli', name: 'uninstall' },
  'cli/update': { category: '04-cli', name: 'update' },
  'cli/voicecall': { category: '04-cli', name: 'voicecall' },
  'cli/approvals': { category: '04-cli', name: 'approvals' },
  'cli/directory': { category: '04-cli', name: 'directory' },
  'cli/dns': { category: '04-cli', name: 'dns' },
  'cli/docs': { category: '04-cli', name: 'docs' },

  // Skills & Tools
  'tools/index': { category: '05-skills', name: 'overview' },
  'tools/skills': { category: '05-skills', name: 'skills' },
  'tools/skills-config': { category: '05-skills', name: 'skills-config' },
  'tools/clawhub': { category: '05-skills', name: 'clawhub' },
  'tools/exec': { category: '05-skills', name: 'exec' },
  'tools/browser': { category: '05-skills', name: 'browser' },
  'tools/browser-login': { category: '05-skills', name: 'browser-login' },
  'tools/chrome-extension': { category: '05-skills', name: 'chrome-extension' },
  'tools/browser-linux-troubleshooting': { category: '05-skills', name: 'browser-linux-troubleshooting' },
  'tools/lobster': { category: '05-skills', name: 'lobster' },
  'tools/llm-task': { category: '05-skills', name: 'llm-task' },
  'tools/web': { category: '05-skills', name: 'web' },
  'tools/apply-patch': { category: '05-skills', name: 'apply-patch' },
  'tools/elevated': { category: '05-skills', name: 'elevated' },
  'tools/thinking': { category: '05-skills', name: 'thinking' },
  'tools/reactions': { category: '05-skills', name: 'reactions' },
  'tools/agent-send': { category: '05-skills', name: 'agent-send' },
  'tools/subagents': { category: '05-skills', name: 'subagents' },
  'tools/slash-commands': { category: '05-skills', name: 'slash-commands' },
  'plugin': { category: '05-skills', name: 'plugin-overview' },
  'plugins/voice-call': { category: '05-skills', name: 'voice-call-plugin' },
  'plugins/zalouser': { category: '05-skills', name: 'zalouser-plugin' },

  // Channels
  'channels/index': { category: '06-channels', name: 'overview' },
  'channels/whatsapp': { category: '06-channels', name: 'whatsapp' },
  'channels/telegram': { category: '06-channels', name: 'telegram' },
  'channels/grammy': { category: '06-channels', name: 'grammy' },
  'channels/discord': { category: '06-channels', name: 'discord' },
  'channels/slack': { category: '06-channels', name: 'slack' },
  'channels/signal': { category: '06-channels', name: 'signal' },
  'channels/imessage': { category: '06-channels', name: 'imessage' },
  'channels/msteams': { category: '06-channels', name: 'msteams' },
  'channels/mattermost': { category: '06-channels', name: 'mattermost' },
  'channels/googlechat': { category: '06-channels', name: 'googlechat' },
  'channels/feishu': { category: '06-channels', name: 'feishu' },
  'channels/line': { category: '06-channels', name: 'line' },
  'channels/matrix': { category: '06-channels', name: 'matrix' },
  'channels/zalo': { category: '06-channels', name: 'zalo' },
  'channels/zalouser': { category: '06-channels', name: 'zalouser' },
  'channels/location': { category: '06-channels', name: 'location' },
  'channels/troubleshooting': { category: '06-channels', name: 'troubleshooting' },

  // Architecture & Concepts
  'concepts/architecture': { category: '07-architecture', name: 'overview' },
  'concepts/agent': { category: '07-architecture', name: 'agent-runtime' },
  'concepts/agent-loop': { category: '07-architecture', name: 'agent-loop' },
  'concepts/system-prompt': { category: '07-architecture', name: 'system-prompt' },
  'concepts/context': { category: '07-architecture', name: 'context' },
  'concepts/agent-workspace': { category: '07-architecture', name: 'agent-workspace' },
  'concepts/memory': { category: '07-architecture', name: 'memory' },
  'concepts/session': { category: '07-architecture', name: 'session' },
  'concepts/sessions': { category: '07-architecture', name: 'sessions' },
  'concepts/session-pruning': { category: '07-architecture', name: 'session-pruning' },
  'concepts/session-tool': { category: '07-architecture', name: 'session-tool' },
  'concepts/compaction': { category: '07-architecture', name: 'compaction' },
  'concepts/multi-agent': { category: '07-architecture', name: 'multi-agent' },
  'concepts/presence': { category: '07-architecture', name: 'presence' },
  'concepts/messages': { category: '07-architecture', name: 'messages' },
  'concepts/streaming': { category: '07-architecture', name: 'streaming' },
  'concepts/retry': { category: '07-architecture', name: 'retry' },
  'concepts/queue': { category: '07-architecture', name: 'queue' },
  'concepts/groups': { category: '07-architecture', name: 'groups' },
  'concepts/group-messages': { category: '07-architecture', name: 'group-messages' },
  'concepts/channel-routing': { category: '07-architecture', name: 'channel-routing' },
  'concepts/model-providers': { category: '07-architecture', name: 'model-providers' },
  'concepts/model-failover': { category: '07-architecture', name: 'model-failover' },
  'concepts/models': { category: '07-architecture', name: 'models' },
  'concepts/oauth': { category: '07-architecture', name: 'oauth' },
  'concepts/typebox': { category: '07-architecture', name: 'typebox' },
  'concepts/markdown-formatting': { category: '07-architecture', name: 'markdown-formatting' },
  'concepts/typing-indicators': { category: '07-architecture', name: 'typing-indicators' },
  'concepts/usage-tracking': { category: '07-architecture', name: 'usage-tracking' },
  'concepts/timezone': { category: '07-architecture', name: 'timezone' },

  // Gateway
  'gateway/index': { category: '08-gateway', name: 'overview' },
  'gateway/authentication': { category: '08-gateway', name: 'authentication' },
  'gateway/health': { category: '08-gateway', name: 'health' },
  'gateway/heartbeat': { category: '08-gateway', name: 'heartbeat' },
  'gateway/doctor': { category: '08-gateway', name: 'doctor' },
  'gateway/logging': { category: '08-gateway', name: 'logging' },
  'gateway/gateway-lock': { category: '08-gateway', name: 'gateway-lock' },
  'gateway/background-process': { category: '08-gateway', name: 'background-process' },
  'gateway/multiple-gateways': { category: '08-gateway', name: 'multiple-gateways' },
  'gateway/troubleshooting': { category: '08-gateway', name: 'troubleshooting' },
  'gateway/security/index': { category: '08-gateway', name: 'security' },
  'gateway/sandboxing': { category: '08-gateway', name: 'sandboxing' },
  'gateway/sandbox-vs-tool-policy-vs-elevated': { category: '08-gateway', name: 'sandbox-vs-tool-policy' },
  'gateway/protocol': { category: '08-gateway', name: 'protocol' },
  'gateway/bridge-protocol': { category: '08-gateway', name: 'bridge-protocol' },
  'gateway/openai-http-api': { category: '08-gateway', name: 'openai-http-api' },
  'gateway/tools-invoke-http-api': { category: '08-gateway', name: 'tools-invoke-http-api' },
  'gateway/cli-backends': { category: '08-gateway', name: 'cli-backends' },
  'gateway/local-models': { category: '08-gateway', name: 'local-models' },
  'gateway/pairing': { category: '08-gateway', name: 'pairing' },
  'gateway/discovery': { category: '08-gateway', name: 'discovery' },
  'gateway/bonjour': { category: '08-gateway', name: 'bonjour' },
  'gateway/remote': { category: '08-gateway', name: 'remote' },
  'gateway/remote-gateway-readme': { category: '08-gateway', name: 'remote-gateway-readme' },
  'gateway/tailscale': { category: '08-gateway', name: 'tailscale' },

  // Model Providers
  'providers/index': { category: '09-providers', name: 'overview' },
  'providers/models': { category: '09-providers', name: 'models-list' },
  'providers/anthropic': { category: '09-providers', name: 'anthropic' },
  'providers/openai': { category: '09-providers', name: 'openai' },
  'providers/openrouter': { category: '09-providers', name: 'openrouter' },
  'bedrock': { category: '09-providers', name: 'bedrock' },
  'providers/vercel-ai-gateway': { category: '09-providers', name: 'vercel-ai-gateway' },
  'providers/moonshot': { category: '09-providers', name: 'moonshot' },
  'providers/minimax': { category: '09-providers', name: 'minimax' },
  'providers/opencode': { category: '09-providers', name: 'opencode' },
  'providers/glm': { category: '09-providers', name: 'glm' },
  'providers/zai': { category: '09-providers', name: 'zai' },
  'providers/synthetic': { category: '09-providers', name: 'synthetic' },

  // Deployment & Platforms
  'platforms/index': { category: '10-deployment', name: 'overview' },
  'platforms/macos': { category: '10-deployment', name: 'macos' },
  'platforms/linux': { category: '10-deployment', name: 'linux' },
  'platforms/windows': { category: '10-deployment', name: 'windows' },
  'platforms/android': { category: '10-deployment', name: 'android' },
  'platforms/ios': { category: '10-deployment', name: 'ios' },
  'platforms/fly': { category: '10-deployment', name: 'fly-io' },
  'platforms/hetzner': { category: '10-deployment', name: 'hetzner' },
  'platforms/gcp': { category: '10-deployment', name: 'gcp' },
  'platforms/macos-vm': { category: '10-deployment', name: 'macos-vm' },
  'platforms/exe-dev': { category: '10-deployment', name: 'exe-dev' },
  'railway': { category: '10-deployment', name: 'railway' },
  'render': { category: '10-deployment', name: 'render' },
  'northflank': { category: '10-deployment', name: 'northflank' },

  // Automation
  'hooks': { category: '11-automation', name: 'hooks' },
  'hooks/soul-evil': { category: '11-automation', name: 'soul-evil' },
  'automation/cron-jobs': { category: '11-automation', name: 'cron-jobs' },
  'automation/cron-vs-heartbeat': { category: '11-automation', name: 'cron-vs-heartbeat' },
  'automation/webhook': { category: '11-automation', name: 'webhook' },
  'automation/gmail-pubsub': { category: '11-automation', name: 'gmail-pubsub' },
  'automation/poll': { category: '11-automation', name: 'poll' },
  'automation/auth-monitoring': { category: '11-automation', name: 'auth-monitoring' },

  // Nodes / Media
  'nodes/index': { category: '12-nodes', name: 'overview' },
  'nodes/images': { category: '12-nodes', name: 'images' },
  'nodes/audio': { category: '12-nodes', name: 'audio' },
  'nodes/camera': { category: '12-nodes', name: 'camera' },
  'nodes/talk': { category: '12-nodes', name: 'talk' },
  'nodes/voicewake': { category: '12-nodes', name: 'voicewake' },
  'nodes/location-command': { category: '12-nodes', name: 'location-command' },

  // Web Interfaces
  'web/index': { category: '13-web', name: 'overview' },
  'web/control-ui': { category: '13-web', name: 'control-ui' },
  'web/dashboard': { category: '13-web', name: 'dashboard' },
  'web/webchat': { category: '13-web', name: 'webchat' },
  'tui': { category: '13-web', name: 'tui' },

  // Reference & Templates
  'reference/rpc': { category: '14-reference', name: 'rpc' },
  'reference/device-models': { category: '14-reference', name: 'device-models' },
  'reference/AGENTS.default': { category: '14-reference', name: 'agents-default' },
  'reference/templates/AGENTS': { category: '14-reference', name: 'template-agents' },
  'reference/templates/BOOT': { category: '14-reference', name: 'template-boot' },
  'reference/templates/BOOTSTRAP': { category: '14-reference', name: 'template-bootstrap' },
  'reference/templates/HEARTBEAT': { category: '14-reference', name: 'template-heartbeat' },
  'reference/templates/IDENTITY': { category: '14-reference', name: 'template-identity' },
  'reference/templates/SOUL': { category: '14-reference', name: 'template-soul' },
  'reference/templates/TOOLS': { category: '14-reference', name: 'template-tools' },
  'reference/templates/USER': { category: '14-reference', name: 'template-user' },
  'reference/RELEASING': { category: '14-reference', name: 'releasing' },
  'reference/session-management-compaction': { category: '14-reference', name: 'session-management-compaction' },

  // Help
  'help/index': { category: '15-help', name: 'overview' },
  'help/troubleshooting': { category: '15-help', name: 'troubleshooting' },
  'help/faq': { category: '15-help', name: 'faq' },
  'debugging': { category: '15-help', name: 'debugging' },
  'testing': { category: '15-help', name: 'testing' },
  'scripts': { category: '15-help', name: 'scripts' },

  // Misc standalone files
  'broadcast-groups': { category: '07-architecture', name: 'broadcast-groups' },
  'multi-agent-sandbox-tools': { category: '05-skills', name: 'multi-agent-sandbox-tools' },
  'token-use': { category: '14-reference', name: 'token-use' },
  'pi': { category: '07-architecture', name: 'pi-agent' },
  'pi-dev': { category: '07-architecture', name: 'pi-agent-dev' },
  'logging': { category: '08-gateway', name: 'logging-standalone' },
  'prose': { category: '14-reference', name: 'prose' },
  'date-time': { category: '14-reference', name: 'date-time' },
  'network': { category: '08-gateway', name: 'network' },
  'perplexity': { category: '09-providers', name: 'perplexity' },
  'brave-search': { category: '09-providers', name: 'brave-search' },
};

// Category metadata
const CATEGORIES = {
  '01-core': { name: 'Core', description: 'Getting started and basic concepts' },
  '02-installation': { name: 'Installation', description: 'Installation methods and package managers' },
  '03-configuration': { name: 'Configuration', description: 'Configuration options and examples' },
  '04-cli': { name: 'CLI Reference', description: 'Command-line interface documentation' },
  '05-skills': { name: 'Skills & Tools', description: 'Skills system, tools, and extensions' },
  '06-channels': { name: 'Channels', description: 'Messaging platform integrations' },
  '07-architecture': { name: 'Architecture', description: 'System design, agents, and concepts' },
  '08-gateway': { name: 'Gateway', description: 'Gateway configuration and protocols' },
  '09-providers': { name: 'Model Providers', description: 'LLM provider configurations' },
  '10-deployment': { name: 'Deployment', description: 'Platform-specific deployment guides' },
  '11-automation': { name: 'Automation', description: 'Hooks, cron jobs, and webhooks' },
  '12-nodes': { name: 'Nodes', description: 'Media and device integrations' },
  '13-web': { name: 'Web Interfaces', description: 'Web UI and dashboard' },
  '14-reference': { name: 'Reference', description: 'Templates, RPC, and technical reference' },
  '15-help': { name: 'Help', description: 'FAQ, troubleshooting, and debugging' },
};

/**
 * Clean MDX content to pure Markdown
 */
function cleanMdx(content) {
  let cleaned = content;

  // Remove import statements
  cleaned = cleaned.replace(/^import\s+.*$/gm, '');

  // Remove export statements
  cleaned = cleaned.replace(/^export\s+.*$/gm, '');

  // Convert MDX components to markdown equivalents
  // <Note> -> blockquote
  cleaned = cleaned.replace(/<Note[^>]*>([\s\S]*?)<\/Note>/g, (_, inner) => {
    return `> **Note:** ${inner.trim()}\n`;
  });

  // <Warning> -> blockquote
  cleaned = cleaned.replace(/<Warning[^>]*>([\s\S]*?)<\/Warning>/g, (_, inner) => {
    return `> **Warning:** ${inner.trim()}\n`;
  });

  // <Tip> -> blockquote
  cleaned = cleaned.replace(/<Tip[^>]*>([\s\S]*?)<\/Tip>/g, (_, inner) => {
    return `> **Tip:** ${inner.trim()}\n`;
  });

  // <Info> -> blockquote
  cleaned = cleaned.replace(/<Info[^>]*>([\s\S]*?)<\/Info>/g, (_, inner) => {
    return `> **Info:** ${inner.trim()}\n`;
  });

  // <Callout> -> blockquote
  cleaned = cleaned.replace(/<Callout[^>]*>([\s\S]*?)<\/Callout>/g, (_, inner) => {
    return `> ${inner.trim()}\n`;
  });

  // <CodeGroup> -> just keep the code blocks inside
  cleaned = cleaned.replace(/<CodeGroup[^>]*>([\s\S]*?)<\/CodeGroup>/g, '$1');

  // <Tab> with title -> ### Title
  cleaned = cleaned.replace(/<Tab\s+title="([^"]*)"[^>]*>([\s\S]*?)<\/Tab>/g, (_, title, inner) => {
    return `### ${title}\n\n${inner.trim()}\n`;
  });

  // <Tabs> -> just keep inner content
  cleaned = cleaned.replace(/<Tabs[^>]*>([\s\S]*?)<\/Tabs>/g, '$1');

  // <Accordion> -> details/summary style using markdown
  cleaned = cleaned.replace(/<Accordion\s+title="([^"]*)"[^>]*>([\s\S]*?)<\/Accordion>/g, (_, title, inner) => {
    return `<details>\n<summary>${title}</summary>\n\n${inner.trim()}\n\n</details>\n`;
  });

  // <AccordionGroup> -> just keep inner
  cleaned = cleaned.replace(/<AccordionGroup[^>]*>([\s\S]*?)<\/AccordionGroup>/g, '$1');

  // <Card> with title -> ### Title
  cleaned = cleaned.replace(/<Card\s+title="([^"]*)"[^>]*>([\s\S]*?)<\/Card>/g, (_, title, inner) => {
    return `### ${title}\n\n${inner.trim()}\n`;
  });

  // <CardGroup> -> just keep inner
  cleaned = cleaned.replace(/<CardGroup[^>]*>([\s\S]*?)<\/CardGroup>/g, '$1');

  // <Steps> -> keep inner with numbered steps
  cleaned = cleaned.replace(/<Steps[^>]*>([\s\S]*?)<\/Steps>/g, '$1');

  // <Step> with title
  cleaned = cleaned.replace(/<Step\s+title="([^"]*)"[^>]*>([\s\S]*?)<\/Step>/g, (_, title, inner) => {
    return `#### ${title}\n\n${inner.trim()}\n`;
  });

  // <Frame> -> just keep inner
  cleaned = cleaned.replace(/<Frame[^>]*>([\s\S]*?)<\/Frame>/g, '$1');

  // <ResponseField> -> formatted field
  cleaned = cleaned.replace(/<ResponseField\s+name="([^"]*)"[^>]*>([\s\S]*?)<\/ResponseField>/g, (_, name, inner) => {
    return `- **${name}**: ${inner.trim()}\n`;
  });

  // <ParamField> -> formatted param
  cleaned = cleaned.replace(/<ParamField[^>]*name="([^"]*)"[^>]*>([\s\S]*?)<\/ParamField>/g, (_, name, inner) => {
    return `- **${name}**: ${inner.trim()}\n`;
  });

  // <Expandable> -> details
  cleaned = cleaned.replace(/<Expandable\s+title="([^"]*)"[^>]*>([\s\S]*?)<\/Expandable>/g, (_, title, inner) => {
    return `<details>\n<summary>${title}</summary>\n\n${inner.trim()}\n\n</details>\n`;
  });

  // Self-closing components - remove completely
  cleaned = cleaned.replace(/<(Icon|Snippet|Check|X)[^>]*\/>/g, '');

  // Remove any remaining JSX-style components we don't handle
  cleaned = cleaned.replace(/<[A-Z][a-zA-Z]*[^>]*>([\s\S]*?)<\/[A-Z][a-zA-Z]*>/g, '$1');
  cleaned = cleaned.replace(/<[A-Z][a-zA-Z]*[^>]*\/>/g, '');

  // Clean up empty lines
  cleaned = cleaned.replace(/\n{3,}/g, '\n\n');

  return cleaned.trim();
}

/**
 * Extract frontmatter and content
 */
function parseFrontmatter(content) {
  const frontmatterMatch = content.match(/^---\n([\s\S]*?)\n---\n([\s\S]*)$/);
  if (frontmatterMatch) {
    const frontmatter = {};
    const lines = frontmatterMatch[1].split('\n');
    for (const line of lines) {
      const match = line.match(/^(\w+):\s*(.*)$/);
      if (match) {
        let value = match[2].trim();
        // Remove quotes
        if ((value.startsWith('"') && value.endsWith('"')) ||
            (value.startsWith("'") && value.endsWith("'"))) {
          value = value.slice(1, -1);
        }
        frontmatter[match[1]] = value;
      }
    }
    return { frontmatter, content: frontmatterMatch[2] };
  }
  return { frontmatter: {}, content };
}

/**
 * Find source file (try .md then .mdx)
 */
function findSourceFile(basePath) {
  const mdPath = path.join(SOURCE_DIR, basePath + '.md');
  const mdxPath = path.join(SOURCE_DIR, basePath + '.mdx');

  if (fs.existsSync(mdPath)) return mdPath;
  if (fs.existsSync(mdxPath)) return mdxPath;
  return null;
}

/**
 * Process a single file
 */
function processFile(pageKey) {
  const mapping = CATEGORY_MAP[pageKey];
  if (!mapping) {
    console.log(`  [SKIP] No mapping for: ${pageKey}`);
    return null;
  }

  const sourcePath = findSourceFile(pageKey);
  if (!sourcePath) {
    console.log(`  [SKIP] File not found: ${pageKey}`);
    return null;
  }

  const rawContent = fs.readFileSync(sourcePath, 'utf-8');
  const { frontmatter, content } = parseFrontmatter(rawContent);
  const cleanedContent = cleanMdx(content);

  const title = frontmatter.title || mapping.name;
  const description = frontmatter.description || '';

  // Build final markdown - avoid duplicate title
  let finalContent = '';

  // Check if content already starts with a title
  const startsWithTitle = cleanedContent.match(/^#\s+.+/);

  if (!startsWithTitle) {
    finalContent = `# ${title}\n\n`;
  }

  if (description && !cleanedContent.includes(description)) {
    finalContent += `> ${description}\n\n`;
  }

  finalContent += cleanedContent;

  return {
    pageKey,
    category: mapping.category,
    name: mapping.name,
    title,
    description,
    content: finalContent,
    sourcePath: sourcePath.replace(SOURCE_DIR + '/', ''),
  };
}

/**
 * Main extraction function
 */
function extractDocs() {
  console.log('OpenClaw Documentation Extractor');
  console.log('================================\n');

  // Create output directories
  for (const category of Object.keys(CATEGORIES)) {
    const dir = path.join(OUTPUT_DIR, category);
    fs.mkdirSync(dir, { recursive: true });
  }

  const metadata = {
    name: 'openclaw-docs',
    version: '1.0.0',
    source: 'https://github.com/openclaw/openclaw',
    extracted_at: new Date().toISOString(),
    documents: [],
    categories: CATEGORIES,
  };

  let processed = 0;
  let skipped = 0;

  for (const pageKey of Object.keys(CATEGORY_MAP)) {
    const result = processFile(pageKey);
    if (result) {
      const outputPath = path.join(OUTPUT_DIR, result.category, `${result.name}.md`);
      fs.writeFileSync(outputPath, result.content);

      metadata.documents.push({
        id: `${result.category}/${result.name}`,
        title: result.title,
        path: `${result.category}/${result.name}.md`,
        source_path: result.sourcePath,
        source_url: `https://docs.openclaw.ai/${result.pageKey.replace('/index', '')}`,
        github_url: `https://github.com/openclaw/openclaw/blob/main/docs/${result.sourcePath}`,
        category: result.category,
        description: result.description,
      });

      console.log(`  [OK] ${result.category}/${result.name}.md`);
      processed++;
    } else {
      skipped++;
    }
  }

  // Write metadata
  const metadataPath = path.join(OUTPUT_DIR, 'metadata.json');
  fs.writeFileSync(metadataPath, JSON.stringify(metadata, null, 2));

  console.log(`\n================================`);
  console.log(`Processed: ${processed} files`);
  console.log(`Skipped: ${skipped} files`);
  console.log(`Output: ${OUTPUT_DIR}`);
  console.log(`Metadata: ${metadataPath}`);
}

// Run extraction
extractDocs();
