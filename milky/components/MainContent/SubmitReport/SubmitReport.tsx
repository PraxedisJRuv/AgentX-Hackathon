import { useState } from "react";
import { createReport, runReport } from "../../../lib/api";

type Props = {
  onSubmitted?: (reportId: string) => void;
};

export default function SubmitReport({ onSubmitted }: Props) {
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [date, setDate] = useState(new Date().toLocaleDateString());
  const [image, setImage] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  function handleImage(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (file) {
      setImage(file);
    }
  }

  function fileToBase64(file: File): Promise<string> {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = () => {
        const result = reader.result as string;
        // Strip the data URL prefix (e.g. "data:image/jpeg;base64,")
        resolve(result.split(",")[1]);
      };
      reader.onerror = reject;
      reader.readAsDataURL(file);
    });
  }

  async function handleSubmit() {
    if (!title || !description || !date) return;
    setLoading(true);
    setError(null);

    try {
      const images_base64 = image ? [await fileToBase64(image)] : [];
      const { report_id } = await createReport({
        name: title,
        description,
        issue_date: date,
        images_base64,
      });
      // Fire-and-forget the agent run; don't await the full SSE stream
      runReport(report_id).catch(() => {});
      onSubmitted?.(report_id);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong");
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
      {error && <p className="text-red-600 text-sm">{error}</p>}
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