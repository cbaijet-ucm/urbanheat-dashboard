# UrbanHeat BCN — construcción de un dashboard narrativo en Streamlit

## 1. Contexto del proyecto

Estás trabajando dentro del repositorio de **UrbanHeat BCN**, un Trabajo Final de Máster de Data Science aplicado al comportamiento térmico urbano de Barcelona.

El proyecto integra:

* temperatura superficial terrestre de Landsat 8/9 Collection 2 Level-2;
* índices espectrales derivados de Sentinel-2;
* meteorología procedente de la red XEMA;
* topografía y morfología urbana;
* Sky View Factor;
* coberturas del suelo;
* distancias a costa, parques y refugios climáticos;
* información demográfica y socioeconómica;
* modelos tabulares y modelos espaciales basados en CNN/U-Net;
* validación temporal y espacial.

El área de estudio es Barcelona y un buffer aproximado de 1 km. La integración geoespacial se realiza mediante una rejilla de 30 × 30 m, principalmente en EPSG:25831. La unidad fundamental del dataset tabular es la combinación:

```text
cell_id + scene_id
```

La variable objetivo es `LST_Celsius`, es decir, temperatura de superficie obtenida mediante Landsat. No debe confundirse con temperatura del aire ni presentarse como la temperatura soportada directamente por la población.

## 2. Naturaleza del producto

El dashboard es un producto complementario del TFM. No constituye el entregable académico principal ni pretende ser una aplicación operacional.

Su finalidad es:

1. presentar visualmente el proyecto;
2. servir como hilo conductor del vídeo de defensa;
3. permitir consultar sus resultados de forma atractiva;
4. mostrar el pipeline completo de Data Science;
5. facilitar una posible demostración pública posterior;
6. incorporar, cuando los artefactos lo permitan, un pequeño experimento exploratorio de tipo *what-if*.

Debe entenderse como un híbrido entre:

* presentación narrativa;
* artículo científico interactivo;
* dashboard cartográfico;
* demostrador técnico.

No debe convertirse en:

* una aplicación de inferencia en tiempo real;
* un explorador GIS genérico;
* una colección de controles sin narrativa;
* una reproducción literal de los notebooks;
* una interfaz cargada de tarjetas, indicadores y botones;
* una exposición de código fuente;
* una herramienta de simulación causal o de planificación urbana operacional.

La aplicación debe contar una historia siguiendo esta secuencia:

```text
problema urbano
→ fuentes heterogéneas
→ armonización espacial
→ dataset celda-fecha
→ modelado tabular
→ modelado espacial
→ evaluación
→ lectura social
→ experimento exploratorio
→ conclusiones
```

## 3. Restricciones de ubicación y migración

Todo lo necesario para construir, ejecutar y desplegar el dashboard debe vivir dentro de:

```text
02_Code/Dashboard
```

No modifiques código, notebooks, configuraciones ni archivos de otras carpetas del repositorio.

La auditoría del repositorio puede leer y analizar archivos externos para comprender el proyecto, pero cualquier código nuevo, documentación del dashboard, configuración, dependencia, script de generación de artefactos o recurso derivado debe crearse dentro de `02_Code/Dashboard`.

Si el dashboard necesita utilizar artefactos generados en otras carpetas, no los referencies de forma frágil mediante rutas relativas arbitrarias. Debes:

1. crear dentro de `02_Code/Dashboard` un registro exhaustivo de todos los archivos externos necesarios;
2. indicar para cada archivo su ruta de origen, tipo, tamaño aproximado, propósito y transformación requerida;
3. distinguir entre archivos imprescindibles y opcionales;
4. crear un script de migración o sincronización que pueda copiar los artefactos necesarios a una estructura autocontenida del dashboard;
5. hacer que, una vez migrado, el dashboard pueda ejecutarse utilizando únicamente el contenido de `02_Code/Dashboard`;
6. documentar el comando de migración y las comprobaciones posteriores.

El registro debe permitir reconstruir el dashboard en otra ubicación sin depender de rutas locales del repositorio original.

No copies datasets raw completos, GeoTIFF innecesarios, mosaicos originales ni otros archivos muy pesados si pueden sustituirse por:

