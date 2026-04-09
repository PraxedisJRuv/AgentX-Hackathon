export default function Report({
  number,
  title,
  date,
  status,
}: {
  number: number;
  title: string;
  date: string;
  status: string;
}) {
  return (
    <div className="flex flex-col align-middle justify-center gap-5 h-fit rounded-xl p-5 bg-[#A3CEF1] text-[#000000]">
      <div className="flex justify-between align-middle w-full">
        <h3 className="font-bold">Report #{number} - {title}</h3>
        <h4>{date}</h4>
      </div>
      <div className="flex justify-start align-middle gap-5 w-full">
        <div className={`border w-6 h-6 rounded-full ${status === "Pending" ? "bg-yellow-400" : "bg-green-500"}`}></div>
        <h4>{status}</h4>
      </div>
    </div>
  )
}