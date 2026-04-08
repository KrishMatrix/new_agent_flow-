import React from 'react';
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, Area, AreaChart, Legend,
} from 'recharts';

function CustomTooltip({ active, payload, label }) {
  if (!active || !payload?.length) return null;

  return (
    <div style={{
      background: '#1e293b',
      border: '1px solid rgba(148,163,184,0.2)',
      borderRadius: '8px',
      padding: '10px 14px',
      fontSize: '12px',
      boxShadow: '0 4px 16px rgba(0,0,0,0.4)',
    }}>
      <div style={{ color: '#94a3b8', marginBottom: '6px', fontWeight: 600 }}>{label}</div>
      {payload.map((entry, i) => (
        <div key={i} style={{ color: entry.color, marginBottom: '2px' }}>
          {entry.name}: <strong>{Math.round(entry.value)}</strong>
        </div>
      ))}
    </div>
  );
}

export default function ForecastChart({ data }) {
  if (!data || data.length === 0) return null;

  // Separate historical and forecast data
  const hasActual = data.some(d => d.actual !== undefined);
  const hasPredicted = data.some(d => d.predicted !== undefined);

  return (
    <div className="message-chart-container">
      <div style={{
        fontSize: '11px',
        fontWeight: 600,
        color: '#94a3b8',
        textTransform: 'uppercase',
        letterSpacing: '0.05em',
        marginBottom: '12px',
      }}>
        📈 Demand Forecast
      </div>
      <ResponsiveContainer width="100%" height={200}>
        <AreaChart data={data} margin={{ top: 5, right: 10, left: -10, bottom: 5 }}>
          <defs>
            <linearGradient id="colorActual" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#8b5cf6" stopOpacity={0.3} />
              <stop offset="95%" stopColor="#8b5cf6" stopOpacity={0} />
            </linearGradient>
            <linearGradient id="colorPredicted" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3} />
              <stop offset="95%" stopColor="#3b82f6" stopOpacity={0} />
            </linearGradient>
            <linearGradient id="colorBounds" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.1} />
              <stop offset="95%" stopColor="#3b82f6" stopOpacity={0} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(148,163,184,0.08)" />
          <XAxis
            dataKey="date"
            tick={{ fill: '#64748b', fontSize: 10 }}
            tickLine={false}
            axisLine={{ stroke: 'rgba(148,163,184,0.1)' }}
            tickFormatter={(v) => {
              const d = new Date(v);
              return `${d.getMonth()+1}/${d.getDate()}`;
            }}
          />
          <YAxis
            tick={{ fill: '#64748b', fontSize: 10 }}
            tickLine={false}
            axisLine={false}
          />
          <Tooltip content={<CustomTooltip />} />
          <Legend
            wrapperStyle={{ fontSize: '11px', paddingTop: '8px' }}
          />
          {hasActual && (
            <Area
              type="monotone"
              dataKey="actual"
              name="Actual"
              stroke="#8b5cf6"
              strokeWidth={2}
              fill="url(#colorActual)"
              dot={{ r: 3, fill: '#8b5cf6' }}
              connectNulls={false}
            />
          )}
          {hasPredicted && (
            <>
              <Area
                type="monotone"
                dataKey="upper"
                name="Upper Bound"
                stroke="transparent"
                fill="url(#colorBounds)"
                connectNulls={false}
              />
              <Area
                type="monotone"
                dataKey="predicted"
                name="Predicted"
                stroke="#3b82f6"
                strokeWidth={2}
                strokeDasharray="6 3"
                fill="url(#colorPredicted)"
                dot={{ r: 3, fill: '#3b82f6' }}
                connectNulls={false}
              />
            </>
          )}
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}
