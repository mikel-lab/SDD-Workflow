# Diseño de la skill global `sdd-workflow`

## Estado

- Fecha: 2026-08-05
- Alcance: skill global reutilizable para coordinar un ciclo completo de Specification-Driven Development
- Estado del diseño: aprobado por el usuario, incluido el documento escrito
- Implementación: no iniciada

## Objetivo

Crear una skill global llamada `sdd-workflow` que convierta una tarea de Jira o una descripción natural en un ciclo SDD gobernado, verificable y reutilizable. La skill coordinará los agentes globales ya instalados, usará SpecKit como generador oficial de artefactos y aplicará prácticas compatibles de Superpowers durante implementación y verificación.

El primer gate de escritura sobre el producto se abrirá únicamente después de que el Planificador genere el conjunto documental completo, el Reviewer lo apruebe de forma independiente y el usuario responda exactamente `Approved, implement.`.

## Principios

1. `sdd-workflow` es la autoridad metodológica única del ciclo.
2. SpecKit produce y mantiene los artefactos oficiales de planificación.
3. Superpowers aporta prácticas compatibles; no se ejecutará `superpowers:brainstorming` como un segundo flujo de planificación porque duplicaría documentos y gates.
4. El Orquestador coordina y conserva los gates, pero no implementa ni duplica el análisis profundo.
5. El Planificador posee el análisis inicial, la generación documental y sus correcciones.
6. El Reviewer es independiente, de solo lectura y revisa tanto la planificación como la implementación.
7. Antes del gate solo pueden escribirse artefactos SDD y, como única excepción de bootstrap, el `.specify/feature.json` que crea o actualiza el `speckit-specify` oficial. Código, tests, recursos y configuración del producto son de solo lectura; ninguna otra ruta bajo `.specify/` queda autorizada por esa excepción.
8. Ninguna ruta, nombre de proyecto o convención específica de un equipo quedará codificada en la skill global.
9. Las dudas no bloqueantes se resuelven de forma autónoma y quedan documentadas. Solo las dudas materialmente bloqueantes llegan al usuario.

## Repositorio fuente y distribución

La fuente de verdad será un repositorio autónomo y reutilizable, independiente de cualquier proyecto consumidor:

```text
codex-sdd-workflow/
├── README.md
├── .gitignore
├── agents/
│   ├── sdd-orchestrator.toml
│   ├── sdd-planner.toml
│   ├── sdd-implementer-main.toml
│   ├── sdd-implementer-high.toml
│   ├── sdd-implementer-simple.toml
│   └── sdd-reviewer.toml
├── skills/
│   └── sdd-workflow/
├── scripts/
│   ├── install.sh
│   └── validate.py
├── tests/
└── docs/
    ├── design.md
    └── implementation-plan.md
```

`scripts/validate.py` comprobará de forma determinista la estructura, referencias, portabilidad, TOML y validación oficial de la skill. `scripts/install.sh` validará primero, conservará backups de destinos existentes e instalará copias en el directorio global de Codex. Estos son scripts de distribución; no forman parte del runtime del workflow.

El repositorio se inicializará localmente con Git y recibirá un único commit inicial limpio. No se configurará remoto ni se hará push.

## Arquitectura de la skill

La skill será modular:

```text
sdd-workflow/
├── SKILL.md
├── agents/
│   └── openai.yaml
└── references/
    ├── lifecycle-and-gates.md
    ├── sources-and-artifacts.md
    ├── orchestrator.md
    ├── planner.md
    ├── implementers.md
    ├── reviewer.md
    ├── luna-lane.md
    └── contracts.md
```

`SKILL.md` será el núcleo compacto: activación, principios universales, secuencia principal y enrutamiento hacia referencias obligatorias por rol. Cada agente leerá el núcleo completo y solo las referencias necesarias para su responsabilidad.

No se añadirá un motor de estado ni scripts propios de ejecución dentro de la skill. SpecKit ya resuelve sus rutas y genera artefactos; duplicarlo aumentaría el riesgo de divergencia. Los scripts del repositorio se limitarán a validar e instalar el paquete.

## Agentes y responsabilidades

### Orquestador

El Orquestador es la única autoridad de coordinación. Sus responsabilidades son:

