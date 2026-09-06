// Middleware de error unico: traduce fallos de mongoose al formato del Contrato Cero.
export function noEncontrado(_req, res) {
  res.status(404).json({ error: "Ruta no encontrada" });
}

export function manejadorErrores(err, _req, res, _next) {
  if (err.name === "ValidationError") {
    return res.status(400).json({ error: "Datos invalidos", detalle: err.message });
  }
  if (err.name === "CastError") {
    return res.status(400).json({ error: "Identificador con formato invalido", detalle: err.value });
  }
  if (err.code === 11000) {
    return res.status(409).json({ error: "El viaje ya fue calificado", detalle: JSON.stringify(err.keyValue) });
  }
  console.error(err);
  res.status(500).json({ error: "Error interno del servidor" });
}

// Envuelve controladores async para no repetir try/catch en cada uno.
export const asyncH = (fn) => (req, res, next) => Promise.resolve(fn(req, res, next)).catch(next);
