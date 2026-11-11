# UNIVERSIDAD NACIONAL ABIERTA Y A DISTANCIA - UNAD
## ESCUELA DE CIENCIAS BÁSICAS, TECNOLOGÍA E INGENIERÍA (ECBTI)
### CURSO DE PROGRAMACIÓN ORIENTADA A OBJETOS (301305)

---

# INFORME DE PRÁCTICA SIMULADA - FASE 4: COMPONENTE PRÁCTICO
## IMPLEMENTACIÓN DEL SISTEMA INTEGRAL DE GESTIÓN PARA LA EMPRESA "SOFTWARE FJ"

**Estudiante:** Sergio Garzón  
**Código / Identificación:** [Ingresar número de documento]  
**Grupo Colaborativo:** [Ingresar número de grupo]  
**Tutor:** [Ingresar nombre del tutor]  
**Fecha:** Noviembre de 2026  
**Ciudad:** [Ingresar ciudad], Colombia  

---

## 1. INTRODUCCIÓN

En la ingeniería de software actual, el paradigma de la Programación Orientada a Objetos (POO) constituye uno de los estándares más sólidos para el modelado, diseño y construcción de soluciones computacionales escalables, modulares y mantenibles. Más allá de estructurar entidades mediante clases y objetos, el desarrollo de aplicaciones para entornos empresariales de misión crítica exige una alta capacidad de resiliencia y tolerancia a fallos. En este contexto, el control estructurado de excepciones y los sistemas de auditoría mediante bitácoras (*logging*) son elementos indispensables que diferencian un sistema vulnerable de uno robusto y confiable.

El presente informe documenta el desarrollo individual y la validación experimental de la Fase 4 del curso de Programación Orientada a Objetos, correspondiente al análisis, diseño e implementación del sistema de gestión para la empresa "Software FJ" (Anexo 3). A través de la implementación en el lenguaje Python 3.13, se aplicaron de forma rigurosa los pilares de la POO: abstracción (clases abstractas `EntidadBase` y `Servicio`), encapsulamiento con reglas estrictas de validación de negocio (`@property` y `@setter`), herencia y polimorfismo dinámico (`ReservaSala`, `AlquilerEquipo`, `AsesoriaEspecializada`), así como un diseño jerárquico de excepciones personalizadas (`ErrorSoftwareFJException`, `ClienteInvalidoException`, `ServicioNoDisponibleException`, `ReservaInvalidaException`). 

Adicionalmente, se integró el sistema de control de versiones Git y la plataforma GitHub para garantizar la trazabilidad del código fuente, documentando una simulación exhaustiva de 10 operaciones de negocio consecutivas que demuestran la captura efectiva de errores sin interrumpir la operatividad del sistema.

---

## 2. ENLACE AL REPOSITORIO DEL PROYECTO EN GITHUB

* **URL del Repositorio:** `[Pegar aquí el enlace público de tu repositorio de GitHub, ej: https://github.com/SergioGarzon/software-fj-fase4]`
* **Rama Principal:** `master` / `main`
* **Herramienta de desarrollo y pruebas:** Antigravity / Python 3.13.13 / Git 2.56

---

## 3. DESCRIPCIÓN DE LA SOLUCIÓN Y ARQUITECTURA TÉCNICA

### 3.1. Arquitectura de Clases y Principios POO Aplicados

1. **Abstracción y Clases Abstractas (`abc.ABC`):**
   * `EntidadBase`: Provee el identificador único numérico protegido `_id_entidad`, asegurando que ninguna entidad carezca de identidad unívoca.
   * `Servicio`: Define la plantilla obligatoria para el catálogo de servicios corporativos a través de los métodos abstractos `@abstractmethod def calcular_costo()` y `@abstractmethod def obtener_descripcion()`.

2. **Encapsulamiento y Validaciones de Negocio:**
   * La clase `Cliente` protege sus atributos privados `_nombre` y `_correo`. Mediante validadores `@setter`, se rechazan nombres vacíos o menores a 3 caracteres, y correos electrónicos con estructura inválida (carentes de `@` o dominio de punto), lanzando de forma preventiva la excepción `ClienteInvalidoException`.

3. **Herencia y Polimorfismo Dinámico:**
   * `ReservaSala`: Sobrescribe `calcular_costo()` incorporando una regla de sobrecosto del 15% para salas de alta capacidad (>10 asistentes) y admitiendo descuentos empresariales.
   * `AlquilerEquipo`: Sobrescribe `calcular_costo()` liquidando horas de uso más un cargo fijo de póliza de seguro tecnológico.
   * `AsesoriaEspecializada`: Sobrescribe `calcular_costo()` calculando honorarios profesionales con discriminación del 19% de IVA colombiano.

4. **Clase Controladora `Reserva`:**
   * Modela la asociación entre clientes y servicios contratados, administrando estados de ciclo de vida (`PENDIENTE`, `CONFIRMADA`, `CANCELADA`) y coordinando el registro de auditoría.

### 3.2. Jerarquía de Excepciones Personalizadas

