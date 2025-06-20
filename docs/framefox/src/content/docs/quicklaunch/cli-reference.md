---
title: CLI Reference - Essential Commands
description: The most important Framefox commands you'll actually use while building GameVault
---

# 🛠️ CLI Reference

Here are the Framefox [terminal commands](/framefox/advanced_features/terminal) you'll actually use! No overwhelming lists - just the essentials that help you build cool stuff.

## The Big 5 Commands 🌟

These 5 commands will handle 90% of what you need:

### 1. Initialize a new project
```bash
mkdir myproject
cd myproject
framefox init
```
Creates a complete new Framefox project with the proper [project structure](/framefox/installation#project-structure).

### 2. Start your development server
```bash
framefox run
```
Runs your app at `http://localhost:8000` with auto-reload when you make changes.

### 3. Create database tables
```bash
framefox database create-migration
framefox database upgrade
```
Updates your database when you add/change [entities](/framefox/core/database).

### 4. Generate code automatically
```bash
framefox create controller
framefox create entity
framefox create crud
```
Creates [controllers](/framefox/core/controllers), [entities](/framefox/core/database), and complete CRUD systems.

### 5. Create user accounts
```bash
framefox create user
```
Sets up [authentication](/framefox/core/security), login, signup - the whole user system!

## Project Commands 🚀

### Starting fresh
```bash
# Create project directory
mkdir gamevault
cd gamevault

# Initialize Framefox project
framefox init

# Start the server
framefox run
```

## Code Generation 🏗️

### Create a simple page
```bash
framefox create controller
# Follow prompts to name your controller
# Creates [controller](/framefox/core/controllers) + [template](/framefox/core/templates)
# Visit: http://localhost:8000/controllername
```

### Create a data model
```bash
framefox create entity
# Follow the prompts to add fields
# Creates: [SQLModel entity](/framefox/core/database) and repository
```

### Create complete CRUD system
```bash
framefox create crud
# Choose your entity, then "Templated CRUD controller"
# Creates: [forms](/framefox/core/forms), pages, everything!
```

### Add user accounts
```bash
framefox create user
# Creates complete [authentication system](/framefox/core/security)
# Login/signup pages included!
```

## Database Commands 💾

### Create your database
```bash
framefox database create
```

### Update database structure
```bash
# After adding/changing [entities](/framefox/core/database)
framefox database create-migration
framefox database upgrade
```

### Check database status
```bash
framefox database status
```

## Debugging Commands 🐛

### See all your pages/routes
```bash
framefox debug router
```

### Clear cache if things get weird
```bash
framefox cache clear
```

## Common Workflows 📋

### Adding a new feature
```bash
# 1. Create the data model
framefox create entity

# 2. Update database
framefox database create-migration
framefox database upgrade

# 3. Create the web interface
framefox create crud

# 4. Test it!
framefox run
```

### Starting a new project
```bash
# 1. Create project
mkdir myproject
cd myproject
framefox init

# 2. Set up database
framefox database create

# 3. Add user accounts
framefox create user
framefox database create-migration
framefox database upgrade

# 4. Run it!
framefox run
```

## When Things Go Wrong 😅

### Server won't start?
```bash
framefox cache clear
framefox run
```

### Database errors?
```bash
framefox database status
# Check what went wrong
```

### Forgot what pages you have?
```bash
framefox debug router
# Lists all your URLs
```

### Want help with any command?
```bash
framefox --help
framefox create --help
framefox database --help
```

## Pro Tips 💡

### Speed up development
- Keep `framefox run` running in one terminal
- Use another terminal for commands
- The server auto-reloads when you change files!

### Save time with CRUD
- Instead of building [forms](/framefox/core/forms) manually, use `framefox create crud`
- It creates everything: forms, validation, pages, buttons
- You can customize the generated code afterward

### Database best practices
- Always run migrations after changing [entities](/framefox/core/database)
- Check `framefox database status` if something seems off
- Never edit migration files directly

### Getting unstuck
- Use `framefox debug router` to see all your pages
- Check the terminal where `framefox run` is running for error messages
- `framefox cache clear` fixes many weird issues

## That's really all you need! 🎉

These commands will take you from zero to a working web application using Framefox's [interactive terminal](/framefox/advanced_features/terminal). Don't get overwhelmed by complex documentation - just start building and learn as you go!

:::tip[Learning tip]
Pick one command, try it out, see what it does. Then try the next one. The best way to learn is by doing, not by reading endless documentation!
:::

Ready to build something awesome? Go back to the QuickLaunch guide and start creating! 🚀
```
Creates your database file (for SQLite) or connects to your database server.

### Create a migration
```bash
framefox database create-migration
```
After you change your models, this creates a "migration" file that updates your database structure.

### Apply migrations
```bash
framefox database upgrade
```
Actually applies the changes to your database. Run this after creating migrations.

### Check database status
```bash
framefox database status
```
Shows you what's currently in your database and if there are pending changes.

## Code Generation Commands ⚡

These are the magic commands that save you tons of time!

### Create a controller
```bash
framefox create controller name
```
Creates a controller (handles web requests) and its template file.

### Create an entity (model)
```bash
framefox create entity name
```
Creates a database model with interactive prompts for properties.

### Create complete CRUD
```bash
framefox create crud entity-name
```
Creates everything needed to add/edit/delete/view records: controller, forms, templates.

### Create user system
```bash
framefox create user
```
Sets up complete user authentication: registration, login, password security.

## Debug Commands 🔍

When things go wrong, these help you figure out what's happening:

### See all routes
```bash
framefox debug router
```
Shows all the URLs your app responds to and which controllers handle them.

### Clear cache
```bash
framefox cache clear
```
If weird things are happening, try this first. Clears all cached data.

## Quick Reference Card 📋

Print this out and keep it handy!

| What you want to do | Command |
|---------------------|---------|
| Start new project | `framefox init project-name` |
| Start development server | `framefox run` |
| Create database | `framefox database create` |
| Add new model | `framefox create entity name` |
| Add web pages for model | `framefox create crud name` |
| Add user accounts | `framefox create user` |
| Update database | `framefox database create-migration` then `framefox database upgrade` |
| See all URLs | `framefox debug router` |
| Fix weird issues | `framefox cache clear` |

## Common Workflows 🔄

### Starting a new project
```bash
framefox init my-app
cd my-app
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
framefox database create
framefox run
```

### Adding a new feature
```bash
# 1. Create the model
framefox create entity feature

# 2. Update database
framefox database create-migration
framefox database upgrade

# 3. Create web pages
framefox create crud feature

# 4. Test it!
framefox run
```

### When things break
```bash
# Try these in order:
framefox cache clear
framefox database status
framefox debug router
```

## Pro Tips 💡

### Use tab completion
Most terminals support tab completion. Type `framefox cr` and press Tab to see `framefox create`.

### Check what's generated
After running generation commands, look at the files created. You'll learn a lot!

### Don't memorize, bookmark
You don't need to remember every command. Keep this page bookmarked and refer to it.

### Start simple
Use the basic commands first. As you get comfortable, explore the advanced options.

## Need More Help? 🆘

- **Full documentation**: Check the main Framefox docs for detailed explanations
- **Interactive help**: Add `--help` to any command for specific options
- **Community**: Join the Framefox Discord or GitHub discussions

Remember: every developer looks up commands. Even experienced ones! Don't feel bad about referring to this page often. 😊

## What's Next? 🚀

These commands will get you through 90% of your Framefox development. As you build more complex apps, you'll naturally discover additional commands and options.

The most important thing? **Start building!** Use these commands to create your first project and see what happens. That's how you really learn.

Happy coding! 🎉
