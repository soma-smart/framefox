---
title: Best Practices - Write Better Code
description: Essential tips to write cleaner, maintainable code as your projects grow
---

# 📋 Best Practices

Great job building GameVault! 🎉 Now let's cover the essential practices that will make your code cleaner and your projects more maintainable.

## 🧹 Code Organization

### Use Clear Names
```python
# ✅ Good - Self-documenting
class Game(AbstractEntity):
    title: str = Field(max_length=200)
    platform: str = Field(max_length=50)
    
# ❌ Confusing - Unclear purpose
class G(AbstractEntity):
    t: str
    p: str
```

### Organize Files Logically
```
src/
├── entity/          # Data models
├── controller/      # Request handlers  
├── form/           # Form definitions
├── repository/     # Data access
└── service/        # Business logic
```

## 💾 Database Best Practices

### Always Create Migrations
```bash
# After changing any entity:
framefox database create-migration
framefox database upgrade
```

### Use Descriptive Field Names
```python
# ✅ Clear purpose
release_date: Optional[date] = Field(default=None)
completed_at: Optional[datetime] = Field(default=None)

# ❌ Ambiguous
date: Optional[date] = Field(default=None)
when: Optional[datetime] = Field(default=None)
```

## 🔒 Security Essentials

### Validate All Input
```python
# ✅ Always validate form data
if not title or len(title.strip()) == 0:
    form.add_error("title", "Title is required")

# ❌ Never trust user input directly
game.title = request.form.get("title")  # Dangerous!
```

### Use Framefox Authentication
Framefox handles password hashing, session management, and CSRF protection automatically when you use the built-in authentication system.

## 🎯 Development Workflow

### Test Your Changes
```bash
# Start server and test manually
framefox run

# Check for errors in browser console
# Test different user scenarios
# Verify database changes work correctly
```

### Use Version Control
```bash
# Track your changes
git add .
git commit -m "Add game rating feature"

# Create branches for new features
git checkout -b feature/game-covers
```

## 🚀 Performance Tips

### Keep Controllers Simple
```python
# ✅ Delegate business logic to services
@Route("/games", "game.create", methods=["POST"])
async def create(self, request: Request):
    form = self.create_form(GameType)
    await form.handle_request(request)
    
    if form.is_valid():
        game = await self.game_service.create_game(form.data)
        return self.redirect("game.index")
    
    return self.render("game/create.html", {"form": form})

# ❌ Don't put business logic in controllers
@Route("/games", "game.create", methods=["POST"])
async def create(self, request: Request):
    # 50 lines of business logic...
```

### Use Database Indexes for Searches
```python
# Add indexes for frequently searched fields
class Game(AbstractEntity):
    title: str = Field(index=True)  # Faster title searches
    platform: str = Field(index=True)  # Faster platform filtering
```

## 🎨 UI/UX Guidelines

### Consistent Styling
```html
<!-- Use consistent Bootstrap classes -->
<div class="card mb-3">
    <div class="card-body">
        <h5 class="card-title">{{ game.title }}</h5>
        <span class="badge bg-primary">{{ game.platform }}</span>
    </div>
</div>
```

### Provide User Feedback
```python
# Show success/error messages
if game_created:
    self.flash_success("Game added successfully!")
else:
    self.flash_error("Failed to add game. Please try again.")
```

## 🔧 Debug Like a Pro

### Use the Web Profiler
Visit `http://localhost:8000/_profiler` to analyze:
- Request performance
- Database queries  
- Template rendering
- Memory usage

### Check Logs Regularly
```bash
# View application logs
tail -f var/log/app.log

# Check for database issues
framefox debug database
```

## 📁 Project Structure Tips

### Environment-Specific Config
```yaml
# config/application.yaml
application:
  env: "${APP_ENV}"
  profiler:
    enabled: true  # Only in development
```

### Secure Your Secrets
```bash
# .env (never commit this file!)
SESSION_SECRET_KEY=your-secret-key
DATABASE_URL=sqlite:///app.db

# Use environment variables in production
```

## 🎯 When to Apply These Practices

**Starting Out:** Focus on clear naming and basic organization
**Growing Project:** Add proper validation and error handling  
**Production Ready:** Implement security, performance, and monitoring

## Key Takeaway 💡

Good practices aren't about perfect code from day one - they're about **sustainable development**. Start simple, then gradually improve as your project grows.

