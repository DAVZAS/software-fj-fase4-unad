"""
========================================================================================
UNIVERSIDAD NACIONAL ABIERTA Y A DISTANCIA - UNAD
ESCUELA DE CIENCIAS BÁSICAS, TECNOLOGÍA E INGENIERÍA (ECBTI)
CURSO: PROGRAMACIÓN ORIENTADA A OBJETOS (POO)
FASE 4: COMPONENTE PRÁCTICO - PRÁCTICAS SIMULADAS
PROYECTO: SISTEMA INTEGRAL DE GESTIÓN DE CLIENTES, SERVICIOS Y RESERVAS ("SOFTWARE FJ")
ESTUDIANTE: SERGIO GARZÓN
LENGUAJE: PYTHON 3.13
========================================================================================
DESCRIPCIÓN GENERAL:
Este programa implementa una solución orientada a objetos pura para la empresa "Software FJ".
Aplica conceptos fundamentales de la POO:
  1. Abstracción y Encapsulamiento (Clases abstractas, propiedades con validación @property/@setter).
  2. Herencia y Polimorfismo (Especialización de servicios y sobreescritura de métodos).
  3. Manejo Robusto de Excepciones (Jerarquía de excepciones personalizadas y bloques try-except-finally).
  4. Persistencia y Auditoría de Eventos (Registro estructurado en archivo 'eventos.log').
  5. Simulación de 10 operaciones de negocio (operaciones válidas e inválidas intencionales).
========================================================================================
"""

import logging
import os
from abc import ABC, abstractmethod
from datetime import datetime

# ======================================================================================
# 1. CONFIGURACIÓN DEL SISTEMA DE AUDITORÍA Y LOGS
# ======================================================================================
# Se establece la ruta del archivo de logs en el directorio del script para evitar fallos de ruta.
DIRECTORIO_ACTUAL = os.path.dirname(os.path.abspath(__file__))
RUTA_LOG = os.path.join(DIRECTORIO_ACTUAL, "eventos.log")

# Configuración básica del módulo logging de Python
logging.basicConfig(
    filename=RUTA_LOG,
    filemode="a",  # Modo append para conservar el historial de eventos
    level=logging.INFO,
    format="%(asctime)s - [%(levelname)s] - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    encoding="utf-8"
)

# Logger específico del sistema
logger = logging.getLogger("SoftwareFJ")


# ======================================================================================
# 2. JERARQUÍA DE EXCEPCIONES PERSONALIZADAS
# ======================================================================================
class ErrorSoftwareFJException(Exception):
    """
    Excepción base para todos los errores de la aplicación Software FJ.
    Permite capturar cualquier error propio del dominio del sistema de forma genérica.
    """
    def __init__(self, mensaje: str, codigo_error: str = "ERR_GRAL"):
        super().__init__(mensaje)
        self.codigo_error = codigo_error
        self.mensaje = mensaje

    def __str__(self):
        return f"[{self.codigo_error}] {self.mensaje}"


class ClienteInvalidoException(ErrorSoftwareFJException):
    """
    Lanzada cuando los datos proporcionados para instanciar o modificar un cliente
    no cumplen las reglas de negocio (longitud del nombre, formato de correo, etc.).
    """
    def __init__(self, mensaje: str):
        super().__init__(mensaje, codigo_error="ERR_CLIENTE_INVALIDO")


class ServicioNoDisponibleException(ErrorSoftwareFJException):
    """
    Lanzada cuando los parámetros de un servicio violan las restricciones operativas
    (tarifas base no positivas, capacidades inválidas de sala, etc.).
    """
    def __init__(self, mensaje: str):
        super().__init__(mensaje, codigo_error="ERR_SERVICIO_INVALIDO")


class ReservaInvalidaException(ErrorSoftwareFJException):
    """
    Lanzada cuando una reserva no puede ser creada o procesada (duración inválida,
    inconsistencias entre cliente y servicio, estado incongruente, etc.).
    """
    def __init__(self, mensaje: str):
        super().__init__(mensaje, codigo_error="ERR_RESERVA_INVALIDA")


