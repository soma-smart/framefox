---
title: Tests
description: Implémentez des tests unitaires et fonctionnels pour votre application Framefox
---

import { Tabs, TabItem } from '@astrojs/starlight/components';
import CodeBlock from '../../../components/CodeBlock.astro';

# Tests dans Framefox

Framefox facilite l'écriture et l'exécution de tests pour assurer la qualité et la fiabilité de votre application. Le framework intègre des outils et des utilitaires spécifiques pour les tests unitaires, d'intégration et fonctionnels.

## Structure des tests

Les tests dans Framefox sont organisés dans le répertoire `src/tests` et suivent une structure similaire à celle de votre application :

```
src/tests/
├── unit/               # Tests unitaires
│   ├── controller/     # Tests des contrôleurs
│   ├── service/        # Tests des services
│   └── entity/         # Tests des entités
├── integration/        # Tests d'intégration
│   ├── repository/     # Tests des repositories
│   └── orm/            # Tests de l'ORM
└── functional/         # Tests fonctionnels
    └── api/            # Tests d'API
```

## Configuration des tests

Framefox utilise PyTest comme framework de test par défaut. La configuration se trouve dans le fichier `pytest.ini` à la racine du projet :

<CodeBlock
  code={`[pytest]
testpaths = src/tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
markers =
    unit: Unit tests
    integration: Integration tests
    functional: Functional tests
    slow: Tests that take a long time to run
    api: API tests
addopts = --cov=src --cov-report=html`}
  lang="ini"
  filename="pytest.ini"
/>

## Tests unitaires

Les tests unitaires vérifient le comportement de composants individuels de votre application.

### Test d'un service

<CodeBlock
  code={`# src/tests/unit/service/test_product_service.py
import pytest
from unittest.mock import AsyncMock, MagicMock

from src.service.product.product_service import ProductService
from src.entity.product import Product

class TestProductService:
    @pytest.fixture
    def entity_manager_mock(self):
        # Créer un mock pour l'EntityManager
        em = AsyncMock()
        
        # Configurer le repository
        repository_mock = AsyncMock()
        repository_mock.find_all.return_value = []
        repository_mock.find.return_value = None
        
        em.get_repository.return_value = repository_mock
        return em
    
    @pytest.fixture
    def event_dispatcher_mock(self):
        return AsyncMock()
    
    @pytest.fixture
    def product_service(self, entity_manager_mock, event_dispatcher_mock):
        return ProductService(entity_manager_mock, event_dispatcher_mock)
    
    @pytest.mark.asyncio
    async def test_create_product(self, product_service, entity_manager_mock):
        # Préparer les données de test
        product_data = {
            "name": "Test Product",
            "price": 19.99,
            "description": "A test product"
        }
        
        # Appeler la méthode à tester
        product = await product_service.create_product(product_data)
        
        # Vérifier le résultat
        assert product.name == "Test Product"
        assert product.price == 19.99
        assert product.description == "A test product"
        
        # Vérifier que les méthodes attendues ont été appelées
        entity_manager_mock.persist.assert_called_once()
        entity_manager_mock.flush.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_product_by_id(self, product_service, entity_manager_mock):
        # Préparer le mock
        product = Product()
        product.id = 1
        product.name = "Test Product"
        
        repository_mock = entity_manager_mock.get_repository.return_value
        repository_mock.find.return_value = product
        
        # Appeler la méthode à tester
        result = await product_service.get_product_by_id(1)
        
        # Vérifier le résultat
        assert result is product
        assert result.id == 1
        assert result.name == "Test Product"
        
        # Vérifier que find a été appelé avec le bon ID
        repository_mock.find.assert_called_once_with(1)`}
  lang="python"
  filename="src/tests/unit/service/test_product_service.py"
/>

### Test d'un contrôleur

