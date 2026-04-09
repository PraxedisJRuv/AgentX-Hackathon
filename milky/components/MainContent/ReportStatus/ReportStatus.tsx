import { useEffect, useState } from "react";
import Report from "../ReportHistory/Report";
import Log from "./Log";
import { getReport, getReportStatuses } from "../../../lib/api";
import type { Report as ReportType, ReportStatusLog } from "../../../lib/types";

type Props = {
  reportId: string | null;
};

export default function ReportStatus({ reportId }: Props) {
  const [report, setReport] = useState<ReportType | null>(null);
  const [logs, setLogs] = useState<ReportStatusLog[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!reportId) return;
    setLoading(true);
    setError(null);
    Promise.all([getReport(reportId), getReportStatuses(reportId)])
      .then(([r, l]) => {
        setReport(r);
        setLogs(l);
      })
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, [reportId]);

  if (!reportId) return <p className="p-4 text-sm">Select a report to see its status.</p>;
  if (loading) return <p className="p-4 text-sm">Loading…</p>;
  if (error) return <p className="p-4 text-sm text-red-600">{error}</p>;
  if (!report) return null;

  return (
    <div className="flex flex-col gap-2 max-h-full">
      <Report
        number={1}
        title={report.name}
        date={report.created_at.slice(0, 10)}
        status={report.status}
      />
      <div className="space-y-2 overflow-scroll">
        {logs.map((log, i) => (
          <Log key={i} date={log.created_at} text={log.text} />
        ))}
      </div>
    </div>
  );
}