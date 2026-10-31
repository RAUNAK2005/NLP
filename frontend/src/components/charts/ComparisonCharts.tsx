import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import type { ComparisonDetail } from "../../types";

const colors = ["#0f766e", "#b45309", "#334155", "#6b7280"];

export default function ComparisonCharts({ detail }: { detail: ComparisonDetail }) {
  const { comparison, original_dataset, synthetic_dataset } = detail;
  const originalStats = original_dataset.statistics?.metrics_payload;
  const syntheticStats = synthetic_dataset.statistics?.metrics_payload;
  const distribution = Object.keys({
    ...(originalStats?.class_distribution ?? {}),
    ...(syntheticStats?.class_distribution ?? {}),
  }).map((label) => ({
    label,
    original: Math.round((originalStats?.class_distribution?.[label]?.proportion ?? 0) * 100),
    synthetic: Math.round((syntheticStats?.class_distribution?.[label]?.proportion ?? 0) * 100),
  }));
  const scores = [
    { name: "Fidelity", value: comparison.fidelity_score },
    { name: "Diversity", value: comparison.diversity_score },
    { name: "Utility", value: comparison.utility_score },
  ];
  const similarity = comparison.metrics
    .filter((metric) => metric.similarity_score !== null)
    .slice(-6)
    .map((metric) => ({ name: metric.metric_name.replace(" Similarity", ""), value: Math.round((metric.similarity_score ?? 0) * 100) }));
  const length = [
    { name: "Original", value: originalStats?.text_length?.mean ?? 0 },
    { name: "Synthetic", value: syntheticStats?.text_length?.mean ?? 0 },
  ];

  return (
    <div className="grid gap-5 lg:grid-cols-2">
      <ChartFrame title="Class Distribution">
        <BarChart data={distribution}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="label" />
          <YAxis unit="%" />
          <Tooltip />
          <Legend />
          <Bar dataKey="original" fill="#0f766e" radius={[4, 4, 0, 0]} />
          <Bar dataKey="synthetic" fill="#b45309" radius={[4, 4, 0, 0]} />
        </BarChart>
      </ChartFrame>
      <ChartFrame title="Dimension Scores">
        <BarChart data={scores}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="name" />
          <YAxis domain={[0, 100]} />
          <Tooltip />
          <Bar dataKey="value" radius={[4, 4, 0, 0]}>
            {scores.map((_, index) => (
              <Cell key={index} fill={colors[index]} />
            ))}
          </Bar>
        </BarChart>
      </ChartFrame>
      <ChartFrame title="Similarity Metrics">
        <LineChart data={similarity}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="name" />
          <YAxis domain={[0, 100]} />
          <Tooltip />
          <Line type="monotone" dataKey="value" stroke="#0f766e" strokeWidth={2} dot={{ r: 4 }} />
        </LineChart>
      </ChartFrame>
      <ChartFrame title="Mean Words Per Document">
        <BarChart data={length}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="name" />
          <YAxis />
          <Tooltip />
          <Bar dataKey="value" fill="#334155" radius={[4, 4, 0, 0]} />
        </BarChart>
      </ChartFrame>
    </div>
  );
}

function ChartFrame({ title, children }: { title: string; children: React.ReactElement }) {
  return (
    <section className="rounded-lg border border-line bg-white p-5 shadow-soft">
      <h3 className="mb-4 text-base font-semibold text-ink">{title}</h3>
      <div className="h-72">
        <ResponsiveContainer width="100%" height="100%">
          {children}
        </ResponsiveContainer>
      </div>
    </section>
  );
}

