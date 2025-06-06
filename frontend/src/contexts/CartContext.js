import React, { createContext, useContext, useState, useEffect } from 'react';
import axios from 'axios';
import { useAuth } from './AuthContext';

const CartContext = createContext();

export const useCart = () => {
  const context = useContext(CartContext);
  if (!context) {
    throw new Error('useCart must be used within a CartProvider');
  }
  return context;
};

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API_BASE = `${BACKEND_URL}/api`;

export const CartProvider = ({ children }) => {
  const [basket, setBasket] = useState(null);
  const [loading, setLoading] = useState(false);
  const { isAuthenticated } = useAuth();

  // Fetch basket when user is authenticated
  useEffect(() => {
    if (isAuthenticated) {
      fetchBasket();
    } else {
      setBasket(null);
    }
  }, [isAuthenticated]);

  const fetchBasket = async () => {
    if (!isAuthenticated) return;
    
    try {
      setLoading(true);
      const response = await axios.get(`${API_BASE}/basket/`);
      setBasket(response.data);
    } catch (error) {
      console.error('Error fetching basket:', error);
    } finally {
      setLoading(false);
    }
  };

  const addToBasket = async (productId, storeId, quantity = 1) => {
    if (!isAuthenticated) return { success: false, error: 'Not authenticated' };

    try {
      setLoading(true);
      const response = await axios.post(`${API_BASE}/basket/items`, {
        product_id: productId,
        store_id: storeId,
        quantity
      });
      setBasket(response.data);
      return { success: true };
    } catch (error) {
      console.error('Error adding to basket:', error);
      return { 
        success: false, 
        error: error.response?.data?.detail || 'Failed to add to basket' 
      };
    } finally {
      setLoading(false);
    }
  };

  const updateBasketItem = async (itemId, quantity) => {
    if (!isAuthenticated) return { success: false, error: 'Not authenticated' };

    try {
      setLoading(true);
      const response = await axios.put(`${API_BASE}/basket/items/${itemId}`, {
        quantity
      });
      setBasket(response.data);
      return { success: true };
    } catch (error) {
      console.error('Error updating basket item:', error);
      return { 
        success: false, 
        error: error.response?.data?.detail || 'Failed to update item' 
      };
    } finally {
      setLoading(false);
    }
  };

  const removeFromBasket = async (itemId) => {
    if (!isAuthenticated) return { success: false, error: 'Not authenticated' };

    try {
      setLoading(true);
      const response = await axios.delete(`${API_BASE}/basket/items/${itemId}`);
      setBasket(response.data);
      return { success: true };
    } catch (error) {
      console.error('Error removing from basket:', error);
      return { 
        success: false, 
        error: error.response?.data?.detail || 'Failed to remove item' 
      };
    } finally {
      setLoading(false);
    }
  };

  const clearBasket = async () => {
    if (!isAuthenticated) return { success: false, error: 'Not authenticated' };

    try {
      setLoading(true);
      const response = await axios.delete(`${API_BASE}/basket/`);
      setBasket(response.data);
      return { success: true };
    } catch (error) {
      console.error('Error clearing basket:', error);
      return { 
        success: false, 
        error: error.response?.data?.detail || 'Failed to clear basket' 
      };
    } finally {
      setLoading(false);
    }
  };

  const getBasketSummary = async () => {
    if (!isAuthenticated) return null;

    try {
      const response = await axios.get(`${API_BASE}/basket/summary`);
      return response.data;
    } catch (error) {
      console.error('Error getting basket summary:', error);
      return null;
    }
  };

  const value = {
    basket,
    loading,
    fetchBasket,
    addToBasket,
    updateBasketItem,
    removeFromBasket,
    clearBasket,
    getBasketSummary,
    itemCount: basket?.total_items || 0,
    totalCost: basket?.total_cost || 0,
    estimatedSavings: basket?.estimated_savings || 0
  };

  return (
    <CartContext.Provider value={value}>
      {children}
    </CartContext.Provider>
  );
};