  
  
  
  









  # Hide id in form 
  ```py
  
        builder.add('product', EntityType, {
            'class': 'Product',
            'multiple': True,
            'required': False,
            'choice_label': 'name',
            'label': 'Product',
            'show_id': False,
        })
```
# Upload File 
```py
        builder.add('image', FileType, {
            'required': False,
            'label': 'Image',
            'accept': 'image/*',
            'allowed_extensions': ['.jpg', '.jpeg', '.png', '.gif'],
            'storage_path': 'public/cni',

            'max_file_size': 2 * 1024 * 1024,  # 2MB
            'help': 'Formats acceptés: JPG, JPEG, PNG, GIF. Max: 2MB.'
        })
```

# Add attribut
```py
        builder.add('roles', TextareaType, {
            'required': False,
            'label': 'Roles',

            'attr': {'rows': 3},

        })
```