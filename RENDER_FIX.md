# 🔧 Быстрое исправление ошибки Render

## ❌ Ошибка: `gunicorn: command not found`

Render пытался запустить приложение через gunicorn, но мы используем uvicorn.

## ✅ Что исправлено:

1. **Dockerfile** - обновлена команда CMD
2. **render.yaml** - убрана переменная PORT (Render сам её подставит)

---

## 🚀 Что делать сейчас:

### Вариант 1: Пересобрать через Git (рекомендуется)

```bash
# Закоммитить изменения
git add Dockerfile render.yaml
git commit -m "Fix: Use uvicorn instead of gunicorn"
git push

# Render автоматически пересоберет приложение
```

### Вариант 2: Ручной Manual Deploy

1. Зайдите в **Render Dashboard**
2. Выберите ваш сервис
3. Нажмите **"Manual Deploy"** → **"Deploy latest commit"**

---

## 📊 Ожидаемый результат:

После пересборки в логах должно быть:

```
==> Build successful 🎉
==> Deploying...
==> Starting service with 'sh -c uvicorn main:app --host 0.0.0.0 --port $PORT'
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
==> Your service is live 🎉
```

---

## ⚠️ Если всё еще не работает:

### Проверьте настройки в Render Dashboard:

1. **Settings** → **Environment**
   - Тип: `Docker`
   - Dockerfile Path: `./Dockerfile`

2. **Environment Variables**:
   - `PYTHONUNBUFFERED=1`
   - **НЕ** устанавливайте `PORT` вручную - Render сам подставит

3. **Start Command** - должно быть **пусто** (использует CMD из Dockerfile)

---

## 🎯 Альтернативное решение:

Если хотите использовать **Start Command** в Render вместо CMD в Dockerfile:

1. В Render Dashboard → **Settings**
2. **Start Command**: 
   ```bash
   uvicorn main:app --host 0.0.0.0 --port $PORT
   ```
3. **Save Changes**
4. **Manual Deploy**

---

## 📝 Checklist:

- [x] Dockerfile обновлен
- [x] render.yaml обновлен
- [ ] Изменения закоммичены в Git
- [ ] Push в GitHub сделан
- [ ] Render пересобирает приложение
- [ ] Проверьте логи на успешный запуск

---

## ✅ После исправления:

Ваше приложение будет доступно по адресу:
```
https://tgads-parser.onrender.com/docs
```

Проверьте:
```bash
curl https://tgads-parser.onrender.com/list_files
```

---

Готово! 🎉

