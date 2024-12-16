from src.core.controller.abstract_controller import AbstractController


class ProductController(AbstractController):
    def __init__(self):
        super().__init__()
        self.add_route("/products", "get_products",
                       self.get_products, methods=["GET"])

    async def get_products(self):

        return self.json({"products": ["Product 1", "Product 2"]})