- recibir el enlace de Jira o la descripción natural;
- verificar que las fuentes necesarias son accesibles;
- solicitar al inicio del ciclo la autorización temporal para tareas visibles de Luna;
- enviar un briefing completo al Planificador;
- transmitir al usuario únicamente preguntas bloqueantes;
- comprobar que las escrituras del Planificador quedan confinadas al directorio SDD resuelto y que cualquier `.specify/feature.json` informado en `changed_paths` procede del bootstrap oficial, rechazando el resto de escrituras bajo `.specify/`;
- solicitar una revisión documental independiente;
- gestionar los ciclos de corrección;
- congelar el conjunto aprobado y controlar el gate `Approved, implement.`;
- convertir `tasks.md` en lotes ejecutables y asignarlos al agente apropiado;
- coordinar revisiones parciales, integraciones y revisión final.

El Orquestador podrá leer lo mínimo para validar la entrada, pero no repetirá la exploración profunda de Jira, Figma o el repositorio.

### Planificador

El Planificador posee las fases de descubrimiento y documentación:

1. Leer la tarea completa, subtareas, adjuntos, Figma cuando aplique y código relevante.
2. Identificar objetivo funcional, flujo afectado, patrones reutilizables, riesgos, contradicciones, exclusiones y suposiciones.
3. Ejecutar `speckit-specify` y registrar `.specify/feature.json` en `changed_paths` cuando la acción oficial lo cree o actualice.
4. Ejecutar `speckit-clarify` solo para dudas realmente bloqueantes y a través del Orquestador.
5. Ejecutar `speckit-checklist` sin convertirlo en un cuestionario cosmético.
6. Ejecutar `speckit-plan`.
7. Ejecutar `speckit-tasks`.
8. Ejecutar `speckit-analyze` en modo de solo lectura.
9. Corregir los artefactos en una acción separada y repetir el análisis hasta obtener coherencia o alcanzar el límite de ciclos.

El Planificador clasifica complejidad, aislamiento, dependencias, propiedad de rutas y verificabilidad, pero no selecciona ejecutor.

### Reviewer

El Reviewer interviene antes y después del gate.

Antes de implementar:

- contrasta Jira, Figma cuando aplique, código existente y artefactos;
- comprueba cobertura de requisitos y criterios de aceptación;
- verifica coherencia entre especificación, checklist, plan y tareas;
- detecta sobreingeniería, refactors innecesarios, alcance extra y riesgos sin tratar;
- valida las etiquetas de paralelización y aislamiento;
- devuelve `approved`, `corrections required` o `conditionally verified` sin editar archivos.

Después de implementar:

- revisa lotes nativos;
- revisa entregas aisladas de Luna antes de integración;
- vuelve a revisar los resultados Luna ya integrados;
- realiza una revisión final contra las fuentes y artefactos aprobados.

`conditionally verified` nunca abre un gate que requiera aprobación plena.

### Implementador Main

Main, con Terra medium, es el ejecutor predeterminado para trabajo no trivial, integración entre componentes, correcciones de Simple, fallback tras rechazo repetido de Luna e integración gated de entregas Luna aprobadas.

### Implementador High

High, con Terra high, sustituye a Main cuando existe evidencia de cambios transversales, depuración compleja, migraciones delicadas, concurrencia, persistencia, contratos difíciles o correcciones fallidas que requieren mayor razonamiento. Main y High nunca trabajan simultáneamente como implementadores principales del mismo ciclo.

### Implementador Simple

Simple, con Terra low, solo recibe tareas pequeñas, aisladas, dependency-ready, con propiedad exclusiva de rutas y validación independiente. Si descubre acoplamiento o ambigüedad no previstos, se detiene sin ampliar el alcance.

## Fuentes externas

El Orquestador verifica accesibilidad; Planificador y Reviewer realizan lecturas independientes y profundas.

Orden de acceso:

1. Conector específico disponible.
2. Navegador autenticado como alternativa.
3. Si la fuente esencial sigue inaccesible, bloqueo y petición del contenido mínimo al usuario.

Jira inaccesible bloquea cuando su contenido no ha sido proporcionado. Figma inaccesible solo bloquea si los requisitos visuales o de interacción esenciales no pueden inferirse con seguridad. Nunca se inventará información ausente.