<CodeBlock
  code={`# src/tests/unit/controller/test_product_controller.py
import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from src.controllers.product_controller import ProductController
from src.entity.product import Product

class TestProductController:
    @pytest.fixture
    def product_controller(self):
        controller = ProductController()
        
        # Simuler les services injectés
        controller.get_service = MagicMock()
        controller.get_service.return_value = AsyncMock()
        
        # Simuler le rendu de template
        controller.render = AsyncMock()
        
        # Simuler la redirection
        controller.redirect = AsyncMock()
        
        # Simuler le repository
        controller.repository = MagicMock()
        controller.repository.return_value = AsyncMock()
        
        return controller
    
    @pytest.mark.asyncio
    async def test_index(self, product_controller):
        # Préparer les données de test
        products = [
            Product(id=1, name="Product 1"),
            Product(id=2, name="Product 2")
        ]
        
        # Configurer le mock du repository
        product_controller.repository.return_value.find_all.return_value = products
        
        # Appeler la méthode à tester
        await product_controller.index()
        
        # Vérifier que render a été appelé avec les bons arguments
        product_controller.render.assert_called_once()
        args = product_controller.render.call_args[0]
        
        # Vérifier le template
        assert args[0] == "product/index.html"
        
        # Vérifier que les produits sont passés au template
        assert "products" in args[1]
        assert args[1]["products"] == products
    
    @pytest.mark.asyncio
    async def test_show(self, product_controller):
        # Préparer les données de test
        product = Product(id=1, name="Test Product")
        
        # Configurer le mock du repository
        product_controller.repository.return_value.find.return_value = product
        
        # Appeler la méthode à tester
        await product_controller.show(1)
        
        # Vérifier que le repository.find a été appelé avec le bon ID
        product_controller.repository.return_value.find.assert_called_once_with(1)
        
        # Vérifier que render a été appelé avec les bons arguments
        product_controller.render.assert_called_once()
        args = product_controller.render.call_args[0]
        
        # Vérifier le template
        assert args[0] == "product/show.html"
        
        # Vérifier que le produit est passé au template
        assert "product" in args[1]
        assert args[1]["product"] == product`}
  lang="python"
  filename="src/tests/unit/controller/test_product_controller.py"
/>

## Tests d'intégration

Les tests d'intégration vérifient que différents composants fonctionnent correctement ensemble.

### Test d'un repository

<CodeBlock
  code={`# src/tests/integration/repository/test_product_repository.py
import pytest
from framefox.core.orm.entity_manager import EntityManager
from framefox.test.database_test_case import DatabaseTestCase

from src.entity.product import Product
from src.entity.category import Category
from src.repository.product_repository import ProductRepository

class TestProductRepository(DatabaseTestCase):
    @pytest.fixture
    async def setup_database(self, entity_manager):
        # Créer des données de test
        category = Category()
        category.name = "Test Category"
        
        await entity_manager.persist(category)
        
        for i in range(5):
            product = Product()
            product.name = f"Product {i}"
            product.price = 10 + i
            product.category = category
            product.active = i % 2 == 0  # Produits pairs actifs
            
            await entity_manager.persist(product)
        
        await entity_manager.flush()
        
        # Retourner les données pour les tests
        return {"category": category}
    
    @pytest.mark.asyncio
    async def test_find_by_category(self, entity_manager, setup_database):
        # Récupérer la catégorie créée dans setup
        category = setup_database["category"]
        
        # Créer le repository à tester
        repository = ProductRepository(entity_manager)
        
        # Appeler la méthode à tester
        products = await repository.find_by_category(category.id)
        
        # Vérifier le résultat
        assert len(products) == 5
        assert all(p.category.id == category.id for p in products)
    
    @pytest.mark.asyncio
    async def test_find_active_products(self, entity_manager, setup_database):
        # Créer le repository à tester
        repository = ProductRepository(entity_manager)
        
        # Appeler la méthode à tester
        products = await repository.find_active_products()
        
        # Vérifier le résultat
        assert len(products) == 3  # Produits 0, 2, 4 sont actifs
        assert all(p.active for p in products)
    
    @pytest.mark.asyncio
    async def test_search_products(self, entity_manager, setup_database):
        # Créer le repository à tester
        repository = ProductRepository(entity_manager)
        
        # Appeler la méthode à tester
        products = await repository.search_products("Product 3")
        
        # Vérifier le résultat
        assert len(products) == 1
        assert products[0].name == "Product 3"`}
  lang="python"
  filename="src/tests/integration/repository/test_product_repository.py"
