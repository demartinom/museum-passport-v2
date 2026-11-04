import path from "path";
import { DatabaseSync } from "node:sqlite";

type CountTotal = { total: number };

export default function Home() {
  const dbPath = path.join(process.cwd(), "..", "data", "collection.db");
  const db = new DatabaseSync(dbPath, { readOnly: true });

  const starterCall = db.prepare("SELECT COUNT(*) AS total from objects");
  const result = starterCall.get() as CountTotal;

  return <div>{result.total}</div>;
}
