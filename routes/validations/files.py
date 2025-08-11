# -*- coding: utf-8 -*-
"""
Rutas de validación de archivos y directorios.

Dos endpoints:

- ``GET /validations/directory/<path:dir_path>``:
  retorna ``{"exists": true|false}`` para directorios.
- ``GET /validations/file/<path:file_path>``:
  retorna ``{"exists": true|false}`` para archivos.

Las rutas se resuelven contra un *chroot lógico* (``BASE_DIR``) para
evitar *path traversal* y accesos fuera del árbol permitido.
"""

from __future__ import annotations
import os
from pathlib import Path
from typing import Final, Literal, Optional, Union
from flask import Blueprint, Response, jsonify

# Se crea el blueprint
bp: Blueprint = Blueprint("validations", __name__)

# Directorio base permitido (chroot lógico). Usa CWD del proceso,
BASE_DIR: Final[Path] = Path.cwd().resolve()

# region helpers
def resolve_safe_path(raw_path: str) -> Optional[Path]:
    """
    Normaliza y valida una ruta contra ``BASE_DIR``.
    La idea es que quede lo mas seguro posible, ya que puede
    ser usada para dejar la cagá.

    Reglas:
    - Rechaza cadenas vacías, >1024 chars o con NUL.
    - Acepta rutas relativas o absolutas, pero siempre las convierte
      a absolutas dentro del ``BASE_DIR``.
    - Resuelve symlinks y ``..`` con ``os.path.realpath`` para que el
      chequeo de confinamiento sea contra el destino final.
    - Si la ruta resuelta queda fuera de ``BASE_DIR`` ⇒ *no autorizada*.

    :param raw_path:
        Ruta cruda provista por el cliente.
    :returns:
        ``Path`` válido si está dentro de ``BASE_DIR``.
        ``Path()`` (vacío) si es *no autorizada* (fora de scope).
        ``None`` si es *inválida* (input mal formado).
    """
    # valida formato basico y tamaño razonable
    if not raw_path or len(raw_path) > 1024 or "\x00" in raw_path:
        return None

    # arma un candidato absoluto bajo BASE_DIR si vino relativo
    candidate: Path = Path(raw_path)
    if not candidate.is_absolute():
        candidate = BASE_DIR / candidate

    try:
        # realpath resuelve symlinks y '..' a su destino final
        real: Path = Path(os.path.realpath(candidate))
    except OSError:
        # errores del FS se tratan como input inválido
        return None

    try:
        # commonpath garantiza que 'real' permanezca bajo BASE_DIR
        base = str(BASE_DIR)
        real_s = str(real)
        if os.path.commonpath([real_s, base]) != base:
            # fuera del árbol permitido retorna 403
            return Path()
    except ValueError:
        return Path()

    # ruta segura y confinada
    return real


# region endpoints
@bp.route("/directory/<path:dir_path>", methods=["GET"])
def directory_exists(
    dir_path: str,
) -> Union[Response, tuple[Response, Literal[400, 403]]]:
    """
    Verifica si un **directorio** existe dentro de ``BASE_DIR``.

    :param dir_path:
        Ruta del directorio (relativa o absoluta).
    :returns:
        JSON ``{"exists": bool}`` o error ``{"error": str}``.
    """
    # resuelve y valida la ruta contra el chroot lógico
    resolved: Optional[Path] = resolve_safe_path(dir_path)

    # input mal formado da error 400
    if resolved is None:
        return jsonify({"error": "Ruta inválida"}), 400

    # fuera del scope permitido retorna error 403
    if resolved == Path():
        return jsonify({"error": "Ruta no autorizada"}), 403

    # verifica existencia como directorio
    exists: bool = resolved.is_dir()

    # responde de forma uniforme
    return jsonify({"exists": exists})


@bp.route("/file/<path:file_path>", methods=["GET"])
def file_exists(
    file_path: str,
) -> Union[Response, tuple[Response, Literal[400, 403]]]:
    """
    Verifica si un **archivo** existe dentro de ``BASE_DIR``.

    :param file_path:
        Ruta del archivo (relativa o absoluta).
    :returns:
        JSON ``{"exists": bool}`` o error ``{"error": str}``.
    """
    # resuelve y valida la ruta contra el chroot lógico
    resolved: Optional[Path] = resolve_safe_path(file_path)

    # input mal formado da error 400
    if resolved is None:
        return jsonify({"error": "Ruta inválida"}), 400

    # fuera del scope permitido retorna error 403
    if resolved == Path():
        return jsonify({"error": "Ruta no autorizada"}), 403

    # verifica existencia como archivo regular
    exists: bool = resolved.is_file()

    # responde de forma uniforme
    return jsonify({"exists": exists})
