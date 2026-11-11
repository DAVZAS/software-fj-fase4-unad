# Sistema Integral de Gestión de Clientes, Servicios y Reservas - Software FJ
## Fase 4: Componente Práctico - Prácticas Simuladas (POO)

**Universidad Nacional Abierta y a Distancia (UNAD)**  
**Escuela de Ciencias Básicas, Tecnología e Ingeniería (ECBTI)**  
**Curso:** Programación Orientada a Objetos (POO)  
**Estudiante:** Sergio Garzón  
**Entorno de desarrollo:** Antigravity / Python 3.13  

---

## 1. Descripción del Proyecto
Este proyecto da cumplimiento a la **Fase 4: Prácticas Simuladas** del curso de POO, basado en los requerimientos del **Anexo 3 - Problemas a desarrollar Fase 4**. Se implementa un sistema para la gestión integral de clientes, catálogo de servicios corporativos y reservas para la compañía **"Software FJ"**.

El desarrollo se enfoca en la robustez de software, asegurando que ante entradas anómalas, violaciones de reglas de negocio o fallos imprevistos, la aplicación capture las excepciones adecuadamente, asiente auditoría en un archivo de eventos (`eventos.log`) y continúe su ejecución sin interrupciones abruptas.

---

## 2. Principios de Programación Orientada a Objetos Aplicados

### A. Abstracción y Encapsulamiento
* **`EntidadBase` (Clase Abstracta):** Superclase que define el identificador numérico protegido (`_id_entidad`) y obliga a una estructura identificable en el dominio.
* **`Cliente`:** Especialización que encapsula los datos personales (`_nombre` y `_correo`). Implementa decoradores `@property` y `@setter` para validar que:
  * El nombre no esté vacío y contenga al menos 3 caracteres.
  * El correo posea estructura básica obligatoria (`@` y dominio con `.`).

### B. Herencia y Polimorfismo
* **`Servicio` (Clase Abstracta):** Define la plantilla base con atributos comunes (`id_servicio`, `nombre_servicio`, `tarifa_base`) y los métodos abstractos:
  * `calcular_costo(horas)`
  * `obtener_descripcion()`
* **Clases Derivadas Especializadas:**
  1. **`ReservaSala`:** Calcula el costo con un recargo del 15% para salas corporativas de más de 10 personas y soporte para descuento empresarial.
  2. **`AlquilerEquipo`:** Liquida tarifa horaria e incluye opción de póliza fija de seguro contra accidentes tecnológicos.
  3. **`AsesoriaEspecializada`:** Liquida horas profesionales de consultoría con discriminación del 19% de IVA colombiano.

### C. Control de Dominio: Clase `Reserva`
* Controla la asociación entre un `Cliente`, un `Servicio` y la duración en horas.
* Gestiona los estados del ciclo de vida (`PENDIENTE`, `CONFIRMADA`, `CANCELADA`).
* Procesa el cálculo delegando polimórficamente al servicio correspondiente y registra los resultados en el log.

### D. Jerarquía de Excepciones Personalizadas
* `ErrorSoftwareFJException`: Clase base de excepción de dominio.
  * `ClienteInvalidoException`: Errores de validación de clientes.
  * `ServicioNoDisponibleException`: Errores en parámetros de servicios o tarifas negativas.
  * `ReservaInvalidaException`: Inconsistencias en duraciones (0 horas o negativas) o fallos de procesamiento.

### E. Auditoría y Persistencia en `eventos.log`
* Implementación del módulo estándar `logging` configurado en formato UTF-8.
* Cada operación (éxitos `[INFO]`, errores de negocio controlados `[WARNING]` y errores críticos `[ERROR]`) queda asentada con marca de tiempo precisa (`YYYY-MM-DD HH:MM:SS`).

---

## 3. Estructura de Archivos del Repositorio

```plaintext
fase4_software_fj/
│
├── sistema_software_fj.py    # Código fuente principal comentado línea a línea
├── eventos.log               # Archivo generado con la auditoría de las 10 operaciones
├── .gitignore                # Reglas de exclusión de archivos temporales
└── README.md                 # Documentación técnica del proyecto
```

---

## 4. Instrucciones de Ejecución

### Requisitos Previos
* Python 3.10 o superior (Probado en Python 3.13).

### Pasos para Ejecutar
1. Clonar el repositorio o ingresar a la carpeta del proyecto:
   ```bash
   git clone <URL_DEL_REPOSITORIO>
   cd fase4_software_fj
   ```
2. Ejecutar el script principal:
   ```bash
   python sistema_software_fj.py
   ```
3. Verificar en la consola la salida de las 10 operaciones simuladas y consultar el archivo generado `eventos.log`.

---

## 5. Resumen de las 10 Operaciones Simuladas

| N.° | Operación | Escenario Probado | Resultado Esperado | Manejo de Excepción / Log |
|---|---|---|---|---|
| **1** | Alta de Cliente Válido | Datos completos y válidos | `[CORRECTO]` Instanciado | `[INFO]` Registrado en log |
| **2** | Alta de Cliente Inválido | Nombre de 2 caracteres ('Al') | `[CAPTURADO]` Rechazado | `ClienteInvalidoException` capturada |
| **3** | Alta de Cliente Inválido | Correo sin `@` ni dominio | `[CAPTURADO]` Rechazado | `ClienteInvalidoException` capturada |
| **4** | Creación de Servicio 1 | ReservaSala (Capacidad 16) | `[CORRECTO]` Instanciado | `[INFO]` Registrado en log |
| **5** | Creación de Servicio Inválido | Tarifa negativa (-$20,000) | `[CAPTURADO]` Rechazado | `ServicioNoDisponibleException` capturada |
| **6** | Creación de Servicio 2 | Asesoría Especializada | `[CORRECTO]` Instanciado | `[INFO]` Registrado en log |
| **7** | Reserva Válida | Sala 16 pax x 4h con descuento | `[ÉXITO]` Confirmada | Cálculo polimórfico y recargo |
| **8** | Reserva Inválida | Duración de 0 horas | `[CAPTURADO]` Rechazado | `ReservaInvalidaException` capturada |
| **9** | Reserva y Cancelación | Alquiler proyector + seguro | `[ÉXITO]` y `[AVISO]` | Estado pasa a `CANCELADA` y se asienta en log |
| **10** | Manejo try-except-finally | Parámetro `None` en cálculo | `[CAPTURADO]` Controlado | Ejecución forzosa de bloque `FINALLY` |

---
*Proyecto elaborado para la UNAD - Curso de Programación Orientada a Objetos 2026.*