* tablas resumidas;
* Parquet filtrados;
* geometrías simplificadas;
* rasters recortados;
* PNG o WebP optimizados;
* NPZ compactos;
* métricas JSON;
* predicciones seleccionadas;
* manifiestos;
* artefactos derivados específicamente para presentación.

La carpeta del dashboard debe contener una separación clara entre:

```text
02_Code/Dashboard/
├── aplicación y código
├── artefactos derivados
├── recursos estáticos
├── documentación
├── scripts de construcción y migración
└── configuración de despliegue
```

No debes modificar archivos externos para adaptarlos al dashboard. Si un artefacto externo no tiene el formato adecuado, genera una copia derivada dentro de `02_Code/Dashboard`.

## 4. Primera actuación: inspección del repositorio

Antes de implementar la interfaz:

1. Lee cualquier `AGENTS.md`, `README`, documentación, configuración o contrato de datos existente.
2. Revisa el estado de Git y respeta todos los cambios actuales del usuario.
3. No modifiques nada fuera de `02_Code/Dashboard`.
4. Localiza los notebooks responsables de:

   * adquisición Landsat y Sentinel-2;
   * construcción de la rejilla;
   * índices espectrales;
   * variables topográficas y morfológicas;
   * coberturas del suelo;
   * distancias;
   * meteorología;
   * construcción del `cell_date_dataset`;
   * particiones temporales y espaciales;
   * modelo tabular;
   * preparación raster;
   * CNN/U-Net;
   * capa social y visualizaciones finales.
5. Identifica los artefactos reales disponibles:

   * Parquet y GeoParquet;
   * GeoTIFF y NPZ;
   * JSON y manifiestos;
   * modelos serializados;
   * métricas;
   * predicciones;
   * importancias o valores SHAP;
   * geometrías administrativas;
   * imágenes y gráficos ya exportados.
6. Verifica en los notebooks y artefactos:

   * modelos finalmente utilizados;
   * modelo temporal real;
   * modelo espacial tabular real;
   * arquitecturas Deep Learning realmente entrenadas;
   * splits definitivos;
   * métricas definitivas;
   * escenas utilizadas;
   * definición real de `is_core`;
   * nombres finales de las variables;
   * rangos y transformaciones de las variables que podrían utilizarse en el experimento *what-if*.

No asumas que el modelo temporal es Elastic Net, que XGBoost es el ganador o que una U-Net llegó a entrenarse correctamente: compruébalo en el repositorio.

No inventes métricas, resultados, nombres de archivos, parámetros ni conclusiones.

Genera un inventario que relacione:

| Sección del dashboard | Contenido | Artefacto fuente | Transformación necesaria |
| --------------------- | --------- | ---------------- | ------------------------ |

Este inventario debe quedar documentado dentro de:

```text
02_Code/Dashboard/docs/artifact_inventory.md
```

Además, crea un registro específico de dependencias externas, por ejemplo:

```text
02_Code/Dashboard/docs/external_artifact_registry.md
```

Debe incluir como mínimo:

| Archivo de origen | Tipo | Tamaño | Uso | ¿Imprescindible? | Copia derivada | Método de migración |
| ----------------- | ---- | -----: | --- | ---------------- | -------------- | ------------------- |

## 5. Arquitectura narrativa

La navegación principal tendrá seis páginas.

### 1. Inicio

Objetivo: explicar el proyecto en menos de un minuto.

Contenido previsto:

* portada de UrbanHeat BCN;
* título y subtítulo breves;
* problema urbano estudiado;
* alcance espacial y temporal;
* aclaración visible: **LST no es temperatura del aire**;
* infografía horizontal o vertical del pipeline;
* tecnologías principales;
* breve explicación de los dos enfoques de modelado;
* indicación de que los resultados corresponden a observaciones diurnas de Landsat;
* mención breve de que el dashboard incluye un escenario exploratorio *what-if*, no causal.

Esta página no debe contener mapas interactivos ni controles complejos.

La infografía debe ser un elemento limpio construido mediante SVG, HTML/CSS o componentes nativos. No debe parecer una arquitectura corporativa recargada.

### 2. Datos

Objetivo: explicar cómo fuentes muy diferentes terminan integradas en un único sistema espacial.

La narrativa vertical incluirá:

1. **Área de estudio**

   * municipio de Barcelona;
   * buffer de 1 km;
   * CRS de trabajo;
   * rejilla de 30 × 30 m;
   * relación entre `cell_id`, fila y columna.

