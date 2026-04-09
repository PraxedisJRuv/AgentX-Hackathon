export default function NavigationBar() {
  return (
    <nav className="col-span-4 flex items-center justify-start m-5 h-15 rounded-xl bg-[#00120B]">
      <img src="/milk.png" className="ml-5 p-1 h-10 w-10 rounded-xl bg-[#F0F8FF]" alt="logo" />
      <h1 className="ml-5 text-[#F0F8FF] font-bold">Milky Chat</h1>
    </nav>
  );
}