:::tip[Remember]
The best practice is the one you actually follow! Start with basics like clear naming and consistent file organization, then add more advanced practices as you gain experience.
:::

Ready to explore what's possible next? Check out **[What's Next?](/framefox/quicklaunch/whats-next)** for your learning journey! 🚀
</div>

<!-- ❌ Mixed styles look messy -->
<div style="margin: 5px; background: red;">
    <h3>{{ game.title }}</h3>
    <p class="badge bg-primary">{{ game.platform }}</p>
</div>
```

### Give users feedback
```python
# ✅ Tell users what happened in [controllers](/framefox/core/controllers)
self.add_flash("success", f"'{game.title}' added to your collection!")
self.add_flash("error", "Something went wrong. Please try again.")

# ❌ Silent failures are confusing
# (nothing happens, user doesn't know why)
```

## � Debugging Tips

### Use the debug commands
```bash
# See all your pages
framefox debug router

# Check database status
framefox database status

# Clear cache when weird things happen
framefox cache clear
```

### Read error messages carefully
When something breaks:
1. **Don't panic!** 😅
2. **Read the error message** - it usually tells you what's wrong
3. **Check the terminal** where `framefox run` is running
4. **Google the error** if you're stuck

### Test as you go
Don't build everything at once! Instead:
1. Add one small feature
2. Test it works
3. Add the next feature
4. Repeat

## 📚 Learning More

### Start small, grow gradually
- GameVault taught you the basics
- Now try adding ONE new feature at a time
- Maybe add game screenshots? Or user reviews?
- Each small project teaches you something new

### Read other people's code
- Look at open source Framefox projects on GitHub
- See how others solve similar problems
- Don't copy blindly - understand WHY they did it that way

### Don't try to memorize everything
- Keep this guide bookmarked
- Use the CLI reference when you forget commands
- Google is your friend!
- Every developer looks things up constantly

## 🚀 What's Next?

You've built a real web application! Here are some ideas for your next steps:

### Add more features to GameVault
- **User profiles** with avatars
- **Game screenshots** and file uploads
- **Game reviews** and ratings
- **Friends** and social features
- **Statistics** and charts

### Try a completely new project
- **Blog** with posts and comments using [entities](/framefox/core/database)
- **Todo app** with categories using [forms](/framefox/core/forms)
- **Recipe manager** with ingredients
- **Bookmarks** organizer

### Learn new skills
- **API development** for mobile apps
- **Real-time features** with WebSockets
- **Better design** with custom CSS
- **[Deployment](/framefox/advanced_features/deployment)** to share with friends

## Remember 💡

- **Every expert was once a beginner**
- **It's okay to not know everything**
- **Building projects is the best way to learn**
- **Have fun with it!** 

You've already accomplished something awesome by building GameVault. Keep experimenting with [controllers](/framefox/core/controllers), [forms](/framefox/core/forms), [entities](/framefox/core/database), and most importantly - enjoy the journey! 🎉

:::tip[The secret to getting better]
The best developers aren't the ones who know everything. They're the ones who keep building things, learning from mistakes, and helping others along the way.
:::

Keep coding with Framefox's [powerful tools](/framefox/advanced_features/terminal), and welcome to the wonderful world of web development! 🚀✨

## Controller Best Practices

### Dependency Injection

Use constructor injection for all dependencies:

```python
class GameController(AbstractController):
    def __init__(
        self,
        template_renderer: TemplateRenderer,
        entity_manager: EntityManagerInterface,
        file_upload_service: FileUploadService,
        game_repository: GameRepository
    ):
        super().__init__()
        self.template_renderer = template_renderer
        self.entity_manager = entity_manager
        self.file_upload_service = file_upload_service
        self.game_repository = game_repository
```

### Route Organization

Group related routes in single controller:

```python
class GameController(AbstractController):
    # List and display routes
    @Route("/games", "game.index", methods=["GET"])
    async def index(self, request: Request):
        """List all games."""
        pass
    
    @Route("/games/{id:int}", "game.show", methods=["GET"])  
    async def show(self, request: Request, id: int):
        """Show single game."""
        pass
    
    # Form routes
    @Route("/games/add", "game.add", methods=["GET", "POST"])
    async def add(self, request: Request):
        """Add new game."""
        pass
    
    @Route("/games/{id:int}/edit", "game.edit", methods=["GET", "POST"])
    async def edit(self, request: Request, id: int):
        """Edit existing game."""
        pass
    
    # Action routes
    @Route("/games/{id:int}/delete", "game.delete", methods=["POST"])
    async def delete(self, request: Request, id: int):
        """Delete game."""
        pass
