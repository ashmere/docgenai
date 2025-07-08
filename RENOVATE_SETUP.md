# Renovate Setup Guide

This repository uses [Renovate](https://docs.renovatebot.com/) to automatically keep dependencies up to date.

## 🚀 Quick Setup

1. **Run the setup script:**

   ```bash
   ./setup-renovate-secrets.sh
   ```

2. **Commit and push the workflow:**

   ```bash
   git add .github/
   git commit -m "feat: add renovate github action workflow"
   git push
   ```

3. **Test the workflow:**
   - Go to the [Actions tab](../../actions)
   - Find the "Renovate" workflow
   - Click "Run workflow" to test manually

## 📋 Manual Setup (Alternative)

If you prefer to set up manually:

### 1. Create Personal Access Token

1. Go to [GitHub Settings > Personal Access Tokens](https://github.com/settings/tokens)
2. Click "Generate new token (classic)"
3. Set expiration (recommend 90 days or 1 year)
4. Select scopes:
   - `repo` (Full control of private repositories)
   - `workflow` (Update GitHub Action workflows)
5. Click "Generate token"
6. Copy the token (you won't see it again!)

### 2. Set Repository Secret

```bash
# Using GitHub CLI
gh secret set RENOVATE_TOKEN --repo your-username/your-repo-name

# Or go to: https://github.com/your-username/your-repo-name/settings/secrets/actions
```

## 📅 Schedule

The Renovate workflow runs:
- **Weekly**: Every Monday at 9:00 AM UTC
- **On-demand**: Manual trigger via GitHub Actions UI

## ⚙️ Configuration

### Workflow Configuration
- **File**: `.github/workflows/renovate.yml`
- **Action**: `renovatebot/github-action@v40.3.2`
- **Triggers**: Weekly schedule + manual dispatch

### Renovate Configuration
- **File**: `.github/renovate.json`
- **Features**:
  - Groups Python dependencies (Poetry)
  - Groups GitHub Actions updates
  - Limits concurrent PRs (5 max)
  - Limits hourly PRs (2 max)
  - Maintains lock files weekly
  - Auto-assigns to repository owner

## 🔧 Customization

### Modify Update Schedule

Edit `.github/renovate.json`:

```json
{
  "schedule": [
    "before 10am every weekday"
  ]
}
```

### Change PR Limits

```json
{
  "prHourlyLimit": 2,
  "prConcurrentLimit": 5
}
```

### Add Package Rules

```json
{
  "packageRules": [
    {
      "matchPackageNames": ["specific-package"],
      "schedule": ["before 10am on monday"]
    }
  ]
}
```

## 📚 Documentation

- [Renovate Documentation](https://docs.renovatebot.com/)
- [Configuration Options](https://docs.renovatebot.com/configuration-options/)
- [GitHub Action Documentation](https://github.com/marketplace/actions/renovate-bot-github-action)

## 🔍 Monitoring

### Check Workflow Status

```bash
gh workflow list
gh run list --workflow=renovate.yml
```

### View Logs

```bash
gh run view --log
```

### Test Configuration

```bash
# Validate renovate.json
npx renovate-config-validator .github/renovate.json
```

## 🚨 Troubleshooting

### Common Issues

1. **Token Permission Error**
   - Ensure PAT has `repo` and `workflow` scopes
   - Check token hasn't expired

2. **No PRs Created**
   - Check if dependencies are already up to date
   - Verify schedule configuration
   - Check workflow logs for errors

3. **Rate Limiting**
   - Reduce `prHourlyLimit` in configuration
   - Spread updates across different times

### Debug Mode

To enable debug logging, modify the workflow:

```yaml
env:
  LOG_LEVEL: debug
```

## 🎯 Best Practices

1. **Regular Monitoring**: Check PRs weekly
2. **Test Updates**: Always test dependency updates before merging
3. **Staged Rollouts**: Use package rules to control update timing
4. **Documentation**: Keep this guide updated with configuration changes
5. **Token Rotation**: Regularly rotate PAT tokens for security
