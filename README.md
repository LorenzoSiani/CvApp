# CVLTURE WordPress Management Interface

A modern, full-stack WordPress management application that provides a beautiful interface for managing WordPress content, WooCommerce products, and custom events.

![CVLTURE Logo](./assets/cvlture-logo.png)

## ✨ Features

- **WordPress Content Management**: View and manage WordPress posts and pages
- **WooCommerce Integration**: Full CRUD operations for products
- **Custom Events Management**: Handle custom event post types
- **Site Analytics**: Traffic statistics and insights (demo data with API integration ready)
- **Modern UI**: Glass-morphism design with green gradient theme
- **Responsive Design**: Works perfectly on desktop and mobile
- **Real-time Connection Status**: Live WordPress connection monitoring

## 🛠️ Tech Stack

- **Frontend**: React 19, Tailwind CSS, Shadcn/UI Components
- **Backend**: FastAPI (Python), Async/Await
- **Database**: MongoDB with Motor (async driver)
- **Authentication**: WordPress Application Passwords
- **API Integration**: WordPress REST API v2

## 📋 Prerequisites

### System Requirements
- **Node.js**: v18.0.0 or higher
- **Python**: v3.9 or higher
- **MongoDB**: v4.4 or higher (or MongoDB Atlas)
- **WordPress Site**: With REST API enabled

### WordPress Requirements
- WordPress 5.6+ (for Application Passwords support)
- REST API enabled (`/wp-json/wp/v2/` accessible)
- For WooCommerce: WooCommerce plugin installed
- For Events: Custom events post type with REST API support

## 🚀 Quick Start

### 1. Clone the Repository
```bash
git clone <your-repo-url>
cd wordpress-management-app
```

### 2. Backend Setup

#### Install Python Dependencies
```bash
cd backend
pip install -r requirements.txt
```

#### Environment Configuration
Create `backend/.env`:
```env
MONGO_URL=mongodb://localhost:27017
DB_NAME=wordpress_manager_db
CORS_ORIGINS=http://localhost:3000,https://your-domain.com
```

#### Start Backend Server
```bash
# Development
uvicorn server:app --reload --host 0.0.0.0 --port 8001

# Or using the existing supervisor setup
sudo supervisorctl start backend
```

### 3. Frontend Setup

#### Install Node Dependencies
```bash
cd frontend
yarn install
# or npm install
```

#### Environment Configuration
Create `frontend/.env`:
```env
REACT_APP_BACKEND_URL=http://localhost:8001
# For production: REACT_APP_BACKEND_URL=https://your-api-domain.com
```

#### Start Frontend Server
```bash
yarn start
# or npm start

# Or using supervisor
sudo supervisorctl start frontend
```

### 4. WordPress Configuration

#### Enable Application Passwords
1. Go to WordPress Admin → Users → Your Profile
2. Scroll to "Application Passwords" section
3. Create a new application password
4. Copy the generated password (you won't see it again!)

#### Enable Events REST API (if using custom events)
Add to your theme's `functions.php` or events plugin:
```php
// Enable REST API for events custom post type
add_action('init', function() {
    global $wp_post_types;
    if (isset($wp_post_types['events'])) {
        $wp_post_types['events']->show_in_rest = true;
        $wp_post_types['events']->rest_base = 'events';
    }
});
```

## 🔧 Configuration

### Environment Variables

#### Backend (`backend/.env`)
| Variable | Description | Example |
|----------|-------------|---------|
| `MONGO_URL` | MongoDB connection string | `mongodb://localhost:27017` |
| `DB_NAME` | Database name | `wordpress_manager_db` |
| `CORS_ORIGINS` | Allowed origins (comma-separated) | `http://localhost:3000,https://yourdomain.com` |

#### Frontend (`frontend/.env`)
| Variable | Description | Example |
|----------|-------------|---------|
| `REACT_APP_BACKEND_URL` | Backend API URL | `http://localhost:8001` |

### WordPress Connection Setup
1. Open the application in your browser
2. Enter your WordPress credentials:
   - **WordPress Username**: Your admin username
   - **Application Password**: Generated from WordPress admin
3. The app will automatically connect to `https://www.cvlture.it`

## 📁 Project Structure

```
wordpress-management-app/
├── backend/                 # FastAPI backend
│   ├── server.py           # Main application file
│   ├── requirements.txt    # Python dependencies
│   └── .env               # Environment variables
├── frontend/               # React frontend
│   ├── src/
│   │   ├── components/ui/  # Shadcn/UI components
│   │   ├── App.js         # Main React component
│   │   ├── App.css        # Global styles
│   │   └── index.js       # Entry point
│   ├── package.json       # Node dependencies
│   └── .env              # Environment variables
├── tests/                 # Test files
└── README.md             # This file
```

## 🔌 API Endpoints

### Authentication
- `POST /api/wp-config` - Configure WordPress connection
- `GET /api/wp-config` - Get current configuration
- `GET /api/test-connection` - Test WordPress connection

### Content Management
- `GET /api/posts` - Get WordPress posts
- `GET /api/products` - Get WooCommerce products
- `POST /api/products` - Create new product
- `PUT /api/products/{id}` - Update product
- `DELETE /api/products/{id}` - Delete product
- `GET /api/events` - Get custom events
- `POST /api/events` - Create new event

### Site Information
- `GET /api/site-info` - Get WordPress site information
- `GET /api/post-types` - Get available post types

## 🧪 Testing

### Backend Testing
```bash
cd backend
python -m pytest tests/
```

### Frontend Testing
```bash
cd frontend
yarn test
# or npm test
```

### Manual Testing
1. Test WordPress connection
2. Verify product CRUD operations
3. Check events management
4. Test responsive design on mobile

## 🚀 Deployment

### Using Docker (Recommended)
```bash
# Build and run with docker-compose
docker-compose up -d
```

### Manual Deployment
1. Set up production MongoDB instance
2. Configure production environment variables
3. Build frontend: `yarn build`
4. Deploy backend with a WSGI server (Gunicorn)
5. Set up reverse proxy (Nginx) for HTTPS

### Environment-Specific Configurations
- **Development**: Use local MongoDB and HTTP
- **Production**: Use MongoDB Atlas, HTTPS, and production domains

## 🔒 Security Considerations

- WordPress credentials are encrypted and stored securely
- All API calls use HTTPS in production
- Input validation on all endpoints
- CORS properly configured for your domains

## 🐛 Troubleshooting

### Common Issues

#### "WordPress connection failed"
- Verify WordPress REST API is accessible: `https://yoursite.com/wp-json/wp/v2/`
- Check Application Password is correct
- Ensure WordPress user has proper permissions

#### "Events not showing"
- Verify events custom post type has REST API enabled
- Check if `show_in_rest => true` is set for events
- Try accessing `/wp-json/wp/v2/events` directly

#### "Frontend can't connect to backend"
- Check `REACT_APP_BACKEND_URL` in frontend `.env`
- Verify backend is running on correct port
- Check CORS configuration in backend

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **CVLTURE** - Brand and design inspiration
- **WordPress REST API** - Content management backbone
- **Shadcn/UI** - Beautiful UI components
- **FastAPI** - High-performance backend framework
- **React** - Frontend framework
- **MongoDB** - Database solution

## 📞 Support

For support and questions:
- Create an issue in the repository
- Check the troubleshooting section above
- Review WordPress REST API documentation

---

Made with ❤️ for CVLTURE
