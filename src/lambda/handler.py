from mangum import Mangum

from app.main import app, init_state

init_state(app)  # module level = once per cold start, reused while the instance is warm
handler = Mangum(app, lifespan="off")
