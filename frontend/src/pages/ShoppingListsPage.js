import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { 
  PlusIcon, 
  ListBulletIcon, 
  PencilIcon, 
  TrashIcon,
  CheckCircleIcon,
  XCircleIcon
} from '@heroicons/react/24/outline';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API_BASE = `${BACKEND_URL}/api`;

const ShoppingListsPage = () => {
  const [shoppingLists, setShoppingLists] = useState([]);
  const [selectedList, setSelectedList] = useState(null);
  const [loading, setLoading] = useState(true);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showItemModal, setShowItemModal] = useState(false);
  const [suggestions, setSuggestions] = useState([]);

  // Form states
  const [newListForm, setNewListForm] = useState({ name: '', description: '' });
  const [newItemForm, setNewItemForm] = useState({
    product_name: '',
    quantity: 1,
    unit: 'each',
    category: '',
    notes: ''
  });

  const units = ['each', 'kg', 'g', 'l', 'ml', 'pack', 'dozen', '2L', '500g', '400g'];

  useEffect(() => {
    fetchShoppingLists();
    fetchSuggestions();
  }, []);

  const fetchShoppingLists = async () => {
    try {
      const response = await axios.get(`${API_BASE}/shopping-lists/`);
      setShoppingLists(response.data);
      if (response.data.length > 0 && !selectedList) {
        setSelectedList(response.data[0]);
      }
    } catch (error) {
      console.error('Error fetching shopping lists:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchSuggestions = async () => {
    try {
      const response = await axios.get(`${API_BASE}/shopping-lists/suggestions/categories`);
      setSuggestions(response.data);
    } catch (error) {
      console.error('Error fetching suggestions:', error);
    }
  };

  const createShoppingList = async (e) => {
    e.preventDefault();
    try {
      const response = await axios.post(`${API_BASE}/shopping-lists/`, newListForm);
      setShoppingLists(prev => [response.data, ...prev]);
      setSelectedList(response.data);
      setNewListForm({ name: '', description: '' });
      setShowCreateModal(false);
    } catch (error) {
      console.error('Error creating shopping list:', error);
    }
  };

  const deleteShoppingList = async (listId) => {
    if (!window.confirm('Are you sure you want to delete this shopping list?')) return;
    
    try {
      await axios.delete(`${API_BASE}/shopping-lists/${listId}`);
      setShoppingLists(prev => prev.filter(list => list.id !== listId));
      if (selectedList?.id === listId) {
        setSelectedList(shoppingLists.length > 1 ? shoppingLists[0] : null);
      }
    } catch (error) {
      console.error('Error deleting shopping list:', error);
    }
  };

  const addItemToList = async (e) => {
    e.preventDefault();
    if (!selectedList) return;

    try {
      const response = await axios.post(
        `${API_BASE}/shopping-lists/${selectedList.id}/items`,
        newItemForm
      );
      setSelectedList(response.data);
      setShoppingLists(prev => 
        prev.map(list => list.id === selectedList.id ? response.data : list)
      );
      setNewItemForm({
        product_name: '',
        quantity: 1,
        unit: 'each',
        category: '',
        notes: ''
      });
      setShowItemModal(false);
    } catch (error) {
      console.error('Error adding item to list:', error);
    }
  };

  const toggleItemCompleted = async (itemId, completed) => {
    if (!selectedList) return;

    try {
      const response = await axios.put(
        `${API_BASE}/shopping-lists/${selectedList.id}/items/${itemId}`,
        { completed }
      );
      setSelectedList(response.data);
      setShoppingLists(prev => 
        prev.map(list => list.id === selectedList.id ? response.data : list)
      );
    } catch (error) {
      console.error('Error updating item:', error);
    }
  };

  const removeItemFromList = async (itemId) => {
    if (!selectedList) return;

    try {
      const response = await axios.delete(
        `${API_BASE}/shopping-lists/${selectedList.id}/items/${itemId}`
      );
      setSelectedList(response.data);
      setShoppingLists(prev => 
        prev.map(list => list.id === selectedList.id ? response.data : list)
      );
    } catch (error) {
      console.error('Error removing item from list:', error);
    }
  };

  const handleSuggestionClick = (suggestion) => {
    setNewItemForm(prev => ({
      ...prev,
      category: suggestion.category,
      unit: suggestion.suggested_unit,
      quantity: suggestion.typical_quantity
    }));
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-green-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white shadow rounded-lg">
        <div className="px-6 py-4">
          <div className="flex items-center justify-between">
            <h1 className="text-2xl font-bold text-gray-900">Shopping Lists</h1>
            <button
              onClick={() => setShowCreateModal(true)}
              className="flex items-center px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700"
            >
              <PlusIcon className="w-5 h-5 mr-2" />
              New List
            </button>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Lists Sidebar */}
        <div className="lg:col-span-1">
          <div className="bg-white shadow rounded-lg">
            <div className="px-4 py-3 border-b border-gray-200">
              <h2 className="text-lg font-medium text-gray-900">Your Lists</h2>
            </div>
            <div className="divide-y divide-gray-200">
              {shoppingLists.length > 0 ? (
                shoppingLists.map((list) => (
                  <div
                    key={list.id}
                    className={`p-4 cursor-pointer hover:bg-gray-50 ${
                      selectedList?.id === list.id ? 'bg-green-50 border-r-2 border-green-500' : ''
                    }`}
                    onClick={() => setSelectedList(list)}
                  >
                    <div className="flex items-center justify-between">
                      <div>
                        <h3 className="font-medium text-gray-900">{list.name}</h3>
                        <p className="text-sm text-gray-500">
                          {list.items.length} item{list.items.length !== 1 ? 's' : ''}
                        </p>
                        {list.description && (
                          <p className="text-xs text-gray-400 mt-1">{list.description}</p>
                        )}
                      </div>
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          deleteShoppingList(list.id);
                        }}
                        className="text-gray-400 hover:text-red-500"
                      >
                        <TrashIcon className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                ))
              ) : (
                <div className="p-8 text-center">
                  <ListBulletIcon className="mx-auto h-12 w-12 text-gray-400" />
                  <h3 className="mt-2 text-sm font-medium text-gray-900">No shopping lists</h3>
                  <p className="mt-1 text-sm text-gray-500">Get started by creating a new list.</p>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* List Details */}
        <div className="lg:col-span-2">
          {selectedList ? (
            <div className="bg-white shadow rounded-lg">
              <div className="px-6 py-4 border-b border-gray-200">
                <div className="flex items-center justify-between">
                  <div>
                    <h2 className="text-xl font-semibold text-gray-900">{selectedList.name}</h2>
                    {selectedList.description && (
                      <p className="text-sm text-gray-500 mt-1">{selectedList.description}</p>
                    )}
                  </div>
                  <button
                    onClick={() => setShowItemModal(true)}
                    className="flex items-center px-3 py-2 bg-green-600 text-white rounded-md hover:bg-green-700"
                  >
                    <PlusIcon className="w-4 h-4 mr-1" />
                    Add Item
                  </button>
                </div>
              </div>

              <div className="p-6">
                {selectedList.items.length > 0 ? (
                  <div className="space-y-2">
                    {selectedList.items.map((item) => (
                      <div
                        key={item.id}
                        className={`flex items-center justify-between p-3 rounded-lg border ${
                          item.completed ? 'bg-gray-50 opacity-75' : 'bg-white'
                        }`}
                      >
                        <div className="flex items-center space-x-3">
                          <button
                            onClick={() => toggleItemCompleted(item.id, !item.completed)}
                            className={`flex-shrink-0 ${
                              item.completed ? 'text-green-600' : 'text-gray-400'
                            }`}
                          >
                            <CheckCircleIcon className="w-5 h-5" />
                          </button>
                          <div>
                            <p className={`font-medium ${item.completed ? 'line-through text-gray-500' : 'text-gray-900'}`}>
                              {item.product_name}
                            </p>
                            <p className="text-sm text-gray-500">
                              {item.quantity} {item.unit}
                              {item.category && ` • ${item.category}`}
                            </p>
                            {item.notes && (
                              <p className="text-xs text-gray-400">{item.notes}</p>
                            )}
                          </div>
                        </div>
                        <button
                          onClick={() => removeItemFromList(item.id)}
                          className="text-gray-400 hover:text-red-500"
                        >
                          <XCircleIcon className="w-5 h-5" />
                        </button>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-8">
                    <ListBulletIcon className="mx-auto h-12 w-12 text-gray-400" />
                    <h3 className="mt-2 text-sm font-medium text-gray-900">List is empty</h3>
                    <p className="mt-1 text-sm text-gray-500">Add items to start planning your shopping.</p>
                  </div>
                )}
              </div>
            </div>
          ) : (
            <div className="bg-white shadow rounded-lg">
              <div className="p-12 text-center">
                <ListBulletIcon className="mx-auto h-12 w-12 text-gray-400" />
                <h3 className="mt-2 text-lg font-medium text-gray-900">Select a shopping list</h3>
                <p className="mt-1 text-sm text-gray-500">
                  Choose a list from the sidebar or create a new one.
                </p>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Create List Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
          <div className="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
            <h3 className="text-lg font-bold text-gray-900 mb-4">Create New Shopping List</h3>
            <form onSubmit={createShoppingList} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700">Name</label>
                <input
                  type="text"
                  required
                  value={newListForm.name}
                  onChange={(e) => setNewListForm(prev => ({ ...prev, name: e.target.value }))}
                  className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 focus:ring-green-500 focus:border-green-500"
                  placeholder="e.g., Weekly Shopping"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Description (Optional)</label>
                <textarea
                  value={newListForm.description}
                  onChange={(e) => setNewListForm(prev => ({ ...prev, description: e.target.value }))}
                  className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 focus:ring-green-500 focus:border-green-500"
                  rows={3}
                  placeholder="Description of your shopping list"
                />
              </div>
              <div className="flex justify-end space-x-3">
                <button
                  type="button"
                  onClick={() => setShowCreateModal(false)}
                  className="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700"
                >
                  Create List
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Add Item Modal */}
      {showItemModal && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
          <div className="relative top-10 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
            <h3 className="text-lg font-bold text-gray-900 mb-4">Add Item to List</h3>
            <form onSubmit={addItemToList} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700">Product Name</label>
                <input
                  type="text"
                  required
                  value={newItemForm.product_name}
                  onChange={(e) => setNewItemForm(prev => ({ ...prev, product_name: e.target.value }))}
                  className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 focus:ring-green-500 focus:border-green-500"
                  placeholder="e.g., Milk"
                />
              </div>
              
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700">Quantity</label>
                  <input
                    type="number"
                    min="0.1"
                    step="0.1"
                    value={newItemForm.quantity}
                    onChange={(e) => setNewItemForm(prev => ({ ...prev, quantity: parseFloat(e.target.value) }))}
                    className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 focus:ring-green-500 focus:border-green-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Unit</label>
                  <select
                    value={newItemForm.unit}
                    onChange={(e) => setNewItemForm(prev => ({ ...prev, unit: e.target.value }))}
                    className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 focus:ring-green-500 focus:border-green-500"
                  >
                    {units.map(unit => (
                      <option key={unit} value={unit}>{unit}</option>
                    ))}
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700">Category (Optional)</label>
                <input
                  type="text"
                  value={newItemForm.category}
                  onChange={(e) => setNewItemForm(prev => ({ ...prev, category: e.target.value }))}
                  className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 focus:ring-green-500 focus:border-green-500"
                  placeholder="e.g., Dairy & Eggs"
                />
                {suggestions.length > 0 && (
                  <div className="mt-2">
                    <p className="text-xs text-gray-500 mb-1">Quick suggestions:</p>
                    <div className="flex flex-wrap gap-1">
                      {suggestions.slice(0, 3).map((suggestion, index) => (
                        <button
                          key={index}
                          type="button"
                          onClick={() => handleSuggestionClick(suggestion)}
                          className="px-2 py-1 text-xs bg-gray-100 text-gray-700 rounded hover:bg-gray-200"
                        >
                          {suggestion.category}
                        </button>
                      ))}
                    </div>
                  </div>
                )}
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700">Notes (Optional)</label>
                <input
                  type="text"
                  value={newItemForm.notes}
                  onChange={(e) => setNewItemForm(prev => ({ ...prev, notes: e.target.value }))}
                  className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 focus:ring-green-500 focus:border-green-500"
                  placeholder="Any special notes"
                />
              </div>

              <div className="flex justify-end space-x-3">
                <button
                  type="button"
                  onClick={() => setShowItemModal(false)}
                  className="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700"
                >
                  Add Item
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default ShoppingListsPage;