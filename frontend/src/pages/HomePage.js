import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { useCart } from '../contexts/CartContext';
import axios from 'axios';
import { 
  MagnifyingGlassIcon, 
  ShoppingCartIcon, 
  ListBulletIcon,
  CurrencyPoundIcon,
  TrophyIcon,
  MapPinIcon
} from '@heroicons/react/24/outline';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API_BASE = `${BACKEND_URL}/api`;

const HomePage = () => {
  const { user } = useAuth();
  const { basket, totalCost, estimatedSavings } = useCart();
  const [featuredProducts, setFeaturedProducts] = useState([]);
  const [stores, setStores] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        // Fetch some featured products (guest search for popular items)
        const productsResponse = await axios.get(`${API_BASE}/products/guest-search?q=milk&per_page=3`);
        setFeaturedProducts(productsResponse.data.products);

        // Fetch stores
        const storesResponse = await axios.get(`${API_BASE}/stores/?delivery_only=true`);
        setStores(storesResponse.data.slice(0, 4)); // Show first 4 stores with delivery
      } catch (error) {
        console.error('Error fetching dashboard data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchDashboardData();
  }, []);

  const stats = [
    {
      name: 'Your Basket',
      value: `£${totalCost.toFixed(2)}`,
      icon: ShoppingCartIcon,
      link: '/basket',
      description: `${basket?.total_items || 0} items`
    },
    {
      name: 'Potential Savings',
      value: `£${estimatedSavings?.toFixed(2) || '0.00'}`,
      icon: CurrencyPoundIcon,
      link: '/basket',
      description: 'Switch stores to save'
    },
    {
      name: 'Stores Available',
      value: '10',
      icon: MapPinIcon,
      link: '/search',
      description: 'UK grocery stores'
    },
    {
      name: 'Best Deals',
      value: 'Updated',
      icon: TrophyIcon,
      link: '/search',
      description: 'Real-time prices'
    }
  ];

  const quickActions = [
    {
      name: 'Search Products',
      description: 'Find the best prices across stores',
      icon: MagnifyingGlassIcon,
      link: '/search',
      color: 'bg-blue-500 hover:bg-blue-600'
    },
    {
      name: 'Shopping Lists',
      description: 'Organize your grocery shopping',
      icon: ListBulletIcon,
      link: '/shopping-lists',
      color: 'bg-green-500 hover:bg-green-600'
    },
    {
      name: 'View Basket',
      description: 'Review and optimize your selection',
      icon: ShoppingCartIcon,
      link: '/basket',
      color: 'bg-purple-500 hover:bg-purple-600'
    }
  ];

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-green-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Welcome Header */}
      <div className="bg-white overflow-hidden shadow rounded-lg">
        <div className="px-4 py-5 sm:p-6">
          <h1 className="text-2xl font-bold text-gray-900">
            Welcome back, {user?.full_name || 'there'}!
          </h1>
          <p className="mt-1 text-sm text-gray-500">
            {user?.location ? `Shopping in ${user.location}` : 'Compare grocery prices across UK stores'}
          </p>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
        {stats.map((stat) => (
          <Link
            key={stat.name}
            to={stat.link}
            className="bg-white overflow-hidden shadow rounded-lg hover:shadow-md transition-shadow"
          >
            <div className="p-5">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <stat.icon className="h-6 w-6 text-gray-400" />
                </div>
                <div className="ml-5 w-0 flex-1">
                  <dl>
                    <dt className="text-sm font-medium text-gray-500 truncate">{stat.name}</dt>
                    <dd className="text-lg font-semibold text-gray-900">{stat.value}</dd>
                    <dd className="text-sm text-gray-500">{stat.description}</dd>
                  </dl>
                </div>
              </div>
            </div>
          </Link>
        ))}
      </div>

      {/* Quick Actions */}
      <div className="bg-white shadow rounded-lg">
        <div className="px-4 py-5 sm:p-6">
          <h2 className="text-lg font-medium text-gray-900 mb-4">Quick Actions</h2>
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
            {quickActions.map((action) => (
              <Link
                key={action.name}
                to={action.link}
                className={`relative block p-6 rounded-lg text-white ${action.color} transition-colors`}
              >
                <div className="flex items-center">
                  <action.icon className="h-8 w-8 mr-3" />
                  <div>
                    <h3 className="text-lg font-semibold">{action.name}</h3>
                    <p className="text-sm opacity-90">{action.description}</p>
                  </div>
                </div>
              </Link>
            ))}
          </div>
        </div>
      </div>

      {/* Featured Products */}
      <div className="bg-white shadow rounded-lg">
        <div className="px-4 py-5 sm:p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-medium text-gray-900">Today's Best Deals</h2>
            <Link to="/search" className="text-sm text-green-600 hover:text-green-500">
              View all →
            </Link>
          </div>
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
            {featuredProducts.map((product) => {
              const cheapestPrice = Math.min(...product.prices.map(p => p.price));
              const cheapestStore = product.prices.find(p => p.price === cheapestPrice);
              
              return (
                <div key={product.id} className="border rounded-lg p-4 hover:shadow-md transition-shadow">
                  <h3 className="font-semibold text-gray-900">{product.name}</h3>
                  <p className="text-sm text-gray-500">{product.category}</p>
                  <div className="mt-2">
                    <div className="flex items-center justify-between">
                      <span className="text-lg font-bold text-green-600">
                        £{cheapestPrice.toFixed(2)}
                      </span>
                      <span className="text-sm text-gray-500">
                        at {cheapestStore?.store_name}
                      </span>
                    </div>
                    <p className="text-xs text-gray-400 mt-1">
                      {product.prices.length} stores available
                    </p>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>

      {/* Available Stores */}
      <div className="bg-white shadow rounded-lg">
        <div className="px-4 py-5 sm:p-6">
          <h2 className="text-lg font-medium text-gray-900 mb-4">Available Stores</h2>
          <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
            {stores.map((store) => (
              <div key={store.id} className="text-center p-4 border rounded-lg">
                <div className="w-12 h-12 mx-auto mb-2 bg-gray-100 rounded-full flex items-center justify-center">
                  <span className="text-sm font-semibold text-gray-600">
                    {store.brand[0]}
                  </span>
                </div>
                <h3 className="text-sm font-medium text-gray-900">{store.brand}</h3>
                <p className="text-xs text-gray-500 capitalize">{store.price_tier}</p>
                {store.delivery_available && (
                  <span className="inline-block mt-1 px-2 py-1 text-xs bg-green-100 text-green-800 rounded">
                    Delivery
                  </span>
                )}
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default HomePage;