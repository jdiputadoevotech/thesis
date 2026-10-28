import { useState } from "react";
import { Button } from "./components/ui/button.jsx";
import { Card, CardContent, CardHeader, CardTitle } from "./components/ui/card.jsx";

function Shell({ children }) {
  return (
    <div className="flex min-h-screen items-center justify-center bg-slate-50/80 px-6 py-10 text-slate-900">
      <div className="w-full max-w-xl">{children}</div>
    </div>
  );
}

export function Notice({ title, children }) {
  return (
    <Shell>
      <Card>
        <CardHeader>
          <CardTitle>{title}</CardTitle>
        </CardHeader>
        <CardContent className="space-y-2 text-sm text-slate-600">{children}</CardContent>
      </Card>
    </Shell>
  );
}

export function ConsentScreen({ me, onAgreed }) {
  const [checked, setChecked] = useState(false);
  const [error, setError] = useState("");

  async function agree() {
    setError("");
    const res = await fetch("/api/consent", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ agree: true, text_sha: me.consent_sha }),
    }).catch(() => null);
    if (res?.ok) onAgreed();
    else setError("Could not record your confirmation. Reload the page and try again.");
  }

  return (
    <Shell>
      <Card>
        <CardHeader>
          <CardTitle>Expert-panel typography rating</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4 text-sm text-slate-700">
          <p>
            You are rater <b>{me.rater}</b>. For each cropped word you will name the closest
            typeface from a fixed list of 80 and say whether the crop is set in one typeface. Please
            read this before you start.
          </p>
          <p className="rounded-md border border-slate-200 bg-slate-50 p-3 leading-relaxed">
            {me.consent_text}
          </p>
          <label className="flex cursor-pointer items-start gap-2">
            <input
              type="checkbox"
              checked={checked}
              onChange={(e) => setChecked(e.target.checked)}
              className="mt-1"
            />
            <span>I have read the statements above and I confirm them.</span>
          </label>
          {error && <p className="text-red-600">{error}</p>}
          <Button disabled={!checked} onClick={agree}>
            Start rating
          </Button>
        </CardContent>
      </Card>
    </Shell>
  );
}

export function ReceiptScreen({ receipt }) {
  const text = [
    `Rater: ${receipt.rater}`,
    `Items answered: ${receipt.rows}`,
    `Finished at (UTC): ${receipt.finished_at}`,
    `Answer-set SHA-256: ${receipt.label_set_sha256}`,
    `Audit-log hash: ${receipt.audit_hash}`,
  ].join("\n");
  return (
    <Shell>
      <Card>
        <CardHeader>
          <CardTitle>Thank you: your answers are submitted and locked</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3 text-sm text-slate-700">
          <p>
            Please copy this receipt and reply to the email that brought you this link,{" "}
            <b>from that same mailbox</b>, with the words "I confirm this receipt is mine". That is
            how the study shows the answers are yours and unchanged.
          </p>
          <pre className="overflow-x-auto rounded-md border border-slate-200 bg-slate-50 p-3 text-xs">
            {text}
          </pre>
          <Button variant="outline" onClick={() => navigator.clipboard?.writeText(text)}>
            Copy receipt
          </Button>
        </CardContent>
      </Card>
    </Shell>
  );
}
