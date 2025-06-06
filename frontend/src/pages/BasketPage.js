import React, { useEffect, useState } from 'react';
import { useCart } from '../contexts/CartContext';
import { 
  ShoppingCartIcon, 
  TrashIcon, 
  MinusIcon, 
  PlusIcon,
  CurrencyPoundIcon,
  ExclamationTriangleIcon
} from '@heroicons/react/24/outline';

const BasketPage = () => {
  const { 
    basket, 
    loading, 
    updateBasketItem, 
    removeFromBasket, 
    clearBasket,
    fetchBasket 
  } = useCart();
  
  const [summary, setSummary] = useState(null);

  useEffect(() => {
    fetchBasket();
  }, []);

  const handleQuantityChange = async (itemId, newQuantity) => {
    if (newQuantity < 0.1) return;
    await updateBasketItem(itemId, newQuantity);
  };

  const handleRemoveItem = async (itemId) => {
    await removeFromBasket(itemId);
  };

  const handleClearBasket = async () => {
    if (window.confirm('Are you sure you want to clear your entire basket?')) {
      await clearBasket();
    }
  };

  const groupItemsByStore = (items) => {
    return items.reduce((acc, item) => {
      if (!acc[item.store_name]) {
        acc[item.store_name] = [];
      }
      acc[item.store_name].push(item);
      return acc;
    }, {});
  };

  const calculateStoreTotal = (storeItems) => {
    return storeItems.reduce((total, item) => total + item.total_price, 0);
  };

  if (loading && !basket) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-green-600"></div>
      </div>
    );
  }

  const hasItems = basket && basket.items && basket.items.length > 0;
  const groupedItems = hasItems ? groupItemsByStore(basket.items) : {};

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white shadow rounded-lg">
        <div className="px-6 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Your Basket</h1>
              <p className="text-sm text-gray-500">
                {hasItems ? `${basket.total_items} items` : 'No items in basket'}
              </p>
            </div>
            {hasItems && (
              <button
                onClick={handleClearBasket}
                className="flex items-center px-4 py-2 text-red-600 border border-red-300 rounded-md hover:bg-red-50"
              >
                <TrashIcon className="w-4 h-4 mr-2" />
                Clear Basket
              </button>
            )}
          </div>
        </div>
      </div>

      {hasItems ? (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Basket Items */}
          <div className="lg:col-span-2 space-y-4">
            {Object.entries(groupedItems).map(([storeName, storeItems]) => (
              <div key={storeName} className="bg-white shadow rounded-lg">
                <div className="px-6 py-4 border-b border-gray-200">
                  <div className="flex items-center justify-between">
                    <h2 className="text-lg font-semibold text-gray-900">{storeName}</h2>
                    <span className="text-sm text-gray-500">
                      £{calculateStoreTotal(storeItems).toFixed(2)}
                    </span>
                  </div>
                </div>
                <div className="divide-y divide-gray-200">
                  {storeItems.map((item) => (
                    <div key={item.id} className="p-6">
                      <div className="flex items-center justify-between">
                        <div className="flex-1">
                          <h3 className="text-sm font-medium text-gray-900">
                            {item.product_name}
                          </h3>
                          <p className="text-sm text-gray-500">
                            £{item.price.toFixed(2)} per {item.unit}
                          </p>
                        </div>
                        
                        <div className="flex items-center space-x-4">
                          {/* Quantity Controls */}
                          <div className="flex items-center space-x-2">
                            <button
                              onClick={() => handleQuantityChange(item.id, item.quantity - 0.5)}
                              className="p-1 rounded-full border border-gray-300 hover:bg-gray-50"
                              disabled={item.quantity <= 0.5}
                            >
                              <MinusIcon className="w-4 h-4" />
                            </button>
                            <span className="text-sm font-medium min-w-[3rem] text-center">
                              {item.quantity}
                            </span>
                            <button
                              onClick={() => handleQuantityChange(item.id, item.quantity + 0.5)}
                              className="p-1 rounded-full border border-gray-300 hover:bg-gray-50"
                            >
                              <PlusIcon className="w-4 h-4" />
                            </button>
                          </div>

                          {/* Item Total */}
                          <div className="text-right min-w-[4rem]">
                            <p className="text-sm font-semibold text-gray-900">
                              £{item.total_price.toFixed(2)}
                            </p>
                          </div>

                          {/* Remove Button */}
                          <button
                            onClick={() => handleRemoveItem(item.id)}
                            className="p-1 text-red-600 hover:text-red-800"
                          >
                            <TrashIcon className="w-4 h-4" />
                          </button>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>

          {/* Basket Summary */}
          <div className="lg:col-span-1">
            <div className="bg-white shadow rounded-lg sticky top-20">
              <div className="px-6 py-4 border-b border-gray-200">
                <h2 className="text-lg font-semibold text-gray-900">Order Summary</h2>
              </div>
              
              <div className="p-6 space-y-4">
                <div className="flex justify-between text-sm">
                  <span className="text-gray-600">Items ({basket.total_items})</span>
                  <span className="font-medium">£{basket.total_cost.toFixed(2)}</span>
                </div>

                {basket.estimated_savings && basket.estimated_savings > 0 && (
                  <div className="p-4 bg-yellow-50 rounded-lg">
                    <div className="flex items-start">
                      <ExclamationTriangleIcon className="w-5 h-5 text-yellow-400 mt-0.5 mr-2" />
                      <div>
                        <p className="text-sm font-medium text-yellow-800">
                          Potential Savings Available
                        </p>
                        <p className="text-sm text-yellow-700 mt-1">
                          You could save £{basket.estimated_savings.toFixed(2)} by shopping at different stores.
                        </p>
                      </div>
                    </div>
                  </div>
                )}

                {basket.alternative_stores && Object.keys(basket.alternative_stores).length > 0 && (
                  <div className="border-t pt-4">
                    <h3 className="text-sm font-medium text-gray-900 mb-3">
                      Price Comparison
                    </h3>
                    <div className="space-y-2">
                      <div className="flex justify-between text-sm">
                        <span className="text-gray-600">Current total:</span>
                        <span className="font-medium">£{basket.total_cost.toFixed(2)}</span>
                      </div>
                      {Object.entries(basket.alternative_stores)
                        .sort(([,a], [,b]) => a - b)
                        .slice(0, 3)
                        .map(([storeId, cost]) => {
                          const savings = basket.total_cost - cost;
                          return (
                            <div key={storeId} className="flex justify-between text-sm">
                              <span className="text-gray-600">Alternative store:</span>
                              <div className="text-right">
                                <span className="font-medium">£{cost.toFixed(2)}</span>
                                {savings > 0 && (
                                  <span className="text-green-600 text-xs block">
                                    Save £{savings.toFixed(2)}
                                  </span>
                                )}
                              </div>
                            </div>
                          );
                        })}
                    </div>
                  </div>
                )}

                <div className="border-t pt-4">
                  <div className="flex justify-between text-lg font-semibold">
                    <span>Total</span>
                    <span>£{basket.total_cost.toFixed(2)}</span>
                  </div>
                </div>

                <button className="w-full bg-green-600 text-white py-3 px-4 rounded-md hover:bg-green-700 font-medium">
                  Proceed to Checkout
                </button>

                <p className="text-xs text-gray-500 text-center">
                  * Prices and availability subject to change
                </p>
              </div>
            </div>
          </div>
        </div>
      ) : (
        /* Empty State */
        <div className="bg-white shadow rounded-lg">
          <div className="px-6 py-12 text-center">
            <ShoppingCartIcon className="mx-auto h-12 w-12 text-gray-400" />
            <h3 className="mt-2 text-lg font-medium text-gray-900">Your basket is empty</h3>
            <p className="mt-1 text-sm text-gray-500">
              Start adding products to compare prices and save money.
            </p>
            <div className="mt-6">
              <a
                href="/search"
                className="inline-flex items-center px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700"
              >
                <CurrencyPoundIcon className="w-5 h-5 mr-2" />
                Start Shopping
              </a>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default BasketPage;