from fastapi import FastAPI

app = FastAPI()

@app.get("/health")
def health():
    return {"status": "ok"}

# Placeholder endpoints invoked by Cloud Scheduler
@app.post("/run-sync")
def run_sync():
    return {"status": "scheduled sync"}

@app.post("/run-newsletter")
def run_newsletter():
    return {"status": "newsletter run (dry-run mode if configured)"}

@app.post("/run-birthday")
def run_birthday():
    return {"status": "birthday run"}

@app.post("/unsubscribe")
def unsubscribe():
    return {"status": "ok"}
