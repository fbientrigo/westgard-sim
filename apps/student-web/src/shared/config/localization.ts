import type { EducationalContent } from "@/shared/types/educational";

const EXPERIMENT_TITLE_ES: Record<string, string> = {
  "Glucose Intro Course": "Curso introductorio de glucosa",
};

const ANALYTE_ES: Record<string, string> = {
  Glucose: "Glucosa",
};

const SCENARIO_TYPE_LABEL_ES: Record<string, string> = {
  normal: "Operacion normal",
  bias: "Sesgo sistematico",
  drift: "Deriva progresiva",
  imprecision: "Imprecision aumentada",
};

const SCENARIO_ID_ES: Record<string, string> = {
  normal: "Normal",
  bias: "Sesgo",
  drift: "Deriva",
  imprecision: "Imprecision",
  syst_bias_early: "Sesgo sistematico temprano",
  trend_progressive: "Tendencia progresiva",
  rand_precision_loss: "Perdida de precision aleatoria",
};

const SCENARIO_NAME_ES: Record<string, string> = {
  "Normal operation": "Operacion normal",
  "Bias shift": "Cambio de sesgo",
  "Progressive drift": "Deriva progresiva",
  "Imprecision increase": "Aumento de imprecision",
  "Systematic error": "Error sistematico",
  Trend: "Tendencia progresiva",
  "Random error": "Error aleatorio",
};

const SCENARIO_DESCRIPTION_ES: Record<string, string> = {
  "Baseline Gaussian QC process with no injected failure.":
    "Proceso de control de calidad en rango esperado, sin falla inyectada.",
  "Sudden mean shift from run 11 onward.":
    "Cambio subito de la media a partir de la ejecucion 11.",
  "Gradual linear drift from run 11 to the final run.":
    "Deriva lineal progresiva desde la ejecucion 11 hasta el final.",
  "Increased random scatter from run 11 onward.":
    "Aumento de la dispersion aleatoria desde la ejecucion 11.",
};

const EDUCATIONAL_CONTENT_ES: Record<string, EducationalContent> = {
  normal: {
    scenario: {
      display_name: "Operacion normal",
      short_description: "Escenario base sin fallas de control",
      educational_message:
        "Cuando el proceso de control funciona correctamente, las mediciones se distribuyen alrededor de la media esperada y las reglas no deberian activarse de forma sostenida.",
      pattern_hint:
        "Busca dispersion aleatoria alrededor de la media, con la mayoria de puntos dentro de ±2SD y sin tendencia persistente.",
      common_mistake:
        "Confundir un punto aislado fuera de ±2SD con falla real. En procesos normales puede ocurrir ocasionalmente.",
    },
    lesson: {
      guiding_questions: [
        "¿Que proporcion de puntos esperas dentro de ±1SD y ±2SD?",
        "¿Un unico punto fuera de ±2SD implica rechazo inmediato?",
        "¿Ves tendencia sostenida en un solo lado de la media?",
      ],
      challenge_prompt:
        "Cuenta cuantos puntos caen en cada zona del grafico y comparalo con lo esperado para una distribucion normal.",
      reveal_text:
        "En 30 ejecuciones, es posible observar algunos puntos fuera de ±2SD sin que exista una falla sistematica.",
    },
  },
  bias: {
    scenario: {
      display_name: "Sesgo sistematico",
      short_description: "Cambio subito del nivel medio",
      educational_message:
        "El sesgo representa un desplazamiento abrupto y sostenido de la media, tipico de errores de calibracion o cambios de reactivo.",
      pattern_hint:
        "Las primeras ejecuciones estan centradas; luego aparece un salto y los puntos se mantienen desplazados.",
      common_mistake:
        "Confundir sesgo con deriva. En el sesgo el cambio es brusco, no gradual.",
    },
    lesson: {
      guiding_questions: [
        "¿En que ejecucion comienza el cambio?",
        "¿Que evento operativo podria explicar este salto?",
        "¿Que reglas detectan mas rapido este patron?",
      ],
      challenge_prompt:
        "Compara el promedio antes y despues del quiebre para estimar cuantas desviaciones estandar cambio el proceso.",
      reveal_text:
        "El sesgo sostenido suele activar 1-3s y 2-2s. Debe investigarse calibracion y condiciones analiticas.",
    },
  },
  drift: {
    scenario: {
      display_name: "Deriva progresiva",
      short_description: "Cambio continuo y gradual de la media",
      educational_message:
        "La deriva aparece como un desplazamiento progresivo en el tiempo, asociado a degradacion de reactivos o comportamiento inestable del equipo.",
      pattern_hint:
        "Observa una tendencia sostenida, con puntos cada vez mas alejados de la media.",
      common_mistake:
        "No detectar la deriva temprana porque los primeros desvios parecen pequenos.",
    },
    lesson: {
      guiding_questions: [
        "¿Que diferencia visual ves entre deriva y sesgo?",
        "¿Desde que ejecucion se hace evidente la tendencia?",
        "¿Que factores tecnicos podrian explicarla?",
      ],
      challenge_prompt:
        "Traza mentalmente la pendiente de la serie e identifica cuando cruza de forma sostenida ±2SD.",
      reveal_text:
        "La deriva es un cambio acumulativo. Requiere monitoreo de tendencia y acciones preventivas sobre equipo y reactivos.",
    },
  },
  imprecision: {
    scenario: {
      display_name: "Imprecision aumentada",
      short_description: "Mayor variabilidad sin cambio claro de media",
      educational_message:
        "Aqui la media puede mantenerse, pero la dispersion aumenta. El problema principal es la perdida de reproducibilidad.",
      pattern_hint:
        "Compara la amplitud de dispersion antes y despues del punto de cambio.",
      common_mistake:
        "Interpretar la imprecision como sesgo. En este caso el centro no se desplaza, aumenta el ruido.",
    },
    lesson: {
      guiding_questions: [
        "¿Cambio la media o cambio la variabilidad?",
        "¿Que impacto clinico tiene mayor dispersion?",
        "¿Que causas operativas podrian introducir esta variabilidad?",
      ],
      challenge_prompt:
        "Compara la SD entre el tramo inicial y el tramo posterior para cuantificar el aumento de variabilidad.",
      reveal_text:
        "La imprecision incrementada compromete confiabilidad. Se debe revisar tecnica, insumos y estabilidad del sistema.",
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
