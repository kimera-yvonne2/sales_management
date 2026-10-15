import React, { useEffect, useState } from 'react';
import { getLowStockReport } from '../services/api';

export default function ReportsDashboard() {
    const [lowStock, setLowStock] = useState([]);

    useEffect(() => {
        getLowStockReport()
            .then(res => setLowStock(res.data))
            .catch(err => console.error(err));
    }, []);

    return (
        <div className="p-6 max-w-4xl mx-auto">
            <h2 className="text-2xl font-bold mb-4 text-red-600">Low Stock Alerts</h2>
            <table className="w-full bg-white shadow-md rounded-lg overflow-hidden">
                <thead className="bg-gray-200 text-gray-700">
                    <tr>
                        <th className="p-3 text-left">Product Name</th>
                        <th className="p-3 text-left">Quantity on Hand</th>
                        <th className="p-3 text-left">Reorder Level</th>
                        <th className="p-3 text-left">Branch</th>
                    </tr>
                </thead>
                <tbody>
                    {lowStock.map((item, index) => (
                        <tr key={index} className="border-b hover:bg-gray-50">
                            <td className="p-3">{item.product_name}</td>
                            <td className="p-3 text-red-500 font-bold">{item.quantity_on_hand}</td>
                            <td className="p-3">{item.reorder_level}</td>
                            <td className="p-3">{item.branch_name}</td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    );
}