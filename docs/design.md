# SDD Workflow: agentes nativos y ejecución autónoma

## Estado y alcance

Fecha del diseño vigente: 2026-09-24. Evolución autorizada por el usuario sobre el ciclo aislado existente. Este documento describe la distribución actual; el historial anterior permanece en Git. Los resultados de verificación corresponden al commit y a su ejecución de CI, no demuestran una instalación global ni una ejecución real de los modelos en el cliente del usuario.

El objetivo es completar una tarea encargada mediante `sdd-workflow` sin confirmaciones rutinarias: planificación, revisión, implementación, corrección y verificación final. Solo requiere atención del usuario un bloqueo ineludible que necesite una decisión, información esencial, acceso o autoridad que el sistema no pueda obtener con la evidencia y permisos disponibles.

## Responsabilidades y perfiles

| Responsabilidad | Perfil | Modelo | Esfuerzo |
| --- | --- | --- | --- |
| Coordinación | Chat raíz; no es otro agente | gpt-6-sol | medium |
| Planificación | sdd-planner | gpt-6-sol | high |
| Implementación principal | sdd-implementer-main | gpt-6-sol | medium |
| Implementación compleja | sdd-implementer-high | gpt-6-sol | high |
| Implementación acotada | sdd-implementer-simple | gpt-6-luna | high |
| Revisión independiente | sdd-reviewer | gpt-6-sol | high |

Existen exactamente cinco agentes configurados, todos nativos. El chat raíz es la única autoridad de coordinación y contacto con el usuario; no despacha `sdd-orchestrator`. La recomendación de modelo del chat no implica que una skill cambie automáticamente el modelo de una sesión ya abierta.

Planner crea y corrige artefactos. Los implementadores trabajan exclusivamente en su alcance asignado. Reviewer permanece read-only y evalúa evidencia de forma independiente. El chat dirige el ciclo y comprueba límites, sin asumir la planificación profunda, implementación o revisión como alternativa a un rol no disponible. Solo el chat raíz despacha agentes; no existe delegación recursiva ni un modo de ejecución especial por el nombre del modelo.

Simple recibe trabajo aislado, bien especificado, con dependencias satisfechas y comprobación directa. Main recibe trabajo no trivial, integración y clasificaciones dudosas. High sustituye a Main cuando la complejidad o un fallo de razonamiento lo justifique. Main y High nunca trabajan simultáneamente en el mismo ciclo. Se permiten como máximo dos Simple concurrentes y un principal, siempre con propiedad exclusiva y no solapada de archivos entre todos los escritores.

## Autonomía y límites

La solicitud original autoriza el ciclo completo dentro de su alcance. No se pide otra aprobación del plan, una frase de confirmación, permiso para corregir un defecto ni una elección rutinaria del implementador. Una solicitud explícita de solo planificación, pausa, cancelación o límite adicional conserva su autoridad.

El chat resuelve internamente los detalles inferibles, instrucciones incompletas, errores corregibles, enrutamiento y obtención de evidencia de pruebas. Ante tres ciclos fallidos de la misma condición, conserva diagnóstico e intentos y cambia de estrategia mediante un escalado interno fundamentado. No reinicia el contador renombrando el defecto ni repite indefinidamente el mismo intento. Un timeout de espera no es un fallo del agente.

La atención del usuario exige simultáneamente: una acción necesaria bloqueada, imposibilidad de resolverla de forma segura con evidencia y recuperación autorizada, y una entrada indispensable que deba aportar el usuario. Se solicita antes de actuar sobre la parte afectada y se identifica la decisión mínima. Un bloqueo puramente técnico sin decisión útil para el usuario se comunica con evidencia, no como una petición vacía de aprobación. El trabajo independiente no afectado puede continuar cuando sus gates y límites lo permitan.

