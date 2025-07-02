---
title: Project Setup - Your First Framefox App
description: Let's create GameVault step by step! Easy setup, no stress.
---

# 🏗️ Project Setup

Alright, let's create your first Framefox project! We're going to build GameVault from scratch, and I promise it's way easier than you might think.



<Steps>

1. **Create your project** ⚡

   First, let's create our GameVault project:

   ```bash title="Create and initialize project"
   # Create project directory
   mkdir gamevault
   cd gamevault
   ```

2. **Set up your environment** 🐍

   Let's create a virtual environment as recommended in the [installation guide](/framefox/installation#installation):

   ```bash title="Create virtual environment"
   # Create a virtual environment
   python -m venv venv

   # Activate it (on Linux/Mac)
   source venv/bin/activate

   # Or on Windows
   venv\Scripts\activate
   ```

   :::note[What's a virtual environment?]
   Think of it as a separate room for your project. All the Python packages you install stay in this room and don't mess with other projects. Smart!
   :::
3. **Install Framefox** 🚀


   Now, let's install Framefox. If you haven't already, follow the [installation guide](/framefox/installation):
   framefox init

   ```bash title="Install Framefox"
   # Install Framefox
   pip install framefox
   ```

   Or if you prefer the faster uv installer:

   ```bash title="Install with uv (faster)"
   uv add framefox
   ```
   And then, 
   ```bash
   framefox init
   ```

   That's it! Framefox just created a complete [project structure](/framefox/installation#project-structure) for you. Pretty cool, right?

   :::tip[What just happened?]
   Framefox created all the folders and files you need:
   - `src/` - Where your Python code lives ([controllers](/framefox/core/controllers), [entities](/framefox/core/database))
   - `templates/` - Your [HTML templates](/framefox/core/templates)
   - `config/` - [Configuration files](/framefox/installation#configuration)
   - `public/` - Static assets (CSS, JavaScript, images)
   - And much more!
   :::



4. **Configure the database** 🗄️

   Let's set up our database. Edit the `.env` file that Framefox created:

   ```bash title=".env"
   # App environment
   APP_ENV=dev
   SESSION_SECRET_KEY=your-very-secret-key-here

   # Database - We'll use SQLite for simplicity
   DATABASE_URL=sqlite:///gamevault.db

   # Mail (optional for now)
   # MAIL_URL=smtp://username:password@host:port?tls=true
   ```

   Now create the database:

   ```bash title="Create database"
   framefox database create
   ```

   You should see: `✓ Database created successfully`

   :::tip[Why SQLite?]
   SQLite is perfect for learning! It's a simple database that lives in a single file. No complex setup needed. You can always switch to PostgreSQL or MySQL later using the [ORM configuration](/framefox/installation#orm-configuration).
   :::

5. **Your first look at the app** 👀

   Let's see what we've got! Start the development server:

   ```bash title="Start development server"
   framefox run
   ```

   You should see something like:

   ```bash title="Server output"
   🦊 Starting Framefox development server...
   INFO: Uvicorn running on http://127.0.0.1:8000
   ```

   Now open your browser and go to `http://localhost:8000`. You should see the Framefox welcome page!

   🎉 **Congratulations!** You just created and ran your first Framefox app!

6. **Create your first controller** 📝

   Let's create a homepage for GameVault. Framefox makes this super easy with the [interactive terminal](/framefox/advanced_features/terminal):

   ```bash title="Create controller"
   framefox create controller
   ```

   When prompted:
   - **Controller name**: `home`

   **That's it!** Framefox just created:
   - A [controller](/framefox/core/controllers) file: `src/controller/home_controller.py`
   - A template file: `templates/home/index.html`

   Let's look at what Framefox generated for us:

   ```python title="src/controller/home_controller.py (generated)"
   from framefox.core.routing.decorator.route import Route
   from framefox.core.controller.abstract_controller import AbstractController

   class HomeController(AbstractController):
       @Route("/home", "home.index", methods=["GET"])
       async def index(self):
           return self.render("home/index.html", {"message": "Welcome to Home"})
   ```

   :::tip[What's a controller?]
   A [controller](/framefox/core/controllers) is like a waiter in a restaurant. When someone visits your website (places an order), the controller decides what to do and what page to show them (serves the food). It's part of Framefox's [MVC architecture](/framefox/introduction).
   :::

7. **Make it your homepage** 🏠

   Let's change the URL from `/home` to `/` to make it our main homepage. Edit `src/controller/home_controller.py`:

   ```python title="src/controller/home_controller.py (update the route)"
   from framefox.core.routing.decorator.route import Route
   from framefox.core.controller.abstract_controller import AbstractController

   class HomeController(AbstractController):
       @Route("/", "home.index", methods=["GET"])  # Changed from "/home" to "/"
       async def index(self):
           return self.render("home/index.html", {"message": "Welcome to GameVault!"})
   ```

   Now your GameVault homepage will be accessible at `http://localhost:8000/` (the root URL)!

8. **Make it look like GameVault** 🎮

   Let's customize that homepage to look like a gaming app! Open `templates/home/index.html` and replace it with:

   ```html title="templates/home/index.html"
   <!DOCTYPE html>
   <html>
   <head>
       <title>GameVault - Your Gaming Collection</title>
       <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
   </head>
   <body>
       <div class="container mt-5">
           <div class="text-center">
               <h1>🎮 Welcome to GameVault!</h1>
               <p class="lead">Your personal gaming collection manager</p>
               <div class="mt-4">
                   <a href="#" class="btn btn-primary btn-lg">Get Started</a>
               </div>
           </div>
       </div>
   </body>
   </html>
   ```

   Refresh your browser at `http://localhost:8000/` and... boom! 🎉 Your homepage now looks like a real gaming app!

</Steps>

## What we just accomplished 🎯

Let's take a moment to appreciate what we did:

1. ✅ **Installed Framefox** - Using pip or uv
2. ✅ **Created a project** - With proper [structure](/framefox/installation#project-structure)
3. ✅ **Set up the database** - SQLite, simple and effective
4. ✅ **Made our homepage** - [Controller](/framefox/core/controllers) + [template](/framefox/core/templates) at the root URL
5. ✅ **Customized the look** - Bootstrap for beautiful styling

And the best part? **We barely wrote any code!** Framefox's [interactive terminal](/framefox/advanced_features/terminal) did most of the heavy lifting for us.

:::tip[No complex setup needed!]
Unlike other frameworks, Framefox works out of the box. The database is already configured with SQLite - no MySQL setup, no complex configuration files to edit. Just code!
:::

## Next Steps 🚀

In the next chapter, we'll:
- Create our first [database entity](/framefox/core/database) (for storing games)
- Learn how Framefox handles data with the [ORM](/framefox/core/database)
- Add our first game to the collection

But for now, take a moment to celebrate! You've got a working web application. Not bad for a few minutes of work! 🎉

:::tip[Stuck somewhere?]
- Make sure Python 3.12+ is installed
- Check that you activated your virtual environment
- If the server won't start, try the [debugging commands](/framefox/quicklaunch/troubleshooting)
- Remember: every developer gets stuck sometimes. It's part of the learning process!
:::

Ready to add some games to your vault? Let's move on to **[Database Design](/framefox/quicklaunch/database-design)**! 🎮✨

