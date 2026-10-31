import Panel from "../components/ui/Panel";

const sections = [
  {
    title: "Research Objective",
    body: "Evaluate whether synthetic datasets preserve statistical characteristics, linguistic characteristics, diversity, class distributions, semantic characteristics, and downstream classification utility.",
  },
  {
    title: "Core Experiment",
    body: "The original dataset is split into train and holdout test sets. A baseline classifier is trained on original train and evaluated on original test. A second classifier is trained on synthetic data and evaluated on the same original test set.",
  },
  {
    title: "Fidelity",
    body: "Fidelity combines vocabulary overlap, n-gram overlap, text-length similarity, TF-IDF centroid similarity, semantic similarity, and class-distribution similarity.",
  },
  {
    title: "Diversity",
    body: "Diversity uses unique text ratio, duplicate rate, type-token ratio, and repeated n-gram behavior. Higher diversity is not automatically better unless it remains aligned with the original task distribution.",
  },
  {
    title: "Utility",
    body: "Utility is measured through macro F1 retention: Synthetic->Real macro F1 divided by Real->Real macro F1 on the original holdout set.",
  },
  {
    title: "Limitation",
    body: "A synthetic dataset that is highly similar to an original dataset is not automatically better. High similarity can indicate fidelity, while excessive similarity may indicate memorization or insufficient novelty.",
  },
];

export default function Methodology() {
  return (
    <div className="grid gap-6">
      <section>
        <h1 className="text-3xl font-bold text-ink">Methodology</h1>
        <p className="mt-2 text-muted">Transparent formulas and assumptions for research reproducibility.</p>
      </section>
      <div className="grid gap-5 md:grid-cols-2">
        {sections.map((section) => (
          <Panel key={section.title} title={section.title}>
            <p className="leading-7 text-muted">{section.body}</p>
          </Panel>
        ))}
      </div>
      <Panel title="Hypotheses Supported By This Tool">
        <div className="grid gap-3 text-sm leading-6 text-muted">
          <p>H1: Synthetic datasets generated to resemble real datasets may preserve similar class distributions.</p>
          <p>H2: Synthetic datasets may exhibit measurable semantic similarity to their corresponding original datasets.</p>
          <p>H3: Synthetic datasets with higher linguistic fidelity may demonstrate better downstream classification utility.</p>
          <p>H4: Synthetic datasets may show reduced diversity or increased repetition compared with original datasets.</p>
        </div>
      </Panel>
    </div>
  );
}