/>

## Tests fonctionnels

Les tests fonctionnels vérifient le comportement de l'application du point de vue de l'utilisateur.

### Test d'une API REST

<CodeBlock
  code={`# src/tests/functional/api/test_product_api.py
import pytest
from starlette.testclient import TestClient
import json

from framefox.test.api_test_case import ApiTestCase
from main import create_app

class TestProductApi(ApiTestCase):
    @pytest.fixture
    def client(self):
        app = create_app(test=True)
        return TestClient(app)
    
    @pytest.fixture
    async def setup_data(self, entity_manager):
        # Créer des données de test
        from src.entity.product import Product
        
        products = []
        for i in range(3):
            product = Product()
            product.name = f"Test Product {i}"
            product.price = 10.99 + i
            product.description = f"Description for product {i}"
            
            await entity_manager.persist(product)
            products.append(product)
        
        await entity_manager.flush()
        
        return products
    
    def test_get_products(self, client, setup_data):
        # Appeler l'API
        response = client.get("/api/products")
        
        # Vérifier la réponse
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) == 3
        
        # Vérifier que tous les produits sont présents
        product_names = [product["name"] for product in data]
        assert "Test Product 0" in product_names
        assert "Test Product 1" in product_names
        assert "Test Product 2" in product_names
    
    def test_get_product(self, client, setup_data):
        # Récupérer l'ID du premier produit
        product_id = setup_data[0].id
        
        # Appeler l'API
        response = client.get(f"/api/products/{product_id}")
        
        # Vérifier la réponse
        assert response.status_code == 200
        
        data = response.json()
        assert data["id"] == product_id
        assert data["name"] == "Test Product 0"
    
    def test_create_product(self, client):
        # Préparer les données
        product_data = {
            "name": "New Product",
            "price": 29.99,
            "description": "A new test product"
        }
        
        # Appeler l'API
        response = client.post(
            "/api/products",
            content=json.dumps(product_data),
            headers={"Content-Type": "application/json"}
        )
        
        # Vérifier la réponse
        assert response.status_code == 201
        
        data = response.json()
        assert data["name"] == "New Product"
        assert data["price"] == 29.99
        assert "id" in data  # Vérifier que l'ID a été généré
    
    def test_update_product(self, client, setup_data):
        # Récupérer l'ID du premier produit
        product_id = setup_data[0].id
        
        # Préparer les données de mise à jour
        update_data = {
            "name": "Updated Product",
            "price": 39.99
        }
        
        # Appeler l'API
        response = client.put(
            f"/api/products/{product_id}",
            content=json.dumps(update_data),
            headers={"Content-Type": "application/json"}
        )
        
        # Vérifier la réponse
        assert response.status_code == 200
        
        data = response.json()
        assert data["id"] == product_id
        assert data["name"] == "Updated Product"
        assert data["price"] == 39.99
        
        # Vérifier que la description n'a pas été modifiée
        assert data["description"] == "Description for product 0"
    
    def test_delete_product(self, client, setup_data):
        # Récupérer l'ID du premier produit
        product_id = setup_data[0].id
        
        # Appeler l'API
        response = client.delete(f"/api/products/{product_id}")
        
        # Vérifier la réponse
        assert response.status_code == 204
        
        # Vérifier que le produit a été supprimé
        response = client.get(f"/api/products/{product_id}")
        assert response.status_code == 404`}
  lang="python"
  filename="src/tests/functional/api/test_product_api.py"
/>

### Test d'un formulaire

