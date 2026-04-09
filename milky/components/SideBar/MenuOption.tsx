export default function MenuOption({
  text,
  active,
  onClick,
}: {
  text: string;
  active: boolean;
  onClick: (text: string) => void;
  }) {
  
  return (
    <div
      onClick={() => onClick(text)}
      className={`text-[#F0F8FF] m-5 rounded-xl ${active ? "bg-[#F0F8FF]" : "hover:bg-[#F0F8FF]"}`}
    >
      <h2 className={`p-2 hover:text-[#000000] ${active ? "text-[#000000]" : "text-[#F0F8FF]"}`}>{text}</h2>
    </div>
  );
}