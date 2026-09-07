# Rediseño de `sdd-workflow`: control en el chat y aislamiento por ciclo

## Estado

- Fecha: 2026-08-06
- Alcance: evolución global y reutilizable de `sdd-workflow`
- Estado del diseño: aprobado por el usuario
- Implementación: verificada e instalada globalmente
- Evidencia final: 57 pruebas Python, pruebas del instalador, validadores de distribución y skill, sintaxis Bash, paridad byte a byte y smoke test del runtime instalado.
- Backup de migración: `$CODEX_HOME/backups/sdd-workflow-20260806T131501Z-48525`
- Motivo: una ejecución real permitió que el chat y un subagente compartieran la coordinación y reutilizó un paquete SpecKit de otra tarea, arrastrando tareas y revisiones históricas.

## Objetivos

1. Convertir el chat donde se invoca `sdd-workflow` en la única autoridad de coordinación y contacto con el usuario.
2. Eliminar el agente nativo `sdd-orchestrator` y la doble capa de control.
3. Crear un paquete SpecKit aislado para cada ciclo nuevo.
4. Impedir que Planner y Reviewer lean o incorporen artefactos SDD de tareas anteriores.
5. Reducir agentes, revisiones repetidas y consumo sin debilitar los gates de planificación, autorización y verificación final.

## Principios normativos

1. El chat raíz es el Orquestador del ciclo. “Orquestador” pasa a ser un rol del chat, no un agente despachable.
2. El chat coordina, conserva el estado, valida límites, aplica gates y habla con el usuario; no planifica en profundidad, revisa su propio trabajo ni implementa código.
3. Planner y Reviewer usan GPT-6 Astra con esfuerzo low. Main, High y Simple conservan sus modelos y esfuerzos actuales.
4. Sol medium será la recomendación operativa para el chat coordinador, pero la skill no fingirá que puede imponer el modelo de la sesión.
5. Cada ciclo nuevo crea un directorio SpecKit nuevo y explícito. La feature activa anterior nunca decide el destino.
6. Ningún artefacto SDD histórico es fuente de verdad para un ciclo nuevo.
7. Reutilizar un paquete anterior exige una orden explícita de continuación y una identidad coincidente.
8. Los límites de aislamiento se validan mediante contratos y un script determinista, no solo mediante instrucciones narrativas.
9. La revisión se concentra en gates y riesgos, no en cada microtarea.

## Arquitectura de agentes

El conjunto canónico se reduce a cinco agentes:

```text
sdd-planner            GPT-6 Astra / low
sdd-implementer-main   GPT-5.6 Terra / medium
sdd-implementer-high   GPT-5.6 Terra / high
sdd-implementer-simple GPT-5.6 Terra / low
sdd-reviewer           GPT-6 Astra / low
```

`sdd-orchestrator.toml` se elimina del repositorio y de la instalación global. La referencia metodológica del Orquestador permanece dentro de la skill, dirigida expresamente al chat raíz.

### Contrato del chat raíz

Al invocar `sdd-workflow`, el chat debe:

- asumir directamente el rol de Orquestador;
- no crear, despachar ni delegar la coordinación completa a otro agente;
- validar acceso a fuentes y dependencias;
- crear la identidad del ciclo antes de pedir trabajo al Planner;
- proporcionar al Planner rutas y fuentes exactas;
- validar lecturas y escrituras de artefactos;
- solicitar la revisión de planificación;
- congelar el baseline aprobado;
- aplicar el gate exacto `Approved, implement.`;
- asignar implementación y revisiones según el presupuesto operativo;
- informar al usuario al cambiar de fase, ante un bloqueo o al terminar.

Si no puede invocar un rol obligatorio, debe detener el ciclo. No puede asumir el trabajo del Planner, Reviewer o implementador para ahorrar una llamada.

## Identidad y aislamiento del ciclo

Antes de leer cualquier artefacto bajo `specs/`, el chat crea:

```text
cycle_id
workspace_root
speckit_root
primary_source
source_ids
artifact_directory
artifacts
continuation_of
```

- `workspace_root` es el proyecto real seleccionado para la sesión.
- `speckit_root` es la raíz técnica que contiene `.specify/`; puede ser superior al workspace.
- `primary_source` identifica la tarea principal. Para Jira es su clave exacta.
- `source_ids` contiene la tarea principal y únicamente sus subtareas o fuentes relacionadas autorizadas para ese ciclo.
- `artifact_directory` es nuevo y exclusivo.

Ejemplo genérico:

```text
specs/20260806-143500-mobile-app-team-123-feature-name/
```

El directorio contiene `sdd-cycle.json`:

```json
{
  "schema_version": 1,
  "cycle_id": "20260806-143500",
  "workspace_root": "<resolved-workspace>",
  "speckit_root": "<resolved-speckit-root>",
  "primary_source": "TEAM-123",
  "source_ids": ["TEAM-123"],
  "artifact_directory": "specs/20260806-143500-mobile-app-team-123-feature-name",
  "artifacts": ["spec.md", "checklists/requirements.md"],
  "continuation_of": null
}
```

El manifiesto es un artefacto gobernado de `sdd-workflow`, aunque no sea generado por SpecKit.
`artifacts` contiene rutas relativas al propio `artifact_directory` y se actualiza
después de cada acción oficial de SpecKit. El validador exige que coincida con
los archivos gobernados que existen realmente en esa carpeta.

### Ciclo nuevo

Para toda solicitud nueva:

1. Ignorar `.specify/feature.json` como entrada de selección.
2. No abrir `spec.md`, `plan.md`, `tasks.md`, checklists, contratos ni otros artefactos de carpetas existentes.
3. Generar un `cycle_id` y un directorio ausente.
4. Pasar el directorio exacto a `speckit-specify` mediante `SPECIFY_FEATURE_DIRECTORY`.
5. Permitir que `speckit-specify` actualice `.specify/feature.json` únicamente como salida de bootstrap.
6. Verificar que el archivo activo apunta al directorio recién creado.
7. Exigir que `tasks.md` pertenezca solo al ciclo y empiece su propia numeración.

No se permite seleccionar una feature porque su nombre, tema o código parezcan relacionados. Una feature activa, una rama parecida o una carpeta semánticamente próxima no prueban continuidad.

### Continuación explícita

Solo se reutiliza un paquete cuando el usuario indica expresamente que desea continuar ese ciclo.

Antes de abrir sus artefactos, el chat valida `sdd-cycle.json`:

- mismo `workspace_root`;
- mismo `primary_source`;
- ruta exacta y no ambigua;
- manifiesto válido;
- ausencia de colisiones o identidades contradictorias.

Si falta el manifiesto, existen varias candidatas o la identidad no coincide, el chat solicita la ruta exacta o crea un ciclo nuevo tras la decisión del usuario. `.specify/feature.json` por sí solo nunca autoriza una continuación.

## Prohibición de contaminación

Planner y Reviewer reciben rutas exactas. No pueden descubrir contexto documental mediante búsquedas sobre la raíz de `specs/`.

Queda prohibido:

- ejecutar `find`, `rg`, globs o recorridos equivalentes sobre todas las features;
- leer artefactos SDD fuera de `artifact_directory`;
- copiar requisitos, dependencias o tareas de otro paquete;
- añadir nuevas tareas al `tasks.md` de una tarea anterior;
- ampliar `source_ids` sin decisión explícita o relación de subtarea confirmada desde la fuente actual;
- tratar artefactos históricos como evidencia del comportamiento solicitado.

El código y los tests del workspace sí pueden consultarse como contexto real del producto. La prohibición afecta a artefactos de planificación histórica, no a la arquitectura vigente del repositorio.

Los contratos de Planner y Reviewer incorporan:

```text
artifact_reads
changed_paths
source_ids
artifact_directory
```

