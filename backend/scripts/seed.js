require('dotenv').config();
const { sequelize } = require('../src/db');
const Product = require('../src/models/Product');

async function run() {
  try {
    console.log('Connecting to DB...');
    await sequelize.authenticate();
    console.log('Connected. Seeding products...');

    const existing = await Product.count();
    if (existing > 0) {
      console.log(`Products already present (${existing}), skipping seed.`);
      process.exit(0);
    }

    const products = [
      { name: 'Smartphone X', description: '5G, OLED 6.1"', price: 699.99, stock: 25 },
      { name: 'Laptop Pro', description: '16GB RAM, 512GB SSD', price: 1299.00, stock: 12 },
      { name: 'Wireless Earbuds', description: 'ANC, Bluetooth 5.3', price: 149.90, stock: 100 },
      { name: 'Gaming Mouse', description: 'RGB, 16000 DPI', price: 59.50, stock: 60 },
      { name: 'USB-C Charger 65W', description: 'GaN fast charging', price: 39.99, stock: 80 }
    ];

    await Product.bulkCreate(products);
    console.log('Seed complete.');
    process.exit(0);
  } catch (e) {
    console.error('Seed failed:', e.message);
    process.exit(1);
  }
}

run();
