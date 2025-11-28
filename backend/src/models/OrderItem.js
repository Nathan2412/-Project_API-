const { DataTypes } = require('sequelize');
const { sequelize } = require('../db');
const Order = require('./Order');
const Product = require('./Product');

const OrderItem = sequelize.define('OrderItem', {
  id: { type: DataTypes.INTEGER, autoIncrement: true, primaryKey: true },
  order_id: { type: DataTypes.INTEGER, allowNull: false },
  product_id: { type: DataTypes.INTEGER, allowNull: false },
  quantity: { type: DataTypes.INTEGER, allowNull: false, defaultValue: 1 },
  price: { type: DataTypes.DECIMAL(10,2), allowNull: false }, // Prix unitaire au moment de la commande
}, {
  tableName: 'order_items',
  timestamps: false,
});

// Relations
OrderItem.belongsTo(Order, { foreignKey: 'order_id' });
OrderItem.belongsTo(Product, { foreignKey: 'product_id' });
Order.hasMany(OrderItem, { foreignKey: 'order_id' });

module.exports = OrderItem;
