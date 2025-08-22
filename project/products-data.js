// products-data.js - Données partagées entre toutes les pages
// Pour ajouter un produit, il suffit de compléter ce tableau
// -- Options centralisées pour réutilisation --
const sauceOptions = [
  { name: "Blanche", price: 0.50, image: "images/sauce-blanche.svg" },
  { name: "Smoky", price: 0.50, image: "images/sauce-smoky.svg" },
  { name: "Chili Thaï", price: 0.50, image: "images/chili-thai.svg" },
  { name: "Mayo Truffe", price: 0.50, image: "images/mayo-truffe.svg" },
  { name: "Fromagère", price: 0.50, image: "images/fromagere.svg" },
  { name: "Mayonnaise", "price": 0, "image": "images/mayo.svg" },
  { name: "Ketchup", "price": 0, "image": "images/ketchup.svg" },
  { name: "Algérienne", "price": 0, "image": "images/algerienne.svg" },
  { name: "Biggy", "price": 0, "image": "images/biggy.svg" },
  { name: "Barbecue", "price": 0, "image": "images/bbq.svg" },
  { name: "Samouraï", "price": 0, "image": "images/samourai.svg" },
  { name: "Curry", "price": 0, "image": "images/curry.svg" },
  { name: "Andalouse", "price": 0, "image": "images/andalouse.svg" },
  { name: "Poivre", "price": 0, "image": "images/poivre.svg" },
  { name: "Marocaine", "price": 0, "image": "images/marocaine.svg" },
  { name: "Harissa", "price": 0, "image": "images/harissa.svg" },
  { "name": "Moutarde", "price": 0, "image": "images/moutarde.svg" }

];

const petitCreuxOptions = [
  { name: "Nuggets", price: 0, image: "images/nuggets.svg" },
  { name: "Potatoes", price: 0, image: "images/potatoes.svg" },
  { name: "Onion Rings", price: 0, image: "images/oignons-rings.svg" },
  { name: "Tiramisu", price: 0, image: "images/tiramisu.svg" }
];

const burgerOptions = [
  { name: "Smash Burger", price: 6.50, image: "images/smash-burger.svg" },
  { name: "Signature Burger", price: 7.90, image: "images/signature-burger.jpg" },
  { name: "Golden Burger", price: 7.50, image: "images/golden-burger.jpg" }
];

const meatOptions = [
  { name: "Poulet mariné", image: "images/poulet.svg" },
  { name: "Kefta", image: "images/kefta.svg" },
  { name: "Tenders", image: "images/tenderssupp.svg" },
  { name: "Cordon Bleu", image: "images/cordon.svg" },
  { name: "Steak haché", image: "images/steak.svg" },
  { name: "Nuggets", image: "images/nuggets.svg" },
  { name: "Kebab", image: "images/kebab.svg" }
];

const meatCounts = [
  { value: 1, label: "1 viande", price: 7.00 },
  { value: 2, label: "2 viandes", price: 8.00 },
  { value: 3, label: "3 viandes", price: 10.00 }
];
// Option centralisée pour "enlever" sur tous les burgers
const removeOptions = [
  { name: "Sans salade", price: 0 },
  { name: "Sans tomate", price: 0 },
  { name: "Sans oignon", price: 0 }
];

// D’abord, tu déclares tes smashBurgers et signatureBurgers
const smashBurgersMenuChoices = [
  { name: "Classique", price: 6.00, image: "images/classique.svg" },
  { name: "Double", price: 7.50, image: "images/double.svg" },
  { name: "Bacon", price: 7.50, image: "images/bacon.svg" },
  { name: "Double Bacon", price: 8.00, image: "images/double-bacon.svg" },
  { name: "Chicken", price: 8.00, image: "images/chicken.svg" },
  { name: "Chèvre Miel", price: 8.00, image: "images/chevre-miel.svg" },
  { name: "Fish", price: 8.00, image: "images/smash-fish.svg" },
];
const signatureBurgersMenuChoices = [
  { name: "Kuisto", price: 10.50, image: "images/kuisto.svg" },
  { name: "Pistachio", price: 12.50, image: "images/signature-pistachio.svg" },
  { name: "Grogon", price: 10.50, image: "images/signature-grogon.svg" },
  { name: "Le Veggie", price: 11.50, image: "images/signature-le-veggie.svg" },
  { name: "Chicken Truff", price: 12.50, image: "images/signature-chicken-truff.svg" },
];
// Pour le menu combo :
const allMenuBurgers = [...smashBurgersMenuChoices, ...signatureBurgersMenuChoices];

