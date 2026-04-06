export type FlashcardStudyCard = {
  id: string;
  card_type: string;
  card_type_label: string;
  sort_order: number | null;
  tags: string[];
  display_tags: string[];
  front_html: string;
  back_html: string;
  front_source: string;
  back_source: string;
};

export type FlashcardStudyDeck = {
  deck_id: string;
  format_version: string;
  metadata: {
    title: string;
    subtitle: string;
    language: string;
    audience: string;
    description: string;
    author: string;
    tags: string[];
    display_tags: string[];
    notes: string | null;
  };
  cards: FlashcardStudyCard[];
};
