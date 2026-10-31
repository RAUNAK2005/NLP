import { useQuery } from "@tanstack/react-query";
import Panel from "../components/ui/Panel";
import { listDatasets } from "../services/api";

export default function DatasetAnalysis() {
  const { data = [], isLoading, error } = useQuery({ queryKey: ["datasets"], queryFn: listDatasets });
  if (isLoading) return <p className="text-muted">Loading datasets...</p>;
  if (error) return <p className="text-red-700">{error.message}</p>;

  return (
    <div className="grid gap-6">
      <section>
        <h1 className="text-3xl font-bold text-ink">Dataset Analysis</h1>
        <p className="mt-2 text-muted">Uploaded datasets with validation, detected columns, and basic statistics.</p>
      </section>
      <div className="grid gap-5">
        {data.map((dataset) => (
          <Panel key={dataset.id} title={`${dataset.name} (${dataset.dataset_type})`}>
            <div className="grid gap-4 md:grid-cols-4">
              <Fact label="Rows" value={dataset.row_count.toLocaleString()} />
              <Fact label="Columns" value={String(dataset.column_count)} />
              <Fact label="Text Column" value={dataset.text_column ?? "N/A"} />
              <Fact label="Label Column" value={dataset.label_column ?? "N/A"} />
            </div>
            <div className="mt-5 grid gap-4 md:grid-cols-4">
              <Fact label="Missing" value={String(dataset.statistics?.missing_count ?? 0)} />
              <Fact label="Duplicates" value={String(dataset.statistics?.duplicate_count ?? 0)} />
              <Fact label="Vocabulary" value={(dataset.statistics?.vocabulary_size ?? 0).toLocaleString()} />
              <Fact label="Avg Words" value={(dataset.statistics?.avg_text_length ?? 0).toFixed(2)} />
            </div>
            <div className="mt-5 overflow-x-auto">
              <table className="w-full min-w-[620px] text-sm">
                <thead>
                  <tr className="border-b border-line text-left text-xs uppercase tracking-wide text-muted">
                    {dataset.columns.map((column) => <th key={column} className="py-2 pr-4">{column}</th>)}
                  </tr>
                </thead>
                <tbody>
                  {dataset.sample_rows.slice(0, 4).map((row, index) => (
                    <tr key={index} className="border-b border-[#edf0f5]">
                      {dataset.columns.map((column) => <td key={column} className="max-w-sm truncate py-2 pr-4 text-muted">{String(row[column] ?? "")}</td>)}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </Panel>
        ))}
        {!data.length ? <Panel><p className="text-muted">No datasets uploaded yet. Use New Evaluation or Try Demo.</p></Panel> : null}
      </div>
    </div>
  );
}

function Fact({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <p className="text-xs font-semibold uppercase tracking-wide text-muted">{label}</p>
      <p className="mt-1 text-lg font-bold text-ink">{value}</p>
    </div>
  );
}

