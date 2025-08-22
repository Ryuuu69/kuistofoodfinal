import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { products } from './data';

export default function ProductDetail() {
  const { slug } = useParams();
  const navigate = useNavigate();
  const product = products.find(p => p.slug === slug);

  if (!product) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-gray-800 mb-4">Produit introuvable</h1>
          <p className="text-gray-600 mb-6">Le produit que vous recherchez n'existe pas.</p>
          <button 
            onClick={() => navigate('/')}
            className="bg-kuistoOrange text-white px-6 py-3 rounded-lg hover:bg-orange-700 transition-colors"
          >
            Retour à la liste
          </button>
        </div>
      </div>
    );
  }

  const [qty, setQty] = useState(1);
  const total = (product.price * qty).toFixed(2);

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header avec bouton retour */}
      <div className="bg-white shadow-sm">
        <div className="max-w-4xl mx-auto px-6 py-4">
          <button 
            onClick={() => navigate('/')} 
            className="flex items-center text-kuistoOrange hover:text-orange-700 transition-colors font-medium"
          >
            <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15 19l-7-7 7-7" />
            </svg>
            Retour à la liste
          </button>
        </div>
      </div>

      {/* Contenu principal */}
      <main className="max-w-4xl mx-auto px-6 py-8">
        <div className="bg-white rounded-2xl shadow-lg overflow-hidden">
          {/* Image du produit */}
          <div className="aspect-video w-full">
            <img 
              src={product.image} 
              alt={product.name} 
              className="w-full h-full object-cover"
            />
          </div>

          {/* Informations du produit */}
          <div className="p-8">
            <div className="mb-6">
              <span className="inline-block bg-kuistoOrange text-white text-xs font-semibold px-3 py-1 rounded-full mb-3">
                {product.category}
              </span>
              <h1 className="text-3xl font-bold text-gray-900 mb-4">{product.name}</h1>
              <p className="text-gray-600 text-lg leading-relaxed">{product.description}</p>
            </div>

            {/* Prix */}
            <div className="mb-8">
              <div className="flex items-baseline">
                <span className="text-3xl font-bold text-gray-900">
                  {product.price.toFixed(2).replace('.', ',')}€
                </span>
                <span className="text-gray-500 ml-2">par unité</span>
              </div>
            </div>

            {/* Options si disponibles */}
            {product.options?.length > 0 && (
              <div className="mb-8 p-6 bg-gray-50 rounded-xl">
                <h2 className="text-xl font-semibold mb-4 text-gray-900">Options disponibles</h2>
                <div className="space-y-2">
                  {product.options.map((opt, index) => (
                    <div key={index} className="flex items-center text-gray-700">
                      <svg className="w-4 h-4 text-bigRed mr-3" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                      </svg>
                      <span className="font-medium">{opt.name}</span>
                      <span className="text-gray-500 ml-2">({opt.choices?.length || 0} choix)</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Contrôles quantité et ajout au panier */}
            <div className="flex items-center justify-between p-6 bg-gray-50 rounded-xl">
              <div className="flex items-center space-x-4">
                <span className="text-gray-700 font-medium">Quantité :</span>
                <div className="flex items-center space-x-3">
                  <button 
                    onClick={() => setQty(q => Math.max(1, q - 1))} 
                    className="w-10 h-10 border-2 border-gray-300 rounded-full flex items-center justify-center hover:border-kuistoOrange hover:text-kuistoOrange transition-colors"
                  >
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M20 12H4" />
                    </svg>
                  </button>
                  <span className="text-xl font-semibold w-8 text-center">{qty}</span>
                  <button 
                    onClick={() => setQty(q => q + 1)} 
                    className="w-10 h-10 border-2 border-gray-300 rounded-full flex items-center justify-center hover:border-kuistoOrange hover:text-kuistoOrange transition-colors"
                  >
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 4v16m8-8H4" />
                    </svg>
                  </button>
                </div>
              </div>

              <button
                onClick={() => {
                  console.log('Ajouter au panier :', { 
                    productId: product.id, 
                    slug: product.slug,
                    name: product.name,
                    qty,
                    unitPrice: product.price,
                    totalPrice: parseFloat(total)
                  });
                  // Utiliser le système de panier global
                  if (window.cartSystem) {
                    window.cartSystem.addToCart(product, qty, {
                      supplements: {},
                      drink: null,
                      remove: {}
                    });
                  } else {
                    alert(`${product.name} (x${qty}) ajouté au panier !`);
                  }
                }}
                className="bg-kuistoOrange hover:bg-orange-700 text-white px-8 py-4 rounded-xl text-lg font-semibold transition-colors flex items-center space-x-2"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M3 3h2l.4 2M7 13h10l4-8H5.4m0 0L7 13m0 0l-2.5 5M7 13l2.5 5m6-5v6a2 2 0 11-4 0v-6m4 0V9a2 2 0 10-4 0v4.01" />
                </svg>
                <span>Ajouter au panier – {total.replace('.', ',')} €</span>
              </button>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}