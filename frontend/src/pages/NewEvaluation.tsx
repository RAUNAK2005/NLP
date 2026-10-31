import { BarChart3, FileText, PlayCircle, UploadCloud } from "lucide-react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { useNavigate } from "react-router-dom";
import Button from "../components/ui/Button";
import Panel from "../components/ui/Panel";
import { createComparison, uploadDataset } from "../services/api";
import type { Dataset } from "../types";

export default function NewEvaluation() {
  const [original, setOriginal] = useState<Dataset | null>(null);
  const [synthetic, setSynthetic] = useState<Dataset | null>(null);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const comparison = useMutation({
    mutationFn: () => {
      if (!original || !synthetic) throw new Error("Upload both datasets first.");
      return createComparison(original.id, synthetic.id);
    },
    onSuccess: (result) => {
      queryClient.invalidateQueries({ queryKey: ["comparisons"] });
      navigate(`/comparisons/${result.id}`);
    },
    onError: (err) => setError(err.message),
  });
  const steps = [
    ["Dataset Type", true],
    ["Original Dataset", Boolean(original)],
    ["Synthetic Dataset", Boolean(synthetic)],
    ["Evaluation", comparison.isSuccess],
    ["Results", false],
  ];

  return (
    <div className="grid gap-6">
      <section>
        <h1 className="text-3xl font-bold text-ink">New Evaluation</h1>
        <p className="mt-2 text-muted">Text classification MVP with sentiment-analysis-ready defaults.</p>
      </section>
      <div className="grid gap-2 md:grid-cols-5">
        {steps.map(([label, done], index) => (
          <div key={String(label)} className="rounded-lg border border-line bg-white p-3">
            <div className="flex items-center gap-2">
              <span className={`grid h-7 w-7 place-items-center rounded-md text-sm font-bold ${done ? "bg-accent text-white" : "bg-[#edf0f5] text-muted"}`}>{index + 1}</span>
              <span className="text-sm font-semibold text-ink">{label}</span>
            </div>
          </div>
        ))}
      </div>
      <div className="grid gap-5 lg:grid-cols-2">
        <UploadPanel title="Original Dataset" datasetType="original" dataset={original} onUploaded={setOriginal} />
        <UploadPanel title="Synthetic Dataset" datasetType="synthetic" dataset={synthetic} onUploaded={setSynthetic} />
      </div>
      <Panel
        title="Run Evaluation"
        action={
          <Button onClick={() => comparison.mutate()} disabled={!original || !synthetic || comparison.isPending}>
            <PlayCircle size={18} />
            {comparison.isPending ? "Running..." : "Compare Datasets"}
          </Button>
        }
      >
        <div className="grid gap-3 text-sm text-muted md:grid-cols-2">
          <Stage done={Boolean(original)} label="Original upload and validation complete" />
          <Stage done={Boolean(synthetic)} label="Synthetic upload and validation complete" />
          <Stage done={comparison.isPending || comparison.isSuccess} label="Linguistic metrics and similarity calculations" />
          <Stage done={comparison.isSuccess} label="Utility experiment and composite score" />
        </div>
        {error ? <p className="mt-4 text-sm font-medium text-red-700">{error}</p> : null}
      </Panel>
    </div>
  );
}

function UploadPanel({ title, datasetType, dataset, onUploaded }: { title: string; datasetType: string; dataset: Dataset | null; onUploaded: (dataset: Dataset) => void }) {
  const [error, setError] = useState<string | null>(null);
  const upload = useMutation({
    mutationFn: (file: File) => uploadDataset(file, datasetType),
    onSuccess: (result) => {
      setError(null);
      onUploaded(result);
    },
    onError: (err) => setError(err.message),
  });

  return (
    <Panel title={title}>
      <label className="flex min-h-40 cursor-pointer flex-col items-center justify-center rounded-lg border border-dashed border-line bg-[#fbfcfd] p-6 text-center transition hover:border-accent">
        <UploadCloud className="mb-3 text-accent" size={30} />
        <span className="font-semibold text-ink">{upload.isPending ? "Uploading..." : "Choose CSV file"}</span>
        <span className="mt-1 text-sm text-muted">UTF-8 CSV with text and label columns</span>
        <input
          type="file"
          accept=".csv,text/csv"
          className="sr-only"
          onChange={(event) => {
            const file = event.target.files?.[0];
            if (file) upload.mutate(file);
          }}
        />
      </label>
      {error ? <p className="mt-3 text-sm font-medium text-red-700">{error}</p> : null}
      {dataset ? (
        <div className="mt-4 rounded-lg border border-line bg-white p-4">
          <div className="flex items-start gap-3">
            <FileText className="mt-1 text-accent" size={20} />
            <div>
              <h3 className="font-semibold text-ink">{dataset.file_name}</h3>
              <p className="text-sm text-muted">
                {dataset.row_count.toLocaleString()} rows, {dataset.column_count} columns, text: {dataset.text_column}, label: {dataset.label_column}
              </p>
            </div>
          </div>
          <div className="mt-3 grid gap-2 text-sm">
            {dataset.validation_report.checks.map((check) => (
              <Stage key={check.label} done={check.status === "passed"} label={check.label} />
            ))}
            {dataset.validation_report.warnings.map((warning) => (
              <div key={warning} className="text-amber">Warning: {warning}</div>
            ))}
          </div>
        </div>
      ) : null}
    </Panel>
  );
}

function Stage({ done, label }: { done: boolean; label: string }) {
  return (
    <div className="flex items-center gap-2">
      <span className={`h-2.5 w-2.5 rounded-full ${done ? "bg-accent" : "bg-[#cbd5e1]"}`} />
      <span>{label}</span>
    </div>
  );
}

