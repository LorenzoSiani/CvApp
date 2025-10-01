import React, { useState, useEffect } from 'react';
import './App.css';
import axios from 'axios';
import { BrowserRouter, Routes, Route, Link, useNavigate } from 'react-router-dom';
import { Button } from './components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './components/ui/card';
import { Input } from './components/ui/input';
import { Label } from './components/ui/label';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './components/ui/tabs';
import { Badge } from './components/ui/badge';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from './components/ui/dialog';
import { Textarea } from './components/ui/textarea';
import { AlertCircle, Settings, Package, Calendar, Plus, Edit, Trash2, ExternalLink, Wifi, WifiOff, BarChart3, TrendingUp, Users, Eye } from 'lucide-react';
import { toast, Toaster } from 'sonner';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Loading Screen Component
const LoadingScreen = ({ onComplete }) => {
  useEffect(() => {
    const timer = setTimeout(() => {
      onComplete();
    }, 3000); // Show for 3 seconds

    return () => clearTimeout(timer);
  }, [onComplete]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-green-500 to-slate-900 flex items-center justify-center">
      <div className="text-center">
        <img 
          src="https://customer-assets.emergentagent.com/job_wp-connect/artifacts/3oa5ol88_animated_logo_cv.gif" 
          alt="CVLTURE Logo" 
          className="w-48 h-48 mx-auto mb-8"
        />
        <div className="animate-pulse">
          <div className="w-64 h-2 bg-green-400/30 rounded-full mx-auto">
            <div className="h-2 bg-gradient-to-r from-green-400 to-emerald-400 rounded-full animate-pulse"></div>
          </div>
        </div>
      </div>
    </div>
  );
};

// Setup Page
const SetupPage = () => {
  const [config, setConfig] = useState({
    site_url: 'https://www.cvlture.it',
    username: '',
    app_password: ''
  });
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    
    try {
      await axios.post(`${API}/wp-config`, config);
      toast.success('WordPress connection configured successfully!');
      navigate('/dashboard');
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to configure WordPress connection');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-green-500 to-slate-900 flex items-center justify-center p-4">
      <Card className="w-full max-w-lg bg-white/10 backdrop-blur-md border-white/20 text-white">
        <CardHeader className="text-center">
          <CardTitle className="text-3xl font-bold bg-gradient-to-r from-blue-400 to-green-400 bg-clip-text text-transparent">
            WordPress Connect
          </CardTitle>
          <CardDescription className="text-gray-300">
            Configure your WordPress site connection to get started
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="text-center mb-6">
              <img 
                src="https://customer-assets.emergentagent.com/job_wp-connect/artifacts/vgk59obo_cropped-cropped-CVLTURE_Monogram_LOCAN_066-1.png" 
                alt="CVLTURE" 
                className="w-16 h-16 mx-auto mb-4 opacity-80"
              />
              <p className="text-green-400 text-sm">Connecting to CVLTURE WordPress Site</p>
            </div>
            <div className="space-y-2">
              <Label htmlFor="username" className="text-gray-200">WordPress Username</Label>
              <Input
                id="username"
                value={config.username}
                onChange={(e) => setConfig(prev => ({...prev, username: e.target.value}))}
                placeholder="Your WordPress username"
                required
                className="bg-white/10 border-white/20 text-white placeholder:text-gray-400"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="app_password" className="text-gray-200">Application Password</Label>
              <Input
                id="app_password"
                type="password"
                value={config.app_password}
                onChange={(e) => setConfig(prev => ({...prev, app_password: e.target.value}))}
                placeholder="Your WordPress application password"
                required
                className="bg-white/10 border-white/20 text-white placeholder:text-gray-400"
              />
            </div>
            <div className="bg-blue-500/10 border border-blue-400/20 rounded-lg p-4">
              <p className="text-sm text-blue-200">
                <AlertCircle className="w-4 h-4 inline mr-2" />
                Go to your WordPress admin → Users → Profile → Application Passwords to create a new application password.
              </p>
            </div>
            <Button 
              type="submit" 
              className="w-full bg-gradient-to-r from-blue-600 to-green-600 hover:from-blue-700 hover:to-green-700" 
              disabled={loading}
            >
              {loading ? 'Connecting...' : 'Connect to WordPress'}
            </Button>
          </form>
        </CardContent>
      </Card>
    </div>
  );
};