# ======================================================================================
# 3. CLASES BASE Y MODELO DE DOMINIO (ABSTRACCIÓN Y ENCAPSULAMIENTO)
# ======================================================================================
class EntidadBase(ABC):
    """
    Clase abstracta base para todas las entidades identificables del sistema.
    Garantiza que toda entidad posea un identificador único numérico protegido.
    """
    def __init__(self, id_entidad: int):
        if not isinstance(id_entidad, int) or id_entidad <= 0:
            raise ErrorSoftwareFJException(
                f"El identificador de entidad '{id_entidad}' debe ser un número entero positivo.",
                codigo_error="ERR_ID_INVALIDO"
            )
        self._id_entidad = id_entidad  # Atributo protegido

    @property
    def id_entidad(self) -> int:
        """Getter para obtener el identificador único."""
        return self._id_entidad


class Cliente(EntidadBase):
    """
    Representa a un cliente dentro de la empresa Software FJ.
    Aplica encapsulamiento estricto mediante getters y setters con validación.
    """
    def __init__(self, id_cliente: int, nombre: str, correo: str):
        super().__init__(id_cliente)
        # Se utilizan los setters para forzar las validaciones desde el constructor
        self.nombre = nombre
        self.correo = correo

    @property
    def nombre(self) -> str:
        """Obtiene el nombre del cliente."""
        return self._nombre

    @nombre.setter
    def nombre(self, valor: str):
        """Valida que el nombre no esté vacío, sea texto y tenga al menos 3 caracteres."""
        if not valor or not isinstance(valor, str) or len(valor.strip()) < 3:
            raise ClienteInvalidoException(
                f"Nombre inválido: '{valor}'. El nombre del cliente debe tener al menos 3 caracteres válidos."
            )
        self._nombre = valor.strip()

    @property
    def correo(self) -> str:
        """Obtiene el correo electrónico del cliente."""
        return self._correo

    @correo.setter
    def correo(self, valor: str):
        """Valida que el correo posea una estructura básica válida con '@' y '.'."""
        if not valor or not isinstance(valor, str):
            raise ClienteInvalidoException("El correo electrónico no puede ser nulo o vacío.")
        valor_limpio = valor.strip()
        if "@" not in valor_limpio or "." not in valor_limpio or valor_limpio.startswith("@") or valor_limpio.endswith("."):
            raise ClienteInvalidoException(
                f"Correo electrónico inválido: '{valor}'. Debe tener una estructura válida (ej. usuario@dominio.com)."
            )
        self._correo = valor_limpio

    def __str__(self) -> str:
        return f"Cliente #{self.id_entidad}: {self.nombre} <{self.correo}>"


# ======================================================================================
# 4. CLASE ABSTRACTA SERVICIO Y POLIMORFISMO DE ESPECIALIDADES
# ======================================================================================
class Servicio(ABC):
    """
    Clase abstracta que define la interfaz común para todos los servicios de Software FJ.
    Exige la implementación de los métodos polimórficos 'calcular_costo' y 'obtener_descripcion'.
    """
    def __init__(self, id_servicio: str, nombre_servicio: str, tarifa_base: float):
        if not id_servicio or not isinstance(id_servicio, str):
            raise ServicioNoDisponibleException("El código del servicio es obligatorio.")
        if not isinstance(tarifa_base, (int, float)) or tarifa_base <= 0:
            raise ServicioNoDisponibleException(
                f"La tarifa base (${tarifa_base}) debe ser un valor numérico estrictamente mayor a 0."
            )
        self.id_servicio = id_servicio.strip().upper()
        self.nombre_servicio = nombre_servicio
        self.tarifa_base = float(tarifa_base)

    @abstractmethod
    def calcular_costo(self, horas: int) -> float:
        """
        Método abstracto polimórfico.
        Calcula el costo total del servicio en función de las horas solicitadas.
        """
        pass

    @abstractmethod
    def obtener_descripcion(self) -> str:
        """
        Método abstracto polimórfico.
        Retorna la descripción técnica y comercial detallada del servicio.
        """
        pass