2. **Escenas satelitales**

   * distribución temporal de escenas;
   * Landsat 8/9;
   * escenas principales y complementarias según la definición real del proyecto;
   * efecto de la nubosidad;
   * mapa de una escena LST representativa.

3. **Predictores espectrales**

   * NDVI;
   * NDBI;
   * MNDWI;
   * selector de variable o pequeños múltiples.

4. **Características urbanas**

   * elevación, pendiente y orientación;
   * SVF;
   * coberturas del suelo;
   * distancia al mar;
   * distancia a parques;
   * distancia a refugios;
   * meteorología interpolada.

5. **Cell-Date Dataset**

   * explicación visual de la clave `cell_id + scene_id`;
   * variables estáticas frente a variables dinámicas;
   * esquema de integración;
   * dimensiones finales;
   * familias de variables;
   * tratamiento de valores ausentes y máscaras.

Debe explicarse que la rejilla trabaja a 30 m, pero que ello no implica disponer de observaciones térmicas independientes reales a 30 m: la banda térmica original de Landsat tiene una resolución efectiva más gruesa y el producto se distribuye remuestreado.

### 3. Modelo tabular

Objetivo: explicar la lógica metodológica y los resultados del modelo tabular ganador.

Narrativa:

1. **Problema inicial**

   * fuerte dependencia de la temperatura absoluta respecto a las condiciones de cada escena;
   * dificultad del modelo directo para representar simultáneamente variación temporal y patrón espacial;
   * mostrar únicamente algún mapa o diagnóstico fallido si existe un artefacto real y resulta explicativo.

2. **Descomposición en dos etapas**

   Mostrar mediante LaTeX una expresión equivalente a:

   ```latex
   \hat{T}_{i,s} = \hat{\mu}_{s} + \hat{\delta}_{i,s}
   ```

   donde:

   * `μ_s` representa la temperatura media o componente temporal de la escena;
   * `δ_i,s` representa la anomalía espacial intraurbana;
   * la predicción final reconstruye ambos componentes.

3. **Modelo temporal**

   * variables utilizadas;
   * modelo real;
   * validación;
   * resultados principales.

4. **Modelo espacial tabular**

   * algoritmo final;
   * variables utilizadas;
   * estrategia de entrenamiento;
   * particiones temporales y espaciales;
   * prevención de fuga de información.

5. **Resultados**

   * métricas MAE, RMSE y R² cuando existan;
   * observado frente a predicho;
   * mapa de residuos;
   * dispersión observado-predicho;
   * importancia de variables o SHAP;
   * comportamiento del peor caso;
   * generalización sobre escenas no vistas.

6. **Interpretación**

   * capacidad explicativa de las features espaciales explícitas;
   * limitaciones derivadas del número y diversidad de escenas.

Debe explicarse correctamente que las filas correspondientes a diferentes celdas de una misma escena no son observaciones completamente independientes. Existe autocorrelación espacial y, por tanto, el volumen efectivo de información depende en gran medida del número y diversidad de escenas, no solamente del número total de filas.

### 4. Deep Learning

Objetivo: mostrar qué aporta un modelo que recibe directamente contexto espacial.

Contenido:

1. motivación de la CNN;
2. transformación del dataset tabular en tensores raster;
3. canales estáticos y dinámicos;
4. target de anomalía espacial;
5. tiles y patches;
6. máscaras;
7. arquitectura o arquitecturas realmente probadas;
8. curvas de entrenamiento;
9. predicciones espaciales;
10. diagnóstico de bordes o discontinuidades;
11. comparación con el modelo tabular.

Mostrar, cuando los artefactos lo permitan:

* esquema del tensor de entrada;
* representación de los patches;
* arquitectura simplificada;
* observado, CNN, modelo tabular y residuos;
* tabla comparativa de métricas;
* mapa de diferencia entre errores;
* comparador deslizante entre observado y predicho.

No presentar Deep Learning como superior por definición. La comparación debe ser honesta y basada en los resultados reales.

El modelo espacial convolucional es una parte central del TFM, aunque no supere al modelo tabular.

### 5. Capa social

Objetivo: relacionar los patrones térmicos con la estructura territorial sin establecer causalidad.

Contenido:

* agregación por barrio o sección censal;
* exposición térmica;
* estructura de edad;
* densidad;
* renta;
* características de vivienda;
* proximidad a zonas verdes;
* accesibilidad a refugios climáticos;
* localización de posibles hotspots sociales.

La capa social debe mantenerse conceptualmente separada del modelo físico de predicción térmica, salvo que los notebooks demuestren lo contrario.

La distancia a refugios climáticos debe presentarse principalmente como indicador de accesibilidad y no necesariamente como predictor térmico.

Incluir de forma visible estas limitaciones:

* Landsat caracteriza la LST aproximadamente a media mañana;
* la exposición representada es diurna;
* no se modela el ciclo térmico nocturno;
* una zona que no aparece como hotspot diurno puede retener calor durante la noche;
* las relaciones sociales mostradas son descriptivas y no causales.

### 6. Conclusiones

Objetivo: cerrar la historia y servir como última sección del vídeo.

Incluir:

* objetivo alcanzado;
* aportaciones principales;
* comparación tabular frente a Deep Learning;
* fortalezas del enfoque multifuente;
* limitaciones temporales y espaciales;
* limitaciones de la LST como proxy;
* aplicabilidad urbana;
* posibles mejoras;
* incorporación futura de datos nocturnos;
* aumento del número de escenas;
* nuevas fuentes y sensores;
* mejora de la validación espacial;
* despliegue público del dashboard;
* posible escenario exploratorio de intervención urbana;
* advertencia de que el *what-if* no constituye una estimación causal.

## 6. Experimento exploratorio *what-if*

El dashboard debe incluir, en algún punto de la narrativa, un experimento mínimo de tipo *what-if*, siempre que los artefactos reales y el modelo final lo permitan sin introducir una complejidad desproporcionada.

La ubicación recomendada es:

* al final de `Modelo tabular`, como extensión de la interpretación del modelo; o
* en `Conclusiones`, como demostración final limitada.

El experimento debe permitir seleccionar un barrio y plantear un escenario como:

> ¿Qué pasaría si para todas las celdas de un barrio seleccionado se aumentara su índice NDVI un 20 %? ¿Cómo cambiaría la predicción?

Requisitos:

1. El usuario debe poder seleccionar un barrio disponible en los artefactos reales.
2. El sistema debe identificar las celdas pertenecientes a ese barrio.
3. Debe aplicar el incremento únicamente a las celdas seleccionadas.
4. El incremento debe respetar los límites físicos o de representación del NDVI:

   * si el NDVI está normalizado o acotado, no debe superar su máximo válido;
   * si el aumento del 20 % satura el valor, debe recortarse al máximo permitido;
   * debe mostrarse cuántas celdas han sido recortadas o qué porcentaje del área ha saturado, si el dato está disponible.
5. Debe recalcularse la predicción utilizando el modelo tabular ganador o una función equivalente basada en artefactos precomputados.
6. Debe compararse:

   * predicción original;
   * predicción bajo el escenario;
   * diferencia absoluta;
   * resumen agregado para el barrio seleccionado.
7. Debe utilizar escalas coherentes y mostrar unidades.
8. Debe indicar claramente:

   * que se modifica únicamente NDVI;
   * que el resto de variables permanece constante;
   * que no se modelan cambios correlacionados en cobertura del suelo, humedad, meteorología, morfología ni otras variables;
   * que el resultado es una simulación del modelo, no una predicción causal del efecto real de plantar vegetación.
9. No debe presentarse como una recomendación urbanística ni como una estimación de impacto real.
10. Si el modelo final no puede utilizarse de forma segura para este experimento, no inventes una aproximación. En ese caso:

    * documenta el bloqueo;
    * deja el componente deshabilitado o claramente marcado como pendiente;
    * explica qué artefactos serían necesarios.

El experimento puede utilizar NDVI, cobertura del suelo o SVF, pero debe implementarse inicialmente como máximo para una variable y un escenario. No añadas un simulador multivariable.

El componente debe ser deliberadamente pequeño:

* un selector de barrio;
* un control de incremento, preferentemente fijo al 20 % o con un rango muy limitado;
* una visualización comparativa;
* una explicación metodológica breve;
* una advertencia de interpretación.

No debe cargar el dataset completo ni ejecutar un entrenamiento. Si requiere inferencia, utiliza únicamente el modelo final validado y cargado mediante `st.cache_resource`, o una versión compacta y trazable del mismo.

