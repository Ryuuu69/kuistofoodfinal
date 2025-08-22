import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

export default function ProductCard({ product }) {
  const navigate = useNavigate();
  const [qty, setQty] = useState(1);
  const [cartQuantity, setCartQuantity] = useState(0);

  // Mettre à jour la quantité du panier au chargement et lors des changements
  React.useEffect(() => {
    const updateCartQuantity = () => {
      if (window.cartSystem) {
        setCartQuantity(window.cartSystem.getProductQuantity(product.slug));
      }
    };

    updateCartQuantity();
    window.addEventListener('cartUpdated', updateCartQuantity);

    return () => {
      window.removeEventListener('cartUpdated', updateCartQuantity);
    };
  }, [product.slug]);

  const changeQty = delta => setQty(q => Math.max(1, q + delta));

  const handleGoToProduct = () => {
    if (product.slug) {
      navigate(`/produit/${product.slug}`);
    } else {
      console.warn('Produit sans slug:', product.name);
    }
  };

  const handleAddToCart = () => {
    if (window.cartSystem) {
      window.cartSystem.addToCart(product, 1, {
        supplements: {},
        drink: null,
        remove: {}
      });
    }
  };

  const handleDecreaseQuantity = () => {
    if (window.cartSystem) {
      window.cartSystem.decreaseQuantity(product.slug);
    }
  };

  const handleRemoveFromCart = () => {
    if (window.cartSystem) {
      window.cartSystem.removeFromCart(product.slug);
    }
  };

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

          {/* Affichage conditionnel selon l'état du panier */}
          {cartQuantity > 0 ? (
            /* Barre rouge avec contrôles de quantité */
            <div className="flex items-center bg-bigRed text-white rounded-full px-3 py-1 space-x-2">
              <button
                onClick={handleDecreaseQuantity}
                className="w-6 h-6 rounded-full flex items-center justify-center hover:bg-white hover:bg-opacity-20 transition-colors"
                title="Diminuer la quantité"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M20 12H4" />
                </svg>
              </button>
              <span className="font-bold text-sm min-w-[20px] text-center">{cartQuantity}</span>
              <button
                onClick={handleAddToCart}
                className="w-6 h-6 rounded-full flex items-center justify-center hover:bg-white hover:bg-opacity-20 transition-colors"
                title="Augmenter la quantité"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 4v16m8-8H4" />
                </svg>
              </button>
              <button
                onClick={handleRemoveFromCart}
                className="w-6 h-6 rounded-full flex items-center justify-center hover:bg-white hover:bg-opacity-20 transition-colors ml-1"
                title="Supprimer du panier"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                </svg>
              </button>
            </div>
          ) : (
            /* Bouton noir + habituel */
            <button
              onClick={handleGoToProduct}
              className="w-11 h-11 bg-black rounded-full flex items-center justify-center hover:bg-bigRed transition-colors duration-200"
            >
              <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 4v16m8-8H4" />
              </svg>
            </button>
          )}
        </div>
      </div>
    </div>
  );
}