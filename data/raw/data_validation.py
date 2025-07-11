import pandas as pd
import pandera as pa
from pandera import Column, DataFrameSchema, Check, errors
import re

def validate_twsc_csv_with_pandera(file_path):
    """
    Validates the twsc.csv file using Pandera.

    Args:
        file_path (str): The path to the twsc.csv file.

    Returns:
        bool: True if all validations pass, False otherwise.
    """
    schema = DataFrameSchema(
        {
            "tweet_id": Column(
                int,
                nullable=False,
                unique=True,
                checks=[
                    Check.ge(0, error="must be non-negative")
                ],
                title="Tweet ID",
                coerce=True
            ),
            "author_id": Column(
                int,
                nullable=False,
                checks=[
                    Check.ge(0, error="must be non-negative")
                ],
                title="Author ID",
                coerce=True
            ),
            "inbound": Column(
                bool,
                nullable=False,
                coerce=True,
                title="Inbound Flag"
            ),
            "created_at": Column(
                pa.DateTime, # Expect Pandera to coerce to datetime
                nullable=False, # This will catch unparseable strings (they become NaT)
                coerce=True,    # CRITICAL: Pandera attempts to convert to datetime here
                # REMOVED: The custom Check for created_at format is redundant and problematic.
                # If a string cannot be parsed to datetime by pandas (used by pa.DateTime with coerce),
                # it will result in NaT, which then fails the nullable=False check.
                title="Creation Timestamp"
            ),
            "text": Column(
                str,
                nullable=False,
                checks=[
                    Check(lambda x: isinstance(x, str) and x.strip() != '', element_wise=True, error="cannot be empty or just whitespace")
                ],
                title="Tweet Text"
            ),
            "response_tweet_id": Column(
                str,
                nullable=True,
                checks=[
                    Check(
                        lambda x: True if pd.isna(x) else bool(re.fullmatch(r'^\d+(,\d+)*$', str(x))),
                        element_wise=True,
                        error="must be a single integer or comma-separated integers"
                    )
                ],
                title="Response Tweet ID"
            ),
            "in_response_to_tweet_id": Column(
                float,
                nullable=True,
                checks=[
                    Check(lambda x: pd.isna(x) or x.is_integer(), element_wise=True, error="must be an integer value"),
                    Check(lambda x: pd.isna(x) or x >= 0, element_wise=True, error="must be non-negative")
                ],
                title="In Response To Tweet ID"
            ),
        }
    )

    try:
        df = pd.read_csv(file_path)
        print(f"'{file_path}' (Read successfully)")

        validated_df = schema.validate(df, lazy=True)
        print("Validation Successful! All checks passed. ✅")
        return True

    except FileNotFoundError:
        print(f"Error: File not found at {file_path} 🚨")
        return False
    except pd.errors.EmptyDataError:
        print(f"Error: The file {file_path} is empty. 🚨")
        return False
    except errors.SchemaErrors as err:
        print("\n--- Pandera Validation Errors --- ❌")
        for failure_case in err.failure_cases.itertuples():
            error_msg = (
                f"Column: '{failure_case.column}', "
                f"Row: {failure_case.index}, "
                f"Value: '{failure_case.failure_case}', "
                f"Check: '{failure_case.check}', "
                f"Error: {failure_case.error}"
            )
            print(error_msg)
        print("\nValidation Failed! 🚨")
        return False
    except Exception as e:
        print(f"An unexpected error occurred: {e} 🚨")
        return False

if __name__ == "__main__":
    csv_file = 'twcs.csv'
    if validate_twsc_csv_with_pandera(csv_file):
        print(f"Data checks passed for '{csv_file}'")
    else:
        print(f"data checks failed for  '{csv_file}'")