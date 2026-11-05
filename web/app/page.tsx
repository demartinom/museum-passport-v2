import path from "path";
import { DatabaseSync } from "node:sqlite";

type Artwork = {
  id: string;
  title: string;
  period: string;
  date_display: string;
};

export default function Home() {
  const dbPath = path.join(process.cwd(), "..", "data", "collection.db");
  const db = new DatabaseSync(dbPath, { readOnly: true });

  const starterCall = db.prepare(
    "SELECT id, title, date_display, period FROM objects WHERE date_begin < 1900 LIMIT 20",
  );
  const result = starterCall.all() as Artwork[];
  const items = result.map((artwork) => (
    <div key={artwork.id}>
      <p>
        <b>Title:</b> {artwork.title}
      </p>
      {artwork.date_display && (
        <p>
          <b>Date:</b> {artwork.date_display}
        </p>
      )}
      <p>
        <b>Period:</b> {artwork.period}
      </p>
      <br />
    </div>
  ));

  return <div>{items}</div>;
}
