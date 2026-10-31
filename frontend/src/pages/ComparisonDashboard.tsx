import { Download, FileJson, TableProperties } from "lucide-react";
import { useQuery } from "@tanstack/react-query";
import { useParams } from "react-router-dom";
import ComparisonCharts from "../components/charts/ComparisonCharts";
import MetricTable from "../components/comparison/MetricTable";
import ScoreRing from "../components/comparison/ScoreRing";
import Button from "../components/ui/Button";
import Panel from "../components/ui/Panel";
import { getComparisonDetail, reportUrl } from "../services/api";

export default function ComparisonDashboard() {
  const { id = "" } = useParams();
  const { data, isLoading, error } = useQuery({ queryKey: ["comparison", id], queryFn: () => getComparisonDetail(id), enabled: Boolean(id) });

  if (isLoading) return <p className="text-muted">Loading evaluation results...</p>;
  if (error) return <p className="text-red-700">{error.message}</p>;
  if (!data) return null;
  const { comparison, original_dataset, synthetic_dataset } = data;

  return (
    <div className="grid gap-6">
      <section className="flex flex-col justify-between gap-4 md:flex-row md:items-end">
        <div>
          <h1 className="text-3xl font-bold text-ink">Synthetic Dataset Evaluation</h1>
          <p className="mt-2 text-muted">Dataset Quality Assessment</p>
        </div>
        <div className="flex flex-wrap gap-2">
          <a href={reportUrl(comparison.id, "csv")}><Button variant="secondary"><TableProperties size={17} /> CSV</Button></a>
          <a href={reportUrl(comparison.id, "json")}><Button variant="secondary"><FileJson size={17} /> JSON</Button></a>
          <a href={reportUrl(comparison.id, "pdf")}><Button variant="secondary"><Download size={17} /> PDF</Button></a>
        </div>
      </section>

      <div className="grid gap-5 lg:grid-cols-[0.8fr_1.2fr]">
        <Panel title="Overall Score">
          <ScoreRing score={comparison.overall_score} />
          <p className="mt-5 text-center text-sm leading-6 text-muted">Project-defined composite evaluation score. Weights: fidelity {Math.round(comparison.payload.weights.fidelity * 100)}%, diversity {Math.round(comparison.payload.weights.diversity * 100)}%, utility {Math.round(comparison.payload.weights.utility * 100)}%.</p>
        </Panel>
        <div className="grid gap-5 sm:grid-cols-2">
          <DatasetSummary title="Original Dataset" name={original_dataset.name} rows={original_dataset.row_count} cols={original_dataset.column_count} classes={original_dataset.statistics?.metrics_payload.number_of_classes ?? 0} />
          <DatasetSummary title="Synthetic Dataset" name={synthetic_dataset.name} rows={synthetic_dataset.row_count} cols={synthetic_dataset.column_count} classes={synthetic_dataset.statistics?.metrics_payload.number_of_classes ?? 0} />
          <Dimension title="Fidelity" value={comparison.fidelity_score} />
          <Dimension title="Diversity" value={comparison.diversity_score} />
          <Dimension title="Utility" value={comparison.utility_score} />
          <Dimension title="Status" value={comparison.overall_score} label={comparison.status} />
        </div>
      </div>

      <Panel title="Overall Assessment">
        <p className="leading-7 text-muted">{comparison.interpretation}</p>
      </Panel>

      <ComparisonCharts detail={data} />

      <Panel title="Metric Comparison">
        <MetricTable metrics={comparison.metrics} />
      </Panel>
    </div>
  );
}

function DatasetSummary({ title, name, rows, cols, classes }: { title: string; name: string; rows: number; cols: number; classes: number }) {
  return (
    <section className="rounded-lg border border-line bg-white p-5 shadow-soft">
      <p className="text-xs font-semibold uppercase tracking-wide text-accent">{title}</p>
      <h2 className="mt-2 text-lg font-bold text-ink">{name}</h2>
      <p className="mt-3 text-sm text-muted">{rows.toLocaleString()} records</p>
      <p className="text-sm text-muted">{cols} columns</p>
      <p className="text-sm text-muted">{classes} classes</p>
    </section>
  );
}

function Dimension({ title, value, label }: { title: string; value: number; label?: string }) {
  return (
    <section className="rounded-lg border border-line bg-white p-5 shadow-soft">
      <p className="text-sm font-semibold text-muted">{title}</p>
      <p className="mt-2 text-3xl font-bold text-ink">{label ?? `${value.toFixed(0)}%`}</p>
    </section>
  );
}