Una ruta de lectura o escritura fuera del paquete autorizado invalida el resultado y detiene el gate.

## Validador de ciclo

La skill incluirá `scripts/validate_cycle.py`. Su responsabilidad será comprobar de forma determinista:

- esquema e identidad de `sdd-cycle.json`;
- contención de todos los artefactos bajo `artifact_directory`;
- coincidencia entre workspace, SpecKit root, fuente y paquete;
- ausencia de enlaces o referencias a otros directorios `specs/`;
- ausencia de claves Jira no incluidas en `source_ids`, salvo referencias permitidas y documentadas;
- coherencia de la lista de artefactos;
- identidad propia de `tasks.md` y ausencia de numeración heredada;
- destino actual de `.specify/feature.json` después del bootstrap.

Se ejecutará como mínimo:

1. después de generar o corregir la planificación;
2. antes de la revisión de planificación;
3. antes de congelar el baseline;
4. antes de despachar implementación;
5. durante la reconciliación final.

Un fallo del validador no es `conditionally verified`: es una violación de aislamiento y bloquea el ciclo.

## Flujo eficiente

El camino normal será:

```text
Chat raíz / Orquestador
→ Planner
→ Reviewer de planificación
→ gate Approved, implement.
→ Main
→ Reviewer final con speckit-analyze
→ complete
```

### Planificación

- Un Planner genera el paquete completo.
- Un Reviewer realiza la revisión completa.
- Las correcciones acotadas vuelven al Planner.
- El mismo Reviewer puede hacer una revisión focalizada del delta.
- Se repite la revisión completa únicamente cuando cambian materialmente el alcance, la arquitectura o los criterios.

### Implementación

- Main es el ejecutor principal por defecto y recibe lotes coherentes, no una microtarea por agente.
- Simple o Luna se usan solo cuando la separación produce un ahorro neto y el trabajo es inequívocamente aislado.
- High sustituye a Main ante complejidad demostrada; no trabaja como segundo implementador principal.
- Cada implementador verifica su trabajo, pero no se crea un Reviewer tras cada microtarea.

### Revisiones obligatorias durante implementación

Se requiere revisión independiente:

- al terminar un lote de riesgo alto;
- tras cambios de seguridad, persistencia, contratos API o código compartido crítico;
- antes y después de integrar una entrega de Luna;
- sobre el resultado final completo.

Un lote normal puede avanzar con la verificación del implementador hasta la revisión final.

### Reconciliación final

Un único Reviewer final ejecuta `speckit-analyze` read-only y, en la misma revisión, comprueba fuentes, artefactos, código, tests y criterios.

- Trabajo pendiente ya presente en `tasks.md`: vuelve al implementador.
- Trabajo aprobado ausente de `tasks.md`: vuelve al Planner, invalida el baseline y exige nueva revisión y aprobación.
- Resultado completo: `approved` final.

No se ejecuta otra revisión completa idéntica después de esta reconciliación.

## Gates conservados

El rediseño no elimina:

- revisión independiente de la planificación;
- congelación del conjunto aprobado;
- frase exacta posterior `Approved, implement.`;
- invalidación del gate cuando cambian artefactos gobernados;
- revisión independiente final;
- distinción entre `approved`, `corrections required` y `conditionally verified`.

La simplificación reduce duplicación, no autoridad ni trazabilidad.

## Manejo de errores

- Feature activa de otra tarea: ignorar y crear un ciclo nuevo.
- Carpeta antigua con nombre similar: ignorar.
- Colisión de directorio: generar otro `cycle_id`; nunca fusionar.
- Continuación sin manifiesto válido: bloquear y pedir la ruta exacta.
- Continuación con workspace o fuente distintos: rechazar.
- Referencia inesperada a otro ticket: detener antes del gate.
- Lectura de artefactos externos al ciclo: invalidar el resultado.
- Imposibilidad de invocar un rol obligatorio: bloquear sin asumirlo desde el chat.
- Tres ciclos de la misma condición bloqueante: escalar al usuario.

