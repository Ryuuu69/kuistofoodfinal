// cart-system.js - Système de panier partagé (à inclure sur toutes les pages)

class CartSystem {
  constructor() {
    this.cart = this.loadCart();
  }

  init() {
    this.createCartBar();
    this.updateCartDisplay();

    // Synchronisation inter-onglets
    window.addEventListener('storage', (e) => {
      if (e.key === 'bigsmash_cart') {
        this.cart = this.loadCart();
        this.updateCartDisplay();
      }
    });

    // Clique sur la barre panier -> page panier
    document.addEventListener('DOMContentLoaded', () => {
      const cartBar = document.getElementById('cart-bar');
      if (cartBar) {
        cartBar.onclick = () => window.location.href = 'panier.html';
      }
    });
  }

  loadCart() {
    try {
      const saved = localStorage.getItem('bigsmash_cart');
      return saved ? JSON.parse(saved) : [];
    } catch (e) {
      console.error('Erreur lors du chargement du panier:', e);
      return [];
    }
  }

  saveCart() {
    try {
      localStorage.setItem('bigsmash_cart', JSON.stringify(this.cart));
      this.updateCartDisplay();
      window.dispatchEvent(new CustomEvent('cartUpdated'));
    } catch (e) {
      console.error('Erreur lors de la sauvegarde du panier:', e);
    }
  }

  /**
   * Calcule le prix d'un item.
   * - basePriceOverride (si fourni) prime sur tout (utile pour menus burger ou tailles spéciales)
   * - sinon: base = product.price, ou options.size.price si présent
   * - ajoute: suppléments, sauces payantes, boisson payante, petit creux payant
   */
  calculateItemPrice(product, quantity, options, basePriceOverride = null) {
    const baseFromProduct = (product && typeof product.price === 'number') ? product.price : 0;

    // Base: override > taille > produit
    let basePrice = 0;
    if (basePriceOverride != null) {
      basePrice = Number(basePriceOverride) || 0;
    } else if (options && options.size && typeof options.size.price === 'number') {
      basePrice = Number(options.size.price) || 0;
    } else {
      basePrice = Number(baseFromProduct) || 0;
    }

    // Prix de ligne (base * qty)
    let price = basePrice * (Number(quantity) || 1);

    // Suppléments
    if (options && options.supplements) {
      Object.values(options.supplements).forEach(supp => {
        const p = Number(supp.price || 0);
        const q = Number(supp.quantity || 0);
        if (q > 0 && p > 0) price += p * q * (Number(quantity) || 1);
      });
    }

    // Sauces payantes
    if (options && options.sauces) {
      Object.values(options.sauces).forEach(sauce => {
        const p = Number(sauce.price || 0);
        if (p > 0) price += p * (Number(quantity) || 1);
      });
    }

    // Boisson payante
    if (options && options.drink && Number(options.drink.price) > 0) {
      price += Number(options.drink.price) * (Number(quantity) || 1);
    }

    // Petit creux payant
    if (options && options.petitCreux && Number(options.petitCreux.price) > 0) {
      price += Number(options.petitCreux.price) * (Number(quantity) || 1);
    }

    return price;
  }

  addToCart(product, quantity = 1, options = {}, basePrice = null) {
    // basePrice vient déjà de ta page produit (ex: burger choisi + supplément menu, ou taille)
    const realBasePrice = (basePrice !== null && basePrice !== undefined) ? basePrice : product.price;

    const cartItem = {
      id: product.id,
      name: product.name,
      slug: product.slug,
      basePrice: realBasePrice, // on garde la base de la ligne pour les recalculs +
      quantity: Number(quantity) || 1,
      options: options,
      totalPrice: this.calculateItemPrice(product, quantity, options, realBasePrice),
      addedAt: new Date().toISOString()
    };

    // Regrouper par produit + mêmes options
    const existingIndex = this.cart.findIndex(item =>
      item.id === product.id && JSON.stringify(item.options) === JSON.stringify(options)
    );

    if (existingIndex > -1) {
      this.cart[existingIndex].quantity += Number(quantity) || 1;
      // recalcul avec base de la ligne existante
      this.cart[existingIndex].totalPrice = this.calculateItemPrice(
        null,
        this.cart[existingIndex].quantity,
        this.cart[existingIndex].options,
        this.cart[existingIndex].basePrice
      );
    } else {
      this.cart.push(cartItem);
    }

    this.saveCart();
    window.location.href = "produits.html";
  }

  getTotalItems() {
    return this.cart.reduce((total, item) => total + (Number(item.quantity) || 1), 0);
  }

