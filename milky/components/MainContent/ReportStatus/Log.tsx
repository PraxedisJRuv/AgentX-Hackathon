export default function Log({
  date,
  text
}: {
  date: string;
  text: string;
}) {
  return (
    <div className="flex align-middle justify-start w-full text-gray-600 gap-5 p-5">
      <p>{date}</p>
      <p>{text}</p>
    </div>
  );
}