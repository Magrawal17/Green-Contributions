import os
import datetime
import random
import subprocess

# --- Configuration ---
# The script assumes it's run from the root of the git repository.
REPO_PATH = '.' 
START_DATE = datetime.date(2025, 1, 1)
# Use the current date provided in the context
END_DATE = datetime.date(2025, 4, 24) 
DUMMY_FILE_NAME = "activity_log.txt"
# Adjust commits per day for desired 'greenness' level
MIN_COMMITS_PER_DAY = 3  # At least 1 commit needed for a green square
MAX_COMMITS_PER_DAY = 7  # Add some randomness 
# --- End Configuration ---

# Function to run shell commands safely
def run_command(command):
    print(f"Executing: {command}")
    try:
        # Use shell=True carefully; okay here as we control the commands.
        # Use check=True to raise an exception on failure.
        subprocess.run(command, shell=True, check=True, text=True, capture_output=True)
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {command}")
        print(f"Stderr: {e.stderr}")
        print(f"Stdout: {e.stdout}")
        # Decide if you want to stop the script on error
        # raise e # Uncomment to stop script on first error
        print("Continuing despite error...") # Or just print and continue


# Initialize dummy file if it doesn't exist
dummy_file_path = os.path.join(REPO_PATH, DUMMY_FILE_NAME)
if not os.path.exists(dummy_file_path):
    print(f"Creating initial dummy file: {DUMMY_FILE_NAME}")
    with open(dummy_file_path, 'w') as f:
        f.write("Repository activity log initialized.\n")
    run_command(f'git add "{DUMMY_FILE_NAME}"')
    # Make an initial commit *without* backdating
    run_command('git commit -m "feat: Initialize activity log"')
    print("Initial commit created.")


# Loop through each day in the specified range
current_date = START_DATE
while current_date <= END_DATE:
    # Decide how many commits for this day
    num_commits = random.randint(MIN_COMMITS_PER_DAY, MAX_COMMITS_PER_DAY)
    print(f"\nProcessing {current_date.isoformat()}: {num_commits} commits")

    for i in range(num_commits):
        # Create a date string for Git. Use a fixed time like noon.
        # Format: "YYYY-MM-DD HH:MM:SS"
        commit_datetime_str = current_date.strftime('%Y-%m-%d 12:00:00')

        # 1. Modify the dummy file to ensure there's a change to commit
        try:
            with open(dummy_file_path, 'a') as f:
                f.write(f"Simulated activity on {commit_datetime_str} - #{i+1}\n")
        except IOError as e:
            print(f"Error writing to file {dummy_file_path}: {e}")
            continue # Skip this commit if file writing fails

        # 2. Stage the changes
        run_command(f'git add "{DUMMY_FILE_NAME}"')

        # 3. Commit with the backdated date using environment variables
        # Escape quotes in the commit message if needed
        commit_message = f"chore: Simulated activity on {current_date.isoformat()} ({i+1}/{num_commits})"

        # Prepare environment variables for the git command
        env_vars = os.environ.copy()
        env_vars['GIT_AUTHOR_DATE'] = commit_datetime_str
        env_vars['GIT_COMMITTER_DATE'] = commit_datetime_str

        # Construct and run the git commit command
        git_commit_cmd = ['git', 'commit', f'-m "{commit_message}"']
        print(f"Executing with backdated date ({commit_datetime_str}): {' '.join(git_commit_cmd)}")
        try:
            # Use subprocess.run for better control over environment
            subprocess.run(git_commit_cmd, env=env_vars, check=True, text=True, capture_output=True)
        except subprocess.CalledProcessError as e:
            print(f"Error executing backdated commit for {commit_datetime_str}")
            print(f"Stderr: {e.stderr}")
            print(f"Stdout: {e.stdout}")
            # Attempting to clean up potential index issues if commit fails
            print("Attempting 'git reset HEAD' to unstage changes...")
            run_command('git reset HEAD') 
            # Decide whether to stop or continue
            # raise e # Uncomment to stop
            print("Continuing to next commit/day despite error...")


    # Move to the next day
    current_date += datetime.timedelta(days=1)

print("\nScript finished generating all commits locally.")
print("----------------------------------------------")
print("VERY IMPORTANT:")
print("The commits have been created locally but are NOT yet on GitHub.")
print("Review the log if desired: git log --oneline -n 20")
print("To push these commits to GitHub and update your contribution graph, run:")
print("git push origin main  (or your default branch name, e.g., master)")
print("----------------------------------------------")
print("Remember the warning about artificial activity!")