import Panel from "../components/ui/Panel";

const settings = [
  ["Random Seed", "42"],
  ["Default Sample Size", "1000"],
  ["Embedding Model", "sentence-transformers/all-MiniLM-L6-v2 with TF-IDF fallback"],
  ["Evaluation Models", "TF-IDF + Logistic Regression, Linear SVM, Naive Bayes"],
  ["Scoring Weights", "Fidelity 40%, Diversity 30%, Utility 30%"],
  ["Maximum Rows", "20,000"],
];

export default function Settings() {
  return (
    <div className="grid gap-6">
      <section>
        <h1 className="text-3xl font-bold text-ink">Settings</h1>
        <p className="mt-2 text-muted">Current reproducibility defaults. Backend values can be overridden through environment variables.</p>
      </section>
      <Panel title="Evaluation Configuration">
        <div className="grid gap-4 md:grid-cols-2">
          {settings.map(([label, value]) => (
            <div key={label} className="rounded-lg border border-line bg-[#fbfcfd] p-4">
              <p className="text-xs font-semibold uppercase tracking-wide text-muted">{label}</p>
              <p className="mt-2 font-semibold text-ink">{value}</p>
            </div>
          ))}
        </div>
      </Panel>
      <Panel title="Future Configurability">
        <p className="leading-7 text-muted">The database already stores configuration JSON with every comparison. A later UI pass can make weights, thresholds, sample sizes, and model choices editable per experiment.</p>
      </Panel>
    </div>
  );
}

