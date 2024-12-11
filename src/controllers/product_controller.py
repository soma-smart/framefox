
from src.core.controller.abstract_controller import AbstractController


class ProductController(AbstractController):
    def __init__(self):
        super().__init__()
        self.add_route("/products", "get_products", self.get_products)

    def get_products(self):

        return self.jsonify({"products": ["Product 1", "Product 2"]})
