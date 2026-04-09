"use client";
import { useState } from "react";
import NavigationBar from "../components/NavigationBar/NavigationBar";
import SideBar from "../components/SideBar/SideBar";
import MainContent from "../components/MainContent/MainContent";

export default function Home() {
  const [active, setActive] = useState("");
  const [selectedReportId, setSelectedReportId] = useState<string | null>(null);

  function handleReportSelect(reportId: string) {
    setSelectedReportId(reportId);
    setActive("Report status");
  }

  function handleReportSubmitted(reportId: string) {
    setSelectedReportId(reportId);
    setActive("Report status");
  }

  return (
    <div className="grid grid-cols-4 grid-rows-10 bg-[#D8E4FF] h-screen w-screen">
      <NavigationBar />
      <SideBar active={active} onSelect={setActive} />
      <MainContent
        activeContent={active}
        selectedReportId={selectedReportId}
        onReportSelect={handleReportSelect}
        onReportSubmitted={handleReportSubmitted}
      />
    </div>
  );
}


