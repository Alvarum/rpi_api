# -*- coding: utf-8 -*-
"""
Configuración tipada y validada (sin pydantic).

Lee variables desde entorno/.env, aplica defaults y valida
estrictamente host/port. Falla rápido con mensajes claros.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from ipaddress import ip_address
from typing import Final, Optional
from dotenv import load_dotenv  # type: ignore

# pylint: disable= W0718
load_dotenv()

DEFAULT_HOST: Final[str] = "0.0.0.0"
DEFAULT_PORT: Final[int] = 5000


@dataclass(frozen=True)
class NetworkConfig:
    """
    Configuración de red validada, clase inmutable que contiene host y
    port.

    :ivar host: Dirección de escucha (IPv4 válida o 0.0.0.0).
    :ivar port: Puerto TCP (1..65535).
    """

    host: str
    port: int


def _parse_host(raw: Optional[str] , default: str) -> str:
    """
    Parsea y valida el host.

    :param raw: Valor crudo desde entorno.
    :param default: Valor por defecto.
    :returns: Host válido.
    :raises ValueError: Si el host es inválido.
    """
    host = (raw or default).strip()
    if host == "0.0.0.0":
        return host
    try:
        ip_address(host)
    except Exception as exc:
        raise ValueError(
            f"GUARDIAN_API_HOST inválido: {host!r}"
        ) from exc
    return host


def _parse_port(raw: str | None, default: int) -> int:
    """
    Parsea y valida el puerto (1..65535).

    :param raw: Valor crudo desde entorno.
    :param default: Valor por defecto.
    :returns: Puerto válido.
    :raises ValueError: Si el puerto es inválido.
    """
    if not raw:
        return default
    try:
        port = int(raw)
    except ValueError as exc:
        raise ValueError("GUARDIAN_API_PORT debe ser entero.") from exc
    if not (1 <= port <= 65535):
        raise ValueError("GUARDIAN_API_PORT fuera de rango 1..65535.")
    return port


def load_settings() -> NetworkConfig:
    """
    Carga y valida configuración desde entorno/.env.

    :returns: Configuración de red validada.
    :rtype: NetworkConfig
    :raises SystemExit: Si la validación falla.
    """
    try:
        host = _parse_host(os.getenv("GUARDIAN_API_HOST"), DEFAULT_HOST)
        port = _parse_port(os.getenv("GUARDIAN_API_PORT"), DEFAULT_PORT)
        return NetworkConfig(host=host, port=port)
    except ValueError as err:
        # Falla rápido; systemd lo verá como on-failure si así lo configuras
        raise SystemExit(f"Configuración inválida: {err}") from err
