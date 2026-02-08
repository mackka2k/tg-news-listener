# 🤖 Telegram News Bot v2.0

Production-ready Telegram bot that forwards news from multiple source channels to your target channel.

## ✨ Features

- ✅ **Auto-forward** from 5+ source channels
- ✅ **Spam filtering** - blocks ads and promotional content
- ✅ **AI hashtags** - powered by Groq API
- ✅ **Daily limits** - control post frequency
- ✅ **Database persistence** - SQLite storage
- ✅ **Health checks** - monitoring endpoints
- ✅ **Production-ready** - error handling, logging, graceful shutdown

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure

Copy `.env.example` to `.env` and fill in:

```env
# Telegram API (get from https://my.telegram.org/auth)
API_ID=your_api_id
API_HASH=your_api_hash

# Channels
SOURCE_CHANNELS=@channel1,@channel2,@channel3
TARGET_CHANNEL=@your_channel

# Settings
MAX_POSTS_PER_DAY=5
KEYWORDS=_DISABLED_  # Forward all (except spam)

# AI (optional)
GROQ_API_KEY=your_groq_api_key
```

### 3. Run Directly

```bash
python -m bot.main
```

## 🐳 Docker Deployment (Recommended)

Run the bot in a container for consistent environment and easy management.

### Build and Run

```bash
# 1. Build the Docker image
docker build -t news-bot .

# 2. Run the container
docker run -d \
  --name news-bot \
  --env-file .env \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/logs:/app/logs \
  -p 8080:8080 \
  news-bot

# 3. Check logs
docker logs -f news-bot
```

### Using Docker Compose

Simplest way to manage the bot:

```bash
# Start bot in background
docker-compose up -d

# View logs
docker-compose logs -f

# Check status
docker-compose ps

# Stop bot
docker-compose down
```

### Health Check (Docker)

Docker uses the builtin healthcheck. Check status:
```bash
docker inspect --format='{{json .State.Health}}' news-bot
```

```
Source Channels → Bot → Spam Filter → @your_channel
                         ↓
                    AI Hashtags
                    Daily Limit
                    Database
```

## ⚙️ Configuration

### Keywords

- `KEYWORDS=_DISABLED_` - Forward ALL messages (except spam)
- `KEYWORDS=AI,news,breaking` - Only forward messages with these keywords

### Spam Filter

Automatically blocks messages containing:
- реклама, купить, скидка, промокод
- казино, ставки, заработок
- And more...

### Daily Limit

`MAX_POSTS_PER_DAY=5` - Maximum posts per day

## 📝 Monitoring

### Health Endpoints

The bot exposes several HTTP endpoints for monitoring:

#### `/health` - Liveness Check
```bash
curl http://localhost:8080/health
# Response: {"status": "healthy", "uptime_seconds": 123, "timestamp": "..."}
```
Use for: Kubernetes liveness probes, uptime monitoring

#### `/ready` - Readiness Check
```bash
curl http://localhost:8080/ready
# Response: {"ready": true, "database": "ok", "telegram": "connected"}
```
Use for: Kubernetes readiness probes, load balancer health checks

#### `/metrics` - Prometheus Metrics
```bash
curl http://localhost:8080/metrics
# Response: Prometheus format metrics
```
Use for: Prometheus scraping, Grafana dashboards

#### `/stats` - Bot Statistics
```bash
curl http://localhost:8080/stats
# Response: {
#   "uptime_seconds": 3600,
#   "ready": true,
#   "last_message_time": "2026-02-08T16:30:00",
#   "database": {
#     "total_messages": 42,
#     "today_count": 5,
#     "last_7_days": 35
#   }
# }
```
Use for: Dashboards, monitoring, debugging

### Logs

- **Console output** - Real-time logs with colors
- **File**: `logs/bot.log` - Persistent logs with rotation
- **Database**: `data/bot.db` - Message history and stats

### Monitoring Best Practices

```bash
# Check if bot is running
curl -f http://localhost:8080/health || echo "Bot is down!"

# Monitor daily posts
curl -s http://localhost:8080/stats | jq '.database.today_count'

# Watch logs in real-time
tail -f logs/bot.log

# Check database size
ls -lh data/bot.db
```

## 🗂️ Project Structure

```
news-bot/
├── bot/              # Bot code (12 files)
│   ├── main.py       # Entry point
│   ├── client.py     # Bot logic
│   ├── config.py     # Configuration
│   ├── storage.py    # Database
│   ├── filters.py    # Spam filtering
│   └── ...
├── docs/             # Documentation
├── .env              # Your config
├── README.md         # This file
└── requirements.txt  # Dependencies
```

## 🚀 Deployment

See `docs/DEPLOYMENT.md` for Railway deployment instructions.

## 📖 Documentation

- `docs/QUICKSTART.md` - Getting started guide
- `docs/ARCHITECTURE.md` - Technical details
- `docs/DEPLOYMENT.md` - Deployment guide
- `docs/TROUBLESHOOTING.md` - Common issues

## 🎯 Current Setup

**Mode**: Direct forwarding (no review)  
**Source channels**: 5 configured  
**Target**: @news_lt_bot  
**Keyword filtering**: Disabled  
**Spam filtering**: Enabled  

---

**Simple. Fast. Production-ready.** 🎉
