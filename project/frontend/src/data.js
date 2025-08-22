// Données mockées pour BigSmash - réplique pixel-perfect

export const categories = [
  'Nouveautés',
  'Kuisto Salades', 
  'Kuisto Burgers',
  'Menus Burger',
  'Extras',
  'Boissons',
  'Desserts'
];

export const locations = [
  {
    id: 'montpellier',
    name: 'MONTPELLIER',
    address: '121 Av. de Palavas, 34000 Montpellier',
    hasClickCollect: true,
    image: 'https://images.unsplash.com/photo-1568901346375-23c9450c58cd?w=128&h=96&fit=crop&crop=center'
  }
];

export const products = [
  // Nouveautés
  {
    id: 1,
    category: 'Nouveautés',
    name: 'KUISTO SALADES',
    description: 'Kuisto Caesar, Salade fraîche, tendres croutons, tomates cerises, copeaux de parmesan.',
    price: 9.90,
    slug: 'kuisto-salades',
    image: 'https://images.unsplash.com/photo-1512621776951-a57141f2eefd?w=300&h=300&fit=crop&crop=center'
  },
  {
    id: 2,
    category: 'Nouveautés', 
    name: 'THÉ & LIMONADE',
    description: 'Thé Blanc Natural, thé blanc purée d\'ananas d\'Orée, abricot, sans sucre',
    price: 2.90,
    slug: 'the-limonade',
    image: 'https://images.unsplash.com/photo-1544145945-f90425340c7e?w=300&h=300&fit=crop&crop=center'
  },
  {
    id: 3,
    category: 'Nouveautés',
    name: 'PISTACHIO',
    description: 'Milkshake au Sundae 7.4 kg de châtaib',
    price: 3.95,
    slug: 'pistachio',
    image: 'https://images.unsplash.com/photo-1579952363873-27d3bfad9c0d?w=300&h=300&fit=crop&crop=center'
  },
  {
    id: 4,
    category: 'Nouveautés',
    name: 'MENU KUISTO CHEESE',
    description: 'Potato bun, double steak haché smashé, oignons frais, pickles, salade double cheddar',
    price: 11.90,
    slug: 'menu-kuisto-cheese-nouveau',
    image: 'https://images.unsplash.com/photo-1568901346375-23c9450c58cd?w=300&h=300&fit=crop&crop=center'
  },
  {
    id: 5,
    category: 'Nouveautés',
    name: 'MENU SURF & TURF',
    description: 'Potato bun, steak haché smashé, crevettes panées, graine de sésame, cheddar',
    price: 11.90,
    slug: 'menu-surf-turf',
    image: 'https://images.unsplash.com/photo-1571091718767-18b5b1457add?w=300&h=300&fit=crop&crop=center'
  },
  {
    id: 6,
    category: 'Nouveautés',
    name: 'TACO SMASH',
    description: 'Choisissez deux Taco (classique ou épicé)',
    price: 7.90,
    slug: 'taco-smash',
    image: 'https://images.unsplash.com/photo-1565299624946-b28f40a0ca4b?w=300&h=300&fit=crop&crop=center'
  },

  // Big Burgers
  {
    id: 7,
    category: 'Kuisto Burgers',
    name: 'KUISTO CHEESE',
    description: 'Potato bun, double steak haché smashé, salade iceberg, pickles, oignons',
    price: 8.90,
    slug: 'kuisto-cheese',
    image: 'https://images.unsplash.com/photo-1568901346375-23c9450c58cd?w=300&h=300&fit=crop&crop=center'
  },
  {
    id: 8,
    category: 'Kuisto Burgers',
    name: 'SURF & TURF',
    description: 'Potato bun, steak haché smashé, crevettes panées, graine de sésame, cheddar',
    price: 8.90,
    slug: 'surf-turf',
    image: 'https://images.unsplash.com/photo-1571091718767-18b5b1457add?w=300&h=300&fit=crop&crop=center'
  },
  {
    id: 9,
    category: 'Kuisto Burgers',
    name: 'KUISTO SMASH',
    description: 'Pain Burger, 2 steaks smashés, 2 tranches de cheddar, pickles, salade',
    price: 6.90,
    slug: 'kuisto-smash',
    image: 'https://images.unsplash.com/photo-1594212699903-ec8a3eca50f5?w=300&h=300&fit=crop&crop=center'
  },

  // Big Salades
  {
    id: 10,
    category: 'Kuisto Salades',
    name: 'KUISTO CAESAR',
    description: 'Salade fraîche, tendres croutons, tomates cerises, copeaux de parmesan',
    price: 8.90,
    slug: 'kuisto-caesar',
    image: 'https://images.unsplash.com/photo-1512621776951-a57141f2eefd?w=300&h=300&fit=crop&crop=center'
  },

  // Menus Burger
  {
    id: 11,
    category: 'Menus Burger',
    slug: 'menu-kuisto-cheese',
    name: 'MENU KUISTO CHEESE',
    description: 'Potato bun, double steak haché smashé, oignons frais, pickles, salade double cheddar + frites + boisson',
    price: 11.90,
    image: 'https://images.unsplash.com/photo-1568901346375-23c9450c58cd?w=300&h=300&fit=crop&crop=center'
  },

  // Extras
  {
    id: 12,
    category: 'Extras',
    name: 'FRITES MAISON',
    description: 'Frites fraîches coupées maison',
    slug: 'frites-maison',
    price: 3.50,
    image: 'https://images.unsplash.com/photo-1573080496219-bb080dd4f877?w=300&h=300&fit=crop&crop=center'
  },

  // Boissons
  {
    id: 13,
    category: 'Boissons',
    name: 'COCA-COLA 33CL',
    description: 'Boisson gazeuse rafraîchissante',
    slug: 'coca-cola-33cl',
    price: 2.90,
    image: 'https://images.unsplash.com/photo-1544145945-f90425340c7e?w=300&h=300&fit=crop&crop=center'
  },

  // Desserts
  {
    id: 14,
    category: 'Desserts',
    name: 'MILKSHAKE VANILLE',
    description: 'Milkshake onctueux à la vanille',
    slug: 'milkshake-vanille',
    price: 4.50,
    image: 'https://images.unsplash.com/photo-1579952363873-27d3bfad9c0d?w=300&h=300&fit=crop&crop=center'
  },
  {
    id: 99,
    category: 'Menus Burger',
    name: 'MENU KUISTO CHEESE',
    description: 'Potato bun, double steak haché smashé, oignons frais, pickles, salade double cheddar + frites + boisson',
    price: 11.90,
    image: 'https://images.unsplash.com/photo-1568901346375-23c9450c58cd?w=300&h=300&fit=crop&crop=center',
    slug: 'menu-kuisto-cheese-options',
    options: [
      {
        name: 'Supplément',
        type: 'checkbox',
        max: 4,
        choices: [
          { label: 'Cheddar', price: 1.00, image: '/images/cheddar.jpg' },
          { label: 'Steak extra', price: 2.50, image: '/images/steak.jpg' },
        ],
      },
      {
        name: 'Retirer quelque chose',
        type: 'checkbox',
        max: 5,
        choices: [
          { label: 'Sans cheddar', price: 0.00, image: '/images/sans-cheddar.jpg' },
          { label: 'Sans oignons', price: 0.00, image: '/images/sans-oignons.jpg' },
          { label: 'Sans salade iceberg', price: 0.00, image: '/images/sans-salade.jpg' },
          { label: 'Sans sauce', price: 0.00, image: '/images/sans-sauce.jpg' },
          { label: 'Sans pickles', price: 0.00, image: '/images/sans-pickles.jpg' },
        ],
      },
      {
        name: 'Boisson',
        type: 'radio',
        max: 1,
        choices: [
          { label: 'Milkshake', price: 2.00, image: '/images/milkshake.jpg' },
          { label: 'Coca Cola', price: 1.00, image: '/images/coca.jpg' },
          { label: 'Limonade', price: 0.50, image: '/images/limonade.jpg' },
        ],
      },
    ],
  },
];