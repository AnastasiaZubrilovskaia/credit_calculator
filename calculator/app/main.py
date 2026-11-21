import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from calculator.app.api.routes import router
from calculator.app.core.config import settings
from calculator.app.core.logging_config import configure_logging

configure_logging(settings.log_level)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Calculator service starting: base_rate=%s insurance_cost=%s log_level=%s",
                settings.base_rate, settings.insurance_cost, settings.log_level)
    yield
    logger.info("Calculator service stopping")


app = FastAPI(
    title="Calculator Microservice",
    description=(
        "Микросервис расчёта кредитных предложений.\n\n"
        "* **POST /calculator/offers** — прескоринг и 4 кредитных предложения;\n"
        "* **POST /calculator/calc** — полный расчёт кредита: платёж, ПСК, график."
    ),
    version="1.0.0",
    lifespan=lifespan,
)
app.include_router(router, prefix="/calculator", tags=["Calculator"])

