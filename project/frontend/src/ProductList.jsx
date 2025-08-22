import React, { useState } from 'react';
import { Header, SectionTitle, LocationCard, Sidebar, ProductCard, Footer, MobileSidebar } from './components';
import { locations, products, categories } from './data';

export default function ProductList() {
  const [activeCategory, setActiveCategory] = useState('Nouveautés');
  const [isMobileSidebarOpen, setIsMobileSidebarOpen] = useState(false);

  const filteredProducts = products.filter(product => product.category === activeCategory);

  const handleLocationClick = () => {
    console.log('Redirection vers la page produits...');
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Header />
      
      <div className="flex">
        {/* Sidebar Desktop */}
        <div className="hidden md:block">
          <Sidebar 
            activeCategory={activeCategory} 
            onCategoryChange={setActiveCategory} 
          />
        </div>

        {/* Mobile Sidebar */}
        <MobileSidebar
          isOpen={isMobileSidebarOpen}
          onClose={() => setIsMobileSidebarOpen(false)}
          activeCategory={activeCategory}
          onCategoryChange={setActiveCategory}
        />

        {/* Main Content */}
        <main className="flex-1 p-6">
          {/* Mobile menu button */}
          <button
            onClick={() => setIsMobileSidebarOpen(true)}
            className="md:hidden mb-6 bg-kuistoOrange text-white px-4 py-2 rounded-lg"
          >
            Catégories
          </button>

          {/* Location Section */}
          <SectionTitle>NOS POINTS DE VENTE</SectionTitle>
          <div className="mb-8">
            {locations.map(location => (
              <LocationCard
                key={location.id}
                image={location.image}
                name={location.name}
                address={location.address}
                onClick={handleLocationClick}
              />
            ))}
          </div>

          {/* Products Section */}
          <SectionTitle>{activeCategory.toUpperCase()}</SectionTitle>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            {filteredProducts.map(product => (
              <ProductCard key={product.id} product={product} />
            ))}
          </div>
        </main>
      </div>

      <Footer />
    </div>
  );
}