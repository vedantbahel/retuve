# Copyright 2024 Adam McArthur
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

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