<CodeBlock
  code={`# src/tests/functional/form/test_product_form.py
import pytest
from starlette.testclient import TestClient
from bs4 import BeautifulSoup

from framefox.test.web_test_case import WebTestCase
from main import create_app

class TestProductForm(WebTestCase):
    @pytest.fixture
    def client(self):
        app = create_app(test=True)
        return TestClient(app)
    
    @pytest.fixture
    async def setup_product(self, entity_manager):
        from src.entity.product import Product
        
        product = Product()
        product.name = "Test Product"
        product.price = 19.99
        product.description = "A test product"
        
        await entity_manager.persist(product)
        await entity_manager.flush()
        
        return product
    
    def test_new_product_form(self, client):
        # Charger le formulaire
        response = client.get("/products/new")
        
        assert response.status_code == 200
        
        # Analyser le HTML
        soup = BeautifulSoup(response.content, "html.parser")
        
        # Vérifier que le formulaire existe
        form = soup.find("form", {"action": "/products"})
        assert form is not None
        
        # Vérifier les champs du formulaire
        assert form.find("input", {"name": "name"}) is not None
        assert form.find("input", {"name": "price"}) is not None
        assert form.find("textarea", {"name": "description"}) is not None
    
    def test_submit_product_form(self, client):
        # Données du formulaire
        form_data = {
            "name": "New Test Product",
            "price": "29.99",
            "description": "A new test product from form"
        }
        
        # Obtenir le token CSRF
        response = client.get("/products/new")
        soup = BeautifulSoup(response.content, "html.parser")
        csrf_token = soup.find("input", {"name": "_csrf_token"})["value"]
        
        # Ajouter le token CSRF aux données
        form_data["_csrf_token"] = csrf_token
        
        # Soumettre le formulaire
        response = client.post("/products", data=form_data, allow_redirects=True)
        
        # Vérifier la redirection
        assert response.status_code == 200
        assert "/products/" in response.url
        
        # Vérifier que le produit apparaît dans la liste
        response = client.get("/products")
        assert "New Test Product" in response.text
    
    def test_edit_product_form(self, client, setup_product):
        product_id = setup_product.id
        
        # Charger le formulaire d'édition
        response = client.get(f"/products/{product_id}/edit")
        
        assert response.status_code == 200
        
        # Analyser le HTML
        soup = BeautifulSoup(response.content, "html.parser")
        
        # Vérifier que le formulaire est pré-rempli
        name_field = soup.find("input", {"name": "name"})
        assert name_field is not None
        assert name_field["value"] == "Test Product"
        
        price_field = soup.find("input", {"name": "price"})
        assert price_field is not None
        assert price_field["value"] == "19.99"
        
        description_field = soup.find("textarea", {"name": "description"})
        assert description_field is not None
        assert description_field.text.strip() == "A test product"`}
  lang="python"
  filename="src/tests/functional/form/test_product_form.py"
/>

## Tests avec base de données

Framefox fournit des classes de base pour simplifier les tests avec une base de données.

### Configuration de la base de données de test

<CodeBlock
  code={`# config/orm_test.yaml
orm:
  connection:
    driver: sqlite
    database: ":memory:"  # Base de données en mémoire pour les tests
  
  options:
    create_schema: true
    debug: false`}
  lang="yaml"
  filename="config/orm_test.yaml"
/>

### Fixture de base de données

<CodeBlock
  code={`# src/tests/conftest.py
import pytest
import os
from framefox.core.orm.entity_manager import EntityManager
from framefox.core.dependency_injection.container import Container

@pytest.fixture
async def entity_manager():
    """Fixture qui fournit un EntityManager configuré pour les tests"""
    # Charger la configuration de test
    os.environ["APP_ENV"] = "test"
    
    # Créer un conteneur
    container = Container()
    
    # Configurer et obtenir l'EntityManager
    entity_manager = EntityManager(config_file="config/orm_test.yaml")
    
    # Créer le schéma
    await entity_manager.create_schema()
    
    # Fournir l'EntityManager
    yield entity_manager
    
    # Nettoyer après les tests
    await entity_manager.close()`}
  lang="python"
  filename="src/tests/conftest.py"