## 7. Diseño visual

El dashboard se diseñará específicamente para navegador de escritorio, principalmente Chrome.

Viewport objetivo:

* óptimo: 1440 × 900;
* mínimo razonable: 1280–1366 px;
* no es necesario optimizar para móvil;
* debe evitarse el desbordamiento horizontal.

Directrices obligatorias:

* fondo blanco;
* texto casi negro;
* líneas divisorias finas;
* ausencia de sombras;
* ausencia de gradientes decorativos;
* radios de borde mínimos;
* mucho espacio en blanco;
* jerarquía tipográfica clara;
* paleta cromática reservada principalmente para los datos;
* controles discretos;
* máximo de uno a tres controles relevantes por bloque;
* nada de tarjetas de KPI coloreadas;
* nada de iconos decorativos;
* nada de emojis;
* nada de grandes cajas grises;
* nada de aspecto corporativo genérico.

La navegación principal estará en la parte superior y se comportará visualmente como pestañas de línea:

* sin fondo;
* sin contenedor grueso;
* texto negro o gris oscuro;
* pestaña activa indicada mediante subrayado negro de 1–2 px;
* separación inferior mediante una línea gris muy fina;
* etiquetas breves: `Inicio`, `Datos`, `Modelo tabular`, `Deep Learning`, `Capa social`, `Conclusiones`.

Utiliza `st.Page` y `st.navigation(position="top")` como estructura principal. No cargues todas las páginas como contenido de un único `st.tabs`.

Dentro de cada página puede haber tabs secundarios únicamente para comparaciones locales y ligeras.

Configura el tema mediante `.streamlit/config.toml` y concentra cualquier CSS adicional en un único archivo o módulo claramente documentado. Evita repartir CSS frágil por toda la aplicación.

Utiliza preferentemente la tipografía sans-serif nativa de Streamlit o una pila de fuentes locales. No hagas depender la aplicación de una CDN externa.

El bloque *what-if* debe respetar el mismo lenguaje visual y no convertirse en una tarjeta de control llamativa. Debe parecer una extensión metodológica de la narrativa, no una herramienta independiente.

## 8. Librerías

### Interfaz

* Streamlit.

### Navegación

* `st.Page`;
* `st.navigation(position="top")`.

### Gráficos

Utiliza Plotly como librería interactiva principal.

Debe existir una plantilla Plotly común que defina:

* fuente;
* tamaños;
* márgenes;
* fondo blanco;
* color de ejes;
* cuadrícula muy tenue;
* formato de tooltips;
* colores categóricos;
* escalas secuenciales;
* escala divergente para residuos y diferencias del *what-if*.

No mezcles Plotly, Bokeh y Altair sin una necesidad justificada.

### Mapas

Utiliza:

* Folium;
* Leaflet;
* `streamlit-folium`;
* un mapa base claro y discreto, preferentemente CartoDB Positron o equivalente.

Funciones previstas:

* selección de escena;
* selección exclusiva de capa;
* control de opacidad;
* tooltips concisos;
* leyenda;
* ajuste automático a Barcelona;
* comparador `SideBySideLayers`;
* mapas duales sincronizados como alternativa.

No intentes enviar al navegador cientos de miles de polígonos de celdas de 30 m.

Para mapas continuos utiliza preferentemente:

* raster preprocesado;
* PNG o WebP con transparencia;
* `ImageOverlay`;
* teselas o COG si el repositorio ya dispone de una solución adecuada.

Para consultas territoriales utiliza geometrías simplificadas de barrios o secciones censales.

## 9. Tratamiento de datos y artefactos

La aplicación no debe cargar el dataset completo de celdas y escenas.

Construye un pipeline separado que genere artefactos compactos para presentación dentro de `02_Code/Dashboard`, por ejemplo:

```text
02_Code/Dashboard/scripts/build_dashboard_assets.py
```

El script debe leer únicamente los artefactos externos registrados y generar copias derivadas autocontenidas dentro de la carpeta del dashboard.

Posibles salidas:

* tablas resumen en Parquet;
* métricas en JSON;
* series de escenas;
* importancias agregadas;
* predicciones seleccionadas;
* geometrías simplificadas;
* mapas raster preparados para navegador;
* límites, escalas y metadatos;
* imágenes optimizadas;
* manifiesto de artefactos;
* tablas o predicciones necesarias para el *what-if*;
* registro de versiones y hashes.

Crear un manifiesto que incluya:

* nombre del artefacto;
* origen;
* fecha o versión;
* unidad;
* CRS;
* variables;
* rango;
* escena;
* modelo;
* transformación aplicada;
* tamaño;
* hash o identificador de integridad;
* dependencia externa original, si existe.

Los modelos de pocos megabytes pueden incluirse únicamente si existe una interacción que requiera inferencia. Si todo se basa en resultados precomputados, no deben cargarse innecesariamente.

Separar claramente:

* artefactos fuente del TFM;
* artefactos derivados para el dashboard;
* recursos estáticos;
* código de la aplicación;
* archivos de migración;
* documentación.

Todas las rutas deben construirse mediante `pathlib` y funcionar desde la raíz del repositorio o desde la carpeta documentada de ejecución.

No usar rutas absolutas locales.

## 10. Migración de artefactos

Dentro de `02_Code/Dashboard/scripts/` crea un script de migración, por ejemplo:

```text
02_Code/Dashboard/scripts/migrate_dashboard_assets.py
```

El script debe:

1. leer el registro de artefactos externos;
2. comprobar que los archivos de origen existen;
3. verificar tamaños y, cuando sea posible, hashes;
4. copiar únicamente los archivos necesarios;
5. generar las versiones derivadas compactas;
6. actualizar el manifiesto;
7. informar de archivos faltantes;
8. evitar copiar datasets raw o rasters innecesarios;
9. permitir ejecutar una migración limpia en otra ubicación del repositorio.

El resultado debe ser una carpeta `02_Code/Dashboard` autocontenida para ejecutar el dashboard, salvo dependencias instaladas mediante el archivo de requisitos.

Documenta el uso, por ejemplo:

```bash
python 02_Code/Dashboard/scripts/migrate_dashboard_assets.py
```

Si el script necesita conocer la raíz del repositorio, debe resolverla de forma robusta mediante `pathlib` y documentar cualquier parámetro requerido.

## 11. Rendimiento

Utiliza:

* `st.cache_data` para tablas, geometrías, imágenes procesadas y resultados serializables;
* `st.cache_resource` únicamente para modelos u otros recursos globales;
* carga diferida de mapas y contenido pesado;
* artefactos preprocesados;
* geometrías simplificadas;
* imágenes optimizadas.

Evita:

* reproyectar rasters al ejecutar cada página;
* recalcular predicciones salvo el pequeño escenario *what-if*;
* reconstruir GeoJSON grandes;
* cargar todos los mapas al iniciar;
* ejecutar notebooks desde el dashboard;
* acceder a Google Earth Engine en tiempo de ejecución;
* cargar datasets completos;
* copiar artefactos raw innecesarios;
* ejecutar simulaciones multivariables.

El *what-if* debe operar sobre una tabla compacta o sobre un subconjunto de celdas del barrio seleccionado. No debe recorrer ni cargar todo el dataset si no es estrictamente necesario.

## 12. Reglas de visualización

* LST observada y predicha deben utilizar la misma escala cuando se comparen.
* Los residuos deben utilizar una escala divergente centrada en cero.
* Las diferencias del *what-if* deben utilizar una escala divergente centrada en cero.
* Los NoData y las máscaras de nube deben mostrarse de forma neutra.
* No cambiar escalas para mejorar artificialmente la apariencia de un modelo.
* Todas las figuras deben indicar variable, unidad, escena y fuente.
* Los mapas deben conservar costa, límites y orientación espacial reconocibles.
* Las cifras deben proceder de artefactos reales.
* Los gráficos deben incluir una frase interpretativa breve.
* Cada bloque debe responder a una pregunta concreta.
* Evitar gráficos redundantes.
* No mostrar todas las visualizaciones de los notebooks: seleccionar únicamente las que hacen avanzar la historia.
* El *what-if* debe mostrar explícitamente la variable modificada, el porcentaje aplicado, el límite utilizado y el número de celdas afectadas.
* No presentar cambios simulados como efectos observados.
* No utilizar lenguaje causal como “el aumento de NDVI reduce la temperatura” si únicamente se ha modificado una entrada del modelo.