class ReservaSala(Servicio):
    """
    Servicio especializado: Reserva de salas de juntas y conferencias.
    Aplica recargos por alta capacidad (> 10 personas) y soporte para descuento empresarial.
    """
    def __init__(self, id_servicio: str, capacidad_personas: int, tarifa_base: float = 60000.0):
        super().__init__(id_servicio, "Reserva de Sala de Juntas", tarifa_base)
        if not isinstance(capacidad_personas, int) or capacidad_personas <= 0:
            raise ServicioNoDisponibleException(
                f"La capacidad de la sala ({capacidad_personas}) debe ser un número entero mayor a cero."
            )
        self.capacidad_personas = capacidad_personas

    def calcular_costo(self, horas: int, descuento_empresarial: float = 0.0) -> float:
        """
        Sobreescritura polimórfica:
        - Si la sala supera 10 personas, se añade un 15% por concepto de logística y aire acondicionado.
        - Permite aplicar un porcentaje de descuento empresarial (parámetro opcional/sobrecarga).
        """
        if not isinstance(horas, int) or horas <= 0:
            raise ReservaInvalidaException(f"Las horas solicitadas ({horas}) deben ser un entero positivo.")
        subtotal = self.tarifa_base * horas
        if self.capacidad_personas > 10:
            subtotal *= 1.15  # Recargo del 15% por sala corporativa grande
        # Aplicación de descuento si aplica
        descuento = max(0.0, min(descuento_empresarial, 0.5))  # Límite máximo 50% descuento
        return round(subtotal * (1.0 - descuento), 2)

    def obtener_descripcion(self) -> str:
        return (
            f"[SALA] {self.nombre_servicio} ({self.id_servicio}) - "
            f"Capacidad: {self.capacidad_personas} personas - Tarifa base/h: ${self.tarifa_base:,.0f}"
        )


class AlquilerEquipo(Servicio):
    """
    Servicio especializado: Alquiler de dispositivos tecnológicos (Laptops, proyectores, servidores).
    Permite incluir una póliza de seguro de equipo contra daños accidentales.
    """
    def __init__(self, id_servicio: str, tipo_equipo: str, tarifa_base: float = 35000.0):
        super().__init__(id_servicio, f"Alquiler de {tipo_equipo}", tarifa_base)
        if not tipo_equipo or not isinstance(tipo_equipo, str) or len(tipo_equipo.strip()) < 3:
            raise ServicioNoDisponibleException("El tipo de equipo debe tener una especificación válida.")
        self.tipo_equipo = tipo_equipo.strip()

    def calcular_costo(self, horas: int, seguro_incluido: bool = True) -> float:
        """
        Sobreescritura polimórfica:
        - Tarifa por hora + seguro de amortización único opcional ($15,000 COP).
        """
        if not isinstance(horas, int) or horas <= 0:
            raise ReservaInvalidaException(f"Las horas de alquiler ({horas}) deben ser un entero positivo.")
        subtotal = self.tarifa_base * horas
        if seguro_incluido:
            subtotal += 15000.0  # Póliza de protección tecnológica
        return round(subtotal, 2)

    def obtener_descripcion(self) -> str:
        return (
            f"[EQUIPO] {self.nombre_servicio} ({self.id_servicio}) - "
            f"Item: {self.tipo_equipo} - Tarifa base/h: ${self.tarifa_base:,.0f} (Seguro opcional: $15.000)"
        )


class AsesoriaEspecializada(Servicio):
    """
    Servicio especializado: Consultoría técnica o asesoría en arquitectura de software.
    Permite la liquidación con o sin Impuesto al Valor Agregado (IVA 19%).
    """
    def __init__(self, id_servicio: str, especialista: str, tarifa_base: float = 120000.0):
        super().__init__(id_servicio, "Asesoría Especializada en Desarrollo", tarifa_base)
        if not especialista or not isinstance(especialista, str) or len(especialista.strip()) < 3:
            raise ServicioNoDisponibleException("El nombre del consultor o especialista es obligatorio.")
        self.especialista = especialista.strip()

    def calcular_costo(self, horas: int, aplicar_iva: bool = True) -> float:
        """
        Sobreescritura polimórfica:
        - Calcula el valor total de horas profesionales liquidando el 19% de IVA según corresponda.
        """
        if not isinstance(horas, int) or horas <= 0:
            raise ReservaInvalidaException(f"Las horas de asesoría ({horas}) deben ser un entero positivo.")
        subtotal = self.tarifa_base * horas
        if aplicar_iva:
            subtotal *= 1.19  # IVA legal colombiano del 19%
        return round(subtotal, 2)

    def obtener_descripcion(self) -> str:
        return (
            f"[ASESORÍA] {self.nombre_servicio} ({self.id_servicio}) - "
            f"Consultor: {self.especialista} - Tarifa base/h: ${self.tarifa_base:,.0f} (IVA 19% aplicable)"
        )