```

### Error Handling

Implement consistent error handling:

```python
@Route("/games/{id:int}", "game.show", methods=["GET"])
async def show(self, request: Request, id: int):
    """Show game details."""
    try:
        game = self.game_repository.find(id)
        
        if not game:
            self.add_flash("error", "Game not found.")
            return self.redirect("/games")
        
        # Check ownership
        user = self.get_user()
        if game.owner_id != user.id:
            self.add_flash("error", "Access denied.")
            return self.redirect("/games")
        
        return self.template_renderer.render("game/show.html", {
            "title": game.title,
            "game": game
        })
        
    except Exception as e:
        self.logger.error(f"Error showing game {id}: {e}")
        self.add_flash("error", "An error occurred while loading the game.")
        return self.redirect("/games")
```

### Form Handling Pattern

Use consistent form handling pattern:

```python
@Route("/games/add", "game.add", methods=["GET", "POST"])
async def add(self, request: Request):
    """Add new game."""
    user = self.get_user()
    if not user:
        return self.redirect("/login")
    
    form = self.create_form(GameType)
    
    if request.method == "POST":
        form_data = await request.form()
        form.submit(form_data)
        
        if form.is_valid():
            try:
                # Create entity
                game = Game(
                    title=form.get_field_value("title"),
                    description=form.get_field_value("description"),
                    platform=form.get_field_value("platform"),
                    status=form.get_field_value("status"),
                    owner_id=user.id
                )
                
                # Handle file upload
                cover_file = form_data.get("cover_image")
                if cover_file and cover_file.filename:
                    filename = await self.file_upload_service.upload_cover(
                        cover_file, 
                        user.id
                    )
                    game.cover_image = filename
                
                # Save to database
                self.entity_manager.persist(game)
                self.entity_manager.flush()
                
                self.add_flash("success", f"'{game.title}' added to your collection!")
                return self.redirect("/games")
                
            except Exception as e:
                self.logger.error(f"Error adding game: {e}")
                self.add_flash("error", "Failed to add game. Please try again.")
    
    return self.template_renderer.render("game/add.html", {
        "title": "Add Game",
        "form": form
    })
```

## Form Design Patterns

### Form Type Structure

Organize form fields logically with proper validation:

```python
class GameType(AbstractFormType):
    def build_form(self, builder: FormBuilder, options: dict):
        # Required fields first
        builder.add("title", TextType, {
            "label": "Game Title",
            "required": True,
            "constraints": [
                LengthConstraint(min_length=1, max_length=200)
            ],
            "attr": {
                "class": "form-control",
                "placeholder": "Enter game title",
                "autofocus": True
            }
        })
        
        # Optional fields
        builder.add("description", TextareaType, {
            "label": "Description",
            "required": False,
            "attr": {
                "class": "form-control",
                "rows": 4,
                "placeholder": "Describe the game..."
            }
        })
        
        # Choice fields with enums
        builder.add("platform", ChoiceType, {
            "label": "Platform",
            "choices": [(p.value, p.get_display_name()) for p in GamePlatform],
            "required": True,
            "attr": {"class": "form-select"}
        })
        
        # File upload fields
        builder.add("cover_image", FileType, {
            "label": "Cover Image",
            "required": False,
            "attr": {
                "class": "form-control",
                "accept": "image/*"
            },
            "help": "Supported formats: JPG, PNG, GIF (max 5MB)"
        })
```

### Custom Validators

Create reusable custom validators:

```python
class UniqueUsernameValidator(Constraint):
    """Validator to ensure username is unique."""
    
    def __init__(self, user_repository: UserRepository, exclude_user_id: int = None):
        self.user_repository = user_repository
        self.exclude_user_id = exclude_user_id
        super().__init__()
    
    def validate(self, value: str) -> bool:
        existing_user = self.user_repository.find_by_username(value)
        
        if not existing_user:
            return True
        
        # Allow current user to keep their username
        if self.exclude_user_id and existing_user.id == self.exclude_user_id:
            return True
        
        return False
    
    def get_message(self) -> str:
        return "This username is already taken."
