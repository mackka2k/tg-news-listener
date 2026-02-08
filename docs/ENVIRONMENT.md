# 📝 Environment Variables Reference

Complete reference for all environment variables used by the Telegram News Bot.

## 🔑 Required Variables

### Telegram API

| Variable | Description | Example | Where to Get |
|----------|-------------|---------|--------------|
| `API_ID` | Telegram API ID | `12345678` | [my.telegram.org/auth](https://my.telegram.org/auth) |
| `API_HASH` | Telegram API Hash | `abc123...` | [my.telegram.org/auth](https://my.telegram.org/auth) |

### Channels

| Variable | Description | Example | Notes |
|----------|-------------|---------|-------|
| `SOURCE_CHANNELS` | Source channels (comma-separated) | `@channel1,@channel2` | Must have access |
| `TARGET_CHANNEL` | Target channel for forwarding | `@my_channel` | Must be admin |

## ⚙️ Optional Variables

### Filtering

| Variable | Default | Description | Example |
|----------|---------|-------------|---------|
| `MAX_POSTS_PER_DAY` | `5` | Maximum posts per day | `10` |
| `KEYWORDS` | `_DISABLED_` | Keywords to match (or `_DISABLED_` for all) | `AI,news,breaking` |
| `SPAM_KEYWORDS` | (see .env.example) | Keywords to reject | `реклама,купить` |

### Paths

| Variable | Default | Description | Notes |
|----------|---------|-------------|-------|
| `DATABASE_PATH` | `data/bot.db` | SQLite database path | Auto-created |
| `LOG_FILE` | `logs/bot.log` | Log file path | Auto-created |

### AI Integration

| Variable | Default | Description | Where to Get |
|----------|---------|-------------|--------------|
| `GROQ_API_KEY` | (none) | Groq API key for AI hashtags | [console.groq.com](https://console.groq.com/) |

### Monitoring

| Variable | Default | Description | Notes |
|----------|---------|-------------|-------|
| `SENTRY_DSN` | (none) | Sentry DSN for error tracking | Optional |
| `METRICS_PORT` | `8080` | Prometheus metrics port | For monitoring |
| `ENVIRONMENT` | `development` | Environment name | `development` or `production` |
| `LOG_LEVEL` | `INFO` | Logging level | `DEBUG`, `INFO`, `WARNING`, `ERROR` |

### Review Mode (Currently Disabled)

| Variable | Default | Description | Notes |
|----------|---------|-------------|-------|
| `BOT_TOKEN` | (none) | Telegram bot token | From [@BotFather](https://t.me/BotFather) |
| `REVIEW_CHANNEL_ID` | (none) | Review channel/chat ID | For approval workflow |

## 📋 Configuration Examples

### Minimal Setup (Development)
```env
API_ID=12345678
API_HASH=abc123def456
SOURCE_CHANNELS=@channel1,@channel2
TARGET_CHANNEL=@my_channel
KEYWORDS=_DISABLED_
```

### Production Setup
```env
API_ID=12345678
API_HASH=abc123def456
SOURCE_CHANNELS=@channel1,@channel2,@channel3
TARGET_CHANNEL=@my_channel

MAX_POSTS_PER_DAY=10
KEYWORDS=AI,news,breaking,important

DATABASE_PATH=data/bot.db
LOG_FILE=logs/bot.log

GROQ_API_KEY=gsk_...
SENTRY_DSN=https://...@sentry.io/...
METRICS_PORT=8080
ENVIRONMENT=production
LOG_LEVEL=INFO
```

### With Keyword Filtering
```env
# ... other vars ...
KEYWORDS=AI,breaking,urgent,важно,срочно
SPAM_KEYWORDS=реклама,купить,скидка,casino
```

### With Review Mode
```env
# ... other vars ...
BOT_TOKEN=1234567890:ABC-DEF...
REVIEW_CHANNEL_ID=8171885011
```

## 🔒 Security Best Practices

1. **Never commit `.env` to git** - Use `.env.example` as template
2. **Rotate API keys regularly** - Especially in production
3. **Use environment-specific configs** - Different keys for dev/prod
4. **Encrypt sensitive values** - Use secrets management in production
5. **Limit access** - Only necessary team members should have access

## 🐛 Troubleshooting

### "Configuration error: API_ID must be set"
- Check `.env` file exists
- Verify `API_ID` is set and is a number
- Ensure no quotes around the value

### "Cannot access channel @channel_name"
- Verify you're a member of the channel
- Check channel username is correct (with @)
- Ensure userbot has access

### "Database locked"
- Check only one instance is running
- Verify `DATABASE_PATH` is writable
- Check file permissions

## 📚 Related Documentation

- [Quick Start Guide](QUICKSTART.md)
- [Deployment Guide](DEPLOYMENT.md)
- [Troubleshooting](TROUBLESHOOTING.md)

---

**Last Updated:** 2026-02-08