## Jerarquía de autoridad

1. Decisiones explícitas del usuario durante el ciclo.
2. Instrucciones y políticas del repositorio para seguridad, alcance y forma de trabajo.
3. Jira o descripción proporcionada para comportamiento y aceptación.
4. Figma para diseño visual e interacción dentro del alcance funcional.
5. Código y tests para comportamiento actual, arquitectura y convenciones.
6. Suposiciones razonables.

Una petición explícita de Jira para cambiar comportamiento existente no es una contradicción. Una diferencia implícita o ambigua sí puede ser bloqueante. Figma no introduce por sí solo reglas de negocio. Los tests contradictorios se identifican como comportamiento que probablemente deba actualizarse; no se eliminan silenciosamente.

Las suposiciones no bloqueantes usan siempre:

```text
Assumption:
Reason:
Risk if wrong:
Validation needed:
```

Una duda solo es bloqueante cuando implementar sin respuesta puede cambiar materialmente el comportamiento funcional, reglas de negocio, criterios de aceptación, modelo de datos, persistencia, contrato de API, autenticación o permisos, navegación, integraciones externas, tracking crítico, compatibilidad hacia atrás, seguridad o una decisión técnica difícil de revertir. También es bloqueante una contradicción material no resoluble entre las fuentes. Naming, organización inferible, estilo, detalles visuales menores y elecciones reversibles no justifican interrumpir el ciclo.

Cuando exista un bloqueo, el Planificador devuelve el mínimo número de preguntas específicas, junto con la evidencia revisada y la razón por la que cada respuesta es necesaria. El Orquestador es el único agente que pregunta al usuario.

## Contrato dinámico de artefactos

La skill resolverá la raíz de SpecKit buscando `.specify/` según las utilidades instaladas. No asumirá que el directorio actual sea la raíz ni usará rutas absolutas.

El conjunto puede incluir, según la tarea:

- `spec.md`;
- `checklists/*.md`;
- `plan.md`;
- `research.md`;
- `data-model.md`;
- `quickstart.md`;
- `contracts/`;
- `tasks.md`;
- cualquier otro artefacto oficial producido por la versión compatible de SpecKit.

El gate abarca todos los artefactos realmente generados, no una lista rígida. El Orquestador registra sus rutas exactas y la revisión que los aprobó. Cuando el bootstrap oficial lo modifica, `.specify/feature.json` también forma parte del baseline gobernado aunque no sea un artefacto de feature. Una modificación posterior invalida la aprobación y devuelve el ciclo a revisión documental.

Antes del gate, `speckit-specify` es el único actor que puede crear o actualizar el `.specify/feature.json` exacto para persistir el directorio activo. Esa ruta debe aparecer en `changed_paths` y en la validación independiente del Orquestador. No se permite ninguna otra escritura bajo `.specify/` fuera del directorio activo de artefactos.

Los informes del Reviewer son evidencia estructurada en su respuesta, no archivos escritos por el agente de solo lectura.

## Máquina de estados

1. `intake`
2. `planning`
3. `planning_blocked`, si existe una duda material
4. `planning_review`
5. `planning_correction`, si hay hallazgos
6. `awaiting_implementation_approval`
7. `implementation`
8. `implementation_review`
9. `implementation_correction`, si hay hallazgos
10. `post_implementation_convergence`
11. `final_review`
12. `complete`, `blocked` o `cancelled`

Solo una revisión documental `approved` permite alcanzar `awaiting_implementation_approval`. Únicamente la cadena exacta `Approved, implement.` abre el gate. Respuestas parecidas pueden pedir explicaciones o cambios, pero no autorizan implementación.

Iniciar el ciclo autoriza al Planificador a crear y corregir automáticamente solo artefactos SDD. `speckit-analyze` permanece estrictamente de solo lectura; las correcciones se realizan como acciones posteriores del Planificador.

La misma condición bloqueante puede atravesar como máximo tres ciclos de corrección y revisión. Si persiste, el Orquestador escala al usuario con evidencia precisa.

## Convergencia posterior a la implementación