```

## Service Layer Patterns

### Service Design

Create focused services with single responsibility:

```python
class FileUploadService:
    """Service for handling file uploads."""
    
    def __init__(self, upload_dir: str, allowed_extensions: List[str], max_size: int):
        self.upload_dir = Path(upload_dir)
        self.allowed_extensions = allowed_extensions
        self.max_size = max_size
        self.upload_dir.mkdir(parents=True, exist_ok=True)
    
    async def upload_cover(self, file: UploadFile, user_id: int) -> str:
        """Upload game cover image."""
        # Validate file
        self._validate_file(file)
        
        # Generate unique filename
        filename = self._generate_filename(file.filename, user_id)
        
        # Save file
        file_path = self.upload_dir / "games" / "covers" / filename
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        content = await file.read()
        with open(file_path, "wb") as f:
            f.write(content)
        
        return filename
    
    def _validate_file(self, file: UploadFile) -> None:
        """Validate uploaded file."""
        if not file.filename:
            raise ValueError("No file selected")
        
        # Check file extension
        extension = file.filename.split(".")[-1].lower()
        if extension not in self.allowed_extensions:
            raise ValueError(f"File type not allowed. Allowed: {', '.join(self.allowed_extensions)}")
        
        # Check file size (implement size check)
        # ... size validation logic
    
    def _generate_filename(self, original_filename: str, user_id: int) -> str:
        """Generate unique filename."""
        extension = original_filename.split(".")[-1].lower()
        timestamp = int(time.time())
        random_string = secrets.token_hex(8)
        return f"{user_id}_{timestamp}_{random_string}.{extension}"
```

### Repository Patterns

Keep repositories focused on data access:

```python
class GameRepository(AbstractRepository):
    """Repository for Game entity."""
    
    def __init__(self):
        super().__init__(Game)
    
    def find_by_owner(self, owner_id: int, **kwargs) -> List[Game]:
        """Find games by owner with optional filters."""
        filters = {"owner_id": owner_id}
        
        # Add optional filters
        if "status" in kwargs:
            filters["status"] = kwargs["status"]
        if "platform" in kwargs:
            filters["platform"] = kwargs["platform"]
        
        return self.find_by(filters, order_by={"created_at": "DESC"})
    
    def search(self, owner_id: int, query: str) -> List[Game]:
        """Search games by title or description."""
        # Implementation depends on database capabilities
        # This is a simplified version
        all_games = self.find_by_owner(owner_id)
        query_lower = query.lower()
        
        return [
            game for game in all_games 
            if query_lower in game.title.lower() 
            or (game.description and query_lower in game.description.lower())
        ]
    
    def get_statistics(self, owner_id: int) -> Dict[str, Any]:
        """Get comprehensive statistics for user's collection."""
        games = self.find_by_owner(owner_id)
        
        return {
            "total_games": len(games),
            "by_status": self._count_by_status(games),
            "by_platform": self._count_by_platform(games),
            "total_playtime": sum(g.playtime_hours or 0 for g in games),
            "average_rating": self._calculate_average_rating(games),
            "completion_rate": self._calculate_completion_rate(games)
        }
    
    def _count_by_status(self, games: List[Game]) -> Dict[str, int]:
        """Count games by status."""
        counts = {}
        for game in games:
            status = game.status.value
            counts[status] = counts.get(status, 0) + 1
        return counts
```

## Template Best Practices

### Template Inheritance

Use template inheritance effectively:

```html
<!-- templates/base.html -->
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>{% block title %}GameVault{% endblock %}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    {% block stylesheets %}{% endblock %}
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
        <!-- Navigation content -->
    </nav>
    
    <main class="{% block main_class %}container my-4{% endblock %}">
        {% block body %}{% endblock %}
    </main>
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    {% block javascripts %}{% endblock %}
</body>
</html>

<!-- templates/game/base.html -->
{% extends "base.html" %}

{% block title %}{{ title }} - GameVault{% endblock %}

{% block body %}
<div class="row">
    <div class="col-md-3">
        {% block sidebar %}
        <div class="card">
            <div class="card-header">
                <h6>Game Management</h6>
            </div>
            <div class="card-body">
                <a href="{{ path('game.add') }}" class="btn btn-primary btn-sm">Add Game</a>
                <a href="{{ path('game.index') }}" class="btn btn-outline-primary btn-sm">My Games</a>
            </div>
        </div>
        {% endblock %}
    </div>
    <div class="col-md-9">
        {% block content %}{% endblock %}
    </div>
