import React, { useState, useEffect } from 'react';
import axios from 'axios';
import {
  AreaChart, Area, XAxis, YAxis, Tooltip,
  ResponsiveContainer, CartesianGrid,
} from 'recharts';

const API_URL = 'http://localhost:8000/api';

function MiniTooltip({ active, payload, label }) {
  if (!active || !payload?.length) return null;
  return (
    <div style={{
      background: '#1e293b',
      border: '1px solid rgba(148,163,184,0.2)',
      borderRadius: '6px',
      padding: '6px 10px',
      fontSize: '11px',
    }}>
      <div style={{ color: '#94a3b8' }}>{label}</div>
      <div style={{ color: '#8b5cf6', fontWeight: 700 }}>
        {Math.round(payload[0].value)} units
      </div>
    </div>
  );
}

export default function DashboardPanel() {
  const [dashboard, setDashboard] = useState(null);
  const [inventory, setInventory] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchData() {
      try {
        const [dashRes, invRes] = await Promise.all([
          axios.get(`${API_URL}/dashboard`),
          axios.get(`${API_URL}/inventory`),
        ]);
        setDashboard(dashRes.data);
        setInventory(invRes.data);
      } catch (err) {
        console.error('Dashboard fetch error:', err);
      } finally {
        setLoading(false);
      }
    }
    fetchData();
  }, []);

  if (loading) {
    return (
      <div className="dashboard-panel">
        <div className="dashboard-header">
          <h2>📋 Dashboard</h2>
        </div>
        <div className="dashboard-content">
          <div className="kpi-grid">
            {[1,2,3,4].map(i => (
              <div key={i} className="kpi-card">
                <div className="skeleton" style={{ width: '60px', height: '12px', marginBottom: '8px' }} />
                <div className="skeleton" style={{ width: '80px', height: '28px' }} />
              </div>
            ))}
          </div>
          <div className="skeleton" style={{ width: '100%', height: '140px' }} />
        </div>
      </div>
    );
  }

  if (!dashboard) {
    return (
      <div className="dashboard-panel">
        <div className="dashboard-header">
          <h2>📋 Dashboard</h2>
        </div>
        <div className="dashboard-content">
          <p style={{ color: 'var(--text-muted)', fontSize: '13px', textAlign: 'center', padding: '20px' }}>
            Failed to load dashboard data. Make sure the backend is running.
          </p>
        </div>
      </div>
    );
  }

  const lowStockItems = inventory
    ? inventory.filter(i => i.status === 'critical' || i.status === 'low').slice(0, 6)
    : [];

  return (
    <div className="dashboard-panel">
      <div className="dashboard-header">
        <h2>📋 Dashboard</h2>
      </div>

      <div className="dashboard-content">
        {/* KPI Cards */}
        <div className="kpi-grid">
          <div className="kpi-card">
            <div className="kpi-label">Total SKUs</div>
            <div className="kpi-value">{dashboard.total_skus}</div>
          </div>
          <div className="kpi-card">
            <div className="kpi-label">Total Stock</div>
            <div className="kpi-value">{dashboard.total_stock.toLocaleString()}</div>
          </div>
          <div className="kpi-card">
            <div className="kpi-label">Avg Daily Sales</div>
            <div className="kpi-value">{dashboard.avg_daily_sales}</div>
            <div className="kpi-trend">units/day</div>
          </div>
          <div className="kpi-card">
            <div className="kpi-label">Low Stock</div>
            <div className={`kpi-value ${dashboard.low_stock_count > 0 ? 'alert' : ''}`}>
              {dashboard.low_stock_count}
            </div>
            <div className="kpi-trend">need attention</div>
          </div>
        </div>

        {/* Sales Trend Chart */}
        {dashboard.sales_trend && (
          <div className="dashboard-chart">
            <div className="dashboard-chart-title">📈 14-Day Sales Trend</div>
            <ResponsiveContainer width="100%" height={120}>
              <AreaChart data={dashboard.sales_trend} margin={{ top: 5, right: 5, left: -15, bottom: 0 }}>
                <defs>
                  <linearGradient id="trendGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#8b5cf6" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="#8b5cf6" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(148,163,184,0.06)" />
                <XAxis
                  dataKey="date"
                  tick={{ fill: '#64748b', fontSize: 9 }}
                  tickLine={false}
                  axisLine={false}
                  tickFormatter={(v) => {
                    const d = new Date(v);
                    return `${d.getMonth()+1}/${d.getDate()}`;
                  }}
                />
                <YAxis tick={{ fill: '#64748b', fontSize: 9 }} tickLine={false} axisLine={false} />
                <Tooltip content={<MiniTooltip />} />
                <Area
                  type="monotone"
                  dataKey="sales"
                  stroke="#8b5cf6"
                  strokeWidth={2}
                  fill="url(#trendGrad)"
                  dot={false}
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        )}

        {/* Top Products */}
        {dashboard.top_products && (
          <div className="top-products">
            <div className="inventory-section-title">🏆 Top Products</div>
            {dashboard.top_products.map((p, i) => (
              <div key={p.sku} className="top-product-row">
                <div className="top-product-rank">{i + 1}</div>
                <div className="top-product-name">{p.name}</div>
                <div className="top-product-sales">{p.total_sold.toLocaleString()}</div>
              </div>
            ))}
          </div>
        )}

        {/* Low Stock Alerts */}
        {lowStockItems.length > 0 && (
          <div className="inventory-section">
            <div className="inventory-section-title">⚠️ Low Stock Alerts</div>
            <div className="inventory-list">
              {lowStockItems.map((item) => (
                <div key={item.sku_id} className="inventory-row">
                  <div className="inventory-name">{item.product_name}</div>
                  <span className={`inventory-stock ${item.status}`}>
                    {item.quantity_on_hand} units
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
