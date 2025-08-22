import { BrowserRouter, Routes, Route } from 'react-router-dom';
import ProductList from './ProductList';
import ProductDetail from './ProductDetail';

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<ProductList />} />
      <Route path="/produit/:slug" element={<ProductDetail />} />
    </Routes>
  );
}