</div>
{% endblock %}

<!-- templates/game/show.html -->
{% extends "game/base.html" %}

{% block content %}
<div class="card">
    <div class="card-header">
        <h1>{{ game.title }}</h1>
    </div>
    <div class="card-body">
        <!-- Game details -->
    </div>
</div>
{% endblock %}
```

### Component Templates

Create reusable template components:

```html
<!-- templates/components/game_card.html -->
<div class="card game-card h-100">
    {% if game.cover_image %}
    <img src="{{ asset('uploads/games/covers/' ~ game.cover_image) }}" 
         class="card-img-top" 
         alt="{{ game.title }}"
         style="height: 200px; object-fit: cover;">
    {% else %}
    <div class="card-img-top bg-light d-flex align-items-center justify-content-center" 
         style="height: 200px;">
        <i class="fas fa-gamepad fa-3x text-muted"></i>
    </div>
    {% endif %}
    
    <div class="card-body d-flex flex-column">
        <h5 class="card-title">{{ game.title }}</h5>
        <p class="card-text">{{ game.platform.get_display_name() }}</p>
        
        <div class="mt-auto">
            <span class="badge {{ game.get_status_badge_class() }}">
                {{ game.get_status_display() }}
            </span>
            {% if game.rating %}
            <div class="mt-2">
                <small class="text-muted">{{ game.get_rating_stars() }}</small>
            </div>
            {% endif %}
        </div>
    </div>
    
    <div class="card-footer">
        <div class="btn-group w-100" role="group">
            <a href="{{ path('game.show', {'id': game.id}) }}" 
               class="btn btn-outline-primary btn-sm">
                <i class="fas fa-eye"></i> View
            </a>
            <a href="{{ path('game.edit', {'id': game.id}) }}" 
               class="btn btn-outline-secondary btn-sm">
                <i class="fas fa-edit"></i> Edit
            </a>
        </div>
    </div>
</div>

<!-- Usage in list template -->
<div class="row">
    {% for game in games %}
    <div class="col-md-6 col-lg-4 mb-4">
        {% include "components/game_card.html" %}
    </div>
    {% endfor %}
</div>
```

## Security Best Practices

### Input Validation

Always validate user input:

```python
# In forms
builder.add("title", TextType, {
    "constraints": [
        LengthConstraint(min_length=1, max_length=200),
        RegexConstraint(
            pattern=r"^[^<>\"'&]*$",
            message="Title contains invalid characters"
        )
    ]
})

# In controllers
@Route("/games/{id:int}", "game.show", methods=["GET"])
async def show(self, request: Request, id: int):
    # Validate ID parameter
    if id <= 0:
        self.add_flash("error", "Invalid game ID.")
        return self.redirect("/games")
    
    # Check ownership
    user = self.get_user()
    game = self.game_repository.find(id)
    
    if not game or game.owner_id != user.id:
        self.add_flash("error", "Game not found or access denied.")
        return self.redirect("/games")
```

### File Upload Security

Secure file upload handling:

```python
class FileUploadService:
    ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "gif", "webp"}
    MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
    
    def _validate_file(self, file: UploadFile) -> None:
        # Check file extension
        if not file.filename:
            raise ValueError("No file provided")
        
        extension = file.filename.split(".")[-1].lower()
        if extension not in self.ALLOWED_EXTENSIONS:
            raise ValueError(f"File type not allowed: {extension}")
        
        # Check file size
        file.file.seek(0, 2)  # Seek to end
        size = file.file.tell()
        file.file.seek(0)  # Reset to beginning
        
        if size > self.MAX_FILE_SIZE:
            raise ValueError(f"File too large: {size} bytes")
        
        # Validate file content (basic check)
        if not self._is_valid_image(file):
            raise ValueError("Invalid image file")
    
    def _is_valid_image(self, file: UploadFile) -> bool:
        """Basic image validation."""
        file.file.seek(0)
        header = file.file.read(16)
        file.file.seek(0)
        
        # Check for common image file signatures
        if header.startswith(b'\xff\xd8'):  # JPEG
            return True
        if header.startswith(b'\x89PNG'):   # PNG
            return True
        if header.startswith(b'GIF8'):      # GIF
            return True
        
        return False
