import Report from "../ReportHistory/Report";
import Log from "./Log";

export default function ReportStatus() {
  const logs = [
    { id: 1, date: "2023-01-01", text: "Report received." },
    { id: 2, date: "2023-01-02", text: "Report is under review." },
    { id: 3, date: "2023-01-03", text: "Additional information requested." },
    { id: 4, date: "2023-01-04", text: "User provided additional details." },
    { id: 5, date: "2023-01-05", text: "Report validated by system." },
    { id: 6, date: "2023-01-06", text: "Assigned to support agent." },
    { id: 7, date: "2023-01-07", text: "Investigation in progress." },
    { id: 8, date: "2023-01-08", text: "Issue partially resolved." },
    { id: 9, date: "2023-01-09", text: "Follow-up required." },
    { id: 10, date: "2023-01-10", text: "User contacted for confirmation." },
    { id: 11, date: "2023-01-11", text: "Awaiting user response." },
    { id: 12, date: "2023-01-12", text: "User responded with confirmation." },
    { id: 13, date: "2023-01-13", text: "Final verification in progress." },
    { id: 14, date: "2023-01-14", text: "Issue fully resolved." },
    { id: 15, date: "2023-01-15", text: "Report closed." },
    { id: 16, date: "2023-01-16", text: "Post-resolution review logged." },
    { id: 17, date: "2023-01-17", text: "Quality assurance check completed." },
    { id: 18, date: "2023-01-18", text: "Feedback request sent to user." },
    { id: 19, date: "2023-01-19", text: "User feedback received." },
    { id: 20, date: "2023-01-20", text: "Case archived." },
  ];

  return (
    <div className="flex flex-col gap-2 max-h-full">
      <Report number={1} title="Payment processed yet order not received" date="2023-01-01" status="Pending" />
      <div className="space-y-2 overflow-scroll">
        {logs.map((log) => (
          <Log key={log.id} date={log.date} text={log.text} />
        ))}
      </div>
    </div>
  );
}