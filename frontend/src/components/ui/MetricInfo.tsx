import { Info } from "lucide-react";

export default function MetricInfo({ label, text }: { label: string; text: string }) {
  return (
    <span className="metric-info relative inline-flex items-center">
      <button aria-label={`About ${label}`} className="rounded-full p-1 text-muted hover:bg-[#edf2f7]">
        <Info size={15} />
      </button>
      <span className="metric-tooltip absolute right-0 top-7 z-30 w-72 rounded-md border border-line bg-white p-3 text-left text-xs leading-5 text-muted shadow-soft transition">
        {text}
      </span>
    </span>
  );
}

