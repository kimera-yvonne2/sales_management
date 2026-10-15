import axios from 'axios';

const API = axios.create({
    baseURL: 'http://127.0.0.1:8000/api/',
});

export const createProduct = (data) => API.post('products/', data);
export const getLowStockReport = () => API.get('reports/low-stock/');