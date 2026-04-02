"""
Evaluation Metrics Module
Scoring system based on 6-Category Rubric with weighted categories
"""
import json
import logging
from typing import Dict, Optional, Tuple, List
from pathlib import Path
from datetime import datetime
import numpy as np
import sys

sys.path.append(str(Path(__file__).parent.parent))

from config.config import (
    EVALUATION_METRICS, LOGS_DIR
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOGS_DIR / "evaluation.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class EvaluationMetrics:
    """
    6-Category Rubric Based Evaluation System
    
    Categories with weights:
    - C1 (15%): Prompt Foundations - Understanding of mechanics
    - C2 (20%): Design & Patterns - Use of deliberate techniques
    - C3 (20%): Iterative Refinement - Diagnostic capability
    - C4 (20%): Domain Application - Adaptation of constraints
    - C5 (15%): Ethics & Safety - Awareness of bias/regulations
    - C6 (10%): Metacognition - Identifying uncertainty
    """
    
    def __init__(self):
        self.metrics = EVALUATION_METRICS
        self.total_weight = sum(self.metrics.values())
        self.evaluation_history = []
        
        logger.info("Initialized Evaluation Metrics with 6-Category Rubric")
        logger.info(f"Total weight: {self.total_weight}")
        for category, weight in self.metrics.items():
            logger.info(f"  {category}: {weight*100:.0f}%")

    def _build_summary_from_history(self, history: List[Dict]) -> Dict:
        """Build summary statistics from any evaluation history list."""
        if not history:
            return {"message": "No evaluations yet"}

        scores = [e["overall_score"] for e in history]
        summary = {
            "total_evaluations": len(history),
            "average_score": float(np.mean(scores)),
            "best_score": float(np.max(scores)),
            "worst_score": float(np.min(scores)),
            "std_dev": float(np.std(scores)),
            "accuracy_distribution": {
                "correct": len([e for e in history if e["accuracy"] == "correct"]),
                "partially_correct": len([e for e in history if e["accuracy"] == "partially_correct"]),
                "incorrect": len([e for e in history if e["accuracy"] == "incorrect"]),
            }
        }
        return summary
    
    def calculate_c1_prompt_foundations(self, similarity_score: float,
                                       retrieval_quality: float) -> float:
        """
        C1 - Prompt Foundations (15%): Understanding of mechanics
        - Evaluates if the prompt correctly used the retrieved context
        - Measures semantic understanding
        
        Args:
            similarity_score: Semantic similarity (0-1)
            retrieval_quality: Quality of retrieved context (0-1)
            
        Returns:
            Score 0-1
        """
        score = (similarity_score * 0.6 + retrieval_quality * 0.4)
        return float(np.clip(score, 0, 1))
    
    def calculate_c2_design_patterns(self, answer_structure: float,
                                    context_usage: float) -> float:
        """
        C2 - Design & Patterns (20%): Use of deliberate techniques
        - Evaluates quality of answer structure
        - Measures effective use of retrieved context
        
        Args:
            answer_structure: How well-structured is the answer (0-1)
            context_usage: How effectively is context used (0-1)
            
        Returns:
            Score 0-1
        """
        score = (answer_structure * 0.5 + context_usage * 0.5)
        return float(np.clip(score, 0, 1))
    
    def calculate_c3_iterative_refinement(self, refine_attempts: int,
                                        improvement_ratio: float) -> float:
        """
        C3 - Iterative Refinement (20%): Diagnostic capability
        - Evaluates if system can identify and fix errors
        - Measures error recovery capability
        
        Args:
            refine_attempts: Number of refinement attempts (0-5)
            improvement_ratio: Improvement from initial to final (0-1)
            
        Returns:
            Score 0-1
        """
        # More attempts but not too many, with improvement
        attempt_score = min(refine_attempts / 5.0, 1.0) if refine_attempts > 0 else 0
        score = (attempt_score * 0.4 + improvement_ratio * 0.6)
        return float(np.clip(score, 0, 1))
    
    def calculate_c4_domain_application(self, domain_relevance: float,
                                       constraint_adherence: float) -> float:
        """
        C4 - Domain Application (20%): Adaptation of constraints
        - Evaluates domain-specific correctness
        - Measures adherence to domain constraints
        
        Args:
            domain_relevance: How relevant is the answer to domain (0-1)
            constraint_adherence: How well constraints are followed (0-1)
            
        Returns:
            Score 0-1
        """
        score = (domain_relevance * 0.5 + constraint_adherence * 0.5)
        return float(np.clip(score, 0, 1))
    
    def calculate_c5_ethics_safety(self, bias_detection: float,
                                  hallucination_check: float) -> float:
        """
        C5 - Ethics & Safety (15%): Awareness of bias/regulations
        - Detects biased or unsafe content
        - Checks for hallucinations
        
        Args:
            bias_detection: Is answer free from bias (0-1)
            hallucination_check: Is answer factually grounded (0-1)
            
        Returns:
            Score 0-1
        """
        score = (bias_detection * 0.5 + hallucination_check * 0.5)
        return float(np.clip(score, 0, 1))
    
    def calculate_c6_metacognition(self, confidence_calibration: float,
                                  uncertainty_expression: float) -> float:
        """
        C6 - Metacognition (10%): Identifying uncertainty
        - Evaluates if system expresses uncertainty appropriately
        - Measures confidence calibration
        
        Args:
            confidence_calibration: How well-calibrated is confidence (0-1)
            uncertainty_expression: Does system express uncertainty (0-1)
            
        Returns:
            Score 0-1
        """
        score = (confidence_calibration * 0.5 + uncertainty_expression * 0.5)
        return float(np.clip(score, 0, 1))
    
    def compute_overall_score(self, category_scores: Dict[str, float]) -> float:
        """
        Compute weighted overall score
        
        Args:
            category_scores: Dictionary of category scores {category: score}
            
        Returns:
            Weighted overall score (0-1)
        """
        overall = 0.0
        for category, weight in self.metrics.items():
            if category in category_scores:
                overall += category_scores[category] * weight
        
        return float(np.clip(overall, 0, 1))
    
    def evaluate_answer(self, 
                       similarity_score: float,
                       retrieved_answer: str,
                       user_answer: str,
                       confidence: float = 0.5) -> Dict:
        """
        Complete evaluation using 6-category rubric
        
        Args:
            similarity_score: Semantic similarity (0-1)
            retrieved_answer: The correct answer
            user_answer: The user's answer
            confidence: Model confidence (0-1)
            
        Returns:
            Complete evaluation result
        """
        logger.info("=" * 70)
        logger.info("EVALUATING ANSWER using 6-Category Rubric")
        logger.info("=" * 70)
        
        # Calculate individual category scores
        category_scores = {}
        
        # C1 - Prompt Foundations (15%)
        retrieval_quality = 0.8 if len(retrieved_answer) > 20 else 0.5
        category_scores["C1_prompt_foundations"] = self.calculate_c1_prompt_foundations(
            similarity_score, retrieval_quality
        )
        
        # C2 - Design & Patterns (20%)
        answer_structure = 0.7 if len(user_answer.split('.')) > 2 else 0.5
        context_usage = similarity_score
        category_scores["C2_design_patterns"] = self.calculate_c2_design_patterns(
            answer_structure, context_usage
        )
        
        # C3 - Iterative Refinement (20%)
        refine_attempts = 1  # Example: 1 refinement
        improvement_ratio = similarity_score
        category_scores["C3_iterative_refinement"] = self.calculate_c3_iterative_refinement(
            refine_attempts, improvement_ratio
        )
        
        # C4 - Domain Application (20%)
        domain_relevance = similarity_score
        constraint_adherence = 0.9 if len(user_answer) > 0 else 0.0
        category_scores["C4_domain_application"] = self.calculate_c4_domain_application(
            domain_relevance, constraint_adherence
        )
        
        # C5 - Ethics & Safety (15%)
        bias_detection = 0.9  # Assume no bias
        hallucination_check = 0.8 if similarity_score > 0.5 else 0.5
        category_scores["C5_ethics_safety"] = self.calculate_c5_ethics_safety(
            bias_detection, hallucination_check
        )
        
        # C6 - Metacognition (10%)
        confidence_calibration = min(confidence, similarity_score)
        uncertainty_expression = 0.7 if confidence < 0.9 else 0.8
        category_scores["C6_metacognition"] = self.calculate_c6_metacognition(
            confidence_calibration, uncertainty_expression
        )
        
        # Compute overall weighted score
        overall_score = self.compute_overall_score(category_scores)
        
        # Determine accuracy
        if similarity_score >= 0.8:
            accuracy = "correct"
        elif similarity_score >= 0.6:
            accuracy = "partially_correct"
        else:
            accuracy = "incorrect"
        
        # Create result dictionary
        result = {
            "timestamp": datetime.now().isoformat(),
            "user_answer": user_answer,
            "retrieved_answer": retrieved_answer,
            "similarity_score": float(similarity_score),
            "accuracy": accuracy,
            "confidence": float(confidence),
            
            # 6-Category Rubric Scores
            "category_scores": {
                k: float(v) for k, v in category_scores.items()
            },
            
            # Overall score
            "overall_score": float(overall_score),
            
            # Score breakdown
            "score_breakdown": {
                "C1_Prompt_Foundations_15%": float(category_scores.get("C1_prompt_foundations", 0)),
                "C2_Design_Patterns_20%": float(category_scores.get("C2_design_patterns", 0)),
                "C3_Iterative_Refinement_20%": float(category_scores.get("C3_iterative_refinement", 0)),
                "C4_Domain_Application_20%": float(category_scores.get("C4_domain_application", 0)),
                "C5_Ethics_Safety_15%": float(category_scores.get("C5_ethics_safety", 0)),
                "C6_Metacognition_10%": float(category_scores.get("C6_metacognition", 0)),
            }
        }
        
        # Log results
        logger.info("\n" + "=" * 70)
        logger.info("EVALUATION RESULTS")
        logger.info("=" * 70)
        logger.info(f"Accuracy: {accuracy}")
        logger.info(f"Similarity Score: {similarity_score:.3f}")
        logger.info(f"Overall Score (Weighted): {overall_score:.3f}")
        logger.info("\n6-CATEGORY RUBRIC SCORES:")
        logger.info(f"  C1 - Prompt Foundations (15%): {category_scores['C1_prompt_foundations']:.3f}")
        logger.info(f"  C2 - Design & Patterns (20%): {category_scores['C2_design_patterns']:.3f}")
        logger.info(f"  C3 - Iterative Refinement (20%): {category_scores['C3_iterative_refinement']:.3f}")
        logger.info(f"  C4 - Domain Application (20%): {category_scores['C4_domain_application']:.3f}")
        logger.info(f"  C5 - Ethics & Safety (15%): {category_scores['C5_ethics_safety']:.3f}")
        logger.info(f"  C6 - Metacognition (10%): {category_scores['C6_metacognition']:.3f}")
        logger.info("=" * 70 + "\n")
        
        # Store in history
        self.evaluation_history.append(result)
        
        return result
    
    def get_evaluation_summary(self) -> Dict:
        """Get summary of all evaluations"""
        return self._build_summary_from_history(self.evaluation_history)
    
    def save_evaluation_report(self, output_path: Optional[str] = None) -> str:
        """
        Save evaluation report to JSON file.
        By default, appends into one stable file instead of creating timestamped files.
        
        Args:
            output_path: Path to save report
            
        Returns:
            Path to saved report
        """
        if output_path is None:
            output_path = LOGS_DIR / "evaluation_report.json"
        
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        existing_evaluations: List[Dict] = []
        if output_path.exists():
            try:
                with open(output_path, 'r', encoding='utf-8') as f:
                    existing_report = json.load(f)
                if isinstance(existing_report, dict):
                    existing_evaluations = existing_report.get("detailed_evaluations", []) or []
            except Exception as e:
                logger.warning(f"Could not read existing report for append: {str(e)}")

        combined_evaluations = existing_evaluations + self.evaluation_history

        report = {
            "last_updated": datetime.now().isoformat(),
            "evaluation_summary": self._build_summary_from_history(combined_evaluations),
            "detailed_evaluations": combined_evaluations,
            "metrics_weights": self.metrics
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        logger.info(
            f"[OK] Saved evaluation report to: {output_path} "
            f"(appended {len(self.evaluation_history)} new evaluations)"
        )
        
        return str(output_path)


if __name__ == "__main__":
    logger.info("Evaluation Metrics Module Ready")