  getTotalPrice() {
    // On pourrait sommer item.totalPrice directement,
    // mais on recalcule en s'assurant que la base de ligne est respectée (sécurité).
    return this.cart.reduce((total, item) => {
      const line = this.calculateItemPrice(
        null,
        item.quantity,
        item.options,
        item.basePrice
      );
      // on synchronise le cache totalPrice si diffère (optionnel)
      if (Math.abs((item.totalPrice || 0) - line) > 0.001) item.totalPrice = line;
      return total + line;
    }, 0);
  }

  getTotalQuantityForProduct(slug) {
    return this.cart
      .filter(item => item.slug === slug)
      .reduce((total, item) => total + (Number(item.quantity) || 1), 0);
  }

  removeLastVariantOfProduct(slug) {
    const candidates = this.cart.filter(item => item.slug === slug);
    if (candidates.length === 0) return;

    let last = candidates[0];
    for (const item of candidates) {
      if (item.addedAt > last.addedAt) last = item;
    }
    const index = this.cart.indexOf(last);

    if (last.quantity > 1) {
      last.quantity--;
      last.totalPrice = this.calculateItemPrice(
        null,
        last.quantity,
        last.options,
        last.basePrice
      );
    } else {
      this.cart.splice(index, 1);
    }
    this.saveCart();
  }

  getProductQuantity(productSlug) {
    const item = this.cart.find(item => item.slug === productSlug);
    return item ? (Number(item.quantity) || 0) : 0;
  }

  createCartBar() {
    if (document.getElementById('cart-bar')) return;

    const cartBar = document.createElement('div');
    cartBar.id = 'cart-bar';
    cartBar.className = 'cart-bar';
    cartBar.innerHTML = `
      <div class="cart-content">
        <span class="cart-icon">🛒</span>
        <span class="cart-text">
          <span id="cart-count">0</span> article(s) —
          <span id="cart-price">0,00 €</span>
        </span>
      </div>
    `;

    // Styles inline
    cartBar.style.cssText = `
      position: fixed;
      bottom: 20px;
      right: 20px;
      background: #191919;
      color: white;
      padding: 12px 20px;
      border-radius: 25px;
      cursor: pointer;
      z-index: 1000;
      box-shadow: 0 4px 20px rgba(0,0,0,0.3);
      transition: all 0.3s ease;
      font-family: 'Montserrat', sans-serif;
      font-size: 14px;
      font-weight: 600;
      display: none;
    `;

    cartBar.addEventListener('click', () => {
      window.location.href = 'panier.html';
    });
    cartBar.addEventListener('mouseenter', () => {
      cartBar.style.background = '#F18701';
      cartBar.style.transform = 'translateY(-2px)';
    });
    cartBar.addEventListener('mouseleave', () => {
      cartBar.style.background = '#191919';
      cartBar.style.transform = 'translateY(0)';
    });

    document.body.appendChild(cartBar);
  }

  updateCartDisplay() {
    const cartBar = document.getElementById('cart-bar');
    const cartCount = document.getElementById('cart-count');
    const cartPrice = document.getElementById('cart-price');
    if (!cartBar || !cartCount || !cartPrice) return;

    const totalItems = this.getTotalItems();
    const totalPrice = this.getTotalPrice();

    cartCount.textContent = totalItems;
    cartPrice.textContent = totalPrice.toFixed(2).replace('.', ',') + ' €';
    cartBar.style.display = totalItems > 0 ? 'block' : 'none';
  }

  clearCart() {
    this.cart = [];
    this.saveCart();
  }

  removeFromCart(productSlug) {
    this.cart = this.cart.filter(item => item.slug !== productSlug);
    this.saveCart();
  }

  decreaseQuantity(productSlug) {
    const itemIndex = this.cart.findIndex(item => item.slug === productSlug);
    if (itemIndex > -1) {
      const it = this.cart[itemIndex];
      if (it.quantity > 1) {
        it.quantity--;
        it.totalPrice = this.calculateItemPrice(
          null,
          it.quantity,
          it.options,
          it.basePrice
        );
      } else {
        this.cart.splice(itemIndex, 1);
      }
      this.saveCart();
    }
  }

  increaseQuantity(productSlug) {
    const itemIndex = this.cart.findIndex(item => item.slug === productSlug);
    if (itemIndex > -1) {
      const it = this.cart[itemIndex];
      it.quantity++;
      it.totalPrice = this.calculateItemPrice(
        null,
        it.quantity,
        it.options,
        it.basePrice
      );
      this.saveCart();
    }
  }
}

// Expose global + init
window.cartSystem = new CartSystem();
window.cartSystem.init();
