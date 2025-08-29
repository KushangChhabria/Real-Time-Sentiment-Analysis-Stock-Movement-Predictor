import React, { useMemo } from "react";
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
} from "recharts";

export function SentimentStream({ data }) {
  const rows = useMemo(() => {
    return data.map((d) => ({
      ts: new Date(d.timestamp).toLocaleTimeString([], {
        hour: "2-digit",
        minute: "2-digit",
        second: "2-digit",
      }),
      s5: d.sentiment_avg_5m ?? 0,
      // Scale probability 0-1 → -1 to 1 for overlay on same axis
      p: d.pred_up_prob != null ? d.pred_up_prob * 2 - 1 : null,
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
      <h3 style={{ margin: 0, marginBottom: 8 }}>
        Sentiment (5m avg) & Predicted Up Probability
      </h3>
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart data={rows}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="ts" minTickGap={24} />
          <YAxis domain={[-1, 1]} />
          <Tooltip />
          <ReferenceLine y={0} stroke="#000" />
          <Area
            type="monotone"
            dataKey="s5"
            stroke="#8884d8"
            fill="#8884d8"
            fillOpacity={0.2}
            connectNulls
          />
          <Area
            type="monotone"
            dataKey="p"
            stroke="#82ca9d"
            fill="#82ca9d"
            fillOpacity={0.2}
            connectNulls
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}
