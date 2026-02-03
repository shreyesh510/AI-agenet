const express = require('express');
const cors = require('cors');
require('dotenv').config();

const { sequelize, connectDB } = require('./config/database');
require('./models');

const customerRoutes = require('./routes/customerRoutes');
const productRoutes = require('./routes/productRoutes');
const orderRoutes = require('./routes/orderRoutes');

const app = express();

// Middleware
app.use(cors());
app.use(express.json());

// Routes
app.use('/api/customers', customerRoutes);
app.use('/api/products', productRoutes);
app.use('/api/orders', orderRoutes);

// Root route
app.get('/', (req, res) => {
  res.json({ message: 'node app is running' });
});

// Health check
app.get('/api/health', (req, res) => {
  res.json({ status: 'OK', message: 'Server is running' });
});

const PORT = process.env.PORT || 3000;

// Start server
const startServer = async () => {
  await connectDB();

  // Sync database (creates tables if they don't exist)
  await sequelize.sync({ alter: true });
  console.log('Database synced');

  app.listen(PORT, () => {
    console.log(`Server running on port ${PORT}`);
  });
};

startServer();
