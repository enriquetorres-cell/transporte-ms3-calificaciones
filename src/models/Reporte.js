import mongoose from "mongoose";

export const MOTIVOS = ["lenguaje_ofensivo", "informacion_falsa", "spam", "otro"];

const reporteSchema = new mongoose.Schema(
  {
    calificacion_id: { type: mongoose.Schema.Types.ObjectId, ref: "Calificacion", required: true },
    reportado_por:   { type: Number, required: true },
    motivo:          { type: String, enum: MOTIVOS, required: true },
    detalle:         { type: String, maxlength: 500, default: "" },
    estado:          { type: String, enum: ["pendiente", "revisado", "descartado"], default: "pendiente" }
  },
  {
    timestamps: { createdAt: "creado_en", updatedAt: "actualizado_en" },
    collection: "reportes",
    versionKey: false
  }
);

reporteSchema.index({ calificacion_id: 1, estado: 1 });

export default mongoose.model("Reporte", reporteSchema);
