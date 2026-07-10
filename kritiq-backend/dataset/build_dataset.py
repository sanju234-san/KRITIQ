# Sanjeevni domain - Dataset build pipeline (loading raw and processing into MongoDB Atlas)
import json
import os


def load_and_clean_examples():
    # TODO: Load raw files, clean and validate them
    pass

def generate_embeddings_and_push():
    # TODO: Generate vectors and upload to MongoDB
    pass


def validate_dataset_file(filepath: str) -> bool:
    """
    Loads the JSON file and checks if every entry matches the DatasetEntry shape.
    Prints which entries fail validation (if any), and returns True if all are valid.
    """
    if not os.path.exists(filepath):
        print(f"Error: File {filepath} does not exist.")
        return False

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error: Failed to load JSON from {filepath}. Exception: {e}")
        return False

    if not isinstance(data, list):
        print(f"Error: The root of the dataset in {filepath} must be a JSON array (list).")
        return False

    required_keys = {
        "id": str,
        "category": str,
        "language": str,
        "code_snippet": str,
        "explanation": str,
        "tags": list,
    }

    all_valid = True

    for index, entry in enumerate(data):
        entry_id = entry.get("id") if isinstance(entry, dict) else None
        label = f"entry at index {index} (id: {entry_id})" if entry_id else f"entry at index {index}"

        if not isinstance(entry, dict):
            print(f"Validation failure: {label} is not a JSON object (dictionary).")
            all_valid = False
            continue

        missing_or_invalid = []

        # Check required fields and types
        for key, expected_type in required_keys.items():
            if key not in entry:
                missing_or_invalid.append(f"missing '{key}'")
                continue

            val = entry[key]
            if not isinstance(val, expected_type):
                missing_or_invalid.append(f"'{key}' is of type {type(val).__name__}, expected {expected_type.__name__}")
                continue

            # Extra checks for tags contents
            if key == "tags":
                for tag_index, tag in enumerate(val):
                    if not isinstance(tag, str):
                        missing_or_invalid.append(f"tag at index {tag_index} is of type {type(tag).__name__}, expected str")

        if missing_or_invalid:
            print(f"Validation failure for {label}: {', '.join(missing_or_invalid)}")
            all_valid = False

    if all_valid:
        print(f"Success: Dataset file {filepath} is valid!")
    else:
        print(f"Failure: One or more entries in {filepath} failed validation.")

    return all_valid


if __name__ == "__main__":
    import sys
    # Direct test run
    test_path = "dataset/processed/bad_practice.json"
    print(f"Validating {test_path}...")
    success = validate_dataset_file(test_path)
    sys.exit(0 if success else 1)