/>

## Mocking et isolation

Framefox facilite l'isolation des composants grâce à l'injection de dépendances.

### Exemple de mocking d'un service externe

<CodeBlock
  code={`# src/tests/unit/service/test_payment_service.py
import pytest
from unittest.mock import patch, AsyncMock, MagicMock

from src.service.payment.payment_service import PaymentService

class TestPaymentService:
    @pytest.fixture
    def logger_mock(self):
        return MagicMock()
    
    @pytest.fixture
    def entity_manager_mock(self):
        return AsyncMock()
    
    @pytest.fixture
    def event_dispatcher_mock(self):
        return AsyncMock()
    
    @pytest.fixture
    def payment_service(self, logger_mock, entity_manager_mock, event_dispatcher_mock):
        # Créer le service avec des mocks
        service = PaymentService(
            api_key="test_key",
            logger=logger_mock,
            entity_manager=entity_manager_mock,
            event_dispatcher=event_dispatcher_mock
        )
        
        # Ne pas appeler initialize() qui utiliserait la vraie API
        return service
    
    @patch("stripe.PaymentIntent.create")
    @pytest.mark.asyncio
    async def test_create_payment(self, mock_create, payment_service, entity_manager_mock):
        # Configurer le mock de l'API Stripe
        mock_intent = MagicMock()
        mock_intent.id = "pi_123456"
        mock_intent.client_secret = "secret_123456"
        mock_create.return_value = mock_intent
        
        # Appeler la méthode à tester
        result = await payment_service.create_payment(
            amount=19.99,
            currency="eur",
            customer_email="test@example.com",
            description="Test payment"
        )
        
        # Vérifier l'appel à l'API Stripe
        mock_create.assert_called_once_with(
            amount=1999,  # 19.99 * 100
            currency="eur",
            receipt_email="test@example.com",
            description="Test payment"
        )
        
        # Vérifier que l'entité a été créée et persistée
        entity_manager_mock.persist.assert_called_once()
        entity_manager_mock.flush.assert_called_once()
        
        # Vérifier le résultat
        assert result["payment_id"] == "pi_123456"
        assert result["client_secret"] == "secret_123456"
        assert "transaction_id" in result`}
  lang="python"
  filename="src/tests/unit/service/test_payment_service.py"
/>

## Tests de sécurité

### Test d'authentification

