# 🚀 Деплой на Render.com

## ⚠️ Важная информация

### Ограничения Render с Selenium:

| План | RAM | Selenium | Рекомендация |
|------|-----|----------|-------------|
| **Free** | 512MB | ❌ Не хватит | Не подходит |
| **Starter** | 512MB | ⚠️ Может падать | Рискованно |
| **Standard** | 2GB+ | ✅ Работает | **Рекомендуется** |

**Chrome + Selenium требуют минимум 1.5-2 GB RAM!**

---

## 📋 Пошаговая инструкция

### 1. Подготовка репозитория

```bash
# Инициализируйте git (если еще не сделано)
git init

# Добавьте все файлы
git add .

# Коммит
git commit -m "Initial commit for Render deploy"

# Создайте репозиторий на GitHub
# Затем:
git remote add origin https://github.com/ваш-username/tgads_new.git
git branch -M main
git push -u origin main
```

### 2. Создание Web Service на Render

1. **Зайдите на** https://render.com
2. **Нажмите** "New +" → "Web Service"
3. **Подключите** ваш GitHub репозиторий
4. **Выберите** репозиторий `tgads_new`

### 3. Настройки при создании сервиса

#### Basic Settings:
- **Name:** `tgads-parser` (или любое)
- **Region:** `Frankfurt` (ближе к России)
- **Branch:** `main`
- **Root Directory:** оставьте пустым

#### Build & Deploy:
- **Environment:** `Docker`
- **Dockerfile Path:** `./Dockerfile`

#### Instance Type:
- ⚠️ **Минимум:** `Starter` ($7/мес)
- ✅ **Рекомендуется:** `Standard` ($25/мес)

### 4. Переменные окружения (Environment Variables)

Добавьте в Render:
```
PYTHONUNBUFFERED=1
PORT=8000
```

### 5. Запуск

Нажмите **"Create Web Service"**

Render автоматически:
1. Соберет Docker образ
2. Установит Chrome и ChromeDriver
3. Запустит приложение

---

## 🔍 Проверка деплоя

### 1. Статус сборки

В Render Dashboard → Logs:
```
==> Building...
==> Deploying...
==> Your service is live 🎉
```

### 2. Проверка API

Ваш сервис будет доступен по адресу:
```
https://tgads-parser.onrender.com
```

Swagger UI:
```
https://tgads-parser.onrender.com/docs
```

### 3. Тест endpoint'а

```bash
curl https://tgads-parser.onrender.com/list_files
```

---

## ⚠️ Известные проблемы на Render

### 1. Selenium падает с "Out of Memory"

**Причина:** Недостаточно RAM

**Решение:**
- Используйте план **Standard** (2GB RAM)
- Или уменьшите количество одновременных парсингов

### 2. Chrome не запускается

**Решение:** Убедитесь, что в Dockerfile есть:
```dockerfile
--headless
--no-sandbox
--disable-dev-shm-usage
```

### 3. Cookies не сохраняются между перезапусками

**Причина:** Render не имеет persistent storage на бесплатном плане

**Решение:**
- Используйте внешнее хранилище (AWS S3, Cloudinary)
- Или используйте Render Disks ($1/GB в месяц)

### 4. Долгое время запуска (Cold Start)

**Причина:** Render "засыпает" после 15 минут неактивности

**Решение:**
- Используйте платный план (не засыпает)
- Или настройте keep-alive ping каждые 10 минут

---

## 💡 Оптимизация для Render

### 1. Добавьте health check endpoint

В `routes.py`:
```python
@router.get('/health')
def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }
```

### 2. Настройте авто-рестарт

В `render.yaml`:
```yaml
services:
  - type: web
    name: tgads-parser
    env: docker
    plan: standard
    healthCheckPath: /health
    autoDeploy: true
```

### 3. Добавьте логирование

Render автоматически собирает логи из `stdout/stderr`.

Убедитесь, что все `print()` работают:
```python
import sys
print("Log message", file=sys.stdout, flush=True)
```

---

## 📊 Мониторинг

### Metrics в Render Dashboard:

- **CPU Usage** - должно быть < 80%
- **Memory Usage** - должно быть < 1.5GB
- **Response Time** - зависит от парсинга

### Alerts:

Настройте уведомления:
- Email при падении сервиса
- Slack интеграция

---

## 💰 Стоимость

### Минимальная конфигурация:
```
Plan: Standard
RAM: 2GB
CPU: 1 vCPU
Цена: $25/месяц
```

### С дополнительными фичами:
```
Standard Plan:        $25/мес
Render Disk (10GB):   $10/мес
Итого:               ~$35/мес
```

---

## 🔐 Безопасность

### 1. Переменные окружения

Храните чувствительные данные в Render Environment Variables:
```
SECRET_KEY=ваш-секретный-ключ
API_TOKEN=токен-api
```

### 2. Ограничьте доступ к API

Добавьте аутентификацию (у вас уже есть `auth.py`):
```python
from auth_deps import get_current_user

@router.post('/univers_parsing', dependencies=[Depends(get_current_user)])
def parse_channel(...):
    ...
```

### 3. Rate limiting

Добавьте ограничение запросов:
```bash
pip install slowapi
```

В `main.py`:
```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.get("/")
@limiter.limit("5/minute")
def read_root(request: Request):
    return {"Hello": "World"}
```

---

## 🚀 Альтернативы Render

Если Selenium не работает стабильно на Render:

### 1. Railway.app
- Похож на Render
- $5/мес starter
- Лучше поддержка Docker

### 2. Fly.io
- Больше контроля
- Pay-as-you-go
- Хорошо для Docker

### 3. DigitalOcean App Platform
- $12/мес basic
- 1GB RAM
- Стабильнее для Selenium

### 4. VPS (рекомендуется для Selenium)
- DigitalOcean Droplet: $6/мес (1GB)
- Hetzner: €4/мес (2GB)
- Полный контроль

---

## 📝 Checklist перед деплоем

- [ ] Git репозиторий создан
- [ ] `render.yaml` настроен
- [ ] `Dockerfile` оптимизирован
- [ ] Requirements.txt актуален
- [ ] `.gitignore` настроен
- [ ] Health check endpoint добавлен
- [ ] Выбран plan Standard или выше
- [ ] Environment variables настроены
- [ ] Протестировано локально с Docker

---

## 🆘 Помощь

### Если что-то не работает:

1. **Проверьте логи** в Render Dashboard
2. **Проверьте использование памяти** - Chrome жрет много!
3. **Попробуйте Standard plan** - Starter может не хватить
4. **Обратитесь в поддержку Render** - очень отзывчивые

### Полезные ссылки:

- [Render Docs](https://render.com/docs)
- [Docker на Render](https://render.com/docs/docker)
- [Selenium в Docker](https://www.selenium.dev/documentation/webdriver/browsers/chrome/#in-docker)

---

## ✅ Готово!

После деплоя ваше приложение будет доступно по адресу:
```
https://ваш-сервис.onrender.com/docs
```

**Важно:** Первый запуск может занять 5-10 минут (сборка Docker образа).

Удачи! 🚀

