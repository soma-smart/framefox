from src.core.controller.abstract_controller import AbstractController
from src.repository.item_test_repository import ItemTestRepository
from src.entity.item_test import ItemTest
from src.core.exception.invalid_input_exception import InvalidInputException


class ItemTestsController(AbstractController):
    """
    Controller class for handling item-related operations.

    This class inherits from the AbstractController class and provides methods for getting all items,
    getting an item by ID, finding items based on criteria, adding an item, and deleting an item.

    Methods:
    - get_items: Get all items.
    - get_item_by_id: Get an item by ID.
    - find_items: Find items based on criteria.
    - add_item: Add an item.
    - delete_item: Delete an item.
    """

    def __init__(self):
        super().__init__()
        # Get all items
        self.add_route(
            path="/items",
            endpoint="get_items",
            view_func=self.get_items,
            methods=["GET"]
        )
        # Get an item by ID
        self.add_route(
            path="/items/<int:id>",
            endpoint="get_item_by_id",
            view_func=self.get_item_by_id,
            methods=["GET"]
        )
        # Find items by criteria
        self.add_route(
            path="/items/find",
            endpoint="find_items",
            view_func=self.find_items,
            methods=["POST"]
        )
        # Add an item
        self.add_route(
            path="/items",
            endpoint="add_item",
            view_func=self.add_item,
            methods=["POST"]
        )
        # Delete an item
        self.add_route(
            path="/items/<int:id>",
            endpoint="delete_item",
            view_func=self.delete_item,
            methods=["DELETE"]
        )

    def get_items(self):
        """
        Get all items.

        Returns:
        - A JSON response containing a list of items and a status code 200.
        """
        items = ItemTestRepository().find_all()
        return self.jsonify([item.to_dict() for item in items], 200)

    def get_item_by_id(self, id):
        """
        Get an item by ID.

        Args:
        - id: The ID of the item.

        Returns:
        - A JSON response containing the item data and a status code 200 if the item exists,
        - A JSON response with a status code 404 if the item does not exist.
        """
        item = ItemTestRepository().find(id)
        print(item)
        if item:
            return self.jsonify(item.to_dict(), 200)
        else:
            return self.jsonify({"message": "Item not found"}, 404)

    def find_items(self):
        """
        Retrieves items based on the provided criteria.

        Args:
            None

        Returns:
            A JSON response containing a list of items and a status code.

        Raises:
            None
        """
        data = self.request().get_json()
        criteria = data.get('criteria', {})
        order_by = data.get('order_by', None)
        limit = data.get('limit', None)
        offset = data.get('offset', None)

        items = ItemTestRepository().find_by(criteria, order_by, limit, offset)
        return self.jsonify([item.to_dict() for item in items], 200)

    def add_item(self):
        """
        Add an item.

        Returns:
        - A JSON response containing the added item data and a status code 201 if the item is added successfully,
          or an error message and a status code 400 if the input is invalid.
        """
        data = self.request().get_json()
        required_fields = ItemTest.required_fields()

        if not data or not all(field in data for field in required_fields):
            return InvalidInputException("Invalid input")

        item_data = {field: data[field]
                     for field in ItemTest.__table__.columns.keys() if field in data}
        item = ItemTest(**item_data)
        try:
            ItemTestRepository().add(item)
        except ValueError as e:
            InvalidInputException(str(e))
        finally:
            return self.jsonify(item.to_dict(), 201)

    def delete_item(self, id):
        """
        Delete an item.

        Args:
        - id: The ID of the item to be deleted.

        Returns:
        - A JSON response with a success message and a status code 200 if the item is deleted successfully,
          or None and a status code 200 if the item does not exist.
        """
        item = ItemTestRepository().find(id)
        if item is None:
            return self.jsonify(None, 200)
        ItemTestRepository().delete(item)
        return self.jsonify({"message": "Item deleted"}, 200)