```

### CSRF Protection

Use CSRF tokens in forms:

```html
<!-- In templates -->
<form method="POST" action="{{ path('game.add') }}">
    {{ csrf_token() }}
    
    <!-- Form fields -->
    <div class="mb-3">
        <label for="title" class="form-label">Title</label>
        <input type="text" class="form-control" id="title" name="title" required>
    </div>
    
    <button type="submit" class="btn btn-primary">Add Game</button>
</form>
```

## Performance Optimization

### Database Optimization

Use efficient queries and eager loading:

```python
# Avoid N+1 queries with relationships
def find_games_with_owners(self, limit: int = 20) -> List[Game]:
    """Load games with their owners in single query."""
    return self.query().join(User).limit(limit).all()

# Use pagination for large datasets
def find_paginated(self, page: int, per_page: int = 20) -> Dict[str, Any]:
    """Return paginated results."""
    offset = (page - 1) * per_page
    games = self.find_by({}, limit=per_page, offset=offset)
    total = self.count({})
    
    return {
        "games": games,
        "pagination": {
            "page": page,
            "per_page": per_page,
            "total": total,
            "pages": (total + per_page - 1) // per_page
        }
    }
```

### Caching Strategies

Implement smart caching:

```python
class GameStatsService:
    def __init__(self, cache_service: CacheService, game_repository: GameRepository):
        self.cache = cache_service
        self.game_repository = game_repository
    
    def get_user_stats(self, user_id: int) -> Dict[str, Any]:
        """Get user statistics with caching."""
        cache_key = f"user_stats:{user_id}"
        
        # Try cache first
        stats = self.cache.get(cache_key)
        if stats:
            return stats
        
        # Calculate stats
        stats = self.game_repository.get_statistics(user_id)
        
        # Cache for 1 hour
        self.cache.set(cache_key, stats, ttl=3600)
        
        return stats
    
    def invalidate_user_stats(self, user_id: int) -> None:
        """Invalidate user stats cache."""
        cache_key = f"user_stats:{user_id}"
        self.cache.delete(cache_key)
```

## Testing Patterns

### Unit Testing

Write focused unit tests:

```python
import pytest
from unittest.mock import Mock, patch
from src.entity.user import User
from src.entity.game import Game, GameStatus, GamePlatform
from src.repository.game_repository import GameRepository

class TestGameRepository:
    @pytest.fixture
    def mock_entity_manager(self):
        return Mock()
    
    @pytest.fixture
    def game_repository(self, mock_entity_manager):
        repo = GameRepository()
        repo.entity_manager = mock_entity_manager
        return repo
    
    def test_find_by_owner(self, game_repository):
        # Arrange
        user_id = 1
        expected_games = [
            Game(id=1, title="Game 1", owner_id=user_id),
            Game(id=2, title="Game 2", owner_id=user_id)
        ]
        game_repository.find_by = Mock(return_value=expected_games)
        
        # Act
        result = game_repository.find_by_owner(user_id)
        
        # Assert
        assert len(result) == 2
        assert result[0].title == "Game 1"
        game_repository.find_by.assert_called_once_with(
            {"owner_id": user_id}, 
            order_by={"created_at": "DESC"}
        )
```

### Integration Testing

Test full workflows:

```python
import pytest
from fastapi.testclient import TestClient
from src.main import app

class TestGameController:
    @pytest.fixture
    def client(self):
        return TestClient(app)
    
    @pytest.fixture
    def authenticated_user(self, client):
        # Create and authenticate test user
        response = client.post("/register", data={
            "username": "testuser",
            "email": "test@example.com",
            "password": "password123"
        })
        assert response.status_code == 302
        
        response = client.post("/login", data={
            "email": "test@example.com",
            "password": "password123"
        })
        assert response.status_code == 302
        
        return client
    
    def test_add_game_success(self, authenticated_user):
        response = authenticated_user.post("/games/add", data={
            "title": "Test Game",
            "platform": "pc",
            "status": "playing"
        })
        
        assert response.status_code == 302
        assert "/games" in response.headers["location"]
    
    def test_add_game_validation_error(self, authenticated_user):
        response = authenticated_user.post("/games/add", data={
            "title": "",  # Empty title should fail validation
            "platform": "pc"
        })
        
        assert response.status_code == 200
        assert "form-error" in response.text or "is-invalid" in response.text
```

This comprehensive best practices guide covers the essential patterns and conventions for building professional Framefox applications. Following these practices will help you create maintainable, secure, and scalable applications like GameVault! 🚀
