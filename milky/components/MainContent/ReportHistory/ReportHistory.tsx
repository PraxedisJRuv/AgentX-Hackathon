import Report from "./Report";

export default function ReportHistory() {
  const reports = [
    { id: 1, title: "Payment processed yet order not received", date: "2023-01-01", status: "Pending" },
    { id: 2, title: "Order has not been received", date: "2023-01-02", status: "Completed" },
    { id: 3, title: "Wrong shipping address", date: "2023-01-03", status: "Pending" },
    { id: 4, title: "Payment processed yet order not received", date: "2023-01-01", status: "Pending" },
    { id: 5, title: "Order has not been received", date: "2023-01-02", status: "Completed" },
    { id: 6, title: "Wrong shipping address", date: "2023-01-03", status: "Pending" },
    { id: 7, title: "Wrong shipping address", date: "2023-01-03", status: "Pending" },
  ].reverse();

  return (
    <div className="space-y-2 max-h-full overflow-scroll">
      {reports.map((report) => (
        <Report
          key={report.id}
          number={report.id}
          title={report.title}
          date={report.date}
          status={report.status}
        />
      ))}
    </div>
  );
}