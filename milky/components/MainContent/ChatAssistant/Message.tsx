export default function Message({
  role,
  text,
}: {
  role: string;
  text: string;
}) {
  return (
    <div className={`flex ${role === "user" ? "justify-end" : "justify-start"}`}>
      <div
        className={`p-3 m-2 max-w-[70%] rounded-lg ${
          role === "user"
            ? "bg-blue-400 text-white"
            : "bg-orange-400 text-black"
        }`}
      >
        <p>{text}</p>
      </div>
    </div>
  );
}