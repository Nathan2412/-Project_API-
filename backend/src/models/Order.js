const { DataTypes } = require('sequelize');
const { sequelize } = require('../db');
const User = require('./User');

const Order = sequelize.define('Order', {
  id: { type: DataTypes.INTEGER, autoIncrement: true, primaryKey: true },
  user_id: { type: DataTypes.INTEGER, allowNull: false },
  total: { type: DataTypes.DECIMAL(10,2), allowNull: false },
  status: { type: DataTypes.STRING, allowNull: false, defaultValue: 'pending' },
}, {
  tableName: 'orders',
  timestamps: false,
});

Order.belongsTo(User, { foreignKey: 'user_id' });

module.exports = Order;
