# OpenClaw Backup & Restore Guide

**Never Lose Your Setup Again!**

---

## 🚧 Scheduling Guardrail

- **Forbidden:** system `crontab` edits for OpenClaw automation jobs.
- **Required:** use OpenClaw gateway cron for reminders/schedules (`openclaw cron ...`), and use launchd-based backup jobs from this repo for backups.

---

## 🔐 What Gets Backed Up

✅ **Configuration**: `~/.openclaw/openclaw.json`
✅ **Credentials**: `~/.openclaw/credentials/` (WhatsApp, Slack tokens)
✅ **LaunchAgent**: `~/Library/LaunchAgents/ai.openclaw.gateway.plist`
✅ **Custom Scripts**: Health check, startup scripts
✅ **Documentation**: All setup guides

---

## 📦 Automatic Daily Backup

Run this command to set up automatic daily backups:

```bash
~/.openclaw/enable-auto-backup.sh
```

This will:
- Create daily backups in `~/.openclaw/backups/`
- Keep last 30 days of backups
- Install launchd-based backup scheduling (no system crontab)
- Encrypt sensitive credentials

---

## 💾 Manual Backup (Right Now)

```bash
# Create timestamped backup
tar -czf ~/openclaw-backup-$(date +%Y%m%d).tar.gz \
  ~/.openclaw/ \
  ~/Library/LaunchAgents/ai.openclaw.gateway.plist

# Backup location
ls -lh ~/openclaw-backup-*.tar.gz
```

---

## 🔄 Restore from Backup

If you ever need to restore (new machine, reinstall, etc.):

```bash
# Install OpenClaw first
npm install -g openclaw@latest

# Restore backup
cd ~
tar -xzf openclaw-backup-YYYYMMDD.tar.gz

# Reload LaunchAgent
launchctl load ~/Library/LaunchAgents/ai.openclaw.gateway.plist

# Verify
openclaw channels list
```

---

## ☁️ Cloud Backup (Recommended)

### Option 1: iCloud
```bash
# Backup to iCloud
cp -r ~/.openclaw ~/Library/Mobile\ Documents/com~apple~CloudDocs/openclaw-backup
```

### Option 2: Encrypted Archive
```bash
# Create encrypted backup
tar -czf - ~/.openclaw ~/Library/LaunchAgents/ai.openclaw.gateway.plist | \
  openssl enc -aes-256-cbc -salt -out ~/openclaw-encrypted-backup.tar.gz.enc

# To restore encrypted backup:
openssl enc -aes-256-cbc -d -in ~/openclaw-encrypted-backup.tar.gz.enc | \
  tar -xzf - -C ~
```

---

## 🔑 Token Storage (Secure)

Your tokens are stored in:
- **WhatsApp**: `~/.openclaw/credentials/whatsapp/`
- **Slack Bot Token**: `SLACK_BOT_TOKEN` environment variable
- **Slack App Token**: `SLACK_APP_TOKEN` environment variable
- **Gateway Token**: `~/.openclaw/openclaw.json`

**NEVER commit these to git or share publicly!**

---

## 📋 Recovery Checklist

If you lose everything and need to restore:

- [ ] Install OpenClaw: `npm install -g openclaw@latest`
- [ ] Restore backup: `tar -xzf openclaw-backup-DATE.tar.gz`
- [ ] Install LaunchAgent: `openclaw gateway install`
- [ ] Verify WhatsApp: `openclaw channels list`
- [ ] Test WhatsApp: Send test message
- [ ] Verify Slack: Check Slack connection
- [ ] Test Slack: Send test message
- [ ] Check auto-start: `launchctl list | grep openclaw`

---

## 🛡️ Protection Strategies

### 1. Version Control (Recommended)
```bash
# Create git repo for config (tokens excluded)
cd ~/.openclaw
git init
echo "credentials/" >> .gitignore
echo "logs/" >> .gitignore
git add openclaw.json *.md *.sh
git commit -m "OpenClaw configuration backup"

# Push to private repo
git remote add origin git@github.com:YOUR-USERNAME/openclaw-config-private.git
git push -u origin main
```

### 2. Time Machine
- macOS Time Machine automatically backs up `~/.openclaw/`
- Restore from Time Machine if needed

### 3. Scheduled Backups
```bash
# OpenClaw reminders/schedules: gateway cron only
openclaw cron --help
openclaw cron status
openclaw cron list

# Backups: install launchd backup schedule (no system crontab)
./scripts/install-openclaw-backup-jobs.sh
```

---

## 🚨 Emergency Token Recovery

If you lose your Slack tokens:

**Bot Token:**
1. Go to: https://api.slack.com/apps/${SLACK_APP_ID}/install-on-team
2. Reinstall app (or view existing installation)
3. Copy Bot Token again

**App Token:**
1. Go to: Basic Information → App-Level Tokens
2. Generate new token with `connections:write` scope
3. Update OpenClaw configuration

**WhatsApp:**
- Cannot be recovered - must relink
- Backup credentials directory regularly!

---

## ✅ What's Already Protected

✓ LaunchAgent auto-starts on boot
✓ Health check runs every 5 minutes
✓ Logs preserved in `~/.openclaw/logs/`
✓ Configuration backed up on every `openclaw doctor --fix`
✓ Backup scheduler uses launchd (no system crontab)

---

**Bottom Line:** As long as you have a backup of `~/.openclaw/` and the LaunchAgent plist, you can restore everything in under 5 minutes!
