---
title: Troubleshooting - When Things Go Wrong
description: Simple solutions to common problems you might face while building with Framefox
---

# 🔧 Troubleshooting

Don't panic! Every developer runs into problems. Here are the most common issues you might face while building GameVault (or any Framefox project) and how to fix them.

## 🚨 Server Won't Start

### Problem: `framefox run` shows errors

**Most common causes:**
- Virtual environment not activated
- Dependencies not installed
- Port already in use

**Solutions:**
```bash
# 1. Make sure your virtual environment is active
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows

# 2. Install/update dependencies (see [installation guide](/framefox/installation))
pip install -r requirements.txt

# 3. Try a different port
framefox run --port=8001

# 4. Clear cache and try again
framefox cache clear
framefox run
```

## 💾 Database Issues

### Problem: "Table doesn't exist" errors

**Solution:** You probably forgot to run [migrations](/framefox/core/database)!
```bash
framefox database create-migration
framefox database upgrade
```

### Problem: Migration fails

**Solution:** Check what changed, rollback if needed
```bash
# See migration status
framefox database status

# Rollback if needed
framefox database downgrade

# Fix your [entity](/framefox/core/database), then create new migration
framefox database create-migration
framefox database upgrade
```

### Problem: "Database locked" (SQLite)

**Solution:** Stop the server, then restart
```bash
# Stop framefox run (Ctrl+C)
# Then restart
framefox run
```

## 🔐 Authentication Problems

### Problem: Can't login/signup

**Check these:**
1. Did you run `framefox create user`?
2. Did you create and apply migrations after creating user?
3. Are you visiting the right URLs (`/login`, `/register`)?

**Solution:**
```bash
# Create [user system](/framefox/core/security) if you haven't
framefox create user

# Apply database changes
framefox database create-migration
framefox database upgrade

# Check routes exist
framefox debug router
```

### Problem: Login redirects to weird page

**Solution:** Check your routes and home [controller](/framefox/core/controllers)
```bash
framefox debug router
# Make sure you have a home route or /dashboard route
```

## 📄 Page Not Found (404)

### Problem: "Page not found" when visiting your pages

**Solutions:**
```bash
# 1. Check what routes actually exist
framefox debug router

# 2. Make sure [controller](/framefox/core/controllers) was created properly
ls src/controller/

# 3. Clear cache
framefox cache clear

# 4. Restart server
framefox run
```

### Problem: Templates not found

**Check:**
- [Template](/framefox/core/templates) files are in the right folder (`templates/controllername/`)
- File names match what the controller expects
- No typos in file names

## 📝 Form Issues

### Problem: Form doesn't save data

**Common causes:**
1. Form method is GET instead of POST
2. CSRF token missing
3. Validation errors not displayed

**Solutions:**
```html
<!-- Make sure form uses POST -->
<form method="POST">
    <!-- Add CSRF token (see [templates guide](/framefox/core/templates)) -->
    {{ csrf_token() }}
    
    <!-- Your form fields -->
</form>
```

### Problem: Validation errors not showing

**Check your [template](/framefox/core/templates) has:**
```html
{% if form.errors %}
    <div class="alert alert-danger">
        {% for field, errors in form.errors.items() %}
            {% for error in errors %}
                <p>{{ error }}</p>
            {% endfor %}
        {% endfor %}
    </div>
{% endif %}
```

## 🎨 Styling Problems

### Problem: Bootstrap styles not working

**Check:**
- Bootstrap CSS is properly linked in your template
- You're using correct Bootstrap class names
- No custom CSS overriding Bootstrap

### Problem: Changes not showing

**Try:**
- Hard refresh your browser (Ctrl+F5)
- Clear browser cache
- Check browser developer tools for errors

## 🔍 General Debugging Tips

### Use the browser developer tools
1. **Open developer tools** (F12)
2. **Check Console tab** for JavaScript errors
3. **Check Network tab** for failed requests
4. **Check Elements tab** to inspect HTML

### Read the terminal output
- Keep an eye on the terminal where `framefox run` is running
- Error messages usually tell you exactly what's wrong
- Don't ignore warnings!

### Check file paths and names
- Python is case-sensitive: `Game` ≠ `game`
- Check spelling in file names and imports
- Make sure files are in the right folders

## 🆘 When You're Really Stuck

### Step 1: Simplify
- Remove recent changes and test again
- Start with a minimal example
- Add complexity back gradually

### Step 2: Check the basics
```bash
# Is everything installed?
pip list

# Is the database working?
framefox database status

# Are routes registered?
framefox debug router

# Clear all cache
framefox cache clear
```

### Step 3: Start fresh
Sometimes it's easier to start over with a new project and copy working code:
```bash
framefox init test-project
cd test-project
# Copy your working files over
```

### Step 4: Ask for help
- Check Framefox documentation
- Search for the error message online
- Ask on Python/web development forums
- Check GitHub issues for Framefox

## 💡 Prevention Tips

### Save working versions
```bash
# Use git to save working versions
git add .
git commit -m "Working game list feature"
```

### Test small changes
- Don't change 10 things at once
- Test each small change before moving on
- If something breaks, you know what caused it

### Keep backups
- Backup your database file (for SQLite projects)
- Keep notes of what you changed
- Save working configurations

## 🎯 Common Error Messages

### "ModuleNotFoundError"
**Meaning:** Python can't find a file/module
**Fix:** Check file paths, imports, and virtual environment

### "NameError"
**Meaning:** Using a variable that doesn't exist
**Fix:** Check spelling, make sure variables are defined

### "AttributeError"
**Meaning:** Trying to use something that doesn't exist on an object
**Fix:** Check object has the property/method you're using

### "TemplateNotFound"
**Meaning:** Jinja2 can't find your template file
**Fix:** Check template file path and name

## Remember! 🌟

- **Every developer faces these problems**
- **Errors are learning opportunities**
- **Google is your friend**
- **Take breaks when frustrated**
- **Start simple, add complexity gradually**

You've got this! Debugging is a skill that improves with practice. Soon you'll be fixing problems like a pro! 🚀

:::tip[Pro debugging tip]
When you fix a problem, write down what caused it and how you fixed it. You'll likely face the same issue again someday!
:::
