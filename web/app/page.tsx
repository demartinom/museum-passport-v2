import { dbPool } from "@/lib/db";

export const instant = false;

type Artwork = {
  id: string;
  title: string;
  period: string;
  date_display: string;
  museum_full_name: string;
};

type Props = {
  searchParams: Promise<{ [key: string]: string | string[] | undefined }>;
};

export default async function Home(props: Props) {
  const searchParams = await props.searchParams;

  let start = -10000;
  if (searchParams.start) {
    start = Number(searchParams.start);
  }

  let end = 30000;
  if (searchParams.end) {
    end = Number(searchParams.end);
  }

  const sql =
    "SELECT id, title, date_display, period, museum_full_name FROM objects WHERE date_begin <= $1 AND date_end >= $2 ORDER BY date_begin, id LIMIT 20";

  const result = await dbPool.query<Artwork>(sql, [end, start]);

  const items = result.rows.map((artwork) => (
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
      <p>
        <b>Museum:</b> {artwork.museum_full_name}
      </p>
      <br />
    </div>
  ));

  return (
    <div>
      <form>
        <label>
          Start year{" "}
          <input type="number" name="start" defaultValue={searchParams.start} />
        </label>

        <label>
          End year{" "}
          <input type="number" name="end" defaultValue={searchParams.end} />
        </label>
        <button type="submit">Filter</button>
      </form>
      {items}
    </div>
  );
}