<CodeBlock
  code={`# src/tests/functional/security/test_authentication.py
import pytest
from starlette.testclient import TestClient
from bs4 import BeautifulSoup

from framefox.test.web_test_case import WebTestCase
from main import create_app

class TestAuthentication(WebTestCase):
    @pytest.fixture
    def client(self):
        app = create_app(test=True)
        return TestClient(app)
    
    @pytest.fixture
    async def setup_user(self, entity_manager):
        from src.entity.user import User
        from framefox.core.security.password_encoder import PasswordEncoder
        
        # Créer un utilisateur de test
        user = User()
        user.email = "test@example.com"
        user.password = PasswordEncoder().encode("password123")
        user.roles = ["ROLE_USER"]
        
        await entity_manager.persist(user)
        await entity_manager.flush()
        
        return user
    
    def test_login_form(self, client):
        # Charger la page de connexion
        response = client.get("/login")
        
        assert response.status_code == 200
        assert "Connexion" in response.text
        
        # Vérifier le formulaire
        soup = BeautifulSoup(response.content, "html.parser")
        form = soup.find("form")
        
        assert form.get("action") == "/login_check"
        assert form.find("input", {"name": "_username"}) is not None
        assert form.find("input", {"name": "_password"}) is not None
    
    def test_login_success(self, client, setup_user):
        # Obtenir le token CSRF
        response = client.get("/login")
        soup = BeautifulSoup(response.content, "html.parser")
        csrf_token = soup.find("input", {"name": "_csrf_token"})["value"]
        
        # Données de connexion
        login_data = {
            "_username": "test@example.com",
            "_password": "password123",
            "_csrf_token": csrf_token
        }
        
        # Soumettre le formulaire de connexion
        response = client.post("/login_check", data=login_data, allow_redirects=True)
        
        # Vérifier la redirection vers la page d'accueil
        assert response.status_code == 200
        assert response.url.endswith("/")
        
        # Vérifier que l'utilisateur est connecté
        assert "Déconnexion" in response.text
        assert "test@example.com" in response.text
    
    def test_login_failure(self, client, setup_user):
        # Obtenir le token CSRF
        response = client.get("/login")
        soup = BeautifulSoup(response.content, "html.parser")
        csrf_token = soup.find("input", {"name": "_csrf_token"})["value"]
        
        # Données de connexion incorrectes
        login_data = {
            "_username": "test@example.com",
            "_password": "wrong_password",
            "_csrf_token": csrf_token
        }
        
        # Soumettre le formulaire de connexion
        response = client.post("/login_check", data=login_data, allow_redirects=True)
        
        # Vérifier que l'utilisateur est redirigé vers la page de connexion
        assert response.status_code == 200
        assert "/login" in response.url
        
        # Vérifier le message d'erreur
        assert "Identifiants invalides" in response.text
    
    def test_protected_page(self, client, setup_user):
        # Essayer d'accéder à une page protégée sans être connecté
        response = client.get("/profile", allow_redirects=True)
        
        # Vérifier la redirection vers la page de connexion
        assert response.status_code == 200
        assert "/login" in response.url
        
        # Se connecter
        self.login(client, "test@example.com", "password123")
        
        # Essayer d'accéder à la page protégée après connexion
        response = client.get("/profile")
        
        # Vérifier que l'accès est autorisé
        assert response.status_code == 200
        assert "Profil" in response.text
    
    def login(self, client, username, password):
        """Méthode utilitaire pour se connecter"""
        # Obtenir le token CSRF
        response = client.get("/login")
        soup = BeautifulSoup(response.content, "html.parser")
        csrf_token = soup.find("input", {"name": "_csrf_token"})["value"]
        
        # Données de connexion
        login_data = {
            "_username": username,
            "_password": password,
            "_csrf_token": csrf_token
        }
        
        # Soumettre le formulaire de connexion
        return client.post("/login_check", data=login_data, allow_redirects=True)`}
  lang="python"
  filename="src/tests/functional/security/test_authentication.py"
/>

## Exécution des tests

Framefox fournit plusieurs commandes pour exécuter les tests :

<CodeBlock
  code={`# Exécuter tous les tests
framefox test

# Exécuter seulement les tests unitaires
framefox test --unit

# Exécuter seulement les tests d'intégration
framefox test --integration

# Exécuter seulement les tests fonctionnels
framefox test --functional

# Exécuter les tests avec un rapport de couverture
framefox test --coverage

# Exécuter un fichier de test spécifique
framefox test src/tests/unit/service/test_product_service.py`}
  lang="bash"
/>

## Bonnes pratiques

1. **Isolez vos tests** : Utilisez des mocks et des fixtures pour isoler chaque test.
2. **Testez une seule chose à la fois** : Chaque test devrait se concentrer sur un aspect spécifique.
3. **Utilisez des noms descriptifs** : Les noms des tests devraient décrire ce qui est testé.
4. **Organisez vos tests** : Suivez la même structure que votre code source.
5. **Utilisez les markers** : Classifiez vos tests avec des markers pour les exécuter sélectivement.
6. **Testez les cas d'erreur** : N'oubliez pas de tester les cas où des erreurs peuvent se produire.
7. **Maintenez vos tests** : Mettez à jour les tests lorsque vous modifiez le code.

Les tests sont un élément essentiel du développement avec Framefox, et le framework fournit tous les outils nécessaires pour garantir la qualité et la fiabilité de votre application.
