import uvicorn
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from src.market.infrastructure.router import router_market
from src.account.infrastructure.router import router_account

app = FastAPI()

origins = [
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router_market)
app.include_router(router_account)


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=9999)
