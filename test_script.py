import argparse
import os
import subprocess

def run_python_script(python_script, input_file, output_file):
    """Run the Python script with the input file and pipe output to the output file."""
    try:
        with open(output_file, 'w') as outfile:
            result = subprocess.run(
                ['python3', python_script, input_file],
                stdout=outfile,
                stderr=subprocess.PIPE,
                text=True
            )
        if result.returncode != 0:
            raise Exception(f"Error running {python_script} on {input_file}: {result.stderr}")
        return True
    except Exception as e:
        print(f"Failed to process {input_file}: {str(e)}")
        return False

def diff_files(file1, file2):
    """Diff two files and return the differences."""
    with open(file1, 'r') as f1, open(file2, 'r') as f2:
        diff = set(f1).symmetric_difference(f2)
    return diff

def main(input_dir, output_dir, python_script):
    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # File to store full diff results
    error_file = os.path.join(output_dir, 'error.txt')
    with open(error_file, 'w') as errfile:
        errfile.write("Diff Results:\n")

    for filename in os.listdir(input_dir):
        if filename.endswith('.frag'):
            input_file = os.path.join(input_dir, filename)
            output_file = os.path.join(output_dir, filename.replace('.frag', '.tmp'))
            expected_file = os.path.join(input_dir, filename.replace('.frag', '.out'))

            # Run the Python script
            if not run_python_script(python_script, input_file, output_file):
                continue

            # Diff the output with the expected file
            if os.path.exists(expected_file):
                diff = diff_files(output_file, expected_file)
                if diff:
                    print(f"Mismatch found for {filename}.")
                    with open(error_file, 'a') as errfile:
                        errfile.write(f"\nDifferences for {filename}:\n")
                        for line in diff:
                            errfile.write(line)
                else:
                    print(f"No differences found for {filename}.")
            else:
                print(f"No expected output file found for {filename}.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run a Python script on files in a directory and diff the output.")
    parser.add_argument('input_dir', type=str, help="Directory containing input files.")
    parser.add_argument('output_dir', type=str, help="Directory to save output files.")
    parser.add_argument('python_script', type=str, help="Path to the Python script to run.")
    args = parser.parse_args()

    main(args.input_dir, args.output_dir, args.python_script)