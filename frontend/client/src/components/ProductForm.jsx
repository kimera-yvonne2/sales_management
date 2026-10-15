import React, { useState } from 'react';
import { createProduct } from '../services/api';

export default function ProductForm() {
    const [formData, setFormData] = useState({
        product_name: '', cost_price: '', selling_price: '', reorder_level: ''
    });

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            await createProduct(formData);
            alert('Product added successfully!');
        } catch (err) {
            console.error('Error adding product', err);
        }
    };

    return (
        <form onSubmit={handleSubmit} className="p-6 max-w-lg mx-auto bg-white rounded-xl shadow-md space-y-4">
            <h2 className="text-xl font-bold text-gray-800">Add New Product</h2>
            <input 
                type="text" 
                placeholder="Product Name" 
                className="w-full p-2 border rounded"
                onChange={(e) => setFormData({...formData, product_name: e.target.value})} 
            />
            <input 
                type="number" 
                placeholder="Cost Price" 
                className="w-full p-2 border rounded"
                onChange={(e) => setFormData({...formData, cost_price: e.target.value})} 
            />
            <input 
                type="number" 
                placeholder="Selling Price" 
                className="w-full p-2 border rounded"
                onChange={(e) => setFormData({...formData, selling_price: e.target.value})} 
            />
            <button type="submit" className="w-full bg-blue-600 text-white p-2 rounded hover:bg-blue-700">
                Save Product
            </button>
        </form>
    );
}