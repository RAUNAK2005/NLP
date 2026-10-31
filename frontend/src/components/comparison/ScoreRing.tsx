import { scoreLabel } from "../../utils/format";

export default function ScoreRing({ score }: { score: number }) {
  const angle = Math.max(0, Math.min(100, score)) * 3.6;
  return (
    <div
      className="mx-auto grid h-48 w-48 place-items-center rounded-full"
      style={{ background: `conic-gradient(#0f766e ${angle}deg, #e4e8ef ${angle}deg)` }}
      aria-label={`Overall score ${score.toFixed(1)} out of 100`}
    >
      <div className="grid h-36 w-36 place-items-center rounded-full bg-white text-center shadow-inner">
        <div>
          <div className="text-4xl font-bold text-ink">{score.toFixed(0)}</div>
          <div className="text-sm font-semibold uppercase tracking-wide text-accent">/ 100</div>
          <div className="mt-1 text-sm text-muted">{scoreLabel(score)}</div>
        </div>
      </div>
    </div>
  );
}

