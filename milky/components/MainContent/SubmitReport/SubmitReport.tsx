import { useState } from "react";

export default function SubmitReport() {
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [date, setDate] = useState(new Date().toLocaleDateString());
  const [image, setImage] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);

  function handleImage(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (file) {
      setImage(file);
    }
  }

  async function handleSubmit() {
    if (!title || !description || !date || !image) return;
    setLoading(true);

    const formData = new FormData();
    formData.append("title", title);
    formData.append("description", description);
    formData.append("date", date);
    formData.append("image", image); // As binary

    try {
      const res = await fetch("jejenohayendpoint", {
        method: "POST",
        body: formData,
      });
      const data = await res.json();
      console.log(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="flex flex-col gap-4 p-6 h-full">
      <div className="flex gap-4 justify-around h-1/12">
        <input
          type="text"
          placeholder="Title"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          className="bg-[#A3CEF1] text-[#282A23] w-10/12 rounded p-2"
        />
        <input
          type="text"
          placeholder="Date"
          value={date}
          onChange={(e) => setDate(e.target.value)}
          className="bg-[#A3CEF1] text-[#282A23] w-2/12 rounded p-2"
        />
      </div>
      <textarea
        placeholder="Description"
        value={description}
        onChange={(e) => setDescription(e.target.value)}
        className="bg-[#A3CEF1] text-[#282A23] rounded p-2 h-9/12"
      />
      <div className="flex justify-between p-5 h-2/12 text-[#000000]">
        <input type="file" accept="image/*" onChange={handleImage} />
        <button
          onClick={handleSubmit}
          disabled={loading}
          className="bg-[#7C9EBA] text-[#000000] rounded p-5"
        >
          {loading ? "Submitting..." : "Submit"}
        </button>
      </div>
    </div>
  );
}