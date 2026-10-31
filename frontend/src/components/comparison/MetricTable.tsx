import MetricInfo from "../ui/MetricInfo";
import type { ComparisonMetric } from "../../types";
import { num, pct } from "../../utils/format";

export default function MetricTable({ metrics }: { metrics: ComparisonMetric[] }) {
  return (
    <div className="overflow-x-auto">
      <table className="w-full min-w-[760px] border-collapse text-sm">
        <thead>
          <tr className="border-b border-line text-left text-xs uppercase tracking-wide text-muted">
            <th className="py-3 pr-4">Metric</th>
            <th className="py-3 pr-4">Original</th>
            <th className="py-3 pr-4">Synthetic</th>
            <th className="py-3 pr-4">Similarity</th>
            <th className="py-3 pr-4">Category</th>
          </tr>
        </thead>
        <tbody>
          {metrics.map((metric) => (
            <tr key={metric.metric_name} className="border-b border-[#edf0f5]">
              <td className="py-3 pr-4 font-medium text-ink">
                <span className="inline-flex items-center gap-1">
                  {metric.metric_name}
                  <MetricInfo label={metric.metric_name} text={metric.interpretation} />
                </span>
              </td>
              <td className="py-3 pr-4 text-muted">{num(metric.original_value)}</td>
              <td className="py-3 pr-4 text-muted">{num(metric.synthetic_value)}</td>
              <td className="py-3 pr-4 font-semibold text-accent">{pct(metric.similarity_score)}</td>
              <td className="py-3 pr-4 capitalize text-muted">{metric.category}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

