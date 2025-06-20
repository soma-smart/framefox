---
title: Database Design - Storing Your Games
description: Learn how to create your first database model to store games in GameVault. Simple and fun!
---

# 🗄️ Database Design

Now that we have our GameVault project running, let's add the ability to store games! Think of this as creating a digital filing cabinet for all your gaming data.

## What we're building 🎯

We want to store information about games like:
- **Title** - "The Legend of Zelda", "Cyberpunk 2077"
- **Platform** - PC, PlayStation, Xbox, Nintendo Switch
- **Status** - Playing, Completed, Wishlist
- **Rating** - How much you liked it (1-10)
- **Notes** - Your personal thoughts

<Steps>

1. **Create your first entity** 📝

   In Framefox, we use **[entities](/framefox/core/database)** to represent data. Think of an entity as a template that describes what information we want to store.

   Let's create our Game entity using the [interactive terminal](/framefox/advanced_features/terminal):

   ```bash title="Create entity"
   framefox create entity
   ```

   Framefox will ask you some questions. Here's what the real interaction looks like:

   ```bash title="Interactive entity creation"
   What is the name of the Entity ?(snake_case)

   Entity name: game
   Creating the entity 'game'

   Entity 'game' and repository created successfully.

   Do you want to add a new property to the entity ?(press enter to quit the terminal)

   Property name: title

   Property type [?] (str): str

   Maximum length (256): 

   Optional [?] (no): 

   Property 'title' added to src/entity/game.py

   Do you want to add a new property to the entity ?(press enter to quit the terminal)

   Property name: platform

   Property type [?] (str): str

   Maximum length (256): 

   Optional [?] (no): 

   Property 'platform' added to src/entity/game.py

   Do you want to add a new property to the entity ?(press enter to quit the terminal)

   Property name: status

   Property type [?] (str): str

   Maximum length (256): 

   Optional [?] (no): yes

   Property 'status' added to src/entity/game.py

   Do you want to add a new property to the entity ?(press enter to quit the terminal)

   Property name: rating

   Property type [?] (str): int

   Maximum length (256): 

   Optional [?] (no): yes

   Property 'rating' added to src/entity/game.py

   Do you want to add a new property to the entity ?(press enter to quit the terminal)

   Property name: notes

   Property type [?] (str): str

   Maximum length (256): 

   Optional [?] (no): yes

   Property 'notes' added to src/entity/game.py

   Do you want to add a new property to the entity ?(press enter to quit the terminal)

   Property name: [press enter to finish]
   ```

   **That's it!** Framefox just created your first [database entity](/framefox/core/database)! 🎉

   :::tip[What just happened?]
   Framefox created:
   - `src/entity/game.py` - The Game entity using [SQLModel](/framefox/core/database)
   - `src/repository/game_repository.py` - Helper methods for working with games

   Each property you add is immediately saved to the entity file. You can see the progress with messages like `Property 'title' added to src/entity/game.py`

   You don't need to understand all the code yet. The important thing is that you now have a way to store games!
   :::

2. **Create the database tables** 🛠️

   Now we need to tell the database about our new Game entity. Framefox uses [migrations](/framefox/core/database) for this:

   ```bash title="Create migration"
   framefox database create-migration
   ```

   You'll see something like:

   ```bash title="Migration output"
   ✓ Migration created: migrations/versions/20240603_152345_create_game_table.py
   ```

   Now apply the migration (create the actual table):

   ```bash title="Apply migration"
   framefox database upgrade
   ```

   You should see:

   ```bash title="Database upgrade output"
   ✓ Running migration 20240603_152345_create_game_table
   ✓ Database schema updated successfully
   ```

   🎉 **Awesome!** Your database now has a `games` table ready to store data!

   :::note[What's a migration?]
   A [migration](/framefox/core/database) is like a recipe that tells the database how to change its structure. When you add new entities or modify existing ones, Framefox creates migrations automatically. Pretty smart!
   :::


## What we accomplished 🏆

In just a few minutes, we:

1. ✅ **Created our first entity** - The Game model with interactive properties
2. ✅ **Generated database tables** - Using migrations automatically  
3. ✅ **Set up the database foundation** - Ready to store game data
4. ✅ **Learned the Framefox workflow** - Entity → Migration → Database

## Understanding what happened 🤔

### The Entity (Game Model)
This is like a blueprint that says "every game should have a title, platform, status, etc." Framefox created the `src/entity/game.py` file with all your properties.

### The Repository  
This is a helper that makes it easy to save, find, and manage games in the database. You got `src/repository/game_repository.py` for free!

### The Migration
This created the actual table in your database where games will be stored. Framefox handled this automatically.

:::tip[Want to peek under the hood?]
If you're curious, you can look at the generated files:
- `src/entity/game.py` - See how the Game model is defined
- The migration file in `migrations/versions/` - See the SQL commands
- But don't worry if it looks complex - you don't need to understand it all yet!
:::

## Next steps 🚀

In the next chapter, we'll:
- Add user accounts to GameVault
- Learn about authentication (login/signup)
- Make sure each user only sees their own games

But right now, you've got the database foundation for a real web app! That's pretty amazing for someone just starting out. 🎉

Ready to add user accounts? Let's move on to **[Authentication](/framefox/quicklaunch/authentication)**! 🔐✨
