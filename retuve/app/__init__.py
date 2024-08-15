"""
Contains all the code for the front-end and API of the Retuve App.

Can be called using

```bash
retuve --task trak --keyphrase_file config.py
```

Swagger Documentaition for the API is coming soon.
"""

from fastapi import FastAPI

from .routes.api import router as routes_app
from .routes.live import router as live_app
from .routes.models import router as models_app
from .routes.ui import router as web_app

app = FastAPI()

app.include_router(routes_app)
app.include_router(models_app)
app.include_router(web_app)
app.include_router(live_app)
