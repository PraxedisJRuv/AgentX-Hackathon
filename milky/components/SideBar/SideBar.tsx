import MenuOption from "./MenuOption";

export default function SideBar({
  active,
  onSelect,
}: {
  active: string;
  onSelect: (text: string) => void;
}) {
  
  return (
    <aside className="row-span-9 row-start-2 m-5 bg-[#00120B] flex-row items-center justify-start rounded-xl">
      <MenuOption text="Submit report" active={active === "Submit report"} onClick={onSelect} />
      <MenuOption text="Report status" active={active === "Report status"} onClick={onSelect} />
      <MenuOption text="Report history" active={active === "Report history"} onClick={onSelect} />
      <MenuOption text="Chat assistant" active={active === "Chat assistant"} onClick={onSelect} />
    </aside>
  );
}
