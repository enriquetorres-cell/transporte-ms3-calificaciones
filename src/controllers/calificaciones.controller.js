import Calificacion from "../models/Calificacion.js";
import Reporte from "../models/Reporte.js";

const LIMITE_MAX = 100;

function paginacion(query) {
  const page = Math.max(1, Number(query.page) || 1);
  const limit = Math.min(LIMITE_MAX, Math.max(1, Number(query.limit) || 20));
  return { page, limit, skip: (page - 1) * limit };
}

// Valida contra MS2 que el viaje exista y este finalizado.
// Se apaga con VALIDAR_VIAJE=false para que la demo no dependa de MS2.
async function viajeEsValido(viaje_id) {
  if (process.env.VALIDAR_VIAJE !== "true") return true;
  const ctrl = new AbortController();
  const t = setTimeout(() => ctrl.abort(), 5000);
  try {
    const r = await fetch(`${process.env.MS2_URL}/viajes/${viaje_id}`, { signal: ctrl.signal });
    if (!r.ok) return false;
    const viaje = await r.json();
    return viaje.estado === "finalizado";
  } catch {
    return true; // MS2 caido: no bloqueamos la creacion, solo dejamos de validar
  } finally {
    clearTimeout(t);
  }
}

export async function crear(req, res) {
  const { viaje_id } = req.body;
  if (!(await viajeEsValido(viaje_id))) {
    return res.status(422).json({ error: "El viaje no existe o no esta finalizado" });
  }
  const creada = await Calificacion.create(req.body);
  res.status(201).json(creada);
}

export async function listar(req, res) {
  const { conductor_id, pasajero_id, min_rating, tag, q } = req.query;
  const { page, limit, skip } = paginacion(req.query);

  const filtro = {};
  if (conductor_id) filtro.conductor_id = Number(conductor_id);
  if (pasajero_id)  filtro.pasajero_id = Number(pasajero_id);
  if (min_rating)   filtro.rating = { $gte: Number(min_rating) };
  if (tag)          filtro.tags = tag;
  if (q)            filtro.$text = { $search: q };

  const [items, total] = await Promise.all([
    Calificacion.find(filtro).sort({ creado_en: -1 }).skip(skip).limit(limit).lean(),
    Calificacion.countDocuments(filtro)
  ]);

  res.json({ total, page, limit, items });
}

export async function obtener(req, res) {
  const doc = await Calificacion.findById(req.params.id).lean();
  if (!doc) return res.status(404).json({ error: "Calificacion no encontrada" });
  res.json(doc);
}

export async function actualizar(req, res) {
  const permitido = ["comentario", "rating", "tags", "anonimo", "respuesta_conductor", "moderacion"];
  const cambios = {};
  for (const k of permitido) if (k in req.body) cambios[k] = req.body[k];

  const doc = await Calificacion.findByIdAndUpdate(req.params.id, cambios, {
    new: true, runValidators: true
  }).lean();
  if (!doc) return res.status(404).json({ error: "Calificacion no encontrada" });
  res.json(doc);
}

export async function eliminar(req, res) {
  const doc = await Calificacion.findByIdAndDelete(req.params.id);
  if (!doc) return res.status(404).json({ error: "Calificacion no encontrada" });
  await Reporte.deleteMany({ calificacion_id: doc._id });
  res.status(204).send();
}

// Consulta estrella: agregacion con $facet sobre las 22k calificaciones sembradas.
// Un solo recorrido de la coleccion devuelve promedio, distribucion y top de tags.
export async function resumenConductor(req, res) {
  const conductor_id = Number(req.params.id);
  if (Number.isNaN(conductor_id)) {
    return res.status(400).json({ error: "conductor_id debe ser un numero" });
  }

  const [datos] = await Calificacion.aggregate([
    { $match: { conductor_id, "moderacion.estado": "publicado" } },
    { $facet: {
        general: [
          { $group: { _id: null, total: { $sum: 1 }, promedio: { $avg: "$rating" } } }
        ],
        distribucion: [
          { $group: { _id: "$rating", n: { $sum: 1 } } },
          { $sort: { _id: 1 } }
        ],
        top_tags: [
          { $unwind: "$tags" },
          { $group: { _id: "$tags", veces: { $sum: 1 } } },
          { $sort: { veces: -1 } },
          { $limit: 5 }
        ]
    }}
  ]);

  const general = datos?.general?.[0];
  if (!general) return res.status(404).json({ error: "El conductor no tiene calificaciones" });

  const distribucion = { 1: 0, 2: 0, 3: 0, 4: 0, 5: 0 };
  for (const d of datos.distribucion) distribucion[d._id] = d.n;

  res.json({
    conductor_id,
    total: general.total,
    promedio: Math.round(general.promedio * 100) / 100,
    distribucion,
    top_tags: datos.top_tags.map((t) => ({ tag: t._id, veces: t.veces }))
  });
}
