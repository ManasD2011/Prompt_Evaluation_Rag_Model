"""
Data Loader Module
Loads and manages different data sources (CSV, JSON, Excel, etc.)
"""
import logging
import sys
from pathlib import Path
from typing import List, Dict, Optional, Union
import pandas as pd
import json

sys.path.append(str(Path(__file__).parent.parent))

from config.config import DATA_RAW_DIR, TEXT_COLUMNS

logger = logging.getLogger(__name__)


class DataLoader:
    """Load data from various formats"""
    
    @staticmethod
    def load_csv(file_path: Union[str, Path]) -> pd.DataFrame:
        """
        Load data from CSV file
        
        Args:
            file_path: Path to CSV file
            
        Returns:
            DataFrame
        """
        try:
            df = pd.read_csv(file_path)
            logger.info(f"Loaded CSV: {file_path} ({len(df)} rows)")
            return df
        except Exception as e:
            logger.error(f"Failed to load CSV: {str(e)}")
            raise
    
    @staticmethod
    def load_json(file_path: Union[str, Path]) -> Union[List[Dict], Dict]:
        """
        Load data from JSON file
        
        Args:
            file_path: Path to JSON file
            
        Returns:
            Parsed JSON data
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            logger.info(f"Loaded JSON: {file_path}")
            return data
        except Exception as e:
            logger.error(f"Failed to load JSON: {str(e)}")
            raise
    
    @staticmethod
    def load_excel(file_path: Union[str, Path], sheet_name: Union[int, str] = 0) -> pd.DataFrame:
        """
        Load data from Excel file
        
        Args:
            file_path: Path to Excel file
            sheet_name: Sheet index or name
            
        Returns:
            DataFrame
        """
        try:
            df = pd.read_excel(file_path, sheet_name=sheet_name)
            logger.info(f"Loaded Excel: {file_path} (sheet={sheet_name}, {len(df)} rows)")
            return df
        except Exception as e:
            logger.error(f"Failed to load Excel: {str(e)}")
            raise
    
    @staticmethod
    def load_jsonl(file_path: Union[str, Path]) -> List[Dict]:
        """
        Load data from JSONL file (JSON Lines)
        
        Args:
            file_path: Path to JSONL file
            
        Returns:
            List of dictionaries
        """
        try:
            data = []
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        data.append(json.loads(line))
            logger.info(f"Loaded JSONL: {file_path} ({len(data)} records)")
            return data
        except Exception as e:
            logger.error(f"Failed to load JSONL: {str(e)}")
            raise
    
    @staticmethod
    def load_directory(
        directory: Union[str, Path],
        file_pattern: str = "*.csv",
        recursive: bool = False
    ) -> Dict[str, pd.DataFrame]:
        """
        Load multiple files from directory
        
        Args:
            directory: Path to directory
            file_pattern: File pattern to match (e.g., "*.csv")
            recursive: Search recursively
            
        Returns:
            Dictionary with dataframes
        """
        directory = Path(directory)
        dataframes = {}
        
        try:
            if recursive:
                files = list(directory.rglob(file_pattern))
            else:
                files = list(directory.glob(file_pattern))
            
            for file_path in files:
                try:
                    if file_path.suffix == '.csv':
                        dataframes[file_path.stem] = DataLoader.load_csv(file_path)
                    elif file_path.suffix == '.json':
                        dataframes[file_path.stem] = pd.DataFrame(DataLoader.load_json(file_path))
                    elif file_path.suffix in ['.xlsx', '.xls']:
                        dataframes[file_path.stem] = DataLoader.load_excel(file_path)
                except Exception as e:
                    logger.warning(f"Failed to load {file_path}: {str(e)}")
            
            logger.info(f"Loaded {len(dataframes)} files from {directory}")
            return dataframes
        except Exception as e:
            logger.error(f"Failed to load directory: {str(e)}")
            raise
    
    @staticmethod
    def extract_texts(df: pd.DataFrame, columns: Optional[List[str]] = None) -> List[str]:
        """
        Extract text content from DataFrame
        
        Args:
            df: Input DataFrame
            columns: Columns to extract from (uses TEXT_COLUMNS if None)
            
        Returns:
            List of text strings
        """
        if columns is None:
            columns = TEXT_COLUMNS
        
        texts = []
        available_columns = [col for col in columns if col in df.columns]
        
        if not available_columns:
            logger.warning(f"No matching columns found. Available: {df.columns.tolist()}")
            return []
        
        for idx, row in df.iterrows():
            row_texts = []
            for col in available_columns:
                value = row[col]
                if pd.notna(value):
                    row_texts.append(str(value))
            
            if row_texts:
                texts.append(" ".join(row_texts))
        
        logger.info(f"Extracted {len(texts)} text entries from DataFrame")
        return texts
