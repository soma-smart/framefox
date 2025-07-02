
# 🦊 Framefox: The Python Web Framework That Actually Makes Sense

*Meet the framework that finally solves the Python web development puzzle*

---

Picture this: You're starting a new Python web project. You stare at your screen, weighing your options. FastAPI? Blazing fast, but you'll spend weeks building basic structure. Django? Powerful, but feels like using a bulldozer to plant flowers. Flask? Great flexibility, terrible for your sanity when the project grows.

Sound familiar? 

We've all been there. That's exactly why we built **Framefox** – the Python web framework that doesn't make you choose between speed, structure, and sanity.

---

## The "Aha!" Moment

After years of wrestling with Python web frameworks, we had an epiphany: **What if we stopped compromising?**

What if we could have:
- FastAPI's lightning speed ⚡
- Django's rock-solid architecture 🏗️
- Laravel's delightful developer experience 😍
- Modern Python's elegance ✨

That "what if" became Framefox. And it's been a game-changer.

---

## Your First "Wow" Moment

Let me show you something that'll make you smile. Here's how you create a complete web application in Framefox:

```bash
# Install and create your project
pip install framefox
mkdir my-app && cd my-app
framefox init

# Generate a complete feature in seconds
framefox create entity User
framefox create crud User

# Launch your app
framefox run
```

**That's it.** You now have a fully functional web app with user management, authentication, beautiful templates, and a database – all running at `http://localhost:8000`.

No configuration hell. No architectural decisions to agonize over. Just working software.

*[Placeholder: Screenshot of a beautiful, working app dashboard]*

---

## The Magic is in the Details

### Code That Reads Like Poetry

```python
from framefox.core.routing.decorator.route import Route
from framefox.core.controller.abstract_controller import AbstractController

class BlogController(AbstractController):
    
    @Route("/posts", "blog.index", methods=["GET"])
    async def index(self, post_service: PostService):
        posts = await post_service.get_published_posts()
        return self.render("blog/index.html", {"posts": posts})
    
    @Route("/posts/{slug}", "blog.show", methods=["GET"])
    async def show(self, slug: str, post_service: PostService):
        post = await post_service.get_by_slug(slug)
        if not post:
            return self.not_found()
        return self.render("blog/post.html", {"post": post})
```

Look at that code. Clean, obvious, purposeful. **It does exactly what you think it does.**

Dependencies are injected automatically. URLs are generated safely. Templates render beautifully. Security is handled invisibly.

### Architecture That Grows With You

```
my-blog/
├── src/
│   ├── controllers/     # HTTP request handlers
│   ├── entity/         # Database models
│   ├── repository/     # Data access layer
│   ├── service/        # Business logic
│   └── form/           # Form validation
├── templates/          # Jinja2 views
├── public/            # Static assets
└── config/            # YAML configuration
```

This isn't arbitrary structure – it's **battle-tested architecture** that scales from weekend projects to enterprise applications.

---

## Security That Doesn't Sleep

Remember the last time you had to implement CSRF protection manually? Or configure password hashing? Or set up session management?

With Framefox, you don't.

```yaml
# config/security.yaml - This gives you enterprise-grade security
security:
  providers:
    users:
      entity: User
      property: email
  
  firewalls:
    main:
      authenticator: src.security.login_authenticator:LoginAuthenticator
      csrf_protection: true    # ✅ Automatic CSRF tokens
      session_lifetime: 3600   # ✅ Secure session management
      
  access_control:
    - { path: ^/admin, roles: ROLE_ADMIN }
    - { path: ^/profile, roles: ROLE_USER }
```

**Every form gets CSRF protection**. Every password gets bcrypt hashing. Every session gets proper rotation. Every input gets XSS prevention.

You don't configure security – you get it by default. **Following OWASP guidelines has never been this easy.**

*[Placeholder: Screenshot of login form with CSRF token visible in dev tools]*

---

## The Debugging Experience You Deserve

Ever spent hours debugging a web application, jumping between log files, database queries, and error traces?

Framefox's built-in profiler changes the game completely.

```bash
framefox run
# 🚀 Server running on http://localhost:8000
# 🔍 Profiler available at /_profiler
```

**Every request becomes a detailed case study.** Click any request, and you see:

- **Performance metrics** down to the millisecond
- **Every SQL query** with execution time
- **Memory usage** patterns
- **Complete stack traces** for errors
- **All log entries** in chronological order
- **User authentication** state and permissions

*[Placeholder: Screenshot of the profiler showing a request breakdown with SQL queries and timing]*

But here's the beautiful part: **a debug toolbar appears automatically** at the bottom of your HTML pages. One click takes you from "something's slow" to "here's exactly why."

*[Placeholder: Screenshot of web page with debug toolbar showing response time and query count]*

---

## Templates That Actually Work

Web development means writing HTML. Framefox makes it pleasant:

```html
{% extends "base.html" %}

{% block content %}
<div class="container">
    <h1>Latest Posts</h1>
    
    <!-- Flash messages appear automatically -->
    {% include_flash_messages %}
    
    <!-- Access control in templates -->
    {% if is_granted('ROLE_AUTHOR') %}
        <a href="{{ url_for('post.create') }}" class="btn btn-primary">
            Write New Post
        </a>
    {% endif %}
    
    <div class="posts">
        {% for post in posts %}
            <article class="post-card">
                <h2>{{ post.title }}</h2>
                <p>{{ post.excerpt|truncate(150) }}</p>
                <span class="meta">{{ post.published_at|date }}</span>
                <a href="{{ url_for('blog.show', slug=post.slug) }}">
                    Read More
                </a>
            </article>
        {% endfor %}
    </div>
</div>
{% endblock %}
```

