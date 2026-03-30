export type ScenarioEducation = {
  display_name: string;
  short_description: string;
  educational_message: string;
  pattern_hint: string;
  common_mistake: string;
};

export type LessonEducation = {
  guiding_questions: string[];
  challenge_prompt: string;
  reveal_text: string;
};

export type EducationalContent = {
  scenario?: ScenarioEducation;
  lesson?: LessonEducation;
};