## 13. Estructura técnica orientativa

Todo debe ubicarse dentro de `02_Code/Dashboard`.

Adapta esta estructura al repositorio existente:

```text
02_Code/Dashboard/
├── app.py
├── pages/
│   ├── home.py
│   ├── data.py
│   ├── tabular_model.py
│   ├── deep_learning.py
│   ├── social.py
│   └── conclusions.py
├── components/
│   ├── charts.py
│   ├── maps.py
│   ├── narrative.py
│   ├── metrics.py
│   └── styles.py
├── data/
│   ├── loaders.py
│   ├── contracts.py
│   ├── manifest.py
│   └── migration.py
├── assets/
│   ├── maps/
│   ├── figures/
│   ├── summaries/
│   └── models/
├── scripts/
│   ├── build_dashboard_assets.py
│   └── migrate_dashboard_assets.py
├── docs/
│   ├── artifact_inventory.md
│   ├── dashboard_content_map.md
│   ├── external_artifact_registry.md
│   └── migration.md
├── .streamlit/
│   └── config.toml
├── requirements-dashboard.txt
└── README_dashboard.md
```

No fuerces esta estructura si el repositorio ya dispone de una organización equivalente dentro de `02_Code/Dashboard`.

No crees ni modifiques archivos fuera de esta carpeta.

## 14. Despliegue posterior

La primera versión se ejecutará localmente desde la raíz del repositorio:

```bash
streamlit run 02_Code/Dashboard/app.py
```

También debe quedar documentada una ejecución equivalente desde la propia carpeta si resulta necesaria.

Debe quedar preparada para un despliegue posterior en Streamlit Community Cloud o un servicio equivalente.

Por ello:

* dependencias mínimas y fijadas;
* ausencia de rutas locales;
* ausencia de secretos;
* tamaño reducido de artefactos;
* tiempos de arranque razonables;
* instrucciones reproducibles;
* archivos grandes excluidos de Git;
* recursos requeridos claramente documentados;
* artefactos externos registrados y migrables;
* dashboard ejecutable a partir del contenido de `02_Code/Dashboard`.

No es necesario desplegarla todavía.

## 15. Control de calidad

Antes de cerrar una iteración:

1. ejecutar la aplicación;
2. comprobar todas las páginas;
3. revisar errores en consola;
4. verificar navegación;
5. comprobar el diseño en Chrome a 1440 × 900 y 1366 × 768;
6. validar que no existe scroll horizontal;
7. comprobar mapas y leyendas;
8. verificar las escalas de comparación;
9. actualizar y ejecutar pruebas;
10. confirmar que no se cargan datasets completos;
11. comprobar que todo resultado tiene trazabilidad;
12. revisar ortografía y terminología en español;
13. ejecutar el script de migración en una ubicación limpia o mediante una prueba equivalente;
14. comprobar que el dashboard funciona utilizando únicamente los artefactos migrados;
15. verificar que no se han modificado archivos fuera de `02_Code/Dashboard`;
16. comprobar el experimento *what-if* con al menos un barrio válido;
17. verificar el comportamiento cuando el NDVI alcanza su límite;
18. confirmar que el *what-if* no se presenta como una estimación causal;
19. comprobar que los artefactos pesados innecesarios no se han copiado.

## 16. Plan de implementación

Trabaja por fases.

### Fase 0 — Auditoría

* inventario de notebooks y artefactos;
* identificación de métricas, modelos y visualizaciones;
* mapa de contenido;
* detección de faltantes;
* propuesta de artefactos compactos;
* identificación de variables y modelos aptos para el *what-if*;
* registro de todos los archivos externos necesarios;
* diseño del proceso de migración.

### Fase 1 — Fundamentos

* estructura de carpetas dentro de `02_Code/Dashboard`;
* dependencias;
* configuración Streamlit;
* tema visual;
* navegación superior;
* componentes comunes;
* loaders;
* manifiesto;
* registro de artefactos externos;
* script de migración;
* aplicación ejecutable.

### Fase 2 — Inicio y Datos

* portada;
* infografía del pipeline;
* área de estudio;
* escenas;
* target;
* predictores;
* Cell-Date Dataset.

### Fase 3 — Modelos