// Dans chaque objet menu (voir plus haut pour la structure)


const products = [
  // Nouveautés
   {
    id: 3,
    name: "Tacos personnalisé",
    slug: "tacos",
    category: "tacos",
    description: "Compose ton tacos : 1, 2 ou 3 viandes au choix, sauces et suppléments.",
    price: 7.00, // base = 1 viande, le reste dynamique via meatCounts
    image: "images/tacos.svg",
    options: {
      meatCounts: meatCounts,   // ← Sélection du nombre de viandes (radio)
      meats: meatOptions,       // ← Liste des viandes possibles (radio ou checkbox selon nb viandes)
      sauces: sauceOptions,     // ← Multi (checkbox)
      supplements: [
         { name: "Oeuf", price: 1.20, image: "images/oeuf.svg" },
    { name: "Chèvre", price: 1.20, image: "images/chevre.svg" },
    { name: "Champignons", price: 1.20, image: "images/champignons.svg" },
    { name: "Vache qui rit", price: 1.20, image: "images/vachequirit.svg" },
    { name: "Boursin", price: 1.20, image: "images/boursin.svg" },
    { name: "Oignons frits", price: 1.20, image: "images/oignonsfrits.svg" },
    { name: "Jambon", price: 1.20, image: "images/jambon.svg" },
    { name: "Cheddar", price: 1.20, image: "images/cheddar.svg" },
    { name: "Bacon", price: 1.20, image: "images/baconsupp.svg" }
      ],
      remove: [
        { name: "Sans oignons", price: 0 },
        { name: "Sans salade", price: 0 },
        { name: "Sans tomate", price: 0 }
      ]
    }
  },
   {
        id: 44,
        name: "Menu Tacos personnalisé",
        slug: "menu-tacos",
        category: "tacos",
        description: "Compose ton tacos : 1, 2 ou 3 viandes au choix, sauces, suppléments, Frites Maison et une boisson.",
        price: 10.00,
        image: "images/menu-tacos.svg",
        options: {
            meatCounts: meatCounts,
            meats: meatOptions,
            sauces: sauceOptions,
            supplements: [
                {"name": "Oeuf", "price": 1.20, "image": "images/oeuf.svg"},
                {"name": "Chèvre", "price": 1.20, "image": "images/chevre.svg"},
                {"name": "Champignons", "price": 1.20, "image": "images/champignons.svg"},
                {"name": "Vache qui rit", "price": 1.20, "image": "images/vachequirit.svg"},
                {"name": "Boursin", "price": 1.20, "image": "images/boursin.svg"},
                {"name": "Oignons frits", "price": 1.20, "image": "images/oignonsfrits.svg"},
                {"name": "Jambon", "price": 1.20, "image": "images/jambon.svg"},
                {"name": "Cheddar", "price": 1.20, "image": "images/cheddar.svg"},
                {"name": "Bacon", "price": 1.20, "image": "images/baconsupp.svg"}
            ],
            remove: [
                {"name": "Sans oignons", "price": 0},
                {"name": "Sans salade", "price": 0},
                {"name": "Sans tomate", "price": 0}
            ],
            drinks: [
  { name: "Coca-Cola",                     price: 0, image: "images/coca-cola.svg" },
  { name: "Coca-Cola Zéro",                price: 0, image: "images/coca-cola-zero.svg" },
  { name: "Coca-Cola Cherry",              price: 0, image: "images/coca-cola-cherry.svg" },
  { name: "Fanta Orange",                  price: 0, image: "images/fanta-orange.svg" },
  { name: "Fanta Citron",                  price: 0, image: "images/fanta-citron.svg" },
  { name: "Fanta fruit du dragon",         price: 0, image: "images/fanta-fruit-du-dragon.svg" },
  { name: "Oasis tropical",                price: 0, image: "images/oasis-tropical.svg" },
  { name: "Oasis Pomme-cassis Framboise",  price: 0, image: "images/oasis-pomme-cassis-framboise.svg" },
  { name: "Lipton Ice Tea",                price: 0, image: "images/lipton-ice-tea.svg" },
  { name: "Fuze tea",                      price: 0, image: "images/fuze-tea.svg" },
  { name: "Hawaï",                         price: 0, image: "images/hawai.svg" },
  { name: "Tropico",                       price: 0, image: "images/tropico.svg" },
  { name: "Schweppes Lemon",               price: 0, image: "images/schweppes-lemon.svg" },
  { name: "Schweppes Pomme",               price: 0, image: "images/schweppes-pomme.svg" },
  { name: "Schweppes Agrumes",             price: 0, image: "images/schweppes-agrumes.svg" },
  { name: "Sprite",                        price: 0, image: "images/sprite.svg" },
  { name: "Orangina",                      price: 0, image: "images/orangina.svg" },
  { name: "7 Up",                          price: 0, image: "images/7up.svg" },
  { name: "Perrier",                       price: 0, image: "images/perrier.svg" },
  { name: "Eau",                           price: 0, image: "images/eau.svg" }
]
        }
    },
  
  
  {
    id: 35,
    name: "Classique",
    slug: "smash-classique",
    category: "smash-burgers",
    description: "Viande hachée, cheddar, salade, tomate, oignon",
    price: 6.00,
    image: "images/classique.svg",
    options: {
      remove: removeOptions,
      sauces: sauceOptions
    }
  },
  {
    id: 36,
    name: "Double",
    slug: "smash-double",
    category: "smash-burgers",
    description: "2 steaks, double cheddar, salade, tomate, oignon",
    price: 7.50,
    image: "images/double.svg",
    options: {
      remove: removeOptions,
      sauces: sauceOptions
    }
  },
  {
    id: 37,
    name: "Bacon",
    slug: "smash-bacon",
    category: "smash-burgers",
    description: "Steak haché, bacon, cheddar, salade, tomate, oignon",
    price: 7.50,
    image: "images/bacon.svg",
    options: {
      remove: removeOptions,
      sauces: sauceOptions
    }
  },
  {
    id: 38,
    name: "Double Bacon",
    slug: "smash-double-bacon",
    category: "smash-burgers",
    description: "2 steaks, bacon, double cheddar, salade, tomate, oignon",
    price: 8.00,
    image: "images/double-bacon.svg",
    options: {
      remove: removeOptions,
      sauces: sauceOptions
    }
  },
  {
    id: 39,
    name: "Chicken",
    slug: "smash-chicken",
    category: "smash-burgers",
    description: "Tenders, cheddar, salade, tomate, oignon",
    price: 8.00,
    image: "images/chicken.svg",
    options: {
      remove: removeOptions,
      sauces: sauceOptions
    }
  },
  {
  id: 42,
  name: "BABY SMASH CHEESE",
  slug: "cheese-burger",
  category: "smash-burgers",
  description: "Portion de fromage.",
  price: 2.90,
  image: "images/baby-smash-cheese.svg",
  options: {}
},
{
  id: 43,
  name: "BABY SMASH DOUBLE CHEESE",
  slug: "double-cheese-burger",
  category: "smash-burgers",
  description: "Double portion de fromage.",
  price: 3.90,
  image: "images/double-cheese.svg",
  options: {}
},
  {
    id: 40,
    name: "Chèvre Miel",
    slug: "smash-chevre-miel",
    category: "smash-burgers",
    description: "Viande hachée, salade, fromage de chèvre, miel",
    price: 8.00,
    image: "images/chevre-miel.svg",
    options: {
      remove: removeOptions,
      sauces: sauceOptions
    }
  },
  {
    id: 41,
    name: "Fish",
    slug: "smash-fish",
    category: "smash-burgers",
    description: "Poisson pané, salade, tomate, oignon, sauce blanche",
    price: 8.00,
    image: "images/smash-fish.svg",
    options: {
      remove: removeOptions,
      sauces: sauceOptions
    }
  },
  {
    id: 4,
    name: "Kuisto",
    slug: "signature-kuisto",
    category: "burgers-signature",
    description: "Viande hachée, 2 tenders, oignons frits, cheddar, salade, ketchup",
    price: 10.50,
    image: "images/kuisto.svg",
    options: {
      remove: removeOptions,
      sauces: sauceOptions
    }
  },
  {
    id: 5,
    name: "Pistachio",
    slug: "signature-pistachio",
    category: "burgers-signature",
    description: "Viande hachée, roquette, tomates poêlées, stracciatella, pistache, parmesan",
    price: 12.50,
    image: "images/signature-pistachio.svg",
    options: {
      remove: removeOptions,
      sauces: sauceOptions
    }
  },
  {
    id: 6,
    name: "Grogon",
    slug: "signature-grogon",
    category: "burgers-signature",
    description: "Double cheese, viande hachée, onion rings, oignons frits, sauce burger, frites, cornichons",
    price: 10.50,
    image: "images/signature-grogon.svg",
    options: {
      remove: removeOptions,
      sauces: sauceOptions
    }
  },
  {
    id: 7,
    name: "Le Veggie",
    slug: "signature-le-veggie",
    category: "burgers-signature",
    description: "Steak de falafel, stracciatella, roquette, tomates poêlées, oignons, sauce blanche ciboulette",
    price: 11.50,
    image: "images/signature-le-veggie.svg",
    options: {
      remove: removeOptions,
      sauces: sauceOptions
    }
  },
  {
    id: 8,
    name: "Chicken Truff",
    slug: "signature-chicken-truff",
    category: "burgers-signature",
    description: "Tenders, oignons, champignons persillés, sauce truffe",
    price: 12.50,
    image: "images/signature-chicken-truff.svg",
    options: {
      remove: removeOptions,
      sauces: sauceOptions
    }
  },
  
  {
  id: 9,
  name: "Menu Smash Burger",
  slug: "menu-smash-burger",
  category: "menus-burgers",
  description: "Smash burger au choix, frites, boisson, sauces",
  price: 8.50, // <-- prix géré dynamiquement
  image: "images/menu-smash.svg",
  options: {
    burgerSelect: smashBurgersMenuChoices,
    sauces: sauceOptions,
    drinks: [
  { name: "Coca-Cola",                     price: 0, image: "images/coca-cola.svg" },
  { name: "Coca-Cola Zéro",                price: 0, image: "images/coca-cola-zero.svg" },
  { name: "Coca-Cola Cherry",              price: 0, image: "images/coca-cola-cherry.svg" },
  { name: "Fanta Orange",                  price: 0, image: "images/fanta-orange.svg" },
  { name: "Fanta Citron",                  price: 0, image: "images/fanta-citron.svg" },
  { name: "Fanta fruit du dragon",         price: 0, image: "images/fanta-fruit-du-dragon.svg" },
  { name: "Oasis tropical",                price: 0, image: "images/oasis-tropical.svg" },
  { name: "Oasis Pomme-cassis Framboise",  price: 0, image: "images/oasis-pomme-cassis-framboise.svg" },
  { name: "Lipton Ice Tea",                price: 0, image: "images/lipton-ice-tea.svg" },
  { name: "Fuze tea",                      price: 0, image: "images/fuze-tea.svg" },
  { name: "Hawaï",                         price: 0, image: "images/hawai.svg" },
  { name: "Tropico",                       price: 0, image: "images/tropico.svg" },
  { name: "Schweppes Lemon",               price: 0, image: "images/schweppes-lemon.svg" },
  { name: "Schweppes Pomme",               price: 0, image: "images/schweppes-pomme.svg" },
  { name: "Schweppes Agrumes",             price: 0, image: "images/schweppes-agrumes.svg" },
  { name: "Sprite",                        price: 0, image: "images/sprite.svg" },
  { name: "Orangina",                      price: 0, image: "images/orangina.svg" },
  { name: "7 Up",                          price: 0, image: "images/7up.svg" },
  { name: "Perrier",                       price: 0, image: "images/perrier.svg" },
  { name: "Eau",                           price: 0, image: "images/eau.svg" }
],
    remove: removeOptions
  }
},
{
  id: 10,
  name: "Menu Signature Burger",
  slug: "menu-signature-burger",
  category: "menus-burgers",
  description: "Burger signature au choix, frites, boisson, sauces",
  price: 13.00, // <-- prix géré dynamiquement
  image: "images/menu-signature.svg",
  options: {
    burgerSelect: signatureBurgersMenuChoices,
    sauces: sauceOptions,
    drinks: [
  { name: "Coca-Cola",                     price: 0, image: "images/coca-cola.svg" },
  { name: "Coca-Cola Zéro",                price: 0, image: "images/coca-cola-zero.svg" },
  { name: "Coca-Cola Cherry",              price: 0, image: "images/coca-cola-cherry.svg" },
  { name: "Fanta Orange",                  price: 0, image: "images/fanta-orange.svg" },
  { name: "Fanta Citron",                  price: 0, image: "images/fanta-citron.svg" },
  { name: "Fanta fruit du dragon",         price: 0, image: "images/fanta-fruit-du-dragon.svg" },
  { name: "Oasis tropical",                price: 0, image: "images/oasis-tropical.svg" },
  { name: "Oasis Pomme-cassis Framboise",  price: 0, image: "images/oasis-pomme-cassis-framboise.svg" },
  { name: "Lipton Ice Tea",                price: 0, image: "images/lipton-ice-tea.svg" },
  { name: "Fuze tea",                      price: 0, image: "images/fuze-tea.svg" },
  { name: "Hawaï",                         price: 0, image: "images/hawai.svg" },
  { name: "Tropico",                       price: 0, image: "images/tropico.svg" },
  { name: "Schweppes Lemon",               price: 0, image: "images/schweppes-lemon.svg" },
  { name: "Schweppes Pomme",               price: 0, image: "images/schweppes-pomme.svg" },
  { name: "Schweppes Agrumes",             price: 0, image: "images/schweppes-agrumes.svg" },
  { name: "Sprite",                        price: 0, image: "images/sprite.svg" },
  { name: "Orangina",                      price: 0, image: "images/orangina.svg" },
  { name: "7 Up",                          price: 0, image: "images/7up.svg" },
  { name: "Perrier",                       price: 0, image: "images/perrier.svg" },
  { name: "Eau",                           price: 0, image: "images/eau.svg" }
],
    remove: removeOptions
  }
},
{
  id: 11,
  name: "Menu Combo",
  slug: "menu-combo",
  category: "menus-burgers",
  description: "Burger au choix, frites, boisson, sauces, petit creux",
  price: 11.00, // <-- prix géré dynamiquement
  image: "images/menu-combo.svg",
  options: {
    burgerSelect: allMenuBurgers,
    petitCreuxSelect: petitCreuxOptions,
    sauces: sauceOptions,
    drinks: [
  { name: "Coca-Cola",                     price: 0, image: "images/coca-cola.svg" },
  { name: "Coca-Cola Zéro",                price: 0, image: "images/coca-cola-zero.svg" },
  { name: "Coca-Cola Cherry",              price: 0, image: "images/coca-cola-cherry.svg" },
  { name: "Fanta Orange",                  price: 0, image: "images/fanta-orange.svg" },
  { name: "Fanta Citron",                  price: 0, image: "images/fanta-citron.svg" },
  { name: "Fanta fruit du dragon",         price: 0, image: "images/fanta-fruit-du-dragon.svg" },
  { name: "Oasis tropical",                price: 0, image: "images/oasis-tropical.svg" },
  { name: "Oasis Pomme-cassis Framboise",  price: 0, image: "images/oasis-pomme-cassis-framboise.svg" },
  { name: "Lipton Ice Tea",                price: 0, image: "images/lipton-ice-tea.svg" },
  { name: "Fuze tea",                      price: 0, image: "images/fuze-tea.svg" },
  { name: "Hawaï",                         price: 0, image: "images/hawai.svg" },
  { name: "Tropico",                       price: 0, image: "images/tropico.svg" },
  { name: "Schweppes Lemon",               price: 0, image: "images/schweppes-lemon.svg" },
  { name: "Schweppes Pomme",               price: 0, image: "images/schweppes-pomme.svg" },
  { name: "Schweppes Agrumes",             price: 0, image: "images/schweppes-agrumes.svg" },
  { name: "Sprite",                        price: 0, image: "images/sprite.svg" },
  { name: "Orangina",                      price: 0, image: "images/orangina.svg" },
  { name: "7 Up",                          price: 0, image: "images/7up.svg" },
  { name: "Perrier",                       price: 0, image: "images/perrier.svg" },
  { name: "Eau",                           price: 0, image: "images/eau.svg" }
],
    remove: removeOptions
  }
},


  

  {
  id: 12,
  name: "CHICKEN POP",
  slug: "chicken-pop",
  category: "sides",
  description: "Petites bouchées de poulet croustillant.",
  price: null, // prix selon la taille
  image: "images/pop.svg",
  options: {
    sizes: [
      { name: "S (200g)", price: 3.90 },
      { name: "M (350g)", price: 5.90 },
      { name: "L (500g)", price: 7.90 }
    ]
  }
},
{
  id: 13,
  name: "STICK MOZZA",
  slug: "stick-mozza",
  category: "sides",
  description: "Bâtonnets de mozzarella panés.",
  price: null,
  image: "images/stick-mozza.svg",
  options: {
    sizes: [
      { name: "4 pièces", price: 3.50 },
      { name: "6 pièces", price: 4.50 },
      { name: "8 pièces", price: 6.50 }
    ]
  }
},
{
  id: 14,
  name: "NUGGETS",
  slug: "nuggets",
  category: "sides",
  description: "Nuggets de poulet.",
  price: null,
  image: "images/nuggets.svg",
  options: {
    sizes: [
      { name: "4 pièces", price: 3.50 },
      { name: "6 pièces", price: 4.50 },
      { name: "8 pièces", price: 6.50 }
    ]
  }
},
{
  id: 15,
  name: "B.CAMEMBERT",
  slug: "b-camembert",
  category: "sides",
  description: "Bouchées de camembert pané.",
  price: null,
  image: "images/b-camembert.svg",
  options: {
    sizes: [
      { name: "4 pièces", price: 3.50 },
      { name: "6 pièces", price: 4.50 },
      { name: "8 pièces", price: 6.50 }
    ]
  }
},
{
  id: 16,
  name: "OIGNONS RINGS",
  slug: "oignons-rings",
  category: "sides",
  description: "Rondelles d’oignons frits.",
  price: null,
  image: "images/oignons-rings.svg",
  options: {
    sizes: [
      { name: "4 pièces", price: 3.50 },
      { name: "6 pièces", price: 4.50 },
      { name: "8 pièces", price: 6.50 }
    ]
  }
},
{
  id: 17,
  name: "JALAPENOS",
  slug: "jalapenos",
  category: "sides",
  description: "Jalapeños panés et fondants.",
  price: null,
  image: "images/jalapenos.svg",
  options: {
    sizes: [
      { name: "4 pièces", price: 3.50 },
      { name: "6 pièces", price: 4.50 },
      { name: "8 pièces", price: 6.50 }
    ]
  }
},
{
  id: 18,
  name: "WINGS",
  slug: "wings",
  category: "sides",
  description: "Ailes de poulet croustillantes.",
  price: null,
  image: "images/wings.svg",
  options: {
    sizes: [
      { name: "4 pièces", price: 3.50 },
      { name: "6 pièces", price: 4.50 },
      { name: "8 pièces", price: 6.50 }
    ]
  }
},
{
  id: 19,
  name: "TENDERS",
  slug: "tenders",
  category: "sides",
  description: "Tenders de poulet.",
  price: null,
  image: "images/tenders.svg",
  options: {
    sizes: [
      { name: "4 pièces", price: 3.50 },
      { name: "6 pièces", price: 4.50 },
      { name: "8 pièces", price: 6.50 }
    ]
  }
},
{
  id: 20,
  name: "FRITES",
  slug: "frites",
  category: "sides",
  description: "Frites maison classiques.",
  price: null,
  image: "images/frites.svg",
  options: {
    sizes: [
      { name: "Petite", price: 1.50 },
      { name: "Grande", price: 3.00 }
    ]
  }
},
{
  id: 21,
  name: "FRITES CHEDDAR",
  slug: "frites-cheddar",
  category: "sides",
  description: "Frites maison nappées de cheddar.",
  price: null,
  image: "images/frites-chedar.svg",
  options: {
    sizes: [
      { name: "Petite", price: 2.50 },
      { name: "Grande", price: 3.50 }
    ]
  }
},
{
  id: 22,
  name: "FRITES CHEDDAR BACON",
  slug: "frites-cheddar-bacon",
  category: "sides",
  description: "Frites maison nappées de cheddar et bacon.",
  price: null,
  image: "images/frites-cheddar-bacon.svg",
  options: {
    sizes: [
      { name: "Petite", price: 3.00 },
      { name: "Grande", price: 4.50 }
    ]
  }
},

  
    {
  id: 23,
  name: "BUCKET DUO",
  slug: "bucket-duo",
  category: "buckets",
  description: "Bucket Duo : 16 wings ou 8 wings + 6 tenders, avec 2 frites maison, 4 sauces et 2 boissons de 33 cl. Le combo parfait à partager.",
  price: null,
  image: "images/bucket-duo.svg",
  options: {
    sizes: [
      { name: "16 wings", price: 18.00 },
      { name: "8 wings et 6 Tenders", price: 19.00 },
    ],
    drinks: [
  { name: "Coca-Cola",                     price: 0, image: "images/coca-cola.svg" },
  { name: "Coca-Cola Zéro",                price: 0, image: "images/coca-cola-zero.svg" },
  { name: "Coca-Cola Cherry",              price: 0, image: "images/coca-cola-cherry.svg" },
  { name: "Fanta Orange",                  price: 0, image: "images/fanta-orange.svg" },
  { name: "Fanta Citron",                  price: 0, image: "images/fanta-citron.svg" },
  { name: "Fanta fruit du dragon",         price: 0, image: "images/fanta-fruit-du-dragon.svg" },
  { name: "Oasis tropical",                price: 0, image: "images/oasis-tropical.svg" },
  { name: "Oasis Pomme-cassis Framboise",  price: 0, image: "images/oasis-pomme-cassis-framboise.svg" },
  { name: "Lipton Ice Tea",                price: 0, image: "images/lipton-ice-tea.svg" },
  { name: "Fuze tea",                      price: 0, image: "images/fuze-tea.svg" },
  { name: "Hawaï",                         price: 0, image: "images/hawai.svg" },
  { name: "Tropico",                       price: 0, image: "images/tropico.svg" },
  { name: "Schweppes Lemon",               price: 0, image: "images/schweppes-lemon.svg" },
  { name: "Schweppes Pomme",               price: 0, image: "images/schweppes-pomme.svg" },
  { name: "Schweppes Agrumes",             price: 0, image: "images/schweppes-agrumes.svg" },
  { name: "Sprite",                        price: 0, image: "images/sprite.svg" },
  { name: "Orangina",                      price: 0, image: "images/orangina.svg" },
  { name: "7 Up",                          price: 0, image: "images/7up.svg" },
  { name: "Perrier",                       price: 0, image: "images/perrier.svg" },
  { name: "Eau",                           price: 0, image: "images/eau.svg" }
]
  }
},
   {
  id: 24,
  name: "BUCKET FAMILY",
  slug: "bucket-family",
  category: "buckets",
  description: "Bucket Family : 28 wings ou 16 wings + 10 tenders, avec 4 frites maison, 8 sauces et boisson 1,5L. Le combo familial à partager.",
  price: null,
  image: "images/bucket-family.svg",
  options: {
    sizes: [
      { name: "28 wings", price: 32.00 },
      { name: "16 wings et 10 Tenders", price: 34.00 },
    ],
    drinks: [
  { name: "Coca-Cola",    price: 0, image: "images/coca-cola.svg" },
  { name: "Pepsi",        price: 0, image: "images/pepsi.svg" },
  { name: "Fanta orange", price: 0, image: "images/fanta-orange.svg" },
  { name: "Ice Tea",      price: 0, image: "images/lipton-ice-tea.svg" }
]
  }
},
  {
  "id": 25,
  "name": "Trompe-l’œil",
  "slug": "trompe-loeil",
  "category": "boissons-desserts",
  "description": "Trompe-l’œil : dessert signature du chef.",
  "price": 7.50,
  "image": "images/trompe-loeil.svg",
  "options": {}
},


  {
  id: 26,
  name: "Tiramisu",
  slug: "tiramisu",
  category: "boissons-desserts",
  description: "Mascarpone crémeux, Nutella, spéculoos croquant et éclats d’Oréo — le tiramisu qui fait fondre.",
  price: 3.50,
  image: "images/tiramisu.svg",
  options: {}
},
  {
  id: 27,
  name: "Boisson 33 CL",
  slug: "boisson-33cl",
  category: "boissons-desserts",
  description: "Canette de 33 cl au choix (Coca-Cola, Sprite, Fanta, etc.).",
  price: 2.00,
  image: "images/boisson-33cl.svg",
  options: {
    drinks: [
  { name: "Coca-Cola",                     price: 0, image: "images/coca-cola.svg" },
  { name: "Coca-Cola Zéro",                price: 0, image: "images/coca-cola-zero.svg" },
  { name: "Coca-Cola Cherry",              price: 0, image: "images/coca-cola-cherry.svg" },
  { name: "Fanta Orange",                  price: 0, image: "images/fanta-orange.svg" },
  { name: "Fanta Citron",                  price: 0, image: "images/fanta-citron.svg" },
  { name: "Fanta fruit du dragon",         price: 0, image: "images/fanta-fruit-du-dragon.svg" },
  { name: "Oasis tropical",                price: 0, image: "images/oasis-tropical.svg" },
  { name: "Oasis Pomme-cassis Framboise",  price: 0, image: "images/oasis-pomme-cassis-framboise.svg" },
  { name: "Lipton Ice Tea",                price: 0, image: "images/lipton-ice-tea.svg" },
  { name: "Fuze tea",                      price: 0, image: "images/fuze-tea.svg" },
  { name: "Hawaï",                         price: 0, image: "images/hawai.svg" },
  { name: "Tropico",                       price: 0, image: "images/tropico.svg" },
  { name: "Schweppes Lemon",               price: 0, image: "images/schweppes-lemon.svg" },
  { name: "Schweppes Pomme",               price: 0, image: "images/schweppes-pomme.svg" },
  { name: "Schweppes Agrumes",             price: 0, image: "images/schweppes-agrumes.svg" },
  { name: "Sprite",                        price: 0, image: "images/sprite.svg" },
  { name: "Orangina",                      price: 0, image: "images/orangina.svg" },
  { name: "7 Up",                          price: 0, image: "images/7up.svg" },
  { name: "Perrier",                       price: 0, image: "images/perrier.svg" },
  { name: "Eau",                           price: 0, image: "images/eau.svg" }
]
}
},
{
  id: 28,
  name: "Boisson 1,5 L",
  slug: "boisson-1-5l",
  category: "boissons-desserts",
  description: "Bouteille de 1,5 litre au choix.",
  price: 3.50,
  image: "images/boisson-1-5l.svg",
  options: {
    drinks: [
  { name: "Coca-Cola",    price: 0, image: "images/coca-cola.svg" },
  { name: "Pepsi",        price: 0, image: "images/pepsi.svg" },
  { name: "Fanta orange", price: 0, image: "images/fanta-orange.svg" },
  { name: "Ice Tea",      price: 0, image: "images/lipton-ice-tea.svg" }
]
  }
},
  {
  "id": 29,
  "name": "Menu Nuggets Bambino",
  "slug": "menu-nuggets-bambino",
  "category": "menus-bambino",
  "description": "5 nuggets, une portion de frites, une boisson et une compote.",
  "price": 4.90,
  "image": "images/menu-nuggets-bambino.svg",
  "options": {}
},
{
  "id": 30,
  "name": "Menu Cheeseburger Bambino",
  "slug": "menu-cheeseburger-bambino",
  "category": "menus-bambino",
  "description": "Cheeseburger, une portion de frites, une boisson et une compote.",
  "price": 4.90,
  "image": "images/menu-cheeseburger-bambino.svg",
  "options": {}
},
{
  "id": 31,
  "name": "Menu Tenders Bambino",
  "slug": "menu-tenders-bambino",
  "category": "menus-bambino",
  "description": "2 tenders, une portion de frites, une boisson et une compote.",
  "price": 4.90,
  "image": "images/menu-tenders-bambino.svg",
  "options": {}
},

  {
  id: 32,
  name: "CÉSARE",
  slug: "salade-cesare",
  category: "salades",
  description: "Tenders, salade, oignon, parmesan, croûtons, oeuf mollet, sauce césar",
  price: 9.00,
  image: "images/salade-cesare.svg",
  options: {
    remove: removeOptions,
    
  }
},
{
  id: 33,
  name: "ITALIENNE",
  slug: "salade-italienne",
  category: "salades",
  description: "Poulet grillé, stracciatella, tomates poêlées, salade, oignon, sauce blanche",
  price: 8.90,
  image: "images/salade-italienne.svg",
  options: {
    remove: removeOptions,
    
  }
},
{
  id: 34,
  name: "VEGGIE",
  slug: "salade-veggie",
  category: "salades",
  description: "Falafel, stracciatella, tomates poêlées, salade, oignon",
  price: 8.90,
  image: "images/salade-veggie.svg",
  options: {
    remove: removeOptions,
   
  }
}
];

// Fonction utilitaire pour générer un slug depuis un nom
function generateSlug(name) {
  return name
    .toLowerCase()
    .replace(/[àáâãäå]/g, 'a')
    .replace(/[èéêë]/g, 'e')
    .replace(/[ìíîï]/g, 'i')
    .replace(/[òóôõö]/g, 'o')
    .replace(/[ùúûü]/g, 'u')
    .replace(/[ç]/g, 'c')
    .replace(/[^a-z0-9\s-]/g, '')
    .replace(/\s+/g, '-')
    .replace(/-+/g, '-')
    .trim('-');
}

// Fonction pour trouver un produit par slug
function findProductBySlug(slug) {
  return products.find(product => product.slug === slug);
}

// Auto-génération des slugs si manquants (optionnel, pour la compatibilité)
products.forEach(product => {
  if (!product.slug) {
    product.slug = generateSlug(product.name);
  }
});
