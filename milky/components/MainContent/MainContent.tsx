import SubmitReport from "./SubmitReport/SubmitReport";
import ReportHistory from "./ReportHistory/ReportHistory";
import ReportStatus from "./ReportStatus/ReportStatus";
import ChatAssistant from "./ChatAssistant/ChatAssistant";

export default function MainContent({
  activeContent
}: {
  activeContent: string;
  }) {

  return (
    <div className="col-span-3 row-span-9 row-start-2 m-5 p-5">
      {activeContent === "Submit report" && <SubmitReport />}
      {activeContent === "Report history" && <ReportHistory />}
      {activeContent === "Report status" && <ReportStatus />}
      {activeContent === "Chat assistant" && <ChatAssistant />}
    </div>
  );
}