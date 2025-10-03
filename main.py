from fastapi import FastAPI
from routes import router
from auth import auth_router

from auth_deps import security

import uvicorn

app = FastAPI(title="Telegram Ads Parser API")
security.handle_errors(app)


app.include_router(auth_router)
app.include_router(router)


if __name__ == '__main__':
    uvicorn.run(app)
