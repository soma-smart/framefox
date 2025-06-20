---
title: Authentication - User Accounts
description: Add login and signup to GameVault so everyone can have their own game collection!
---

# 🔐 Authentication

Time to add user accounts to GameVault! This way, everyone can have their own personal game collection, and we can keep games private to each user.

## Why do we need user accounts? 🤔

Right now, anyone who visits our site sees the same games. But what if:
- You want to track YOUR games, not someone else's
- Multiple people want to use GameVault 
- You want to keep your gaming habits private

That's where user accounts come in! Each person gets their own login and their own game collection.

<Steps>

1. **Create the User system** 👤

   Framefox has a special command that creates everything we need for [user authentication](/framefox/core/security). Let's use the [interactive terminal](/framefox/advanced_features/terminal):

   ```bash title="Create user authentication system"
   framefox create user
   ```

   This special command creates everything we need for user accounts:
   - A User entity with all the right fields
   - [Authentication setup](/framefox/core/security) and configuration
   - Login/signup controllers
   - Password security and hashing
   - Session management

   **That's it!** Framefox just set up a complete user system! 🎉

   :::tip[What just happened?]
   Framefox created:
   - `src/entity/user.py` - User entity with email, password, etc.
   - Authentication [controllers](/framefox/core/controllers) for login/signup
   - [Security configuration](/framefox/core/security) files
   - Password hashing (keeps passwords safe!)
   - [Session management](/framefox/installation#configuration) setup
   :::

2. **Update the database** 🛠️

   Now we need to add the users table to our database using [migrations](/framefox/core/database):

   ```bash title="Create user migration"
   framefox database create-migration
   ```

   Apply the changes:

   ```bash title="Apply database changes"
   framefox database upgrade
   ```

   Great! Now your database can store users AND games.

3. **Test the login system** 🧪

   Let's see our [authentication system](/framefox/core/security) in action! Framefox created login pages for us.

   Start your server if it's not running:

   ```bash title="Start development server"
   framefox run
   ```

   Now visit these URLs:
   - `http://localhost:8000/register` - Create a new account
   - `http://localhost:8000/login` - Login page

   Try creating an account and logging in. Pretty cool, right?

4. **Protect your game pages** 🛡️

   Right now, anyone can visit your game page without logging in. Let's add **access control** to make sure only logged-in users can manage games.

   In Framefox, you protect routes by adding them to the `config/security.yaml` file. Create or edit this file and add:

   ```yaml title="config/security.yaml"
   security:
     access_control:
       - { path: ^/game, roles: ROLE_USER }
   ```

   This single line tells Framefox: "Only users with ROLE_USER (logged-in users) can access any route starting with `/game`."

   That's it! Now visit `http://localhost:8000/game`:

   - **Not logged in?** → Redirected to login page automatically
   - **Logged in?** → See your personal game collection!

   :::tip[Your first access control rule!]
   The line `{ path: ^/game, roles: ROLE_USER }` is your first introduction to **access control** in Framefox. This simple configuration protects all your game-related pages without touching your controller code!

   The `^/game` pattern means "any route starting with /game" and `ROLE_USER` means "any logged-in user".
   :::

</Steps>

## Understanding what happened 🎯

### User Entity
Stores user information like email, username, and encrypted password using [SQLModel](/framefox/core/database).

### Authentication System
Handles login/logout, password checking, and keeping users logged in using Framefox's [security system](/framefox/core/security).

### Access Control with security.yaml
Your first taste of **access control**! The `security.yaml` file is where you define which pages require login. This clean separation keeps security configuration in one place, separate from your controller logic.

## What we accomplished 🏆

In just a few commands, we added:

1. ✅ **User registration** - People can create accounts
2. ✅ **Login/logout** - Secure access to accounts using [authentication](/framefox/core/security)
3. ✅ **Password security** - Passwords are encrypted automatically
4. ✅ **Page protection** - Login required to access certain pages using `access_control` rules

## Next steps 🚀

In the next chapter, we'll:
- Create a complete game management interface
- Build working [forms](/framefox/core/forms) to add/edit games
- Connect users to their personal game collections

But right now, you have a multi-user web application with secure authentication! That's professional-level stuff! 🎉

:::tip[Try it out!]
1. Create a few user accounts
2. Login as different users  
3. Try accessing protected pages both logged in and logged out
4. This is the foundation for a real web application!
:::

Ready to build the game management system? Let's move on to **[Game Management](/framefox/quicklaunch/game-management)**! 🎮✨