La autonomía no amplía alcance, permisos ni acceso. No permite inventar reglas de negocio, omitir validaciones, debilitar el sandbox, ignorar aprobaciones impuestas por la plataforma, aceptar riesgos por el usuario ni publicar o desplegar sin autoridad aplicable. Tampoco vuelve a pedir un permiso ya concedido para la misma acción y alcance.

## Identidad y aislamiento del ciclo

El chat establece antes de cualquier lectura de planificación:

```text
cycle_id
workspace_root
speckit_root
primary_source
source_ids
artifact_directory
identity_mode
```

`workspace_root` identifica el producto; `speckit_root` la raíz de `.specify/`. No se asume que ambas coincidan. Cada nueva tarea obtiene un directorio ausente y exclusivo, relativo a `speckit_root`, y su propio manifiesto `sdd-cycle.json` con esquema 1. El manifiesto contiene la identidad, el inventario dinámico `artifacts` y `continuation_of`.

El Planner crea primero el manifiesto y ejecuta `speckit-specify` con `SPECIFY_FEATURE_DIRECTORY` igual al directorio asignado. `.specify/feature.json` se trata únicamente como salida del bootstrap, nunca como entrada para seleccionar una tarea antigua. Una continuación exige solicitud explícita y coincidencia de directorio, workspace y fuente; no se deduce del nombre de una rama o de una feature activa.

Los artefactos generados pueden incluir especificación, checklists, plan, investigación, modelo de datos, contratos, quickstart y tareas. Se inventarían todos los archivos oficiales efectivamente generados. Planner y Reviewer reciben rutas exactas, reportan `artifact_reads` y no descubren ni importan paquetes históricos. El código y pruebas actuales sí son evidencia del producto; las planificaciones de otras tareas no lo son.

Antes del gate de implementación solo se escribe en el paquete asignado. La única excepción es el archivo exacto `.specify/feature.json` escrito por el `speckit-specify` oficial, que debe figurar en `changed_paths` y en el baseline. No se concede una excepción general a `.specify/`.

## Fuentes y preguntas materiales

La prioridad es: decisiones explícitas del usuario, políticas aplicables del repositorio, Jira o descripción funcional, Figma para lo visual dentro del alcance, código y pruebas actuales, y supuestos documentados. Un cambio expresamente pedido no se rechaza porque una prueba anterior represente el comportamiento antiguo.

Se intenta primero el conector correspondiente y después una sesión autenticada cuando esté autorizada y sea necesaria. La ausencia de una fuente visual opcional se registra como limitación. No se inventa contenido inaccesible. Las elecciones de estilo o implementación inferibles se resuelven mediante el formato Assumption, Reason, Risk if wrong y Validation needed. Una contradicción material no resuelta sobre retención, permisos, contratos u otro comportamiento necesita la entrada indispensable antes de decidirla.

## Validación y flujo

Cada invocación de `validate_cycle.py` recibe valores externos del chat, sin reconstruir las expectativas a partir del propio manifiesto:

```text
--manifest
--expected-workspace
--expected-cycle-id
--expected-speckit-root
--expected-source
--expected-source-id (una vez por cada fuente completa)
--expected-artifact-directory
--new-cycle O --expected-continuation-of
```

El validador comprueba identidades, contención, inventario, fuentes autorizadas, referencias cruzadas, symlinks y numeración de tareas. Se mantiene sin cambios funcionales en esta actualización. Un fallo bloquea la transición afectada y se intenta resolver por el rol responsable; no convierte automáticamente la situación en una pregunta al usuario.

El camino normal es:

```text
Intake -> Planner -> Reviewer de planificación
       -> approved + validación + baseline congelado
       -> implementación nativa y pruebas
       -> Reviewer final con speckit-analyze -> complete
```

La secuencia SpecKit conserva specify, clarify solo cuando sea indispensable, checklist, plan, tasks y analyze read-only. Las correcciones de artefactos son acciones separadas del Planner. Una corrección acotada vuelve al mismo Reviewer para revisión del delta; un cambio material requiere revisión completa nueva.

