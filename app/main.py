from fastapi import FastAPI
from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

from app.api.agent import router as agent_router
from app.api.search import router as search_router
from app.api.auth import router as auth_router
from app.api.admin import router as admin_router

# Configure OpenTelemetry tracing.
resource = Resource.create(
    {
        "service.name": "enterprise-ai-operations-copilot",
        "service.version": "0.1.0",
    }
)

tracer_provider = TracerProvider(resource=resource)

tracer_provider.add_span_processor(
    BatchSpanProcessor(
        OTLPSpanExporter(
            endpoint="http://localhost:4318/v1/traces"
        )
    )
)

trace.set_tracer_provider(tracer_provider)


app = FastAPI(
    title="Enterprise AI Operations Copilot",
    description="Production-oriented GenAI reference application",
    version="0.1.0",
)

app.include_router(search_router)
app.include_router(agent_router)
app.include_router(auth_router)
app.include_router(admin_router)

FastAPIInstrumentor.instrument_app(app)


@app.get("/health")
def health():
    return {
        "status": "UP",
        "service": "enterprise-ai-operations-copilot",
    }


@app.get("/")
def root():
    return {
        "message": "Enterprise AI Operations Copilot",
        "version": "0.1.0",
    }