import { Router } from "express";
import { asyncH } from "../middleware/errores.js";
import * as cal from "../controllers/calificaciones.controller.js";
import * as rep from "../controllers/reportes.controller.js";

const router = Router();

router.get("/health", (_req, res) =>
  res.json({ status: "ok", servicio: "ms3" })
);

router.post("/calificaciones",        asyncH(cal.crear));
router.get("/calificaciones",         asyncH(cal.listar));
router.get("/calificaciones/:id",     asyncH(cal.obtener));
router.patch("/calificaciones/:id",   asyncH(cal.actualizar));
router.delete("/calificaciones/:id",  asyncH(cal.eliminar));

router.get("/conductores/:id/resumen", asyncH(cal.resumenConductor));

router.post("/reportes", asyncH(rep.crear));
router.get("/reportes",  asyncH(rep.listar));

export default router;