# ======================================================================================
# 5. CLASE CONTROLADORA: RESERVA
# ======================================================================================
class Reserva:
    """
    Gestiona el ciclo de vida de una reserva para un cliente y servicio determinados.
    Controla estados, liquidación de costos y registro de auditoría en logs.
    """
    ESTADOS_VALIDOS = ("PENDIENTE", "CONFIRMADA", "CANCELADA", "COMPLETADA")

    def __init__(self, id_reserva: int, cliente: Cliente, servicio: Servicio, horas: int):
        if not isinstance(id_reserva, int) or id_reserva <= 0:
            raise ReservaInvalidaException(f"ID de reserva inválido: {id_reserva}.")
        if not isinstance(cliente, Cliente):
            raise ReservaInvalidaException("La reserva requiere un objeto Cliente válido.")
        if not isinstance(servicio, Servicio):
            raise ReservaInvalidaException("La reserva requiere un objeto Servicio válido.")
        if not isinstance(horas, int) or horas <= 0:
            raise ReservaInvalidaException(f"La duración de la reserva debe ser de al menos 1 hora (recibido: {horas}).")

        self.id_reserva = id_reserva
        self.cliente = cliente
        self.servicio = servicio
        self.horas = horas
        self.estado = "PENDIENTE"
        self.costo_total = 0.0
        self.fecha_creacion = datetime.now()

    def procesar_reserva(self, **kwargs) -> float:
        """
        Calcula el costo polimórficamente, actualiza el estado a CONFIRMADA y registra en el log.
        Si ocurre algún error inesperado, cancela la reserva y lanza ReservaInvalidaException.
        """
        try:
            # Llamado polimórfico a calcular_costo aceptando kwargs opcionales
            self.costo_total = self.servicio.calcular_costo(self.horas, **kwargs)
            self.estado = "CONFIRMADA"
            mensaje_exito = (
                f"Reserva #{self.id_reserva} CONFIRMADA con éxito | "
                f"Cliente: '{self.cliente.nombre}' | Servicio: '{self.servicio.nombre_servicio}' | "
                f"Horas: {self.horas} | Costo Total: ${self.costo_total:,.2f} COP"
            )
            logger.info(mensaje_exito)
            print(f"  [ÉXITO] {mensaje_exito}")
            return self.costo_total

        except Exception as error:
            self.estado = "CANCELADA"
            mensaje_error = f"Fallo al procesar la Reserva #{self.id_reserva}: {str(error)}"
            logger.error(mensaje_error)
            raise ReservaInvalidaException(mensaje_error) from error

    def cancelar_reserva(self, motivo: str = "Solicitud voluntaria del cliente"):
        """Cancela la reserva y asienta el registro en auditoría."""
        self.estado = "CANCELADA"
        mensaje_cancelacion = f"Reserva #{self.id_reserva} CANCELADA. Motivo: {motivo}."
        logger.warning(mensaje_cancelacion)
        print(f"  [AVISO] {mensaje_cancelacion}")

    def __str__(self) -> str:
        return (
            f"Reserva #{self.id_reserva} [{self.estado}] - {self.cliente.nombre} | "
            f"{self.servicio.nombre_servicio} ({self.horas}h) | Total: ${self.costo_total:,.2f}"
        )


