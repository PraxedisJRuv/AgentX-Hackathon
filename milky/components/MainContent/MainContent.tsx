import SubmitReport from "./SubmitReport/SubmitReport";
import ReportHistory from "./ReportHistory/ReportHistory";
import ReportStatus from "./ReportStatus/ReportStatus";
import ChatAssistant from "./ChatAssistant/ChatAssistant";

type Props = {
  activeContent: string;
  selectedReportId: string | null;
  onReportSelect: (reportId: string) => void;
  onReportSubmitted: (reportId: string) => void;
};

export default function MainContent({ activeContent, selectedReportId, onReportSelect, onReportSubmitted }: Props) {
  return (
    <div className="col-span-3 row-span-9 row-start-2 m-5 p-5">
      {activeContent === "Submit report" && <SubmitReport onSubmitted={onReportSubmitted} />}
      {activeContent === "Report history" && <ReportHistory onSelect={onReportSelect} />}
      {activeContent === "Report status" && <ReportStatus reportId={selectedReportId} />}
      {activeContent === "Chat assistant" && <ChatAssistant />}
    </div>
  );
}