Al terminar las tareas aprobadas, el Reviewer ejecuta primero `speckit-analyze` en modo de solo lectura y contrasta el resultado implementado con las fuentes y artefactos.

- Si falta completar una tarea ya aprobada, el hallazgo vuelve al implementador como corrección normal sin modificar la planificación.
- Si el trabajo necesario no existe en `tasks.md`, el Planificador añade cobertura acotada aplicando el contrato de `speckit-tasks`.
- `speckit-converge` solo puede invocarse cuando existe evidencia de que `speckit-implement` ejecutó el `tasks.md` actual, o cuando una versión futura declara explícitamente compatibilidad con el ejecutor real.
- Como cualquier reparación de `tasks.md` modifica artefactos después del gate, la aprobación anterior queda invalidada.
- El nuevo conjunto pasa por `planning_review` y las nuevas tareas requieren otra respuesta exacta `Approved, implement.`.

El flujo no utilizará `speckit-tasks` ni `speckit-converge` para ampliar el alcance original o convertir mejoras opcionales en requisitos.

## Enrutamiento de implementación

El Orquestador procesa `tasks.md` por dependencias. Cada asignación incluye objetivo, criterios aplicables, rutas permitidas, rutas prohibidas, dependencias, validación y contrato de entrega.

Reglas principales:

- Las clasificaciones dudosas van a Main.
- High reemplaza a Main; no se suma a él.
- El carril simple admite como máximo dos ejecuciones simultáneas sumando Luna y Simple.
- No se asignan rutas solapadas ni tareas con dependencias no resueltas.
- Los implementadores siguen el alcance aprobado y no redefinen criterios.
- Las correcciones se enrutan conforme al origen y a las reglas de escalado.

## Carril Luna

Luna no es un agente nativo. El Orquestador puede crear una tarea visible con GPT-5.6 Luna Max únicamente si existe autorización explícita para el ciclo actual y la tarea es inequívocamente simple, aislada, dependency-ready, verificable y proporcionada al coste de coordinación.

Cada tarea Luna:

- utiliza un worktree aislado;
- recibe un briefing autosuficiente;
- no depende de documentación ignorada ausente del worktree;
- produce exactamente un commit local de entrega cuando el gate y la autoridad vigentes lo permiten;
- recibe una revisión independiente antes de integrar;
- requiere el gate manual de integración;
- es integrada únicamente por Main;
- recibe una segunda revisión después de la integración.

Luna dispone de una ronda de corrección. Tras un segundo rechazo, el resultado aislado se conserva como evidencia, no se integra y la tarea original pasa a Main. Simple es el fallback nativo cuando Luna no está autorizado, no aporta valor, carece de herramientas o no puede aislarse con seguridad.

## Uso compatible de Superpowers

La planificación no invoca `superpowers:brainstorming` como flujo independiente. `sdd-workflow` y SpecKit poseen la planificación oficial.

Durante implementación y revisión se usarán cuando correspondan:

- test-driven development para funcionalidades y bug fixes;
- systematic debugging para fallos y comportamiento inesperado;
- paralelización solo para trabajo realmente independiente;
- recepción rigurosa de code review antes de aplicar correcciones;
- verification-before-completion antes de declarar éxito.

Las instrucciones concretas de cada skill aplicable se leerán completas y se respetarán, siempre subordinadas a las decisiones explícitas del usuario y a las políticas del repositorio.

## Contratos de salida

Las referencias definirán formatos mínimos comunes:

- estado actual y transición propuesta;
- fuentes consultadas y evidencia;
- artefactos o rutas cambiados;
- criterios cubiertos;
- suposiciones;
- preguntas bloqueantes;
- decisiones de routing y justificación;
- comandos y resultados de verificación;
- hallazgos confirmados frente a hipótesis;
- riesgos residuales;
- siguiente acción y gate requerido.

El Reviewer emitirá exactamente uno de los estados normativos: `approved`, `corrections required` o `conditionally verified`.

## Gestión de errores

