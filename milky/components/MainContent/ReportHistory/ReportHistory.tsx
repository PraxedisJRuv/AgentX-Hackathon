import { useEffect, useState } from "react";
import Report from "./Report";
import { getReports } from "../../../lib/api";
import type { Report as ReportType } from "../../../lib/types";

type Props = {
  onSelect: (reportId: string) => void;
};

export default function ReportHistory({ onSelect }: Props) {
  const [reports, setReports] = useState<ReportType[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getReports()
      .then((data) => setReports([...data].reverse()))
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <p className="p-4 text-sm">Loading reports…</p>;
  if (error) return <p className="p-4 text-sm text-red-600">{error}</p>;
  if (reports.length === 0) return <p className="p-4 text-sm">No reports yet.</p>;

  return (
    <div className="space-y-2 max-h-full overflow-scroll">
      {reports.map((report, i) => (
        <div key={report.id} onClick={() => onSelect(report.id)} className="cursor-pointer">
          <Report
            number={reports.length - i}
            title={report.name}
            date={report.created_at.slice(0, 10)}
            status={report.status}
          />
        </div>
      ))}
    </div>
  );
}