* modelo tabular;
* descomposición en dos etapas;
* resultados;
* Deep Learning;
* comparación;
* primer prototipo del *what-if* si los artefactos ya están preparados.

### Fase 4 — Capa social y cierre

* agregaciones territoriales;
* hotspots;
* experimento *what-if* final;
* limitaciones;
* conclusiones;
* próximos pasos.

### Fase 5 — Empaquetado

* optimización;
* documentación;
* prueba limpia;
* migración de artefactos;
* verificación de autocontención;
* preparación para despliegue.

## 17. Alcance de esta primera iteración

En esta primera iteración:

1. completa la auditoría del repositorio;
2. crea `02_Code/Dashboard/docs/artifact_inventory.md`;
3. crea `02_Code/Dashboard/docs/dashboard_content_map.md`;
4. crea `02_Code/Dashboard/docs/external_artifact_registry.md`;
5. crea la documentación inicial del proceso de migración;
6. propone la correspondencia entre páginas, gráficos y artefactos;
7. implementa la estructura base de la aplicación dentro de `02_Code/Dashboard`;
8. configura el tema y la navegación;
9. deja las seis páginas accesibles;
10. implementa completamente `Inicio`;
11. implementa la primera versión de `Datos` con artefactos reales;
12. crea el script de migración de artefactos;
13. no intentes finalizar todavía las páginas de modelos y capa social;
14. analiza si el *what-if* de NDVI puede implementarse de forma segura con los artefactos existentes;
15. si es viable sin cargar datasets pesados ni modificar código externo, deja preparado su contrato de datos y una primera implementación mínima;
16. si no es viable, documenta exactamente los artefactos faltantes y deja el componente pendiente, sin inventar resultados.

En las páginas pendientes puede existir una estructura mínima claramente identificada, pero no deben mostrarse métricas, mapas ni textos ficticios.

Al terminar:

* resume los archivos creados o modificados;
* confirma que todos están dentro de `02_Code/Dashboard`;
* indica qué artefactos se han encontrado;
* señala los faltantes reales;
* explica qué archivos externos son necesarios;
* explica cómo se migran;
* indica qué artefactos pesados se han evitado;
* explica las decisiones técnicas;
* indica si el *what-if* es viable, parcial o está bloqueado;
* proporciona el comando de ejecución;
* proporciona el comando de migración;
* muestra el resultado de las pruebas;
* enumera únicamente los bloqueos o decisiones que requieran intervención del usuario.

## Referencias visuales

Estas son las que daría a Codex, cada una por un motivo concreto:

1. [Distill — Communicating with Interactive Articles](https://distill.pub/2020/communicating-with-interactive-articles)

   Es la referencia conceptual principal: investigación presentada como secuencia vertical, con explicaciones breves e interacciones insertadas en el punto exacto del relato. El dashboard debe parecerse más a esto que a Power BI.

2. [Our World in Data](https://ourworldindata.org/) y su [explicación del rediseño de visualizaciones](https://ourworldindata.org/redesigning-our-interactive-data-visualizations)

   Buena referencia para combinar texto, gráficos, mapas, fuentes y controles sin saturar. Resulta especialmente útil su principio de mostrar solamente los controles pertinentes para la vista actual.

3. [IBM Carbon — Line tabs](https://carbondesignsystem.com/components/tabs/usage/)

   Es prácticamente la referencia exacta para la navegación solicitada: fondo blanco, etiquetas simples y pestaña activa marcada mediante una línea fina. Carbon recomienda además etiquetas breves, idealmente de una o dos palabras.

4. [SEI — Urban Heat Islands StoryMap](https://www.sei.org/features/urban-heat-islands-cities-storymap/)

   Referencia temática para la secuencia mapas → gráficos → análisis espacial → población afectada. No copiaría su apariencia literal, pero sí su narrativa.

5. [Barcelona — Atlas de resiliencia: calor](https://coneixement-eu.bcn.cat/widget/atles-resiliencia/en_index_calor.html)

   Sirve como referencia local de contenido: exposición, vulnerabilidad, mapas territoriales y explicación institucional. UrbanHeat BCN debe diferenciarse mostrando mejor el pipeline de Data Science y la comparación entre modelos.

La referencia visual dominante debe ser **Distill + Our World in Data**, usando **Carbon únicamente para la navegación** y los visores urbanos para seleccionar contenido cartográfico.