# ======================================================================================
# 6. BANCO DE PRUEBAS CONTROLADAS (SIMULACIÓN DE 10 OPERACIONES DE NEGOCIO)
# ======================================================================================
def ejecutar_simulacion():
    """
    Ejecuta 10 operaciones de negocio consecutivas combinando casos exitosos y
    errores controlados mediante bloques try-except-finally.
    Garantiza que la aplicación maneje cada situación sin detener su ejecución.
    """
    print("\n" + "=" * 80)
    print("      SISTEMA INTEGRAL DE GESTIÓN 'SOFTWARE FJ' - FASE 4 PRÁCTICAS SIMULADAS")
    print("      Curso: Programación Orientada a Objetos - UNAD 2026")
    print("=" * 80 + "\n")

    logger.info("================ INICIO DE CICLO DE SIMULACIÓN (10 OPERACIONES) ================")

    # ----------------------------------------------------------------------------------
    # OPERACIÓN 1: Creación de Cliente Válido (Éxito)
    # ----------------------------------------------------------------------------------
    print("Operación 1: Instanciación de Cliente Válido (Sergio Garzón)...")
    try:
        c1 = Cliente(id_cliente=1, nombre="Sergio Garzón", correo="sergio.garzon@unad.edu.co")
        logger.info(f"Op 1 completada con éxito: {c1}")
        print(f"  [CORRECTO] {c1}")
    except ErrorSoftwareFJException as e:
        logger.error(f"Op 1 falló: {e}")
        print(f"  [ERROR]: {e}")

    # ----------------------------------------------------------------------------------
    # OPERACIÓN 2: Cliente Inválido - Longitud de Nombre Insuficiente (Excepción Controlada)
    # ----------------------------------------------------------------------------------
    print("\nOperación 2: Creación de Cliente con Nombre Inválido ('Al')...")
    try:
        c_inv1 = Cliente(id_cliente=2, nombre="Al", correo="al@dominio.com")
        print(f"  [INCORRECTO]: No debió crearse {c_inv1}")
    except ClienteInvalidoException as e:
        logger.warning(f"Op 2 error controlado: {e}")
        print(f"  [CAPTURADO] Excepción controlada: {e}")

    # ----------------------------------------------------------------------------------
    # OPERACIÓN 3: Cliente Inválido - Formato de Correo Erróneo (Excepción Controlada)
    # ----------------------------------------------------------------------------------
    print("\nOperación 3: Creación de Cliente con Correo sin Dominio/Arroba...")
    try:
        c_inv2 = Cliente(id_cliente=3, nombre="Carlos Rodríguez", correo="carlos_rodriguez_sin_correo")
        print(f"  [INCORRECTO]: No debió crearse {c_inv2}")
    except ClienteInvalidoException as e:
        logger.warning(f"Op 3 error controlado: {e}")
        print(f"  [CAPTURADO] Excepción controlada: {e}")

    # ----------------------------------------------------------------------------------
    # OPERACIÓN 4: Creación de Servicio 1 - ReservaSala Válida (Éxito)
    # ----------------------------------------------------------------------------------
    print("\nOperación 4: Creación de Servicio de Sala de Juntas Corporativa (Capacidad 16)...")
    try:
        s1 = ReservaSala(id_servicio="SALA-101", capacidad_personas=16, tarifa_base=75000.0)
        logger.info(f"Op 4 servicio creado: {s1.obtener_descripcion()}")
        print(f"  [CORRECTO] {s1.obtener_descripcion()}")
    except ServicioNoDisponibleException as e:
        logger.error(f"Op 4 falló: {e}")
        print(f"  [ERROR]: {e}")

    # ----------------------------------------------------------------------------------
    # OPERACIÓN 5: Creación de Servicio Inválido - Tarifa Base Negativa (Excepción Controlada)
    # ----------------------------------------------------------------------------------
    print("\nOperación 5: Creación de Servicio con Tarifa Negativa (-$20,000 COP)...")
    try:
        s_inv = AlquilerEquipo(id_servicio="EQ-ERR", tipo_equipo="Servidor Dell", tarifa_base=-20000.0)
        print(f"  [INCORRECTO]: No debió crearse {s_inv}")
    except ServicioNoDisponibleException as e:
        logger.warning(f"Op 5 error controlado: {e}")
        print(f"  [CAPTURADO] Excepción controlada: {e}")

    # ----------------------------------------------------------------------------------
    # OPERACIÓN 6: Creación de Servicio 2 - Asesoría Especializada Válida (Éxito)
    # ----------------------------------------------------------------------------------
    print("\nOperación 6: Creación de Servicio de Asesoría Técnica de Software...")
    try:
        s2 = AsesoriaEspecializada(id_servicio="ASES-301", especialista="Ing. de Software Senior", tarifa_base=130000.0)
        logger.info(f"Op 6 servicio creado: {s2.obtener_descripcion()}")
        print(f"  [CORRECTO] {s2.obtener_descripcion()}")
    except ServicioNoDisponibleException as e:
        logger.error(f"Op 6 falló: {e}")
        print(f"  [ERROR]: {e}")

    # ----------------------------------------------------------------------------------
    # OPERACIÓN 7: Procesamiento de Reserva Válida (Éxito - Sala con Recargo de Capacidad)
    # ----------------------------------------------------------------------------------
    print("\nOperación 7: Procesamiento de Reserva #101 (Sala 16 pax por 4 horas)...")
    try:
        reserva1 = Reserva(id_reserva=101, cliente=c1, servicio=s1, horas=4)
        # Se procesa con un 10% de descuento corporativo
        reserva1.procesar_reserva(descuento_empresarial=0.10)
    except ReservaInvalidaException as e:
        logger.error(f"Op 7 falló: {e}")
        print(f"  [ERROR]: {e}")

    # ----------------------------------------------------------------------------------
    # OPERACIÓN 8: Reserva Inválida - Duración en Cero Horas (Excepción Controlada)
    # ----------------------------------------------------------------------------------
    print("\nOperación 8: Creación de Reserva con Duración Inadmisible (0 horas)...")
    try:
        reserva_inv = Reserva(id_reserva=102, cliente=c1, servicio=s2, horas=0)
        reserva_inv.procesar_reserva()
    except ReservaInvalidaException as e:
        logger.warning(f"Op 8 error controlado: {e}")
        print(f"  [CAPTURADO] Excepción controlada: {e}")

    # ----------------------------------------------------------------------------------
    # OPERACIÓN 9: Alquiler de Equipo, Reserva y Cancelación Voluntaria (Éxito)
    # ----------------------------------------------------------------------------------
    print("\nOperación 9: Alquiler de Videoproyector Láser 4K y Cancelación Controlada...")
    try:
        s3 = AlquilerEquipo(id_servicio="EQ-204", tipo_equipo="Videoproyector Láser 4K", tarifa_base=40000.0)
        reserva3 = Reserva(id_reserva=103, cliente=c1, servicio=s3, horas=5)
        reserva3.procesar_reserva(seguro_incluido=True)
        # Se efectúa la cancelación por decisión del cliente
        reserva3.cancelar_reserva(motivo="Reprogramación de evento empresarial")
    except ErrorSoftwareFJException as e:
        logger.error(f"Op 9 falló: {e}")
        print(f"  [ERROR]: {e}")

    # ----------------------------------------------------------------------------------
    # OPERACIÓN 10: Demostración Integral try-except-finally (Manejo de Error Inesperado)
    # ----------------------------------------------------------------------------------
    print("\nOperación 10: Prueba crítica de robustez y ejecución del bloque FINALLY...")
    recurso_conectado = True
    try:
        print("  -> Recurso en memoria activado para auditoría.")
        # Se invoca deliberadamente el cálculo pasando un parámetro de tipo erróneo (None)
        print("  -> Ejecutando cálculo de costo con argumento de tipo nulo (TypeError)...")
        _ = s2.calcular_costo(horas=None)
    except TypeError as te:
        mensaje_tipo = f"TypeError capturado oportunamente: Argumento de tipo no compatible ({te})"
        logger.error(mensaje_tipo)
        print(f"  [CAPTURADO] {mensaje_tipo}")
    except Exception as ex_gen:
        logger.error(f"Error imprevisto: {ex_gen}")
        print(f"  [CAPTURADO]: {ex_gen}")
    finally:
        recurso_conectado = False
        logger.info("Op 10: Bloque FINALLY ejecutado. Liberación de recursos exitosa.")
        print(f"  -> [BLOQUE FINALLY] Recursos liberados con éxito. Estado recurso: {recurso_conectado}")

    print("\n" + "=" * 80)
    print("RESUMEN DE LA SIMULACIÓN:")
    print("  * Total de operaciones ejecutadas: 10/10")
    print("  * Comportamiento del sistema: Robusto y resiliente (0 interrupciones abruptas)")
    print(f"  * Archivo de auditoría generado: {RUTA_LOG}")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    ejecutar_simulacion()
