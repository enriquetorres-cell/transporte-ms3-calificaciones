import express from "express";
import swaggerUi from "swagger-ui-express";
import YAML from "yamljs";
import { fileURLToPath } from "node:url";
import path from "node:path";

import router from "./routes/index.js";
import { noEncontrado, manejadorErrores } from "./middleware/errores.js";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const PREFIX = process.env.PREFIX || "/ms3";

const app = express();
app.use(express.json());

// Swagger UI en /ms3/docs
const openapi = YAML.load(path.join(__dirname, "..", "docs", "openapi.yaml"));
app.use(`${PREFIX}/docs`, swaggerUi.serve, swaggerUi.setup(openapi));

// Todas las rutas cuelgan del prefijo (clausula 2.1 del Contrato Cero)
app.use(PREFIX, router);

app.use(noEncontrado);
app.use(manejadorErrores);

export default app;
