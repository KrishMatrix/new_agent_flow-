import React from 'react';

export default function InventoryTable({ data }) {
  if (!data || data.length === 0) return null;

  // Detect table format — could be metrics (key-value) or tabular
  const isMetrics = data[0]?.metric !== undefined;

  if (isMetrics) {
    return (
      <div className="message-table-container">
        <table className="message-table">
          <tbody>
            {data.map((row, i) => (
              <tr key={i}>
                <td style={{ fontWeight: 500, width: '180px' }}>{row.metric}</td>
                <td style={{ fontWeight: 700 }}>{row.value}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    );
  }

  // General table rendering
  const keys = Object.keys(data[0]);

  return (
    <div className="message-table-container">
      <table className="message-table">
        <thead>
          <tr>
            {keys.map((key) => (
              <th key={key}>{key.replace(/_/g, ' ')}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {data.map((row, i) => (
            <tr key={i}>
              {keys.map((key) => (
                <td key={key}>
                  {key === 'severity' || key === 'risk' ? (
                    <span className={`severity-badge ${row[key]}`}>
                      {row[key]}
                    </span>
                  ) : (
                    String(row[key])
                  )}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
