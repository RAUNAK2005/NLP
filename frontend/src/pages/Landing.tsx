import { ArrowRight, FlaskConical, PlayCircle } from "lucide-react";
import { useMutation } from "@tanstack/react-query";
import { useNavigate } from "react-router-dom";
import Button from "../components/ui/Button";
import Panel from "../components/ui/Panel";
import { runDemo } from "../services/api";

export default function Landing() {
  const navigate = useNavigate();
  const demo = useMutation({
    mutationFn: runDemo,
    onSuccess: (comparison) => navigate(`/comparisons/${comparison.id}`),
  });

  return (
    <div className="grid gap-8">
      <section className="grid gap-8 rounded-lg border border-line bg-white p-6 shadow-soft lg:grid-cols-[1.2fr_0.8fr] lg:p-8">
        <div className="flex flex-col justify-center">
          <div className="mb-4 inline-flex w-fit items-center gap-2 rounded-md bg-[#e9f5f3] px-3 py-2 text-sm font-semibold text-accent">
            <FlaskConical size={16} />
            Research-grade synthetic data evaluation
          </div>
          <h1 className="max-w-3xl text-4xl font-bold leading-tight text-ink md:text-5xl">Evaluate Synthetic Data</h1>
          <p className="mt-4 max-w-2xl text-lg leading-8 text-muted">
            Compare fidelity, diversity, class distributions, semantic similarity, and downstream classification utility against real datasets.
          </p>
          <div className="mt-7 flex flex-wrap gap-3">
            <Button onClick={() => navigate("/new")}>
              Start Evaluation <ArrowRight size={18} />
            </Button>
            <Button variant="secondary" onClick={() => demo.mutate()} disabled={demo.isPending}>
              <PlayCircle size={18} />
              {demo.isPending ? "Running demo..." : "Try Demo"}
            </Button>
          </div>
          {demo.error ? <p className="mt-3 text-sm font-medium text-red-700">{demo.error.message}</p> : null}
        </div>
        <div className="grid content-center gap-3">
          {[
            ["Fidelity", "Vocabulary, n-gram, TF-IDF, semantic, and label-distribution similarity."],
            ["Diversity", "Unique ratio, duplicate rate, vocabulary richness, and repeated phrase checks."],
            ["Utility", "Real->Real baseline versus Synthetic->Real evaluation on the same holdout test set."],
          ].map(([title, body]) => (
            <div key={title} className="rounded-lg border border-line bg-[#fbfcfd] p-4">
              <h2 className="font-semibold text-ink">{title}</h2>
              <p className="mt-1 text-sm leading-6 text-muted">{body}</p>
            </div>
          ))}
        </div>
      </section>

      <div className="grid gap-5 md:grid-cols-3">
        <Panel title="Pipeline">
          <p className="text-sm leading-6 text-muted">Upload original data, validate columns, run identical analysis, upload synthetic data, then compare.</p>
        </Panel>
        <Panel title="No Fabricated Results">
          <p className="text-sm leading-6 text-muted">Demo and upload flows call the same backend metric engine. Scores are calculated from CSV content.</p>
        </Panel>
        <Panel title="Paper Support">
          <p className="text-sm leading-6 text-muted">Exports include configuration, metric definitions, model names, random seed, and methodology notes.</p>
        </Panel>
      </div>
    </div>
  );
}

