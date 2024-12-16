import uvicorn
from src.core.kernel import Kernel

app = Kernel().app

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
