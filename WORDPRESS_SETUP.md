# WordPress Setup Guide for CVLTURE Events

This guide explains how to configure your WordPress site to work with the enhanced events management interface.

## Required WordPress Configuration

### 1. Custom Post Type 'evento' (Already Done)

Your custom post type should be registered with:
```php
'show_in_rest' => true,
'rest_base'    => 'eventi',
'rest_controller_class' => 'WP_REST_Posts_Controller',
```

### 2. Register Meta Fields for REST API

Add this code to your theme's `functions.php` or your custom events plugin:

```php
// Register meta fields for evento custom post type
function register_evento_meta_fields() {
    // Event date
    register_post_meta('evento', 'data_evento', [
        'show_in_rest' => true,
        'single' => true,
        'type'   => 'string',
        'description' => 'Event date (YYYY-MM-DD format)'
    ]);

    // Event time
    register_post_meta('evento', 'ora_evento', [
        'show_in_rest' => true,
        'single' => true,
        'type'   => 'string',
        'description' => 'Event time (HH:MM format)'
    ]);

    // Event venue
    register_post_meta('evento', 'luogo_evento', [
        'show_in_rest' => true,
        'single' => true,
        'type'   => 'string',
        'description' => 'Event venue/location'
    ]);

    // Additional location info
    register_post_meta('evento', 'location', [
        'show_in_rest' => true,
        'single' => true,
        'type'   => 'string',
        'description' => 'Additional location information'
    ]);

    // DJ name
    register_post_meta('evento', 'dj', [
        'show_in_rest' => true,
        'single' => true,
        'type'   => 'string',
        'description' => 'DJ name'
    ]);

    // Host name
    register_post_meta('evento', 'host', [
        'show_in_rest' => true,
        'single' => true,
        'type'   => 'string',
        'description' => 'Host name'
    ]);

    // Guest information
    register_post_meta('evento', 'guest', [
        'show_in_rest' => true,
        'single' => true,
        'type'   => 'string',
        'description' => 'Guest information'
    ]);
}
add_action('init', 'register_evento_meta_fields');
```

### 3. Register Custom Taxonomy 'categorie_eventi'

Add this code to register the event categories taxonomy:

```php
// Register event categories taxonomy
function register_evento_taxonomy() {
    register_taxonomy('categorie_eventi', 'evento', [
        'labels' => [
            'name' => 'Categorie Eventi',
            'singular_name' => 'Categoria Evento',
            'menu_name' => 'Categorie Eventi',
            'all_items' => 'Tutte le Categorie',
            'add_new_item' => 'Aggiungi Nuova Categoria',
            'new_item_name' => 'Nome Nuova Categoria',
            'edit_item' => 'Modifica Categoria',
            'update_item' => 'Aggiorna Categoria',
            'view_item' => 'Visualizza Categoria',
            'search_items' => 'Cerca Categorie',
        ],
        'hierarchical' => true,
        'public' => true,
        'show_ui' => true,
        'show_admin_column' => true,
        'show_in_nav_menus' => true,
        'show_tagcloud' => true,
        'show_in_rest' => true,
        'rest_base' => 'categorie_eventi',
        'rest_controller_class' => 'WP_REST_Terms_Controller',
    ]);
}
add_action('init', 'register_evento_taxonomy');
```

### 4. Enable Featured Image Support

Ensure your custom post type supports featured images:

```php
// Add this to your evento post type registration
'supports' => [
    'title',
    'editor',
    'thumbnail', // This enables featured images
    'excerpt',
    'custom-fields'
],
```

### 5. Complete Setup Code

Here's the complete code you can add to your theme's `functions.php` file:

```php
<?php
/**
 * CVLTURE Events - WordPress REST API Setup
 * Add this code to your theme's functions.php file
 */

// Register meta fields for evento custom post type
function register_evento_meta_fields() {
    $meta_fields = [
        'data_evento' => 'Event date (YYYY-MM-DD format)',
        'ora_evento' => 'Event time (HH:MM format)',
        'luogo_evento' => 'Event venue/location',
        'location' => 'Additional location information',
        'dj' => 'DJ name',
        'host' => 'Host name',
        'guest' => 'Guest information'
    ];

    foreach ($meta_fields as $field => $description) {
        register_post_meta('evento', $field, [
            'show_in_rest' => true,
            'single' => true,
            'type' => 'string',
            'description' => $description,
            'auth_callback' => function() {
                return current_user_can('edit_posts');
            }
        ]);
    }
}
add_action('init', 'register_evento_meta_fields');

// Register event categories taxonomy
function register_evento_taxonomy() {
    register_taxonomy('categorie_eventi', 'evento', [
        'labels' => [
            'name' => 'Categorie Eventi',
            'singular_name' => 'Categoria Evento',
            'menu_name' => 'Categorie Eventi',
            'all_items' => 'Tutte le Categorie',
            'add_new_item' => 'Aggiungi Nuova Categoria',
            'new_item_name' => 'Nome Nuova Categoria',
            'edit_item' => 'Modifica Categoria',
            'update_item' => 'Aggiorna Categoria',
        ],
        'hierarchical' => true,
        'public' => true,
        'show_ui' => true,
        'show_admin_column' => true,
        'show_in_rest' => true,
        'rest_base' => 'categorie_eventi',
        'rest_controller_class' => 'WP_REST_Terms_Controller',
    ]);
}
add_action('init', 'register_evento_taxonomy');

// Ensure proper REST API permissions
function evento_rest_permissions($permission, $request, $object_id) {
    // Allow reading for everyone
    if ($request->get_method() === 'GET') {
        return true;
    }
    
    // Require authentication for write operations
    return current_user_can('edit_posts');
}
add_filter('rest_pre_insert_evento', 'evento_rest_permissions', 10, 3);
```

## Testing the Setup

After adding the code above, test your setup:

### 1. Check REST API Endpoints

Visit these URLs in your browser to verify the configuration:

- **Events**: `https://www.cvlture.it/wp-json/wp/v2/eventi`
- **Categories**: `https://www.cvlture.it/wp-json/wp/v2/categorie_eventi`
- **Media**: `https://www.cvlture.it/wp-json/wp/v2/media`

### 2. Verify Meta Fields

Create a test event and check if meta fields appear in the JSON response:

```bash
curl "https://www.cvlture.it/wp-json/wp/v2/eventi/EVENT_ID"
```

The response should include a `meta` object with your custom fields.

### 3. Test Categories

Create some event categories in WordPress admin and verify they appear at:
`https://www.cvlture.it/wp-json/wp/v2/categorie_eventi`

## WordPress Admin Configuration

### 1. Create Event Categories

1. Go to WordPress Admin → Eventi → Categorie Eventi
2. Create categories like:
   - Concerti
   - DJ Set
   - Live Performance
   - Workshop
   - Festival

### 2. Upload Media

1. Go to Media → Library
2. Upload images that can be used as featured images for events
3. Note the media IDs for testing

### 3. Test Event Creation

1. Create a test event in WordPress admin
2. Fill in the custom fields
3. Set categories and featured image
4. Check if it appears in the REST API

## Troubleshooting

### Meta Fields Not Showing
- Ensure `register_post_meta` is called on the `init` hook
- Check that `show_in_rest => true` is set
- Verify the post type is 'evento'

### Categories Not Working
- Make sure the taxonomy is registered with `show_in_rest => true`
- Check the `rest_base` matches 'categorie_eventi'
- Verify the taxonomy is associated with 'evento' post type

### Permission Errors
- Ensure your Application Password has proper permissions
- Check that the user can edit posts
- Verify CORS settings allow your domain

### Featured Images Not Showing
- Confirm the post type supports 'thumbnail'
- Check that featured images are set in WordPress admin
- Verify media permissions in REST API

## Expected API Response Format

After proper configuration, your eventi endpoint should return:

```json
{
  "id": 123,
  "title": {"rendered": "Event Title"},
  "content": {"rendered": "Event description"},
  "status": "publish",
  "featured_media": 456,
  "meta": {
    "data_evento": ["2024-12-31"],
    "ora_evento": ["20:00"],
    "luogo_evento": ["Milan Club"],
    "location": ["Via Roma 123"],
    "dj": ["DJ Nome"],
    "host": ["Host Nome"],
    "guest": ["Special guests info"]
  },
  "categorie_eventi": [12, 14],
  "_links": {...}
}
```

## Support

If you encounter issues:

1. Check WordPress error logs
2. Test REST API endpoints directly
3. Verify user permissions
4. Ensure all code is properly added to functions.php
5. Clear any caching plugins

The management interface will automatically detect and use these fields once properly configured in WordPress.