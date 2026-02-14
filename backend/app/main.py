from fastapi import FastAPI, HTTPException
from .schemas import EventSchema
from .publisher import publish_event

app = FastAPI()


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/api/events", status_code=202)
def publish_event_api(event: EventSchema):
    try:
        publish_event(event.model_dump(mode="json"))
        return {"message": "Event published successfully"}
    except Exception as e:
        print("Publish error:", e)
        raise HTTPException(status_code=500, detail=str(e))
 
