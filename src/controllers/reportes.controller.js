import Reporte from "../models/Reporte.js";
import Calificacion from "../models/Calificacion.js";

export async function crear(req, res) {
  const calificacion = await Calificacion.findById(req.body.calificacion_id);
  if (!calificacion) return res.status(404).json({ error: "La calificacion no existe" });

  const reporte = await Reporte.create(req.body);
  calificacion.moderacion.reportes += 1;
  if (calificacion.moderacion.reportes >= 3) calificacion.moderacion.estado = "en_revision";
  await calificacion.save();

  res.status(201).json(reporte);
}

export async function listar(req, res) {
  const page = Math.max(1, Number(req.query.page) || 1);
  const limit = Math.min(100, Number(req.query.limit) || 20);
  const filtro = req.query.estado ? { estado: req.query.estado } : {};

  const [items, total] = await Promise.all([
    Reporte.find(filtro).sort({ creado_en: -1 }).skip((page - 1) * limit).limit(limit).lean(),
    Reporte.countDocuments(filtro)
  ]);
  res.json({ total, page, limit, items });
}