## Distribución y migración

El repositorio conserva su estructura portátil, con estos cambios:

- eliminar `agents/sdd-orchestrator.toml`;
- mantener cinco agentes canónicos;
- mantener `references/orchestrator.md` como contrato del chat raíz;
- añadir `skills/sdd-workflow/scripts/validate_cycle.py`;
- actualizar `SKILL.md`, referencias, README, instalador, validador y pruebas;
- actualizar la documentación de arquitectura y plan.

El instalador:

1. valida antes de escribir;
2. guarda backup del agente Orquestador instalado;
3. elimina únicamente `sdd-orchestrator.toml` gestionado;
4. instala la skill y los cinco agentes canónicos;
5. no modifica otros agentes globales;
6. permite dry-run y restauración manual desde backup.

La distribución seguirá teniendo un inventario exacto de archivos. Al retirar un TOML y añadir el validador runtime, el recuento esperado permanece estable salvo una decisión posterior justificada.

## Estrategia de pruebas

La modificación seguirá RED→GREEN→REFACTOR para skills y scripts.

Escenarios mínimos:

1. El chat invoca SDD y no crea un Orquestador subagente.
2. `.specify/feature.json` apunta a una tarea anterior.
3. Existe una carpeta histórica semánticamente parecida.
4. Dos proyectos comparten raíz Git o SpecKit.
5. Un ciclo nuevo obtiene un paquete y `tasks.md` propios.
6. Una continuación explícita del mismo workspace y fuente reutiliza solo su carpeta.
7. Una continuación con identidad diferente se rechaza.
8. Planner y Reviewer no leen artefactos externos al ciclo.
9. El validador rechaza referencias cruzadas y claves Jira no autorizadas.
10. Un lote normal no genera una revisión por microtarea.
11. Un lote crítico conserva la revisión independiente.
12. El camino normal usa Planner, Reviewer de planificación, Main y Reviewer final.
13. La actualización elimina solo el antiguo agente gestionado y preserva todos los demás.

Las pruebas de comportamiento conservarán prompts, identidades, resultados crudos y puntuación manual. Los controles que ya se comporten correctamente se clasificarán como no-regresión, no como causalidad RED→GREEN.

## Fuera de alcance

- Modificar las skills oficiales de SpecKit.
- Convertir Luna en agente nativo.
- Permitir planificación histórica automática entre tickets.
- Eliminar el gate manual de implementación.
- Hacer que la skill afirme controlar el modelo del chat.
- Publicar cambios en el remoto sin autorización explícita.

## Criterios de aceptación

1. La invocación de `sdd-workflow` deja la coordinación en el chat raíz y no despacha `sdd-orchestrator`.
2. El repositorio y la instalación global contienen exactamente cinco agentes SDD canónicos.
3. Todo ciclo nuevo crea `sdd-cycle.json` y un `SPECIFY_FEATURE_DIRECTORY` ausente y explícito.
4. `.specify/feature.json` nunca selecciona por sí solo una feature anterior.
5. Planner y Reviewer no leen artefactos de otros ciclos.
6. Una continuación exige orden explícita y coincidencia de workspace y fuente.
7. `validate_cycle.py` bloquea contaminación, referencias cruzadas e identidad incoherente.
8. `tasks.md` no contiene tareas heredadas de otro paquete.
9. El flujo normal no crea agentes ni revisiones por microtarea.
10. Los cambios críticos, Luna y el resultado final conservan revisión independiente.
11. El Reviewer final unifica reconciliación y verificación completa.
12. Los gates de planificación, autorización exacta e invalidación permanecen vigentes.
13. El instalador respalda y retira solo el antiguo Orquestador gestionado.
14. La suite RED/GREEN, el validador de distribución y el validador oficial pasan.
15. La instalación global coincide con la fuente y los agentes no gestionados permanecen intactos.
