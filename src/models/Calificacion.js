import mongoose from "mongoose";

export const TAGS = [
  "puntual", "auto_limpio", "conduccion_segura", "amable",
  "musica_agradable", "ruta_eficiente", "tarde", "brusco"
];

const calificacionSchema = new mongoose.Schema(
  {
    viaje_id:     { type: Number, required: true, unique: true },
    pasajero_id:  { type: Number, required: true, index: true },
    conductor_id: { type: Number, required: true, index: true },
    rating:       { type: Number, required: true, min: 1, max: 5 },
    tags:         { type: [String], enum: TAGS, default: [] },
    comentario:   { type: String, maxlength: 500, default: "" },
    idioma:       { type: String, default: "es" },
    distrito_origen:  { type: String },
    distrito_destino: { type: String },
    anonimo:      { type: Boolean, default: false },
    respuesta_conductor: {
      texto: { type: String, maxlength: 500 },
      fecha: { type: Date }
    },
    moderacion: {
      estado:   { type: String, enum: ["publicado", "oculto", "en_revision"], default: "publicado" },
      reportes: { type: Number, default: 0 }
    }
  },
  {
    timestamps: { createdAt: "creado_en", updatedAt: "actualizado_en" },
    collection: "calificaciones",
    versionKey: false
  }
);

calificacionSchema.index({ conductor_id: 1, creado_en: -1 });
calificacionSchema.index({ tags: 1 });
calificacionSchema.index({ comentario: "text" }, { default_language: "spanish" });

export default mongoose.model("Calificacion", calificacionSchema);