El gate de implementación se abre automáticamente con revisión independiente `approved`, validación exitosa y baseline intacto. `approved` es el veredicto del Reviewer, no una frase que deba escribir el usuario. Cambiar cualquier artefacto congelado invalida su revisión; se revisa, valida y congela el nuevo conjunto antes de reanudar automáticamente.

Los lotes normales no generan una revisión por microtarea. Los cambios de alto riesgo, seguridad, persistencia o migración, contratos API y código compartido crítico requieren revisión intermedia. El Reviewer final unifica reconciliación y veredicto integrado. Sus correcciones vuelven a esa revisión final tras las comprobaciones correspondientes, sin añadir una revisión intermedia redundante.

Si falta trabajo ya definido en tareas, se corrige implementación. Si falta cobertura de un requisito existente en `tasks.md`, Planner aplica el contrato `speckit-tasks` y se renueva la revisión del baseline. `speckit-converge` solo es compatible cuando `speckit-implement` ejecutó las tareas actuales o un contrato futuro admite expresamente el ejecutor empleado. No se incorporan mejoras opcionales como requisitos de convergencia.

Reviewer no ejecuta comprobaciones que escriban. Tras abrirse implementación, el chat encarga esas pruebas al implementador permitido y devuelve comando, salida, código de salida e identidad del baseline para evaluación independiente. La comprobación pendiente sigue siendo `conditionally verified` hasta obtener evidencia suficiente; no se cambia el sandbox ni se considera una aprobación.

## Contexto y recuperación

La delegación utiliza controles reales de perfiles; escribir un nombre en el prompt no configura el modelo. Los encargos autosuficientes empiezan sin historial paterno mediante `fork_context=false` o `fork_turns="none"`, según el esquema expuesto, nunca ambos. Toda herencia excepcional necesita motivo y límites de ciclo.

El Delegation Record separa configuración solicitada de metadatos observados. La ausencia de telemetría se registra como `not verified`, sin inventar valores ni añadir una aprobación. Una incompatibilidad confirmada sí requiere recuperación o bloqueo de la asignación afectada.

El Orchestrator Checkpoint conserva identidad, estado, baseline, decisiones, asignaciones, dependencias, revisiones e intentos y próxima transición. Reside en el chat o almacenamiento de sesión disponible, fuera del conjunto de artefactos congelados. Tras compactación se recuperan evidencia y agentes existentes, sin reiniciar trabajo completado o todavía activo.

## Distribución y actualización

La distribución mantiene 25 archivos: cinco agentes, siete referencias, scripts, documentación, pruebas y el workflow de CI. El instalador valida antes de escribir, respalda íntegramente la skill gestionada y los agentes existentes y reemplaza la carpeta gestionada completa. Los archivos retirados no quedan activos; sus bytes se conservan en el backup. El antiguo `sdd-orchestrator.toml` sigue retirándose por su ruta exacta y los agentes no gestionados no se modifican.

No se añaden dependencias de ejecución al consumidor aparte de las existentes. El workflow de GitHub usa permisos de lectura, no persiste credenciales del checkout y ejecuta verificaciones de la distribución en un entorno temporal. Publicar una PR no instala la skill en el equipo del usuario.

## Criterios y límites de verificación

Se comprueban la matriz de modelos en TOML y validador, las reglas de autonomía y recuperación, la ausencia del mecanismo externo retirado, la identidad de ciclo, los gates independientes, la revisión por riesgo y la actualización con backup y eliminación de archivos obsoletos. Se conservan pruebas negativas del validador para inventarios, identidades, referencias, fuentes y codificación inválidos.

La suite de políticas analiza texto y configuración. Los tests de validador e instalación ejecutan scripts reales en copias temporales. CI no demuestra selección efectiva de modelo, obediencia de subagentes, comportamiento después de compactación, calidad de código generado ni ahorro de tokens. Esas propiedades requieren una prueba posterior en el runtime real con tareas comparables y evidencia vinculada a cada agente.
