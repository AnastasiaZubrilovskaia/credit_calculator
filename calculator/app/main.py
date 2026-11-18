import logging
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exception_handlers import request_validation_exception_handler
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from calculator.app.api.routes import router
from calculator.app.core.config import settings
from calculator.app.core.logging_config import configure_logging
from calculator.app.services.loan_terms import PrescoringError

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


@app.exception_handler(PrescoringError)
async def prescoring_error_handler(request: Request, exc: PrescoringError) -> JSONResponse:
    logger.warning("%s %s rejected by prescoring: %s", request.method, request.url.path, exc.reasons)
    return JSONResponse(status_code=400, content={"detail": exc.reasons})


@app.exception_handler(RequestValidationError)
async def validation_error_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    errors = [{"loc": e["loc"], "type": e["type"]} for e in exc.errors()]
    logger.warning("%s %s validation failed: %s", request.method, request.url.path, errors)
    return await request_validation_exception_handler(request, exc)


