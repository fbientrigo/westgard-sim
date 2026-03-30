import type { EducationalContent } from "@/shared/types/educational";

const EXPERIMENT_TITLE_ES: Record<string, string> = {
  "Glucose Intro Course": "Curso Introductorio de Glucosa",
};

const ANALYTE_ES: Record<string, string> = {
  Glucose: "Glucosa",
};

const SCENARIO_TYPE_LABEL_ES: Record<string, string> = {
  normal: "Operación normal",
  bias: "Sesgo sistemático",
  drift: "Deriva progresiva",
  imprecision: "Imprecisión aumentada",
};

const SCENARIO_ID_ES: Record<string, string> = {
  normal: "Normal",
  bias: "Sesgo",
  drift: "Deriva",
  imprecision: "Imprecisión",
  syst_bias_early: "Sesgo sistemático temprano",
  trend_progressive: "Tendencia progresiva",
  rand_precision_loss: "Pérdida de precisión aleatoria",
};

const SCENARIO_NAME_ES: Record<string, string> = {
  "Normal operation": "Operación normal",
  "Bias shift": "Cambio de sesgo",
  "Progressive drift": "Deriva progresiva",
  "Imprecision increase": "Aumento de imprecisión",
  "Systematic error": "Error sistemático",
  Trend: "Tendencia progresiva",
  "Random error": "Error aleatorio",
};

const SCENARIO_DESCRIPTION_ES: Record<string, string> = {
  "Baseline Gaussian QC process with no injected failure.":
    "Proceso de control de calidad en rango esperado, sin falla inyectada.",
  "Sudden mean shift from run 11 onward.":
    "Cambio súbito de la media a partir de la corrida 11.",
  "Gradual linear drift from run 11 to the final run.":
    "Deriva lineal progresiva desde la corrida 11 hasta el final.",
  "Increased random scatter from run 11 onward.":
    "Aumento de la dispersión aleatoria desde la corrida 11.",
};

const EDUCATIONAL_CONTENT_ES: Record<string, EducationalContent> = {
  normal: {
    scenario: {
      display_name: "Operación normal",
      short_description: "Escenario base sin fallas de control",
      educational_message:
        "Cuando el proceso de control funciona correctamente, las mediciones se distribuyen alrededor de la media esperada y las reglas no deberían activarse de forma sostenida.",
      pattern_hint:
        "Busca dispersión aleatoria alrededor de la media, con la mayoría de puntos dentro de ±2SD y sin tendencia persistente.",
      common_mistake:
        "Confundir un punto aislado fuera de ±2SD con falla real. En procesos normales puede ocurrir ocasionalmente.",
    },
    lesson: {
      guiding_questions: [
        "¿Qué proporción de puntos esperas dentro de ±1SD y ±2SD?",
        "¿Un único punto fuera de ±2SD implica rechazo inmediato?",
        "¿Ves tendencia sostenida en un solo lado de la media?",
      ],
      challenge_prompt:
        "Cuenta cuántos puntos caen en cada zona del gráfico y compáralo con lo esperado para una distribución normal.",
      reveal_text:
        "En 30 corridas, es posible observar algunos puntos fuera de ±2SD sin que exista una falla sistemática.",
    },
  },
  bias: {
    scenario: {
      display_name: "Sesgo sistemático",
      short_description: "Cambio súbito del nivel medio",
      educational_message:
        "El sesgo representa un desplazamiento abrupto y sostenido de la media, típico de errores de calibración o cambios de reactivo.",
      pattern_hint:
        "Las primeras corridas están centradas; luego aparece un salto y los puntos se mantienen desplazados.",
      common_mistake:
        "Confundir sesgo con deriva. En el sesgo el cambio es brusco, no gradual.",
    },
    lesson: {
      guiding_questions: [
        "¿En qué corrida comienza el cambio?",
        "¿Qué evento operativo podría explicar este salto?",
        "¿Qué reglas detectan más rápido este patrón?",
      ],
      challenge_prompt:
        "Compara el promedio antes y después del quiebre para estimar cuántas desviaciones estándar cambió el proceso.",
      reveal_text:
        "El sesgo sostenido suele activar 1-3s y 2-2s. Debe investigarse calibración y condiciones analíticas.",
    },
  },
  drift: {
    scenario: {
      display_name: "Deriva progresiva",
      short_description: "Cambio continuo y gradual de la media",
      educational_message:
        "La deriva aparece como un desplazamiento progresivo en el tiempo, asociado a degradación de reactivos o comportamiento inestable del equipo.",
      pattern_hint:
        "Observa una tendencia sostenida, con puntos cada vez más alejados de la media.",
      common_mistake:
        "No detectar la deriva temprana porque los primeros desvíos parecen pequeños.",
    },
    lesson: {
      guiding_questions: [
        "¿Qué diferencia visual ves entre deriva y sesgo?",
        "¿Desde qué corrida se hace evidente la tendencia?",
        "¿Qué factores técnicos podrían explicarla?",
      ],
      challenge_prompt:
        "Traza mentalmente la pendiente de la serie e identifica cuándo cruza de forma sostenida ±2SD.",
      reveal_text:
        "La deriva es un cambio acumulativo. Requiere monitoreo de tendencia y acciones preventivas sobre equipo/reactivos.",
    },
  },
  imprecision: {
    scenario: {
      display_name: "Imprecisión aumentada",
      short_description: "Mayor variabilidad sin cambio claro de media",
      educational_message:
        "Aquí la media puede mantenerse, pero la dispersión aumenta. El problema principal es la pérdida de reproducibilidad.",
      pattern_hint:
        "Compara la amplitud de dispersión antes y después del punto de cambio.",
      common_mistake:
        "Interpretar la imprecisión como sesgo. En este caso el centro no se desplaza, aumenta el ruido.",
    },
    lesson: {
      guiding_questions: [
        "¿Cambió la media o cambió la variabilidad?",
        "¿Qué impacto clínico tiene mayor dispersión?",
        "¿Qué causas operativas podrían introducir esta variabilidad?",
      ],
      challenge_prompt:
        "Compara la SD entre el tramo inicial y el tramo posterior para cuantificar el aumento de variabilidad.",
      reveal_text:
        "La imprecisión incrementada compromete confiabilidad. Se debe revisar técnica, insumos y estabilidad del sistema.",
    },
  },
};

export function translateExperimentTitle(value: string): string {
  return EXPERIMENT_TITLE_ES[value] ?? value;
}

export function translateAnalyte(value: string): string {
  return ANALYTE_ES[value] ?? value;
}

export function translateScenarioType(value: string): string {
  return SCENARIO_TYPE_LABEL_ES[value] ?? value;
}

export function translateScenarioId(value: string): string {
  return SCENARIO_ID_ES[value] ?? value;
}

export function translateScenarioName(value: string): string {
  return SCENARIO_NAME_ES[value] ?? value;
}

export function translateScenarioDescription(value: string): string {
  return SCENARIO_DESCRIPTION_ES[value] ?? value;
}

export function getEducationalContentEs(scenarioType: string): EducationalContent | null {
  return EDUCATIONAL_CONTENT_ES[scenarioType] ?? null;
}
