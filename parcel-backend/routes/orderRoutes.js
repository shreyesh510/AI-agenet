const express = require('express');
const router = express.Router();
const {
  createOrder,
  getAllOrders,
  getOrderById,
  getOrdersByCustomer,
  updateOrderStatus,
  deleteOrder
} = require('../controllers/orderController');

router.post('/', createOrder);
router.get('/', getAllOrders);
router.get('/:id', getOrderById);
router.get('/customer/:customerId', getOrdersByCustomer);
router.put('/:id/status', updateOrderStatus);
router.delete('/:id', deleteOrder);

module.exports = router;
