import path from "path";
import { DatabaseSync } from "node:sqlite";

export const instant = false;

type Artwork = {
  id: string;
  title: string;
  period: string;
  date_display: string;
};

type Props = {
  searchParams: Promise<{ [key: string]: string | string[] | undefined }>;
};

export default async function Home(props: Props) {
  const searchParams = await props.searchParams;
  const startParam = Number(searchParams.start);
  const endParam = Number(searchParams.end);

  const dbPath = path.join(process.cwd(), "..", "data", "collection.db");
  const db = new DatabaseSync(dbPath, { readOnly: true });

  const dbCall = db.prepare(
    "SELECT id, title, date_display, period FROM objects WHERE date_begin <= :end AND date_end >= :start",
  );

  const result = dbCall.all({
    start: startParam,
    end: endParam,
  }) as Artwork[];
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

  return (
    <div>
      <form>
        <label>Start year</label>
        <input type="number" name="start" />
        <label>End year</label>
        <input type="number" name="end" />
        <button type="submit">Filter</button>
      </form>

      <p>Results Length: {result.length}</p>
      {items}
    </div>
  );
}
