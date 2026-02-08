# Changelog

All notable changes to the Telegram News Bot will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2026-02-08

### 🎉 Major Release - Production Ready

Complete refactoring into production-ready application with modular architecture.

### Added
- **Modular Architecture** - Separated into `bot/` directory with 12 modules
- **Database Persistence** - SQLite storage for message history and stats
- **Health Checks** - `/health`, `/ready`, `/metrics`, `/stats` endpoints
- **Monitoring** - Sentry integration, Prometheus metrics, and custom Performance Metrics
- **Performance Tracking** - Detailed timing for DB queries, message processing, and AI latency
- **Rate Limiting** - Token bucket algorithm with exponential backoff
- **AI Hashtags** - Groq API integration for intelligent hashtag generation
- **Graceful Shutdown** - Proper cleanup on SIGTERM/SIGINT
- **Error Handling** - Comprehensive error handling with custom exceptions and error codes
- **Logging** - Structured logging with file rotation
- **Configuration** - Pydantic-based config with validation
- **Documentation** - Comprehensive docs in `docs/` directory
- **Project Structure** - Clean organization with `data/`, `logs/`, `scripts/`
- **Smart Deduplication** - Fuzzy string matching to filter out duplicate news (using `thefuzz`)
- **Docker Support** - Multi-stage `Dockerfile` and `docker-compose.yml` for containerized deployment
- **CI/CD** - Automatic testing pipeline with GitHub Actions
- **Database Migrations** - Framework for schema versioning and rollbacks

### Changed
- **Keyword Filtering** - Now properly enforced (was bypassed in v1)
- **File Structure** - Reorganized into professional layout
- **Configuration** - Moved to `.env` with better organization
- **Logging** - Now uses `logs/bot.log` instead of root directory
- **Database** - Now in `data/bot.db` for better organization

### Fixed
- **Critical: Keyword filtering bypass** - Now strictly enforces keywords
- **Session handling** - Better error messages for authentication
- **Windows compatibility** - UTF-8 encoding fixes for console
- **Signal handlers** - Disabled on Windows (not supported)
- **Database locking** - Better concurrent access handling

### Security
- **Session files** - Moved to `data/` directory (gitignored)
- **Environment variables** - Comprehensive validation
- **Input sanitization** - Added for channel names
- **Secrets management** - Documented best practices

## [1.0.0] - 2026-01-15

### Initial Release

Basic Telegram news forwarding bot.

### Added
- Basic message forwarding from source channels
- Simple keyword filtering
- Spam detection
- AI hashtag generation (Groq)
- Basic logging

### Known Issues
- Keyword filtering not enforced
- No database persistence
- No health checks
- Limited error handling

---

## Upgrade Guide

### From 1.0.0 to 2.0.0

**Breaking Changes:**
1. File structure changed - update paths in deployment
2. Configuration format changed - update `.env` file
3. Database schema changed - old data not compatible

**Migration Steps:**

1. **Backup your data:**
```bash
cp .env .env.backup
cp *.session session.backup/
```

2. **Update configuration:**
```bash
cp .env.example .env
# Copy your values from .env.backup
```

3. **Update file paths:**
```env
DATABASE_PATH=data/bot.db
LOG_FILE=logs/bot.log
```

4. **Create new directories:**
```bash
mkdir -p data logs scripts
```

5. **Move session files:**
```bash
mv *.session data/
```

6. **Restart bot:**
```bash
python -m bot.main
```

---

## Version History

| Version | Date | Status | Notes |
|---------|------|--------|-------|
| 2.0.0 | 2026-02-08 | ✅ Current | Production ready |
| 1.0.0 | 2026-01-15 | ⚠️ Deprecated | Basic version |

---

## Planned Features

### v2.1.0 (Next Release)
- [ ] Comprehensive test suite
- [ ] Database migrations (Alembic)
- [ ] Performance optimizations
- [ ] Enhanced monitoring dashboards

### v2.2.0 (Future)
- [ ] Multi-language support
- [ ] Advanced filtering rules
- [ ] Scheduled posting
- [ ] Analytics dashboard

### v3.0.0 (Long-term)
- [ ] Web UI for management
- [ ] Multiple bot instances
- [ ] Advanced AI features
- [ ] Plugin system

---

**Maintained by:** Telegram News Bot Team  
**License:** MIT  
**Last Updated:** 2026-02-08
