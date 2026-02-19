const { Order, OrderItem, Customer, Product } = require('../models');
const { sequelize } = require('../config/database');

// Create order
const createOrder = async (req, res) => {
  const transaction = await sequelize.transaction();
  try {
    const { customerId, items } = req.body;

    // Verify customer exists
    const customer = await Customer.findByPk(customerId);
    if (!customer) {
      await transaction.rollback();
      return res.status(404).json({ success: false, error: 'Customer not found' });
    }

    // Calculate total and validate products
    let totalAmount = 0;
    const orderItems = [];

    for (const item of items) {
      const product = await Product.findByPk(item.productId);
      if (!product) {
        await transaction.rollback();
        return res.status(404).json({ success: false, error: `Product ${item.productId} not found` });
      }
      if (product.stock < item.quantity) {
        await transaction.rollback();
        return res.status(400).json({ success: false, error: `Insufficient stock for ${product.name}` });
      }

      const itemTotal = parseFloat(product.price) * item.quantity;
      totalAmount += itemTotal;
      orderItems.push({
        productId: item.productId,
        quantity: item.quantity,
        price: product.price
      });

      // Reduce stock
      await product.update({ stock: product.stock - item.quantity }, { transaction });
    }

    // Create order
    const order = await Order.create({ customerId, totalAmount }, { transaction });

    // Create order items
    for (const item of orderItems) {
      await OrderItem.create({ ...item, orderId: order.id }, { transaction });
    }

    await transaction.commit();

    // Fetch complete order with relations
    const completeOrder = await Order.findByPk(order.id, {
      include: [
        { model: Customer, as: 'customer' },
        { model: OrderItem, as: 'items', include: [{ model: Product, as: 'product' }] }
      ]
    });

    res.status(201).json({ success: true, data: completeOrder });
  } catch (error) {
    await transaction.rollback();
    res.status(400).json({ success: false, error: error.message });
  }
};

// Get all orders
const getAllOrders = async (req, res) => {
  try {
    const orders = await Order.findAll({
      include: [
        { model: Customer, as: 'customer' },
        { model: OrderItem, as: 'items', include: [{ model: Product, as: 'product' }] }
      ]
    });
    res.status(200).json({ success: true, data: orders });
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
};

// Get order by ID
const getOrderById = async (req, res) => {
  try {
    const order = await Order.findByPk(req.params.id, {
      include: [
        { model: Customer, as: 'customer' },
        { model: OrderItem, as: 'items', include: [{ model: Product, as: 'product' }] }
      ]
    });
    if (!order) {
      return res.status(404).json({ success: false, error: 'Order not found' });
    }
    res.status(200).json({ success: true, data: order });
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
};

// Get orders by customer
const getOrdersByCustomer = async (req, res) => {
  try {
    const orders = await Order.findAll({
      where: { customerId: req.params.customerId },
      include: [
        { model: Customer, as: 'customer' },
        { model: OrderItem, as: 'items', include: [{ model: Product, as: 'product' }] }
      ]
    });
    res.status(200).json({ success: true, data: orders });
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
};

// Update order status
const updateOrderStatus = async (req, res) => {
  try {
    const order = await Order.findByPk(req.params.id);
    if (!order) {
      return res.status(404).json({ success: false, error: 'Order not found' });
    }
    const { status } = req.body;
    await order.update({ status });
    res.status(200).json({ success: true, data: order });
  } catch (error) {
    res.status(400).json({ success: false, error: error.message });
  }
};

// Delete order
const deleteOrder = async (req, res) => {
  const transaction = await sequelize.transaction();
  try {
    const order = await Order.findByPk(req.params.id, {
      include: [{ model: OrderItem, as: 'items' }]
    });
    if (!order) {
      await transaction.rollback();
      return res.status(404).json({ success: false, error: 'Order not found' });
    }

    // Restore product stock
    for (const item of order.items) {
      const product = await Product.findByPk(item.productId);
      if (product) {
        await product.update({ stock: product.stock + item.quantity }, { transaction });
      }
    }

    // Delete order items first
    await OrderItem.destroy({ where: { orderId: order.id }, transaction });

    // Delete order
    await order.destroy({ transaction });

    await transaction.commit();
    res.status(200).json({ success: true, message: 'Order deleted successfully' });
  } catch (error) {
    await transaction.rollback();
    res.status(500).json({ success: false, error: error.message });
  }
};

// Quick create order with just customerId and productId
const quickCreateOrder = async (req, res) => {
  const transaction = await sequelize.transaction();
  try {
    const customerId = req.params.customerId;
    const { product_id } = req.body;

    const customer = await Customer.findByPk(customerId);
    if (!customer) {
      await transaction.rollback();
      return res.status(404).json({ success: false, error: 'Customer not found' });
    }

    const product = await Product.findByPk(product_id);
    if (!product) {
      await transaction.rollback();
      return res.status(404).json({ success: false, error: 'Product not found' });
    }

    if (product.stock < 1) {
      await transaction.rollback();
      return res.status(400).json({ success: false, error: `Insufficient stock for ${product.name}` });
    }

    const totalAmount = parseFloat(product.price);

    // Reduce stock
    await product.update({ stock: product.stock - 1 }, { transaction });

    // Create order
    const order = await Order.create({ customerId, totalAmount }, { transaction });

    // Create order item
    await OrderItem.create({ orderId: order.id, productId: product_id, quantity: 1, price: product.price }, { transaction });

    await transaction.commit();

    const completeOrder = await Order.findByPk(order.id, {
      include: [
        { model: Customer, as: 'customer' },
        { model: OrderItem, as: 'items', include: [{ model: Product, as: 'product' }] }
      ]
    });
    console.log('completeOrder', completeOrder)
    res.status(201).json({ success: true, data: completeOrder });
  } catch (error) {
    await transaction.rollback();
    res.status(400).json({ success: false, error: error.message });
  }
};

module.exports = {
  createOrder,
  quickCreateOrder,
  getAllOrders,
  getOrderById,
  getOrdersByCustomer,
  updateOrderStatus,
  deleteOrder
};
