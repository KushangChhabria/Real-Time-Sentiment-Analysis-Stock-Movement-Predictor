import React, { useMemo } from "react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
} from "recharts";

export function PriceChart({ data }) {
  const rows = useMemo(() => {
    return data
      .filter((d) => d.price != null)
      .map((d) => ({
        ts: new Date(d.timestamp).toLocaleTimeString([], {
          hour: "2-digit",
          minute: "2-digit",
          second: "2-digit",
        }),
        price: d.price,
        change_1m: d.change_1m,
      }));
  }, [data]);

  return (
    <div
      style={{
        height: 320,
        padding: 12,
        border: "1px solid #eee",
        borderRadius: 12,
      }}
    >
      <h3 style={{ margin: 0, marginBottom: 8 }}>Price (1m updates)</h3>
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={rows}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="ts" minTickGap={24} />
          <YAxis domain={["auto", "auto"]} />
          <Tooltip />
          <Line type="monotone" dataKey="price" dot={false} stroke="#ff7300" />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