- Skill obligatoria ausente o ilegible: fallo cerrado antes de cualquier rol.
- SpecKit ausente o incompatible: bloqueo antes de escribir artefactos.
- Jira esencial inaccesible: bloqueo y solicitud mínima.
- Figma esencial inaccesible: bloqueo; si no es esencial, limitación documentada.
- Escritura del Planificador fuera del directorio SDD: detener y reportar sin limpieza destructiva.
- Workspace inesperadamente sucio o rutas solapadas: pausar el alcance afectado.
- Contradicción material: pregunta mínima a través del Orquestador.
- Verificación ambientalmente bloqueada: `conditionally verified`, nunca aprobación plena.
- Tres ciclos para la misma condición: escalado al usuario.

## Validación de la skill

La creación seguirá TDD para skills.

### RED

Agentes nuevos recibirán escenarios representativos antes de instalar la skill. Deben fallar de forma segura por la dependencia ausente. Los resultados se conservarán como baseline.

### GREEN

- Ejecutar el validador oficial `quick_validate.py`.
- Validar frontmatter, `agents/openai.yaml` y enlaces internos.
- Buscar rutas absolutas, nombres de proyectos y referencias accidentales al equipo actual.
- Parsear los TOML modificados.
- Confirmar que los agentes globales no gestionados permanecen idénticos.

### Pruebas de presión con agentes nuevos

Los escenarios cubrirán:

1. Planificación autónoma sin bloqueos.
2. Ambigüedad funcional bloqueante.
3. Duda cosmética resuelta como suposición.
4. Jira inaccesible.
5. Figma inaccesible pero no esencial.
6. Criterio ausente en `tasks.md`.
7. Reviewer manteniendo solo lectura.
8. Frase de aprobación casi correcta.
9. Artefactos modificados después del gate.
10. Clasificación simple dudosa.
11. Luna sin autorización vigente.
12. Segundo rechazo de Luna.
13. Verificación condicionada.
14. Tres ciclos de la misma condición.
15. Convergencia que añade tareas e invalida el gate anterior.

Se añadirá una simulación completa Planificador → Reviewer → gate → Implementador → Reviewer en un entorno temporal, sin modificar el código del proyecto actual.

## Cambios de agentes requeridos

Solo se actualizarán de forma mínima:

- `sdd-orchestrator.toml`: ordenar explícitamente la revisión documental antes del gate.
- `sdd-reviewer.toml`: incorporar explícitamente la auditoría independiente del paquete de planificación.

Los otros cuatro agentes ya son compatibles con este diseño. Todos seguirán dependiendo de `sdd-workflow` y fallarán de forma cerrada si no pueden leerla.

## Fuera de alcance

- Cambiar modelos, esfuerzos o permisos de los agentes ya aprobados.
- Crear un agente nativo Luna.
- Implementar funcionalidad de una tarea concreta.
- Introducir un motor persistente propio de workflow.
- Codificar rutas, nombres o convenciones de un proyecto determinado.
- Realizar commits intermedios, pushes o cambios destructivos; solo se autoriza el commit inicial final del repositorio autónomo.
- Configurar un remoto o publicar el repositorio.
- Vincular la distribución a un repositorio de aplicación concreto.

## Criterios de aceptación

1. La skill se instala globalmente como `sdd-workflow` y pasa la validación oficial.
2. Los seis agentes pueden localizarla y leen las referencias requeridas por su rol.
3. El Planificador puede crear y corregir únicamente artefactos SDD antes del gate.
4. El Reviewer aprueba o rechaza independientemente la planificación sin escribir archivos.
5. El Orquestador no abre la implementación sin revisión documental aprobada y la frase exacta.
6. Los artefactos se resuelven dinámicamente sin rutas o proyectos codificados.
7. El routing Main, High, Simple y Luna respeta los límites ya aprobados.
8. La modificación posterior de artefactos invalida la aprobación.
9. Los estados condicionados y los bloqueos no se presentan como éxito.
10. Las pruebas RED/GREEN y los escenarios de presión producen evidencia reproducible.
11. El trabajo nuevo descubierto mediante convergencia vuelve a revisión y requiere una nueva aprobación exacta.
12. El repositorio fuente contiene la skill, los seis agentes, documentación, pruebas y utilidades de instalación y validación sin referencias a un proyecto consumidor.
13. El instalador conserva backups, valida antes de copiar y solo modifica los siete destinos gestionados.
14. El repositorio Git queda limpio tras un commit inicial y sin remoto configurado.
