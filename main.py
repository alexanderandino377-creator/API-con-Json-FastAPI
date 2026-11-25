import json
from pathlib import Path
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field

app = FastAPI(
    title="API de Películas",
    version="1.0.0",
    description="API CRUD de películas con persistencia en archivo JSON.",
)

ARCHIVO_JSON = Path("peliculas.json")


# Modelo Pydantic SIN el id (para crear y editar)
class PeliculaEntrada(BaseModel):
  titulo: str = Field(..., min_length=1, examples=["Matrix"])
  director: str = Field(..., min_length=1, examples=["Lana y Lilly Wachowski"])
  anio: int = Field(..., ge=1888, le=2100, examples=[1999])
  vista: bool = Field(default=False, examples=[True])


# Funciones auxiliares para leer y escribir en el JSON
def leer_peliculas() -> list[dict]:
  if not ARCHIVO_JSON.exists():
    return []
  with ARCHIVO_JSON.open("r", encoding="utf-8") as archivo:
    return json.load(archivo)


def guardar_peliculas(peliculas: list[dict]) -> None:
  with ARCHIVO_JSON.open("w", encoding="utf-8") as archivo:
    json.dump(peliculas, archivo, ensure_ascii=False, indent=2)


# 1. LISTAR todas las películas
@app.get("/peliculas")
def listar_peliculas():
  return leer_peliculas()


# 2. BUSCAR película por ID
@app.get("/peliculas/{pelicula_id}")
def obtener_pelicula(pelicula_id: int):
  peliculas = leer_peliculas()
  for pelicula in peliculas:
    if pelicula["id"] == pelicula_id:
      return pelicula
  raise HTTPException(
      status_code=status.HTTP_404_NOT_FOUND,
      detail=f"No existe ninguna película con id {pelicula_id}",
  )


# 3. AGREGAR una nueva película (la API calcula el id)
@app.post("/peliculas", status_code=status.HTTP_201_CREATED)
def agregar_pelicula(datos: PeliculaEntrada):
  peliculas = leer_peliculas()
  nuevo_id = max((p["id"] for p in peliculas), default=0) + 1

  nueva_pelicula = {
      "id": nuevo_id,
      **datos.model_dump(),
  }
  peliculas.append(nueva_pelicula)
  guardar_peliculas(peliculas)
  return nueva_pelicula


# 4. EDITAR una película existente por ID
@app.put("/peliculas/{pelicula_id}")
def editar_pelicula(pelicula_id: int, datos: PeliculaEntrada):
  peliculas = leer_peliculas()
  for indice, pelicula in enumerate(peliculas):
    if pelicula["id"] == pelicula_id:
      pelicula_actualizada = {
          "id": pelicula_id,
          **datos.model_dump(),
      }
      peliculas[indice] = pelicula_actualizada
      guardar_peliculas(peliculas)
      return pelicula_actualizada

  raise HTTPException(
      status_code=status.HTTP_404_NOT_FOUND,
      detail=f"No existe ninguna película con id {pelicula_id}",
  )


# 5. BORRAR una película por ID
@app.delete("/peliculas/{pelicula_id}", status_code=status.HTTP_204_NO_CONTENT)
def borrar_pelicula(pelicula_id: int):
  peliculas = leer_peliculas()
  for indice, pelicula in enumerate(peliculas):
    if pelicula["id"] == pelicula_id:
      peliculas.pop(indice)
      guardar_peliculas(peliculas)
      return

  raise HTTPException(
      status_code=status.HTTP_404_NOT_FOUND,
      detail=f"No existe ninguna película con id {pelicula_id}",
  )