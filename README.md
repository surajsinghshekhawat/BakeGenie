## Prerequisites

- Python 3.8 or higher
- Kaggle API credentials
- Required Python packages (see requirements.txt)

## Installation

1. Clone the repository:

```bash
git clone <repository-url>
cd recipe-assistant
```

2. Create and activate a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install required packages:

```bash
pip install -r requirements.txt
```

4. Set up Kaggle API credentials:
   - Go to your Kaggle account settings
   - Click on "Create New API Token"
   - Save the downloaded kaggle.json file
   - Place it in ~/.kaggle/kaggle.json (Windows: C:\Users\<username>\.kaggle\kaggle.json)
   - Set appropriate permissions:
     ```bash
     chmod 600 ~/.kaggle/kaggle.json  # On Unix-based systems
     ```

## Usage

1. Initialize the database:

```bash
python -m database.recipes_db
```

2. Download and process datasets:

```bash
python -m database.dataset_processor
```

3. Import processed recipes into the database:

```bash
python -m database.recipes_db import_recipes_from_csv datasets/epicurious/processed_recipes.csv
```

## Dataset Sources

The system processes recipes from the following Kaggle datasets:

1. Epicurious Recipes Dataset

   - Contains recipes with ratings and nutritional information
   - Source: https://www.kaggle.com/hugodarwood/epicurious-recipes-with-rating-and-nutritional-information

2. Food.com Recipes and Interactions Dataset

   - Includes recipes and user interactions
   - Source: https://www.kaggle.com/shuyangli94/food-com-recipes-and-user-interactions

3. Food Recipes Dataset
   - Comprehensive collection of recipes
   - Source: https://www.kaggle.com/shuyangli94/food-recipes-dataset

## Data Processing

The system performs the following processing steps:

1. Data Cleaning

   - Remove duplicates
   - Standardize formats
   - Handle missing values
   - Validate data

2. Feature Extraction

   - Estimate recipe difficulty
   - Generate cooking tips
   - Process nutritional information
   - Extract equipment requirements

3. Data Standardization
   - Convert measurements
   - Normalize ingredient names
   - Standardize instructions format
   - Categorize recipes

## Database Schema

### Recipes Table

- id (PRIMARY KEY)
- name
- description
- instructions
- image_path
- dietary
- difficulty
- serving_size
- prep_time
- cook_time
- total_time
- calories
- protein
- carbs
- fat
- fiber
- sugar
- cuisine_type
- meal_type
- author
- rating
- review_count
- tips
- storage_instructions
- equipment_needed
- temperature
- source

### Recipe Ingredients Table

- id (PRIMARY KEY)
- recipe_id (FOREIGN KEY)
- ingredient_name
- amount
- unit
- notes
- substitute
- is_optional
- category
- preparation

## Error Handling

The system includes comprehensive error handling for:

- API authentication issues
- Data download failures
- Processing errors
- Database operations
- Invalid data formats

## Logging

Logs are generated for:

- Dataset downloads
- Processing steps
- Database operations
- Errors and warnings
- Successful completions

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
