import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useCart } from '../contexts/CartContext';
import { MagnifyingGlassIcon, ShoppingCartIcon, TagIcon } from '@heroicons/react/24/outline';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API_BASE = `${BACKEND_URL}/api`;

const SearchPage = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [products, setProducts] = useState([]);
  const [categories, setCategories] = useState([]);
  const [selectedCategory, setSelectedCategory] = useState('');
  const [sortBy, setSortBy] = useState('relevance');
  const [loading, setLoading] = useState(false);
  const [page, setPage] = useState(1);
  const [totalResults, setTotalResults] = useState(0);
  const [searchPerformed, setSearchPerformed] = useState(false);

  const { addToBasket } = useCart();

  // Fetch categories on component mount
  useEffect(() => {
    const fetchCategories = async () => {
      try {
        const response = await axios.get(`${API_BASE}/products/categories`);
        setCategories(response.data);
      } catch (error) {
        console.error('Error fetching categories:', error);
      }
    };

    fetchCategories();
  }, []);

  const searchProducts = async (resetPage = false) => {
    if (!searchQuery.trim()) return;

    setLoading(true);
    const currentPage = resetPage ? 1 : page;
    
    try {
      const params = new URLSearchParams({
        q: searchQuery,
        page: currentPage,
        per_page: 12,
        sort_by: sortBy
      });

      if (selectedCategory) {
        params.append('category', selectedCategory);
      }

      const response = await axios.get(`${API_BASE}/products/search?${params}`);
      
      if (resetPage) {
        setProducts(response.data.products);
        setPage(1);
      } else {
        setProducts(prev => [...prev, ...response.data.products]);
      }
      
      setTotalResults(response.data.total);
      setSearchPerformed(true);
    } catch (error) {
      console.error('Error searching products:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = (e) => {
    e.preventDefault();
    searchProducts(true);
  };

  const handleLoadMore = () => {
    setPage(prev => prev + 1);
    searchProducts(false);
  };

  const handleAddToBasket = async (product, storeId) => {
    const result = await addToBasket(product.id, storeId, 1);
    if (result.success) {
      // You could add a toast notification here
      console.log('Added to basket successfully');
    } else {
      console.error('Failed to add to basket:', result.error);
    }
  };

  // Update search when filters change
  useEffect(() => {
    if (searchPerformed) {
      searchProducts(true);
    }
  }, [selectedCategory, sortBy]);

  const ProductCard = ({ product }) => {
    const sortedPrices = [...product.prices].sort((a, b) => a.price - b.price);
    const cheapestPrice = sortedPrices[0];
    const mostExpensivePrice = sortedPrices[sortedPrices.length - 1];
    const priceRange = mostExpensivePrice.price - cheapestPrice.price;

    return (
      <div className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow">
        <div className="flex justify-between items-start mb-4">
          <div>
            <h3 className="text-lg font-semibold text-gray-900">{product.name}</h3>
            <p className="text-sm text-gray-500">{product.category}</p>
            {product.brand && (
              <p className="text-sm text-gray-400">{product.brand}</p>
            )}
          </div>
          <div className="text-right">
            <div className="text-sm text-gray-500">from</div>
            <div className="text-xl font-bold text-green-600">
              £{cheapestPrice.price.toFixed(2)}
            </div>
            <div className="text-xs text-gray-400">
              {cheapestPrice.unit}
            </div>
          </div>
        </div>

        {priceRange > 0 && (
          <div className="mb-4 p-3 bg-yellow-50 rounded-lg">
            <div className="flex items-center justify-between text-sm">
              <span className="text-yellow-800">💰 Save up to</span>
              <span className="font-semibold text-yellow-900">
                £{priceRange.toFixed(2)}
              </span>
            </div>
            <div className="text-xs text-yellow-700 mt-1">
              vs most expensive option
            </div>
          </div>
        )}

        <div className="space-y-2">
          <h4 className="text-sm font-medium text-gray-700">Available at:</h4>
          {sortedPrices.slice(0, 3).map((price, index) => (
            <div key={`${price.store_id}-${index}`} className="flex items-center justify-between p-2 bg-gray-50 rounded">
              <div className="flex items-center space-x-2">
                <span className={`w-2 h-2 rounded-full ${index === 0 ? 'bg-green-500' : 'bg-gray-400'}`}></span>
                <span className="text-sm font-medium">{price.store_name}</span>
                {price.promotion && (
                  <span className="px-2 py-1 bg-red-100 text-red-800 text-xs rounded">
                    {price.promotion}
                  </span>
                )}
              </div>
              <div className="flex items-center space-x-2">
                <span className="text-sm font-semibold">£{price.price.toFixed(2)}</span>
                <button
                  onClick={() => handleAddToBasket(product, price.store_id)}
                  disabled={!price.availability}
                  className="p-1 bg-green-600 text-white rounded hover:bg-green-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
                  title={price.availability ? 'Add to basket' : 'Out of stock'}
                >
                  <ShoppingCartIcon className="w-4 h-4" />
                </button>
              </div>
            </div>
          ))}
          
          {sortedPrices.length > 3 && (
            <div className="text-center">
              <span className="text-sm text-gray-500">
                +{sortedPrices.length - 3} more stores
              </span>
            </div>
          )}
        </div>
      </div>
    );
  };

  return (
    <div className="space-y-6">
      {/* Search Header */}
      <div className="bg-white shadow rounded-lg">
        <div className="px-6 py-4">
          <h1 className="text-2xl font-bold text-gray-900 mb-4">Search Products</h1>
          
          {/* Search Form */}
          <form onSubmit={handleSearch} className="space-y-4">
            <div className="flex space-x-4">
              <div className="flex-1">
                <div className="relative">
                  <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
                  <input
                    type="text"
                    placeholder="Search for products (e.g., milk, bread, apples)"
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-md focus:ring-green-500 focus:border-green-500"
                  />
                </div>
              </div>
              <button
                type="submit"
                disabled={!searchQuery.trim() || loading}
                className="px-6 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
              >
                {loading ? 'Searching...' : 'Search'}
              </button>
            </div>

            {/* Filters */}
            <div className="flex space-x-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Category
                </label>
                <select
                  value={selectedCategory}
                  onChange={(e) => setSelectedCategory(e.target.value)}
                  className="border border-gray-300 rounded-md px-3 py-2 text-sm focus:ring-green-500 focus:border-green-500"
                >
                  <option value="">All Categories</option>
                  {categories.map((category) => (
                    <option key={category} value={category}>
                      {category}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Sort By
                </label>
                <select
                  value={sortBy}
                  onChange={(e) => setSortBy(e.target.value)}
                  className="border border-gray-300 rounded-md px-3 py-2 text-sm focus:ring-green-500 focus:border-green-500"
                >
                  <option value="relevance">Relevance</option>
                  <option value="price_low">Price: Low to High</option>
                  <option value="price_high">Price: High to Low</option>
                  <option value="name">Name A-Z</option>
                </select>
              </div>
            </div>
          </form>
        </div>
      </div>

      {/* Search Results */}
      {searchPerformed && (
        <div className="bg-white shadow rounded-lg">
          <div className="px-6 py-4">
            {totalResults > 0 ? (
              <>
                <div className="flex items-center justify-between mb-6">
                  <h2 className="text-lg font-medium text-gray-900">
                    Found {totalResults} result{totalResults !== 1 ? 's' : ''}
                    {selectedCategory && ` in ${selectedCategory}`}
                  </h2>
                  <div className="flex items-center space-x-2 text-sm text-gray-500">
                    <TagIcon className="w-4 h-4" />
                    <span>Best prices highlighted</span>
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                  {products.map((product) => (
                    <ProductCard key={product.id} product={product} />
                  ))}
                </div>

                {/* Load More Button */}
                {products.length < totalResults && (
                  <div className="text-center mt-8">
                    <button
                      onClick={handleLoadMore}
                      disabled={loading}
                      className="px-6 py-2 bg-gray-100 text-gray-700 rounded-md hover:bg-gray-200 disabled:opacity-50"
                    >
                      {loading ? 'Loading...' : 'Load More Products'}
                    </button>
                  </div>
                )}
              </>
            ) : (
              <div className="text-center py-12">
                <MagnifyingGlassIcon className="mx-auto h-12 w-12 text-gray-400" />
                <h3 className="mt-2 text-sm font-medium text-gray-900">No products found</h3>
                <p className="mt-1 text-sm text-gray-500">
                  Try adjusting your search terms or filters.
                </p>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Initial State */}
      {!searchPerformed && (
        <div className="bg-white shadow rounded-lg">
          <div className="px-6 py-12 text-center">
            <MagnifyingGlassIcon className="mx-auto h-12 w-12 text-gray-400" />
            <h3 className="mt-2 text-lg font-medium text-gray-900">
              Search for grocery products
            </h3>
            <p className="mt-1 text-sm text-gray-500">
              Compare prices across {categories.length > 0 ? categories.length : ''} categories and 10 UK stores
            </p>
            <div className="mt-6">
              <div className="flex justify-center space-x-4 text-sm">
                <span className="px-3 py-1 bg-gray-100 rounded-full">🥛 milk</span>
                <span className="px-3 py-1 bg-gray-100 rounded-full">🍞 bread</span>
                <span className="px-3 py-1 bg-gray-100 rounded-full">🍎 apples</span>
                <span className="px-3 py-1 bg-gray-100 rounded-full">🥕 carrots</span>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default SearchPage;