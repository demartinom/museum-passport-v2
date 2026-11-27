import { Pool } from "pg";

if (!process.env.DATABASE_URL) {
  throw new Error("DATABASE_URL is not set");
}

export const dbPool = new Pool({ connectionString: process.env.DATABASE_URL });