**URLs generate safely.** Assets version automatically. Access control works naturally. Flash messages appear magically.

These aren't add-ons – they're core features that every web application needs.

---

## The CLI That Thinks Ahead

Most frameworks give you a basic CLI. Framefox gives you a **code generation powerhouse**:

```bash
$ framefox create entity
? Enter entity name: Article
? Add field 'title' (string): yes
? Add field 'content' (text): yes  
? Add field 'published_at' (datetime): yes
✅ Entity created with validation
✅ Repository generated
✅ Database migration ready

$ framefox create crud
? Choose entity: Article
? Include search functionality: yes
? Include file upload: yes
? Controller type: Web Interface
✅ ArticleController created with 7 routes
✅ Templates generated with Bootstrap
✅ Forms configured with validation
✅ Upload handling configured
```

The generated code isn't just functional – **it's production-ready**. Complete with validation, error handling, security measures, and beautiful styling.

*[Placeholder: Animated GIF showing the CLI generating a complete CRUD interface]*

---

## Performance That Impresses

Built on FastAPI's foundation, Framefox delivers **enterprise performance** without the enterprise complexity:

```python
class ArticleApiController(AbstractController):
    
    @Route("/api/articles", "api.articles.list", methods=["GET"])
    async def list_articles(self, article_service: ArticleService) -> list[Article]:
        # The profiler automatically tracks:
        # - Method execution time
        # - SQL queries and their performance  
        # - Memory allocation patterns
        # - Authentication overhead
        return await article_service.get_published_articles()
```

**Async everywhere.** Type-safe database queries. Intelligent caching. Automatic API documentation.

And when you need to optimize? The profiler shows you **exactly** where to focus your efforts.

---

## From Weekend Project to Production

### Lightning Start

```bash
# Saturday morning
framefox init
framefox create auth          # Complete authentication system
framefox create entity Post   # Blog post model
framefox create crud Post     # Full CRUD interface

# Saturday evening
framefox run                  # Beautiful app running locally
```

### Production Deploy

```bash
# Production ready
export APP_ENV=prod          # Profiler auto-disables
export DATABASE_URL=postgresql://...
gunicorn main:app --worker-class uvicorn.workers.UvicornWorker
```

**Same codebase.** Different configuration. Zero surprises.

---

## Real Talk: How It Compares

| What You Care About | **Framefox** | FastAPI | Django | Flask |
|---------------------|:------------:|:-------:|:------:|:-----:|
| **Get running fast** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐ |
| **Code stays clean** | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐ |
| **Security by default** | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ |
| **Debug easily** | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐ |
| **Learn gradually** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ | ⭐⭐ |
| **Runs fast** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ |

The honest truth? **You don't have to compromise anymore.**

---

## Stories from the Trenches

### "The Weekend Founder"

*"I had an idea for a SaaS app. With Framefox, I had a working prototype with user auth, billing, and admin panel by Sunday night. The profiler helped me optimize before I even had users."*

### "The Enterprise Team"

*"We migrated our Flask app to Framefox. The architecture forced us to clean up our code, the security features eliminated our vulnerabilities, and the profiler helped us improve performance by 40%."*

### "The Bootcamp Graduate"

*"Coming from tutorials that skip the 'boring' architecture stuff, Framefox taught me how professional web apps are actually built. The patterns it enforces made me a better developer."*

---

## The Philosophy Behind the Framework

We believe **good tools create good habits.**

When security is automatic, you build secure apps.  
When architecture is clear, you write maintainable code.  
When debugging is pleasant, you ship with confidence.  
When generating code is easy, you focus on business logic.

**Framefox doesn't just help you build web applications – it teaches you to build them right.**

---

## Ready for Your "Aha!" Moment?

```bash
pip install framefox
mkdir my-next-big-thing
cd my-next-big-thing
framefox init
framefox run
```

**Your application is waiting at `http://localhost:8000`**  
**Your debugging paradise is waiting at `/_profiler`**

### What happens next?

1. **This week**: Build something small. Feel the difference.
2. **This month**: Tackle a real project. Experience the architecture.
3. **This year**: Ship with confidence. Join the community.

---

## The Team Behind the Magic

Framefox is built by **SOMA Smart** 🇫🇷, a French company passionate about making developers' lives better.

**Meet the core team:**
- **[Rayen BOUMAZA](https://www.linkedin.com/in/rayen-boumaza)** - Framework Architect  
- **[Raphaël LEUROND](https://www.linkedin.com/in/raphael-leurond)** - Core Developer

*Psst... We speak French too! N'hésitez pas à nous contacter directement.*

---

## Join the Revolution

Framefox isn't just another framework – it's a **new way of thinking about Python web development**.

One that doesn't make you choose between speed and structure.  
One that doesn't make you choose between simplicity and power.  
One that doesn't make you choose between learning and shipping.

**The future of Python web development is here.**

And it's **swift, smart, and a bit foxy.** 🦊

---

### Ready to experience the difference?

**🚀 [Start building with Framefox](https://soma-smart.github.io/framefox/)**  
**📖 [Read the docs](https://soma-smart.github.io/framefox/quicklaunch/)**  
**⭐ [Star us on GitHub](https://github.com/soma-smart/framefox)**  
**💼 [Connect with the team](https://www.linkedin.com/company/soma-smart)**

*Your next great web application starts with a single command:*

```bash
pip install framefox
```

**What will you build?**