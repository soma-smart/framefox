---
title: File Upload - Adding Game Covers
description: Learn how to add file upload functionality to your GameVault app for game cover images
---

import { Steps } from '@astrojs/starlight/components';

# 📁 File Upload - Adding Game Covers

Let's make GameVault even more visual by adding the ability to upload game cover images! Framefox makes file uploads easy and secure.

## What we'll add 🎯

- ✅ **Game cover uploads** - Add cover images to your games
- ✅ **File validation** - Ensure only images are uploaded
- ✅ **Secure storage** - Files stored safely in public directory
- ✅ **Display covers** - Show uploaded images in game lists

<Steps>

1. **Add cover field to Game entity** 🖼️

   First, let's add a cover field to store the filename of uploaded images.

   Edit `src/entity/game.py`:

   ```python title="src/entity/game.py (add cover field)"
   from typing import Optional
   from sqlmodel import Field
   from framefox.core.orm.abstract_entity import AbstractEntity

   class Game(AbstractEntity, table=True):
       # ...existing fields...
       cover: Optional[str] = Field(default=None, max_length=255)
   ```

   Create and apply a migration:

   ```bash title="Add cover field migration"
   framefox database create-migration
   framefox database upgrade
   ```

2. **Update the form to include file upload** 📤

   Now let's add file upload to our game form. Edit `src/form/game_type.py`:

   ```python title="src/form/game_type.py (add file upload)"
   from framefox.core.form.type.file_type import FileType

   class GameType(FormType):
       def build_form(self, form_builder):
           # ...existing fields...
           
           form_builder.add("cover", FileType, {
               "label": "Game Cover",
               "required": False,
               "accept": "image/*",
               "storage_path": "public/uploads/covers",
               "max_file_size": "5MB"
           })
   ```

3. **Display covers in your templates** 🖼️

   Update your game list template to show the cover images. Edit `templates/game/index.html`:

   ```html title="templates/game/index.html (add cover display)"
   <div class="game-item">
       {% if game.cover %}
           <img src="{{ url_for('static', path='uploads/covers/' + game.cover) }}" 
                alt="{{ game.title }} cover" 
                style="width: 100px; height: auto;">
       {% else %}
           <div class="no-cover">No cover</div>
       {% endif %}
       
       <h3>{{ game.title }}</h3>
       <p>Platform: {{ game.platform }}</p>
       <!-- ...rest of game info... -->
   </div>
   ```

4. **Test your file upload** ✅

   Start your server and test the upload:

   ```bash title="Test file upload"
   framefox run
   ```

   1. Go to `/games/create`
   2. Fill out the form and select a cover image
   3. Submit the form
   4. Check that the image appears in your game list!

</Steps>

## Understanding Framefox File Upload 📁

### FileType Features
- **Automatic validation** - File size, extension, and MIME type checks
- **Secure storage** - Files stored in designated public directories  
- **Rename protection** - Automatic file renaming to prevent conflicts
- **Easy integration** - Works seamlessly with forms and templates

### Storage Structure
When you upload files, they're stored like this:
```
public/
├── uploads/
│   └── covers/          # Game cover images
│       ├── game_001.jpg
│       ├── game_002.png
│       └── ...
```

### Template Helper Functions
Display uploaded files easily:
```html
<!-- Check if file exists -->
{% if game.cover %}
    <img src="{{ url_for('static', path='uploads/covers/' + game.cover) }}" alt="Cover">
{% endif %}

<!-- With fallback image -->
<img src="{{ game.cover ? url_for('static', path='uploads/covers/' + game.cover) : '/images/no-cover.png' }}" 
     alt="{{ game.title }} cover">
```

## What you accomplished! 🎉

Your GameVault now has:
- ✅ **File upload functionality** with validation and security
- ✅ **Visual game library** with cover images
- ✅ **Proper file storage** in organized directories
- ✅ **Template integration** for displaying images

:::tip[Pro Tips]
- The `FileType` automatically handles file validation and security
- Images are resized and renamed automatically to prevent conflicts
- You can add multiple file fields for different types of uploads
- File uploads work seamlessly with the CRUD system we built earlier
:::

Ready to learn about development tools and CLI commands? Let's move on to **[CLI Reference](/framefox/quicklaunch/cli-reference)**!
