import { ExternalLink } from "lucide-react";
import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import Button from "../components/ui/Button";
import Panel from "../components/ui/Panel";
import { listComparisons } from "../services/api";

export default function History() {
  const { data = [], isLoading, error } = useQuery({ queryKey: ["comparisons"], queryFn: listComparisons });
  if (isLoading) return <p className="text-muted">Loading experiment history...</p>;
  if (error) return <p className="text-red-700">{error.message}</p>;

  return (
    <div className="grid gap-6">
      <section>
        <h1 className="text-3xl font-bold text-ink">Experiment History</h1>
        <p className="mt-2 text-muted">Saved comparison runs can be reopened for review or export.</p>
      </section>
      <Panel>
        <div className="overflow-x-auto">
          <table className="w-full min-w-[760px] text-sm">
            <thead>
              <tr className="border-b border-line text-left text-xs uppercase tracking-wide text-muted">
                <th className="py-3 pr-4">Experiment</th>
                <th className="py-3 pr-4">Task</th>
                <th className="py-3 pr-4">Overall</th>
                <th className="py-3 pr-4">Fidelity</th>
                <th className="py-3 pr-4">Utility</th>
                <th className="py-3 pr-4">Date</th>
                <th className="py-3 pr-4">Open</th>
              </tr>
            </thead>
            <tbody>
              {data.map((comparison) => (
                <tr key={comparison.id} className="border-b border-[#edf0f5]">
                  <td className="py-3 pr-4 font-semibold text-ink">Comparison #{comparison.id}</td>
                  <td className="py-3 pr-4 text-muted">{comparison.configuration.task_type}</td>
                  <td className="py-3 pr-4 text-accent">{comparison.overall_score.toFixed(1)}</td>
                  <td className="py-3 pr-4 text-muted">{comparison.fidelity_score.toFixed(1)}</td>
                  <td className="py-3 pr-4 text-muted">{comparison.utility_score.toFixed(1)}</td>
                  <td className="py-3 pr-4 text-muted">{new Date(comparison.created_at).toLocaleString()}</td>
                  <td className="py-3 pr-4">
                    <Link to={`/comparisons/${comparison.id}`}>
                      <Button variant="ghost"><ExternalLink size={16} /> Open</Button>
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        {!data.length ? <p className="mt-4 text-muted">No completed experiments yet.</p> : null}
      </Panel>
    </div>
  );
}

