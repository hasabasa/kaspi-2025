// Minimal mock data used across the app. Expand as needed by features.

export const mockSalesData = [
  {
    date: new Date().toISOString(),
  orders: 12,
  revenue: 125000,
  items_sold: 34,
  count: 12,
  amount: 125000,
    store_id: '1'
  },
  {
    date: new Date(Date.now() - 86400000).toISOString(),
    orders: 8,
    revenue: 80000,
    items_sold: 20,
  count: 8,
  amount: 80000,
  store_id: '1'
  },
  {
    date: new Date(Date.now() - 2 * 86400000).toISOString(),
    orders: 15,
    revenue: 150000,
    items_sold: 45,
  count: 15,
  amount: 150000,
  store_id: '2'
  }
];

export const mockGoldCommissions = [
  { month: 'Jan', commission: 1200 },
  { month: 'Feb', commission: 900 },
  { month: 'Mar', commission: 1300 },
];

export const mockRedKreditCommissions = [
  { month: 'Jan', commission: 400 },
  { month: 'Feb', commission: 350 },
  { month: 'Mar', commission: 420 },
];

export const mockInstallmentCommissions = [
  { month: 'Jan', commission: 700 },
  { month: 'Feb', commission: 650 },
  { month: 'Mar', commission: 720 },
];
