// frontend/src/BigCheeseDetail.jsx
import React, { useState } from 'react';
import { useNavigate }     from 'react-router-dom';
import { products }        from './data';

export default function BigCheeseDetail() {
  const navigate = useNavigate();
  const product  = products.find(p => p.id === 99);
  if (!product) return <div>Produit non trouvé</div>;

  // Initialisation de l'état des sélections
  const init = {};
  product.options.forEach((opt, i) => {
    init[i] = opt.type === 'checkbox'
      ? Array(opt.choices.length).fill(0)
      : 0;
  });
  const [sel, setSel] = useState(init);

  // Handler +/– pour les checkbox
  const handleCheckbox = (g, c, delta) => {
    setSel(prev => {
      const arr = [...prev[g]];
      const max = product.options[g].max;
      arr[c] = Math.max(0, Math.min(max, arr[c] + delta));
      return { ...prev, [g]: arr };
    });
  };

  // Calcul du total
  const total = product.price + Object.entries(sel).reduce((sum, [g, val]) => {
    const opt = product.options[g];
    if (opt.type === 'checkbox') {
      return sum + val.reduce((s, v, i) => s + v * opt.choices[i].price, 0);
    }
    return sum + opt.choices[val].price;
  }, 0);

  return (
    <div className="max-w-4xl mx-auto p-6">
      <button onClick={() => navigate(-1)} className="text-gray-600 mb-4">
        ← Retour
      </button>

      <h1 className="text-3xl font-bold mb-4">{product.name}</h1>
      <img
        src={product.image}
        alt={product.name}
        className="w-full rounded-lg mb-6"
      />

      <p className="text-xl font-semibold mb-6">
        Prix de base&nbsp;: {product.price.toFixed(2)} €
      </p>

      {product.options.map((opt, g) => (
        <section key={g} className="mb-8">
          <h2 className="text-2xl font-semibold">{opt.name}</h2>
          <p className="text-sm text-gray-500 mb-2">
            Choix max : {opt.max}
          </p>
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4">
            {opt.choices.map((c, j) => (
              <div key={j} className="border rounded-lg p-4 text-center">
                <img
                  src={c.image}
                  alt={c.label}
                  className="h-24 mx-auto mb-2 rounded"
                />
                <p className="font-medium">{c.label}</p>
                {c.price > 0 && (
                  <p className="text-sm text-green-600">
                    +{c.price.toFixed(2)} €
                  </p>
                )}

                {opt.type === 'checkbox' && (
                  <div className="flex items-center justify-center space-x-3 mt-3">
                    <button
                      onClick={() => handleCheckbox(g, j, -1)}
                      className="px-2 py-1 bg-gray-200 rounded"
                    >
                      –
                    </button>
                    <span className="font-mono">{sel[g][j]}</span>
                    <button
                      onClick={() => handleCheckbox(g, j, 1)}
                      className="px-2 py-1 bg-gray-200 rounded"
                    >
                      +
                    </button>
                  </div>
                )}

                {opt.type === 'radio' && (
                  <label className="block mt-3">
                    <input
                      type="radio"
                      name={`opt-${g}`}
                      checked={sel[g] === j}
                      onChange={() =>
                        setSel(prev => ({ ...prev, [g]: j }))
                      }
                      className="mr-2"
                    />
                    Sélectionner
                  </label>
                )}

                {opt.type === 'select' && j === 0 && (
                  <select
                    value={sel[g]}
                    onChange={e =>
                      setSel(prev => ({ ...prev, [g]: +e.target.value }))
                    }
                    className="mt-3 w-full border rounded p-2"
                  >
                    {opt.choices.map((c2, ii) => (
                      <option key={ii} value={ii}>
                        {c2.label}
                        {c2.price > 0 ? ` (+${c2.price.toFixed(2)} €)` : ''}
                      </option>
                    ))}
                  </select>
                )}
              </div>
            ))}
          </div>
        </section>
      ))}

      <button
        onClick={() =>
          console.log('Ajout au panier :', {
            productId: product.id,
            selections: sel,
          })
        }
        className="mt-6 w-full bg-blue-600 hover:bg-blue-700 text-white py-3 rounded-lg text-lg transition"
      >
        Ajouter au panier – Total {total.toFixed(2)} €
      </button>
    </div>
  );
}
