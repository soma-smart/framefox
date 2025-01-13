import uvicorn
import warnings
from framefox.core.kernel import Kernel

warnings.filterwarnings("ignore", category=RuntimeWarning, module="runpy")
app = Kernel().app

if __name__ == "__main__":

    uvicorn.run(app, host="0.0.0.0", port=8000)