// Dashboard Page
const DashboardPage = () => {
  const [activeTab, setActiveTab] = useState('overview');
  const [connectionStatus, setConnectionStatus] = useState(null);
  const [siteInfo, setSiteInfo] = useState(null);
  const [posts, setPosts] = useState([]);
  const [products, setProducts] = useState([]);
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(false);
  
  // Modal states
  const [showProductModal, setShowProductModal] = useState(false);
  const [showEventModal, setShowEventModal] = useState(false);
  const [editingProduct, setEditingProduct] = useState(null);
  const [editingEvent, setEditingEvent] = useState(null);

  useEffect(() => {
    checkConnection();
    loadSiteInfo();
  }, []);

  useEffect(() => {
    if (activeTab === 'products') loadProducts();
    if (activeTab === 'events') loadEvents();
    if (activeTab === 'posts') loadPosts();
  }, [activeTab]);

  const checkConnection = async () => {
    try {
      const response = await axios.get(`${API}/test-connection`);
      setConnectionStatus('connected');
    } catch (error) {
      setConnectionStatus('disconnected');
    }
  };

  const loadSiteInfo = async () => {
    try {
      const response = await axios.get(`${API}/site-info`);
      setSiteInfo(response.data);
    } catch (error) {
      console.error('Failed to load site info:', error);
    }
  };

  const loadPosts = async () => {
    setLoading(true);
    try {
      const response = await axios.get(`${API}/posts?per_page=10`);
      setPosts(response.data);
    } catch (error) {
      toast.error('Failed to load posts');
    } finally {
      setLoading(false);
    }
  };

  const loadProducts = async () => {
    setLoading(true);
    try {
      const response = await axios.get(`${API}/products?per_page=10`);
      setProducts(response.data);
    } catch (error) {
      toast.error('Failed to load products');
    } finally {
      setLoading(false);
    }
  };

  const loadEvents = async () => {
    setLoading(true);
    try {
      const response = await axios.get(`${API}/events?per_page=10`);
      setEvents(response.data);
    } catch (error) {
      toast.error('Failed to load events');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateProduct = async (productData) => {
    try {
      await axios.post(`${API}/products`, productData);
      toast.success('Product created successfully!');
      setShowProductModal(false);
      loadProducts();
    } catch (error) {
      toast.error('Failed to create product');
    }
  };

  const handleCreateEvent = async (eventData) => {
    try {
      if (editingEvent) {
        await axios.put(`${API}/events/${editingEvent.id}`, eventData);
        toast.success('Event updated successfully!');
      } else {
        await axios.post(`${API}/events`, eventData);
        toast.success('Event created successfully!');
      }
      setShowEventModal(false);
      setEditingEvent(null);
      loadEvents();
    } catch (error) {
      toast.error(editingEvent ? 'Failed to update event' : 'Failed to create event');
    }
  };

  const handleDeleteEvent = async (eventId) => {
    if (!window.confirm('Are you sure you want to delete this event?')) return;
    
    try {
      await axios.delete(`${API}/events/${eventId}`);
      toast.success('Event deleted successfully!');
      loadEvents();
    } catch (error) {
      toast.error('Failed to delete event');
    }
  };

  const handleDeleteProduct = async (productId) => {
    if (!window.confirm('Are you sure you want to delete this product?')) return;
    
    try {
      await axios.delete(`${API}/products/${productId}`);
      toast.success('Product deleted successfully!');
      loadProducts();
    } catch (error) {
      toast.error('Failed to delete product');
    }
  };

  if (connectionStatus === 'disconnected') {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-green-500 to-slate-900 flex items-center justify-center p-4">
        <Card className="w-full max-w-md bg-white/10 backdrop-blur-md border-white/20 text-white text-center">
          <CardHeader>
            <WifiOff className="w-12 h-12 text-red-400 mx-auto mb-4" />
            <CardTitle className="text-xl text-red-400">Connection Lost</CardTitle>
            <CardDescription className="text-gray-300">
              WordPress connection not configured
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Link to="/setup">
              <Button className="bg-gradient-to-r from-blue-600 to-green-600 hover:from-blue-700 hover:to-green-700">
                Setup Connection
              </Button>
            </Link>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-green-500 to-slate-900">
      <div className="container mx-auto p-6">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-4xl font-bold text-white mb-2">WordPress Manager</h1>
            <div className="flex items-center gap-2">
              {connectionStatus === 'connected' ? (
                <><Wifi className="w-4 h-4 text-green-400" /><span className="text-green-400 text-sm">Connected</span></>
              ) : (
                <><WifiOff className="w-4 h-4 text-red-400" /><span className="text-red-400 text-sm">Disconnected</span></>
              )}
              {siteInfo && (
                <span className="text-gray-400 text-sm ml-4">→ {siteInfo.name}</span>
              )}
            </div>
          </div>
          <Link to="/setup">
            <Button variant="outline" className="border-white/20 text-white hover:bg-white/10">
              <Settings className="w-4 h-4 mr-2" />
              Settings
            </Button>
          </Link>
        </div>

        {/* Main Content */}
        <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
          <TabsList className="grid w-full grid-cols-5 bg-white/10 backdrop-blur-md">
            <TabsTrigger value="overview" className="text-white data-[state=active]:bg-white/20">Overview</TabsTrigger>
            <TabsTrigger value="products" className="text-white data-[state=active]:bg-white/20">Products</TabsTrigger>
            <TabsTrigger value="events" className="text-white data-[state=active]:bg-white/20">Events</TabsTrigger>
            <TabsTrigger value="posts" className="text-white data-[state=active]:bg-white/20">Posts</TabsTrigger>
            <TabsTrigger value="analytics" className="text-white data-[state=active]:bg-white/20">Analytics</TabsTrigger>
          </TabsList>

          <TabsContent value="overview" className="space-y-6 mt-6">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <Card className="bg-white/10 backdrop-blur-md border-white/20">
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium text-white">Total Products</CardTitle>
                  <Package className="h-4 w-4 text-blue-400" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold text-white">{products.length}</div>
                  <p className="text-xs text-blue-400">WooCommerce products</p>
                </CardContent>
              </Card>
              <Card className="bg-white/10 backdrop-blur-md border-white/20">
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium text-white">Total Eventi</CardTitle>
                  <Calendar className="h-4 w-4 text-green-400" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold text-white">{events.length}</div>
                  <p className="text-xs text-green-400">Custom events (eventi)</p>
                </CardContent>
              </Card>
              <Card className="bg-white/10 backdrop-blur-md border-white/20">
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium text-white">Total Posts</CardTitle>
                  <Edit className="h-4 w-4 text-purple-400" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold text-white">{posts.length}</div>
                  <p className="text-xs text-purple-400">Blog posts & articles</p>
                </CardContent>
              </Card>
            </div>

            {/* Quick Actions */}
            <Card className="bg-white/10 backdrop-blur-md border-white/20">
              <CardHeader>
                <CardTitle className="text-white">Quick Actions</CardTitle>
                <CardDescription className="text-gray-300">
                  Manage your CVLTURE WordPress site content
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <Button 
                    className="bg-blue-600 hover:bg-blue-700 h-12"
                    onClick={() => {
                      setActiveTab('products');
                      setShowProductModal(true);
                    }}
                  >
                    <Package className="w-4 h-4 mr-2" />
                    Add Product
                  </Button>
                  <Button 
                    className="bg-green-600 hover:bg-green-700 h-12"
                    onClick={() => {
                      setActiveTab('events');
                      setShowEventModal(true);
                    }}
                  >
                    <Calendar className="w-4 h-4 mr-2" />
                    Create Event
                  </Button>
                  <Button 
                    variant="outline"
                    className="border-white/20 text-white hover:bg-white/10 h-12"
                    onClick={() => window.open('https://www.cvlture.it/wp-admin', '_blank')}
                  >
                    <ExternalLink className="w-4 h-4 mr-2" />
                    WordPress Admin
                  </Button>
                </div>
              </CardContent>
            </Card>

            {/* Connection Status */}
            <Card className="bg-green-500/10 border border-green-400/20">
              <CardContent className="pt-6">
                <div className="flex items-start gap-3">
                  <Wifi className="w-5 h-5 text-green-400 mt-0.5" />
                  <div>
                    <p className="text-green-200 text-sm font-medium">CVLTURE WordPress Connected</p>
                    <p className="text-green-300 text-sm mt-1">
                      Successfully connected to https://www.cvlture.it with full REST API access.
                      Events endpoint: /wp-json/wp/v2/eventi
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="products" className="space-y-6 mt-6">
            <div className="flex items-center justify-between">
              <h2 className="text-2xl font-bold text-white">Products Management</h2>
              <Dialog open={showProductModal} onOpenChange={setShowProductModal}>
                <DialogTrigger asChild>
                  <Button className="bg-gradient-to-r from-blue-600 to-green-600 hover:from-blue-700 hover:to-green-700">
                    <Plus className="w-4 h-4 mr-2" />
                    Add Product
                  </Button>
                </DialogTrigger>
                <ProductModal 
                  onSubmit={handleCreateProduct} 
                  product={editingProduct}
                  onClose={() => {
                    setShowProductModal(false);
                    setEditingProduct(null);
                  }}
                />
              </Dialog>
            </div>
            
            {loading ? (
              <div className="text-center text-white">Loading products...</div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {products.map((product) => (
                  <ProductCard 
                    key={product.id} 
                    product={product} 
                    onEdit={(product) => {
                      setEditingProduct(product);
                      setShowProductModal(true);
                    }}
                    onDelete={handleDeleteProduct}
                  />
                ))}
              </div>
            )}
          </TabsContent>

          <TabsContent value="events" className="space-y-6 mt-6">
            <div className="flex items-center justify-between">
              <h2 className="text-2xl font-bold text-white">Events Management</h2>
              <Dialog open={showEventModal} onOpenChange={setShowEventModal}>
                <DialogTrigger asChild>
                  <Button className="bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-700 hover:to-emerald-700">
                    <Plus className="w-4 h-4 mr-2" />
                    Add Event
                  </Button>
                </DialogTrigger>
                <EventModal 
                  onSubmit={handleCreateEvent} 
                  event={editingEvent}
                  onClose={() => {
                    setShowEventModal(false);
                    setEditingEvent(null);
                  }}
                />
              </Dialog>
            </div>
            
            {loading ? (
              <div className="text-center text-white">Loading events...</div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {events.map((event) => (
                  <EventCard 
                    key={event.id} 
                    event={event}
                    onEdit={(event) => {
                      setEditingEvent(event);
                      setShowEventModal(true);
                    }}
                    onDelete={handleDeleteEvent}
                  />
                ))}
              </div>
            )}
          </TabsContent>

          <TabsContent value="posts" className="space-y-6 mt-6">
            <h2 className="text-2xl font-bold text-white mb-4">Recent Posts</h2>
            
            {loading ? (
              <div className="text-center text-white">Loading posts...</div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {posts.map((post) => (
                  <PostCard key={post.id} post={post} />
                ))}
              </div>
            )}
          </TabsContent>

          <TabsContent value="analytics" className="space-y-6 mt-6">
            <AnalyticsTab />
          </TabsContent>
        </Tabs>
      </div>
      <Toaster position="top-right" />
    </div>
  );
};

// Component for individual product cards
const ProductCard = ({ product, onEdit, onDelete }) => {
  return (
    <Card className="bg-white/10 backdrop-blur-md border-white/20 hover:bg-white/15 transition-all duration-300">
      <CardHeader>
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <CardTitle className="text-white text-lg line-clamp-2">{product.title}</CardTitle>
            <div className="flex gap-2 mt-2">
              <Badge variant="secondary" className="bg-blue-500/20 text-blue-300 border-blue-500/20">
                {product.status}
              </Badge>
            </div>
          </div>
          <div className="flex gap-2">
            <Button
              size="sm"
              variant="ghost"
              className="text-white hover:bg-white/10 p-2"
              onClick={() => onEdit(product)}
            >
              <Edit className="w-4 h-4" />
            </Button>
            <Button
              size="sm"
              variant="ghost"
              className="text-red-400 hover:bg-red-500/10 p-2"
              onClick={() => onDelete(product.id)}
            >
              <Trash2 className="w-4 h-4" />
            </Button>
            <Button
              size="sm"
              variant="ghost"
              className="text-white hover:bg-white/10 p-2"
              onClick={() => window.open(product.link, '_blank')}
            >
              <ExternalLink className="w-4 h-4" />
            </Button>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <div 
          className="text-gray-300 text-sm line-clamp-3" 
          dangerouslySetInnerHTML={{ __html: product.excerpt }} 
        />
      </CardContent>
    </Card>
  );
};

// Component for individual event cards
const EventCard = ({ event, onEdit, onDelete }) => {
  return (
    <Card className="bg-white/10 backdrop-blur-md border-white/20 hover:bg-white/15 transition-all duration-300">
      <CardHeader>
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <CardTitle className="text-white text-lg line-clamp-2">{event.title}</CardTitle>
            <div className="flex gap-2 mt-2">
              <Badge variant="secondary" className="bg-green-500/20 text-green-300 border-green-500/20">
                {event.type === 'evento' ? 'Evento' : 'Event'}
              </Badge>
              <Badge variant="outline" className="border-white/20 text-gray-300">
                {event.status}
              </Badge>
            </div>
          </div>
          <div className="flex gap-2">
            <Button
              size="sm"
              variant="ghost"
              className="text-white hover:bg-white/10 p-2"
              onClick={() => onEdit(event)}
            >
              <Edit className="w-4 h-4" />
            </Button>
            <Button
              size="sm"
              variant="ghost"
              className="text-red-400 hover:bg-red-500/10 p-2"
              onClick={() => onDelete(event.id)}
            >
              <Trash2 className="w-4 h-4" />
            </Button>
            <Button
              size="sm"
              variant="ghost"
              className="text-white hover:bg-white/10 p-2"
              onClick={() => window.open(event.link, '_blank')}
            >
              <ExternalLink className="w-4 h-4" />
            </Button>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <div 
          className="text-gray-300 text-sm line-clamp-3" 
          dangerouslySetInnerHTML={{ __html: event.excerpt }} 
        />
        <div className="text-xs text-gray-400 mt-2">
          Created: {new Date(event.date).toLocaleDateString()}
          {event.modified !== event.date && (
            <span className="ml-2">
              • Updated: {new Date(event.modified).toLocaleDateString()}
            </span>
          )}
        </div>
      </CardContent>
    </Card>
  );
};

// Component for individual post cards
const PostCard = ({ post }) => {
  return (
    <Card className="bg-white/10 backdrop-blur-md border-white/20 hover:bg-white/15 transition-all duration-300">
      <CardHeader>
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <CardTitle className="text-white text-lg line-clamp-2">{post.title}</CardTitle>
            <div className="flex gap-2 mt-2">
              <Badge variant="secondary" className="bg-green-500/20 text-green-300 border-green-500/20">
                {post.status}
              </Badge>
            </div>
          </div>
          <Button
            size="sm"
            variant="ghost"
            className="text-white hover:bg-white/10 p-2"
            onClick={() => window.open(post.link, '_blank')}
          >
            <ExternalLink className="w-4 h-4" />
          </Button>
        </div>
      </CardHeader>
      <CardContent>
        <div 
          className="text-gray-300 text-sm line-clamp-3" 
          dangerouslySetInnerHTML={{ __html: post.excerpt }} 
        />
        <div className="text-xs text-gray-400 mt-2">
          {new Date(post.date).toLocaleDateString()}
        </div>
      </CardContent>
    </Card>
  );
};

// Product Modal Component
const ProductModal = ({ onSubmit, product, onClose }) => {
  const [formData, setFormData] = useState({
    title: product?.title || '',
    content: product?.content || '',
    status: product?.status || 'draft',
    featured_image_url: ''
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit(formData);
    setFormData({ title: '', content: '', status: 'draft', featured_image_url: '' });
  };

  return (
    <DialogContent className="bg-slate-800 border-slate-700 text-white max-w-2xl">
      <DialogHeader>
        <DialogTitle>{product ? 'Edit Product' : 'Create New Product'}</DialogTitle>
        <DialogDescription className="text-gray-400">
          Add a new product to your WooCommerce store
        </DialogDescription>
      </DialogHeader>
      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="space-y-2">
          <Label htmlFor="title">Product Title</Label>
          <Input
            id="title"
            value={formData.title}
            onChange={(e) => setFormData(prev => ({...prev, title: e.target.value}))}
            placeholder="Enter product title"
            required
            className="bg-slate-700 border-slate-600 text-white"
          />
        </div>
        <div className="space-y-2">
          <Label htmlFor="content">Product Description</Label>
          <Textarea
            id="content"
            value={formData.content}
            onChange={(e) => setFormData(prev => ({...prev, content: e.target.value}))}
            placeholder="Enter product description"
            rows={4}
            className="bg-slate-700 border-slate-600 text-white"
          />
        </div>
        <div className="space-y-2">
          <Label htmlFor="status">Status</Label>
          <select
            id="status"
            value={formData.status}
            onChange={(e) => setFormData(prev => ({...prev, status: e.target.value}))}
            className="w-full p-2 bg-slate-700 border border-slate-600 rounded-md text-white"
          >
            <option value="draft">Draft</option>
            <option value="publish">Published</option>
            <option value="private">Private</option>
          </select>
        </div>
        <div className="flex gap-2 pt-4">
          <Button type="submit" className="bg-blue-600 hover:bg-blue-700">
            {product ? 'Update Product' : 'Create Product'}
          </Button>
          <Button type="button" variant="outline" onClick={onClose} className="border-slate-600 text-white hover:bg-slate-700">
            Cancel
          </Button>
        </div>
      </form>
    </DialogContent>
  );
};

// Analytics Tab Component
const AnalyticsTab = () => {
  const [analyticsData, setAnalyticsData] = useState({
    overview: null,
    topPages: [],
    trafficSources: [],
    status: null
  });
  const [loading, setLoading] = useState(true);
  const [showSetup, setShowSetup] = useState(false);
  const [ga4Config, setGa4Config] = useState({ ga4_property_id: '' });

  useEffect(() => {
    loadAnalyticsData();
    checkAnalyticsStatus();
  }, []);

  const loadAnalyticsData = async () => {
    setLoading(true);
    try {
      // Load all analytics data in parallel
      const [overview, topPages, trafficSources] = await Promise.all([
        axios.get(`${API}/analytics/overview`),
        axios.get(`${API}/analytics/top-pages`),
        axios.get(`${API}/analytics/traffic-sources`)
      ]);

      setAnalyticsData({
        overview: overview.data.data,
        topPages: topPages.data.data,
        trafficSources: trafficSources.data.data,
        status: 'loaded'
      });
    } catch (error) {
      console.error('Failed to load analytics data:', error);
      toast.error('Failed to load analytics data');
    } finally {
      setLoading(false);
    }
  };

  const checkAnalyticsStatus = async () => {
    try {
      const response = await axios.get(`${API}/analytics/health`);
      setAnalyticsData(prev => ({ ...prev, status: response.data }));
    } catch (error) {
      console.error('Failed to check analytics status:', error);
    }
  };

  const handleSetupGA4 = async (e) => {
    e.preventDefault();
    try {
      await axios.post(`${API}/analytics-config`, ga4Config);
      toast.success('Google Analytics 4 configured! Upload your service account JSON file to the backend.');
      setShowSetup(false);
      loadAnalyticsData();
    } catch (error) {
      toast.error('Failed to configure Google Analytics 4');
    }
  };

  const getStatusColor = (status) => {
    if (!status) return 'gray';
    if (status.status === 'connected') return 'green';
    if (status.status === 'demo_mode') return 'yellow';
    return 'red';
  };

  const getStatusText = (status) => {
    if (!status) return 'Loading...';
    if (status.status === 'connected') return 'Google Analytics 4 Connected';
    if (status.status === 'demo_mode') return 'Demo Mode (Connect GA4 for real data)';
    return 'Connection Error';
  };

  if (loading) {
    return (
      <div className="text-center text-white py-12">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-green-400 mx-auto mb-4"></div>
        <p>Loading analytics data...</p>
      </div>
    );
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold text-white">Site Analytics & Traffic Stats</h2>
        <div className="flex items-center gap-4">
          <div className={`flex items-center gap-2 px-3 py-1 rounded-full text-sm ${
            getStatusColor(analyticsData.status) === 'green' ? 'bg-green-500/20 text-green-300' :
            getStatusColor(analyticsData.status) === 'yellow' ? 'bg-yellow-500/20 text-yellow-300' :
            'bg-red-500/20 text-red-300'
          }`}>
            <div className={`w-2 h-2 rounded-full ${
              getStatusColor(analyticsData.status) === 'green' ? 'bg-green-400' :
              getStatusColor(analyticsData.status) === 'yellow' ? 'bg-yellow-400' :
              'bg-red-400'
            }`}></div>
            {getStatusText(analyticsData.status)}
          </div>
          <Button 
            onClick={() => setShowSetup(true)}
            variant="outline" 
            className="border-white/20 text-white hover:bg-white/10"
          >
            <Settings className="w-4 h-4 mr-2" />
            Setup GA4
          </Button>
        </div>
      </div>

      {/* Overview Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <Card className="bg-white/10 backdrop-blur-md border-white/20">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-white">Total Users</CardTitle>
            <Users className="h-4 w-4 text-green-400" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-white">
              {analyticsData.overview?.total_users?.toLocaleString() || '0'}
            </div>
            <p className="text-xs text-green-400">Last 30 days</p>
          </CardContent>
        </Card>
        
        <Card className="bg-white/10 backdrop-blur-md border-white/20">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-white">Page Views</CardTitle>
            <Eye className="h-4 w-4 text-blue-400" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-white">
              {analyticsData.overview?.page_views?.toLocaleString() || '0'}
            </div>
            <p className="text-xs text-blue-400">Last 30 days</p>
          </CardContent>
        </Card>
        
        <Card className="bg-white/10 backdrop-blur-md border-white/20">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-white">Bounce Rate</CardTitle>
            <TrendingUp className="h-4 w-4 text-yellow-400" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-white">
              {analyticsData.overview?.bounce_rate || '0%'}
            </div>
            <p className="text-xs text-yellow-400">Last 30 days</p>
          </CardContent>
        </Card>
        
        <Card className="bg-white/10 backdrop-blur-md border-white/20">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-white">Avg. Session</CardTitle>
            <BarChart3 className="h-4 w-4 text-purple-400" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-white">
              {analyticsData.overview?.avg_session_duration || '0s'}
            </div>
            <p className="text-xs text-purple-400">Last 30 days</p>
          </CardContent>
        </Card>
      </div>

      {/* Top Pages and Traffic Sources */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        <Card className="bg-white/10 backdrop-blur-md border-white/20">
          <CardHeader>
            <CardTitle className="text-white">Top Pages</CardTitle>
            <CardDescription className="text-gray-300">Most visited pages this month</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {analyticsData.topPages.length > 0 ? (
                analyticsData.topPages.slice(0, 5).map((page, index) => (
                  <div key={index} className="flex items-center justify-between">
                    <div className="flex-1 min-w-0">
                      <p className="text-white text-sm truncate">{page.title || page.path}</p>
                      <p className="text-gray-400 text-xs">{page.path}</p>
                    </div>
                    <span className="text-green-400 text-sm ml-4">
                      {page.page_views?.toLocaleString()} views
                    </span>
                  </div>
                ))
              ) : (
                <p className="text-gray-400 text-sm">No page data available</p>
              )}
            </div>
          </CardContent>
        </Card>

        <Card className="bg-white/10 backdrop-blur-md border-white/20">
          <CardHeader>
            <CardTitle className="text-white">Traffic Sources</CardTitle>
            <CardDescription className="text-gray-300">Where your visitors come from</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {analyticsData.trafficSources.length > 0 ? (
                analyticsData.trafficSources.slice(0, 5).map((source, index) => (
                  <div key={index} className="flex items-center justify-between">
                    <span className="text-white text-sm">{source.source_medium}</span>
                    <div className="text-right">
                      <span className="text-blue-400 text-sm">{source.percentage}</span>
                      <p className="text-gray-400 text-xs">{source.sessions} sessions</p>
                    </div>
                  </div>
                ))
              ) : (
                <p className="text-gray-400 text-sm">No traffic source data available</p>
              )}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Status Card */}
      <Card className={`border ${
        analyticsData.status?.status === 'connected' ? 'bg-green-500/10 border-green-400/20' :
        analyticsData.status?.status === 'demo_mode' ? 'bg-yellow-500/10 border-yellow-400/20' :
        'bg-blue-500/10 border-blue-400/20'
      }`}>
        <CardContent className="pt-6">
          <div className="flex items-start gap-3">
            <AlertCircle className={`w-5 h-5 mt-0.5 ${
              analyticsData.status?.status === 'connected' ? 'text-green-400' :
              analyticsData.status?.status === 'demo_mode' ? 'text-yellow-400' :
              'text-blue-400'
            }`} />
            <div>
              <p className={`text-sm font-medium ${
                analyticsData.status?.status === 'connected' ? 'text-green-200' :
                analyticsData.status?.status === 'demo_mode' ? 'text-yellow-200' :
                'text-blue-200'
              }`}>
                {analyticsData.status?.status === 'connected' ? 'Google Analytics 4 Connected' :
                 analyticsData.status?.status === 'demo_mode' ? 'Demo Mode Active' :
                 'Analytics Integration'}
              </p>
              <p className={`text-sm mt-1 ${
                analyticsData.status?.status === 'connected' ? 'text-green-300' :
                analyticsData.status?.status === 'demo_mode' ? 'text-yellow-300' :
                'text-blue-300'
              }`}>
                {analyticsData.status?.message || 'Configure Google Analytics 4 to see real data from your WordPress site.'}
              </p>
              {analyticsData.overview?.source && (
                <p className="text-xs text-gray-400 mt-2">
                  Data source: {analyticsData.overview.source}
                </p>
              )}
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Setup Dialog */}
      <Dialog open={showSetup} onOpenChange={setShowSetup}>
        <DialogContent className="bg-slate-800 border-slate-700 text-white max-w-2xl">
          <DialogHeader>
            <DialogTitle>Google Analytics 4 Setup</DialogTitle>
            <DialogDescription className="text-gray-400">
              Connect your Google Analytics 4 property to see real data
            </DialogDescription>
          </DialogHeader>
          
          <form onSubmit={handleSetupGA4} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="ga4_property_id">GA4 Property ID</Label>
              <Input
                id="ga4_property_id"
                value={ga4Config.ga4_property_id}
                onChange={(e) => setGa4Config(prev => ({...prev, ga4_property_id: e.target.value}))}
                placeholder="123456789"
                required
                className="bg-slate-700 border-slate-600 text-white"
              />
              <p className="text-xs text-gray-400">
                Find this in GA4 Admin → Property Settings → Property Details
              </p>
            </div>

            <div className="bg-blue-500/10 border border-blue-400/20 rounded-lg p-4">
              <h4 className="text-blue-200 font-medium mb-2">Next Steps:</h4>
              <ol className="text-sm text-blue-300 space-y-1 list-decimal list-inside">
                <li>Create a Google Cloud service account</li>
                <li>Download the service account JSON file</li>
                <li>Upload it to <code className="bg-slate-700 px-1 rounded">/app/backend/service_account.json</code></li>
                <li>Add the service account email to your GA4 property as Viewer</li>
              </ol>
            </div>

            <div className="flex gap-2 pt-4">
              <Button type="submit" className="bg-green-600 hover:bg-green-700">
                Save Configuration
              </Button>
              <Button 
                type="button" 
                variant="outline" 
                onClick={() => setShowSetup(false)}
                className="border-slate-600 text-white hover:bg-slate-700"
              >
                Cancel
              </Button>
            </div>
          </form>
        </DialogContent>
      </Dialog>
    </div>
  );
};

// Event Modal Component
const EventModal = ({ onSubmit, event, onClose }) => {
  const [formData, setFormData] = useState({
    title: '',
    content: '',
    data_evento: '',
    ora_evento: '',
    luogo_evento: '',
    location: '',
    dj: '',
    host: '',
    guest: '',
    categorie_eventi: [],
    featured_media: null
  });

  const [categories, setCategories] = useState([]);
  const [mediaItems, setMediaItems] = useState([]);
  const [showMediaPicker, setShowMediaPicker] = useState(false);

  // Load categories and media on mount
  useEffect(() => {
    loadCategories();
    loadMedia();
  }, []);

  // Update form data when event prop changes (for editing)
  useEffect(() => {
    if (event) {
      setFormData({
        title: event.title || '',
        content: event.content?.replace(/<[^>]*>/g, '') || '',
        data_evento: event.data_evento || '',
        ora_evento: event.ora_evento || '',
        luogo_evento: event.luogo_evento || '',
        location: event.location || '',
        dj: event.dj || '',
        host: event.host || '',
        guest: event.guest || '',
        categorie_eventi: event.categorie_eventi || [],
        featured_media: event.featured_media || null
      });
    }
  }, [event]);

  const loadCategories = async () => {
    try {
      const response = await axios.get(`${API}/event-categories`);
      setCategories(response.data.data || []);
    } catch (error) {
      console.error('Failed to load categories:', error);
    }
  };

  const loadMedia = async () => {
    try {
      const response = await axios.get(`${API}/media?per_page=50`);
      setMediaItems(response.data.data || []);
    } catch (error) {
      console.error('Failed to load media:', error);
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit(formData);
    if (!event) {
      setFormData({
        title: '',
        content: '',
        data_evento: '',
        ora_evento: '',
        luogo_evento: '',
        location: '',
        dj: '',
        host: '',
        guest: '',
        categorie_eventi: [],
        featured_media: null
      });
    }
  };

  const handleCategoryChange = (categoryId) => {
    setFormData(prev => ({
      ...prev,
      categorie_eventi: prev.categorie_eventi.includes(categoryId)
        ? prev.categorie_eventi.filter(id => id !== categoryId)
        : [...prev.categorie_eventi, categoryId]
    }));
  };

  const selectedMedia = mediaItems.find(item => item.id === formData.featured_media);

  return (
    <DialogContent className="bg-slate-800 border-slate-700 text-white max-w-2xl">
      <DialogHeader>
        <DialogTitle>{event ? 'Edit Event' : 'Create New Event'}</DialogTitle>
        <DialogDescription className="text-gray-400">
          Add a new event to your WordPress site
        </DialogDescription>
      </DialogHeader>
      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="space-y-2">
          <Label htmlFor="title">Event Title</Label>
          <Input
            id="title"
            value={formData.title}
            onChange={(e) => setFormData(prev => ({...prev, title: e.target.value}))}
            placeholder="Enter event title"
            required
            className="bg-slate-700 border-slate-600 text-white"
          />
        </div>
        <div className="space-y-2">
          <Label htmlFor="location">Location</Label>
          <Input
            id="location"
            value={formData.location}
            onChange={(e) => setFormData(prev => ({...prev, location: e.target.value}))}
            placeholder="Event location"
            required
            className="bg-slate-700 border-slate-600 text-white"
          />
        </div>
        <div className="space-y-2">
          <Label htmlFor="event_date">Event Date</Label>
          <Input
            id="event_date"
            type="datetime-local"
            value={formData.event_date}
            onChange={(e) => setFormData(prev => ({...prev, event_date: e.target.value}))}
            required
            className="bg-slate-700 border-slate-600 text-white"
          />
        </div>
        <div className="space-y-2">
          <Label htmlFor="content">Event Description</Label>
          <Textarea
            id="content"
            value={formData.content}
            onChange={(e) => setFormData(prev => ({...prev, content: e.target.value}))}
            placeholder="Enter event description"
            rows={4}
            className="bg-slate-700 border-slate-600 text-white"
          />
        </div>
        <div className="flex gap-2 pt-4">
          <Button type="submit" className="bg-green-600 hover:bg-green-700">
            {event ? 'Update Event' : 'Create Event'}
          </Button>
          <Button type="button" variant="outline" onClick={onClose} className="border-slate-600 text-white hover:bg-slate-700">
            Cancel
          </Button>
        </div>
      </form>
    </DialogContent>
  );
};

function App() {
  const [showLoading, setShowLoading] = useState(true);

  if (showLoading) {
    return <LoadingScreen onComplete={() => setShowLoading(false)} />;
  }

  return (
    <div className="App">
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<SetupPage />} />
          <Route path="/setup" element={<SetupPage />} />
          <Route path="/dashboard" element={<DashboardPage />} />
        </Routes>
      </BrowserRouter>
    </div>
  );
}

export default App;
