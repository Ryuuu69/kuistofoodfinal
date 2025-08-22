// frontend/src/components.js – version corrigée

import React, { useState } from 'react';
import { useNavigate }      from 'react-router-dom';
import { categories }       from './data'; // seuls les "categories" sont utilisés ici

/* --------------------------------------------------
   1. HEADER + HERO
-------------------------------------------------- */
export const Header = () => (
  <header className="bg-bigRed">
    {/* barre logo 88 px */}
    <div className="h-[88px] flex items-center px-4">
      <div className="bg-red-700 rounded-lg p-3 shadow-lg">
        <div className="text-white font-bold">
          <div className="text-sm leading-none">BIG</div>
          <div className="text-base leading-none -mt-0.5">SMASH</div>
        </div>
      </div>
    </div>

    {/* hero */}
    <div className="relative flex h-[219px]">
      <div className="flex flex-1 bg-bigRed items-center justify-center">
        <h1 className="font-montserrat font-extrabold text-white text-[32px] leading-[40px] text-center max-w-[340px]">
          THE BEST SMASH <br /> BURGER ARE MADE <span className="italic">HERE</span>
        </h1>
      </div>

      <img
        src="https://images.unsplash.com/photo-1568901346375-23c9450c58cd?w=600&h=400&fit=crop&crop=center"
        alt="Burger"
        className="flex-1 object-cover object-center"
      />

      <div className="pointer-events-none absolute inset-x-0 bottom-0 h-4 bg-gradient-to-b from-transparent to-black/10" />
    </div>
  </header>
);

/* --------------------------------------------------
   2. SECTION TITLE
-------------------------------------------------- */
export const SectionTitle = ({ children }) => (
  <h2 className="flex items-center gap-3 mb-6 font-montserrat font-medium text-[16px] leading-6 text-black">
    {children}
    <span className="flex-1 h-px bg-gray-300" />
  </h2>
);

/* --------------------------------------------------
   3. LOCATION CARD
-------------------------------------------------- */
export const LocationCard = ({ image, name, address, onClick }) => (
  <div className="store-card" onClick={onClick}>
    <img src={image} alt="store" className="w-[128px] h-[96px] object-cover rounded-md shrink-0" />

    <div>
      <p className="font-montserrat text-[14px] leading-[16px] text-black">{name}</p>
      <p className="font-montserrat text-[14px] leading-[21px] text-[#808080]">{address}</p>
      <p className="font-montserrat text-[14px] leading-[21px] text-[#008000]">✓ Click & Collect</p>
    </div>

    <a
      href="#"
      className="card-arrow"
      aria-label="Accéder à la fiche du restaurant"
      onClick={e => {
        e.preventDefault();
        onClick();
      }}
    >
      <svg viewBox="0 0 24 24" className="icon">
        <line x1="5" y1="12" x2="19" y2="12" />
        <polyline points="12 5 19 12 12 19" />
      </svg>
    </a>
  </div>
);

/* --------------------------------------------------
   4. SIDEBAR CATÉGORIES
-------------------------------------------------- */
export const Sidebar = ({ activeCategory, onCategoryChange }) => (
  <div className="w-64 bg-white border-r border-gray-200 h-screen sticky top-0">
    <div className="p-4">
      {categories.map(cat => (
        <button
          key={cat}
          onClick={() => onCategoryChange(cat)}
          className={`w-full text-left py-3 px-4 text-sm font-semibold transition-colors ${
            activeCategory === cat ? 'bg-bigRed text-white' : 'text-gray-700 hover:bg-gray-100'} rounded-full`}
        >
          {cat}
        </button>
      ))}
    </div>
  </div>
);

/* --------------------------------------------------
   5. PRODUCT CARD
-------------------------------------------------- */
export const ProductCard = ({ product }) => {
  const navigate = useNavigate();
  const [qty, setQty] = useState(1);

  const changeQty = delta => setQty(q => Math.max(1, q + delta));

  return (
    <div className="bg-white rounded-lg shadow-sm hover:-translate-y-1 hover:shadow-lg transition-all duration-200 overflow-hidden">
      <div className="aspect-square w-full">
        <img src={product.image} alt={product.name} className="w-full h-full object-cover" />
      </div>

      <div className="p-4">
        <h3 className="font-montserrat text-sm text-black mb-2 line-clamp-2">{product.name}</h3>
        <p className="font-montserrat text-xs text-gray-500 mb-3 line-clamp-3">{product.description}</p>
        <p className="font-montserrat font-bold text-sm text-black mb-4">À partir de {product.price.toFixed(2).replace('.', ',')}€</p>

        <div className="flex items-center justify-between">
          {/* contrôles quantité */}
          <div className="flex items-center space-x-2">
            <button onClick={() => changeQty(-1)} className="w-7 h-7 border rounded-full flex items-center justify-center hover:bg-gray-100">
              –
            </button>
            <span className="w-6 text-center text-sm font-medium">{qty}</span>
            <button onClick={() => changeQty(1)} className="w-7 h-7 border rounded-full flex items-center justify-center hover:bg-gray-100">
              +
            </button>
          </div>

          {/* bouton + -> page détail générique */}
          <button
            onClick={() => {
              console.log('CLICK', product.slug);   // ← 1 ligne de debug
              navigate(`/produit/${product.slug}`);
            }}
            className="w-11 h-11 bg-black rounded-full flex items-center justify-center"
          >
            <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 4v16m8-8H4" />
            </svg>
          </button>
        </div>
      </div>
    </div>
  );
};

/* --------------------------------------------------
   6. FOOTER (icônes flottantes)
-------------------------------------------------- */
export const Footer = () => (
  <div className="fixed bottom-4 left-4 z-50">
    <div className="flex space-x-3">
      {['M10 20v-6h4v6h5v-8h3L12 3 2 12h3v8z', 'M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z'].map((d, i) => (
        <button
          key={i}
          className="w-12 h-12 bg-bigRed text-white hover:bg-white hover:text-bigRed rounded-full flex items-center justify-center transition-colors duration-200 shadow-lg"
        >
          <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 24 24">
            <path d={d} />
          </svg>
        </button>
      ))}
    </div>
  </div>
);

/* --------------------------------------------------
   7. MOBILE SIDEBAR DRAWER
-------------------------------------------------- */
export const MobileSidebar = ({ isOpen, onClose, activeCategory, onCategoryChange }) => {
  if (!isOpen) return null;
  return (
    <div className="fixed inset-0 z-50">
      <div className="absolute inset-0 bg-black/50" onClick={onClose}></div>
      <div className="absolute left-0 top-0 h-full w-64 bg-white shadow-lg p-4">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-lg font-semibold">Catégories</h2>
          <button onClick={onClose} className="w-8 h-8 flex items-center justify-center">✕</button>
        </div>
        {categories.map(cat => (
          <button
            key={cat}
            onClick={() => {
              onCategoryChange(cat);
              onClose();
            }}
            className={`w-full text-left py-3 px-4 text-sm font-semibold transition-colors ${
              activeCategory === cat ? 'bg-bigRed text-white' : 'text-gray-700 hover:bg-gray-100'} rounded-full`}
          >
            {cat}
          </button>
        ))}
      </div>
    </div>
  );
};
