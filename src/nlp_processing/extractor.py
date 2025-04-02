import spacy
from spacy.tokens import Doc
from typing import List, Dict

class EntityRelationExtractor:
    def __init__(self, model="en_core_web_lg"):
        """Initialize the extractor with a spaCy model"""
        self.nlp = spacy.load(model)
        self.nlp.max_length = 2000000  # افزایش حد مجاز طول متن به 2,000,000 کاراکتر
    
    def extract_entities(self, text: str) -> List[Dict]:
        """Extract entities from text"""
        if len(text) > self.nlp.max_length:
            print(f"Warning: Text length ({len(text)}) exceeds maximum allowed length ({self.nlp.max_length}).")
        
        doc = self.nlp(text)  # پردازش متن
        entities = []
        
        for ent in doc.ents:
            entities.append({
                "text": ent.text,
                "label": ent.label_,
                "start": ent.start_char,
                "end": ent.end_char
            })
            
        return entities
    
    def extract_relations(self, text: str) -> List[Dict]:
        """Extract potential relations between entities"""
        if len(text) > self.nlp.max_length:
            print(f"Warning: Text length ({len(text)}) exceeds maximum allowed length ({self.nlp.max_length}).")
        
        doc = self.nlp(text)  # پردازش متن
        relations = []
        
        # Simple relation extraction based on dependency parsing
        for sent in doc.sents:
            for token in sent:
                if token.dep_ in ("ROOT", "nsubj"):
                    subject = token.text
                    subject_type = self._get_entity_type(token, doc)
                    
                    for child in token.children:
                        if child.dep_ in ("dobj", "pobj"):
                            object_ = child.text
                            object_type = self._get_entity_type(child, doc)
                            relation = {
                                "subject": subject,
                                "subject_type": subject_type,
                                "predicate": token.text if token.dep_ != "nsubj" else self._get_predicate(token, sent),
                                "object": object_,
                                "object_type": object_type,
                                "confidence": 0.7  # Placeholder for actual confidence calculation
                            }
                            relations.append(relation)
        
        return relations
    
    def _get_entity_type(self, token, doc: Doc) -> str:
        """Get entity type for a token if it's part of a named entity"""
        for ent in doc.ents:
            if token.i >= ent.start and token.i < ent.end:
                return ent.label_
        return "UNKNOWN"
    
    def _get_predicate(self, subject_token, sent) -> str:
        """Extract predicate for a subject token"""
        for token in sent:
            if token.head == subject_token.head and token.dep_ == "ROOT":
                return token.text
        return ""