"""
Data Preprocessing Module
Converts Excel/XLS to JSON/CSV format and cleans data
"""
import json
import pandas as pd
import logging
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import re
import sys

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from config.config import (
    DATA_RAW_DIR, DATA_PROCESSED_DIR, TEXT_COLUMNS, 
    CLEAN_TEXT, REMOVE_DUPLICATES, NORMALIZE_TEXT, 
    MIN_TEXT_LENGTH, LOGS_DIR
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOGS_DIR / "preprocessing.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class DataPreprocessor:
    """Handle data loading, cleaning, and preprocessing"""
    
    def __init__(self):
        self.raw_data = None
        self.processed_data = None
        self.metadata = {
            "total_records": 0,
            "null_values_removed": 0,
            "duplicates_removed": 0,
            "normalized_records": 0,
            "final_records": 0
        }
    
    def load_excel(self, file_path: str, sheet_name: int = 0) -> pd.DataFrame:
        """
        Load data from an Excel file or a directory of Excel files
        
        Args:
            file_path: Path to .xls/.xlsx file or a directory
            sheet_name: Sheet index or name
            
        Returns:
            DataFrame with loaded data
        """
        try:
            path_obj = Path(file_path)

            if path_obj.is_dir():
                excel_files = sorted([p for p in path_obj.glob("*.xls*") if p.is_file()])
                if not excel_files:
                    raise FileNotFoundError(f"No Excel files found in directory: {file_path}")

                logger.info(f"Loading all Excel files from directory: {file_path}")
                dataframes = []
                for excel_file in excel_files:
                    logger.info(f"Loading Excel file: {excel_file}")
                    df_file = pd.read_excel(excel_file, sheet_name=sheet_name)
                    if "source_file" not in df_file.columns:
                        df_file["source_file"] = excel_file.name
                    dataframes.append(df_file)
                df = pd.concat(dataframes, ignore_index=True)
                logger.info(f"Loaded {len(excel_files)} Excel files")
            else:
                logger.info(f"Loading Excel file: {file_path}")
                df = pd.read_excel(path_obj, sheet_name=sheet_name)

            self.raw_data = df.copy()
            logger.info(f"[OK] Loaded {len(df)} rows, {len(df.columns)} columns")
            logger.info(f"Columns: {list(df.columns)}")
            return df
        except FileNotFoundError:
            logger.error(f"File not found: {file_path}")
            raise
        except Exception as e:
            logger.error(f"Error loading Excel: {str(e)}")
            raise
    
    def remove_null_values(self, df: pd.DataFrame, subset: Optional[List[str]] = None) -> pd.DataFrame:
        """
        Remove rows with null values
        
        Args:
            df: Input DataFrame
            subset: Specific columns to check for null
            
        Returns:
            DataFrame with null values removed
        """
        initial_rows = len(df)
        df_clean = df.dropna(subset=subset) if subset else df.dropna()
        removed = initial_rows - len(df_clean)
        
        self.metadata["null_values_removed"] += removed
        logger.info(f"Removed {removed} rows with null values. Remaining: {len(df_clean)}")
        return df_clean
    
    def normalize_text(self, text: str) -> str:
        """
        Normalize text: lowercase, remove extra whitespace, remove special chars
        
        Args:
            text: Input text
            
        Returns:
            Normalized text
        """
        if not isinstance(text, str):
            return str(text)
        
        # Lowercase
        text = text.lower()
        
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', text)
        
        # Remove URLs
        text = re.sub(r'http\S+|www\S+', '', text)
        
        # Remove special characters but keep basic punctuation
        text = re.sub(r'[^\w\s?.!,;:-]', '', text)
        
        # Remove extra punctuation
        text = re.sub(r'\.{2,}|!{2,}|\?{2,}', lambda m: m.group(0)[0], text)
        
        return text.strip()
    
    def deduplicate(self, df: pd.DataFrame, subset: Optional[List[str]] = None) -> pd.DataFrame:
        """
        Remove duplicate rows
        
        Args:
            df: Input DataFrame
            subset: Columns to consider for duplicates
            
        Returns:
            DataFrame without duplicates
        """
        initial_rows = len(df)
        df_unique = df.drop_duplicates(subset=subset, keep='first')
        removed = initial_rows - len(df_unique)
        
        self.metadata["duplicates_removed"] += removed
        logger.info(f"Removed {removed} duplicate rows. Remaining: {len(df_unique)}")
        return df_unique
    
    def validate_text(self, text: str) -> bool:
        """Check if text meets minimum quality criteria"""
        if not isinstance(text, str):
            return False
        if len(text.strip()) < MIN_TEXT_LENGTH:
            return False
        return True
    
    def process_dataframe(self, df: pd.DataFrame, 
                         identify_text_columns: bool = True) -> pd.DataFrame:
        """
        Main preprocessing pipeline
        
        Args:
            df: Input DataFrame
            identify_text_columns: Auto-identify text columns if not in CONFIG
            
        Returns:
            Processed DataFrame
        """
        logger.info("=" * 60)
        logger.info("Starting data preprocessing pipeline")
        logger.info("=" * 60)
        
        self.metadata["total_records"] = len(df)
        
        # Step 1: Remove null values
        if REMOVE_DUPLICATES:
            null_subset = [col for col in TEXT_COLUMNS if col in df.columns]
            df = self.remove_null_values(df, subset=null_subset if null_subset else None)
        
        # Step 2: Remove duplicates
        if REMOVE_DUPLICATES:
            df = self.deduplicate(df)
        
        # Step 3: Identify or validate text columns
        available_cols = [col for col in TEXT_COLUMNS if col in df.columns]
        if not available_cols:
            available_cols = list(df.columns)
            logger.warning(f"No configured text columns found. Using all columns: {available_cols}")
        
        logger.info(f"Text columns to process: {available_cols}")
        
        # Step 4: Normalize text
        if NORMALIZE_TEXT:
            for col in available_cols:
                if col in df.columns and df[col].dtype == 'object':
                    df[col] = df[col].apply(lambda x: self.normalize_text(str(x)) if pd.notna(x) else x)
            self.metadata["normalized_records"] = len(df)
        
        # Step 5: Validate text quality
        df['is_valid'] = df[available_cols[0]].apply(self.validate_text)
        df = df[df['is_valid']].drop('is_valid', axis=1)
        
        self.metadata["final_records"] = len(df)
        
        logger.info("=" * 60)
        logger.info("Preprocessing Summary:")
        logger.info(f"  Initial records: {self.metadata['total_records']}")
        logger.info(f"  Null values removed: {self.metadata['null_values_removed']}")
        logger.info(f"  Duplicates removed: {self.metadata['duplicates_removed']}")
        logger.info(f"  Final records: {self.metadata['final_records']}")
        logger.info("=" * 60)
        
        self.processed_data = df.copy()
        return df
    
    def to_json(self, df: pd.DataFrame, output_path: str) -> None:
        """
        Save DataFrame to JSON format
        
        Args:
            df: DataFrame to save
            output_path: Output file path
        """
        try:
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Convert to list of dictionaries
            records = df.to_dict(orient='records')
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(records, f, indent=2, ensure_ascii=False)
            
            logger.info(f"[OK] Saved {len(records)} records to JSON: {output_path}")
        except Exception as e:
            logger.error(f"Error saving JSON: {str(e)}")
            raise
    
    def to_csv(self, df: pd.DataFrame, output_path: str) -> None:
        """
        Save DataFrame to CSV format
        
        Args:
            df: DataFrame to save
            output_path: Output file path
        """
        try:
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            df.to_csv(output_path, index=False, encoding='utf-8')
            logger.info(f"[OK] Saved {len(df)} records to CSV: {output_path}")
        except Exception as e:
            logger.error(f"Error saving CSV: {str(e)}")
            raise
    
    def save_metadata(self, output_path: str) -> None:
        """Save preprocessing metadata"""
        try:
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(self.metadata, f, indent=2)
            
            logger.info(f"[OK] Saved metadata to: {output_path}")
        except Exception as e:
            logger.error(f"Error saving metadata: {str(e)}")
            raise


def preprocess_dataset(excel_file_path: str, 
                      output_json: Optional[str] = None,
                      output_csv: Optional[str] = None) -> Tuple[pd.DataFrame, Dict]:
    """
    Complete preprocessing pipeline
    
    Args:
        excel_file_path: Path to an input Excel file or a directory of Excel files
        output_json: Optional path to save JSON output
        output_csv: Optional path to save CSV output
        
    Returns:
        Tuple of (processed DataFrame, metadata dictionary)
    """
    preprocessor = DataPreprocessor()
    
    # Load
    df = preprocessor.load_excel(excel_file_path)
    
    # Process
    df_processed = preprocessor.process_dataframe(df)
    
    # Save
    if output_json is None:
        output_json = DATA_PROCESSED_DIR / "processed_data.json"
    if output_csv is None:
        output_csv = DATA_PROCESSED_DIR / "processed_data.csv"
    
    preprocessor.to_json(df_processed, str(output_json))
    preprocessor.to_csv(df_processed, str(output_csv))
    preprocessor.save_metadata(str(DATA_PROCESSED_DIR / "preprocessing_metadata.json"))
    
    return df_processed, preprocessor.metadata


if __name__ == "__main__":
    # Example usage
    logger.info("Data Preprocessor Module Ready")