Se estructuró una jerarquía especializada de errores que permite aislar fallos del dominio de negocio respecto a errores sintácticos o del intérprete:
* `ErrorSoftwareFJException` (Hereda de `Exception`)
  * `ClienteInvalidoException` (Código `ERR_CLIENTE_INVALIDO`)
  * `ServicioNoDisponibleException` (Código `ERR_SERVICIO_INVALIDO`)
  * `ReservaInvalidaException` (Código `ERR_RESERVA_INVALIDA`)

### 3.3. Sistema de Auditoría y Persistencia de Eventos (`eventos.log`)

A través del módulo estándar `logging`, se implementó una bitácora persistente en codificación UTF-8 que asienta cada evento con formato:
`%(asctime)s - [%(levelname)s] - %(message)s`
Garantizando que las transacciones exitosas queden en nivel `[INFO]`, las excepciones de negocio controladas en nivel `[WARNING]`, y los errores de tipo o críticos en nivel `[ERROR]`.

---

## 4. EVIDENCIA DE LAS 10 OPERACIONES DE LA PRÁCTICA SIMULADA

A continuación se detalla la matriz de pruebas ejecutada en la consola, demostrando la resiliencia del software ante datos correctos y erróneos:

| N.° | Operación de Negocio | Condición Probada | Excepción / Resultado | Evidencia en `eventos.log` |
|---|---|---|---|---|
| **1** | Registro de Cliente 1 | Datos correctos: "Sergio Garzón" | Operación exitosa (Instanciado) | `[INFO]` Cliente registrado con éxito |
| **2** | Registro de Cliente 2 | Nombre corto ("Al" < 3 letras) | `ClienteInvalidoException` capturada | `[WARNING]` Nombre inválido controlado |
| **3** | Registro de Cliente 3 | Correo sin `@` ni dominio válido | `ClienteInvalidoException` capturada | `[WARNING]` Formato de correo inválido |
| **4** | Creación Servicio Sala | Capacidad 16 personas, tarifa $75.000 | Operación exitosa (Instanciado) | `[INFO]` Servicio Sala creado |
| **5** | Creación Servicio Inválido | Tarifa base negativa (-$20.000) | `ServicioNoDisponibleException` capturada | `[WARNING]` Tarifa negativa rechazada |
| **6** | Creación Servicio Asesoría | Consultor Senior, tarifa $130.000 | Operación exitosa (Instanciado) | `[INFO]` Servicio Asesoría creado |
| **7** | Procesamiento Reserva 101 | 4 horas en Sala 16 pax + 10% desc. | Confirmada ($310.500 COP) | `[INFO]` Reserva confirmada y calculada |
| **8** | Procesamiento Reserva 102 | Duración inadmisible de 0 horas | `ReservaInvalidaException` capturada | `[WARNING]` Horas mínimas requeridas |
| **9** | Alquiler y Cancelación 103 | Alquiler de proyector + seguro | Confirmada y posterior Cancelación | `[INFO]` Confirmada / `[WARNING]` Cancelada |
| **10** | Prueba de Robustez Crítica | Paso de parámetro nulo (`horas=None`) | Captura de error y bloque `FINALLY` | `[ERROR]` Controlado y `[INFO]` FINALLY |

---

## 5. CONCLUSIONES

1. El uso adecuado de la Programación Orientada a Objetos, en particular el encapsulamiento a través de propiedades y la validación en tiempo de asignación, previene la dispersión de datos inconsistentes en el sistema, asegurando que los objetos solo existan en estados válidos.
2. La implementación de una jerarquía de excepciones personalizadas confiere una semántica clara a los errores operacionales, permitiendo diferenciar entre fallos humanos o de negocio (ej. correos mal digitados, duraciones nulas) y fallos graves del entorno de ejecución.
3. El uso coordinado de bloques `try-except-finally` y el registro de bitácoras (*logging*) desacopla la detección de anomalías de la caída del programa, permitiendo que la aplicación continúe atendiendo operaciones y que el personal técnico disponga de una traza auditable para análisis forense.
4. La gestión del ciclo de vida del código mediante Git y GitHub facilita la documentación paso a paso, la entrega estructurada de evidencias académicas y la reproducibilidad de software bajo buenas prácticas profesionales de la industria.

---

## 6. REFERENCIAS BIBLIOGRÁFICAS (NORMAS APA 7.ª EDICIÓN)

* Deitel, P. J., & Deitel, H. M. (2020). *Python for Programmers: with Big Data and Artificial Intelligence Case Studies*. Pearson Education.
* Gamma, E., Helm, R., Johnson, R., & Vlissides, J. (1994). *Design Patterns: Elements of Reusable Object-Oriented Software*. Addison-Wesley Professional.
* Lutz, M. (2013). *Learning Python: Powerful Object-Oriented Programming* (5.ª ed.). O'Reilly Media.
* Python Software Foundation. (2026). *Errors and Exceptions — Python 3.13 Documentation*. https://docs.python.org/3/tutorial/errors.html
* Python Software Foundation. (2026). *Logging facility for Python*. https://docs.python.org/3/library/logging.html
* Sommerville, I. (2016). *Software Engineering* (10.ª ed.). Pearson.
