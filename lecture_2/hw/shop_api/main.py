from fastapi import FastAPI
from lecture_2.hw.shop_api.routers import cartRouter, itemRouter

app = FastAPI(title="Shop API")

app.include_router(cartRouter)
app.include_router(itemRouter)