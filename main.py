import os
import importlib
import traceback
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from docs import setup_docs

app = FastAPI()

app.swagger_ui_parameters = {
    "favicon_url": "https://raw.githubusercontent.com/Bell575/dat4/main/uploads/e1ea60-1762003495228.jpg"
}

setup_docs(app)

ROUTERS_DIR = "routers"

router_files = sorted([f for f in os.listdir(ROUTERS_DIR) if f.endswith(".py") and not f.startswith("__")])

for filename in router_files:
    module_name = filename[:-3]
    try:
        module = importlib.import_module(f"{ROUTERS_DIR}.{module_name}")
        if hasattr(module, "router"):
            if module.router.tags:
                module.router.tags = sorted(module.router.tags)
            app.include_router(module.router)
            print(f"✅ Loaded router: {module_name}")
        else:
            print(f"⚠️ File {module_name}.py tidak punya 'router'")
    except Exception as e:
        print(f"❌ Gagal load router {module_name}: {e}")
        traceback.print_exc()

@app.get("/", include_in_schema=False)
def redirect_to_docs():
    return RedirectResponse("/docs")