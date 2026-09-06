import mongoose from "mongoose";
import app from "./app.js";

const PORT = Number(process.env.PORT) || 8003;
const MONGO_URI = process.env.MONGO_URI || "mongodb://localhost:27017/calificaciones_db";

async function main() {
  await mongoose.connect(MONGO_URI, { serverSelectionTimeoutMS: 10000 });
  console.log("MongoDB conectado");

  app.listen(PORT, "0.0.0.0", () =>
    console.log(`MS3 escuchando en http://0.0.0.0:${PORT}${process.env.PREFIX || "/ms3"}`)
  );
}

main().catch((e) => {
  console.error("No se pudo iniciar MS3:", e.message);
  process.exit(1);
});

for (const s of ["SIGINT", "SIGTERM"]) {
  process.on(s, async () => {
    await mongoose.connection.close();
    process.exit(0);
  });
}
