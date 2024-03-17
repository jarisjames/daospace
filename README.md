# DAO Points Distribution Algorithm

This project implements an algorithm to calculate and distribute points to DAO contributors based on forum participation. It takes into account the likes on topic creations, regular post likes, and the alignment of replies with the sentiment of the original post.

Topic Likes = 10 points
Regular Post Likes = 1 point
Aligned Topic Replies = 20 points
Aligned Regular Replies = 2 points

## Getting Started

Follow these instructions to set up and run the project on your local machine.

### Prerequisites

- Python 3.8 or newer
- SQLite3
- NLTK with VADER Sentiment Analysis

### Installation

1. **Clone the repository**: Clone this repository to your local machine using Git.
2. **Install Python**: Make sure you have Python 3.8 or newer installed. You can download it from [python.org](https://www.python.org/downloads/).
3. **Install required packages**: Install the necessary Python packages by running the following command in your terminal:
    ```
    pip install -r requirements.txt
    ```
   This will install NLTK and other dependencies required by the script.
4. **Download the database file**: Download the database file named `optimism.db` from this [Google Drive link]:

(https://drive.google.com/file/d/1MWk2__rPbIpdzs6T6yDKoJoNY0m0l6fq/view?usp=sharing). 

Remember to save the file in a known directory on your machine.

### Configuration

After downloading the `optimism.db` file, update the script to point to the correct path of your downloaded database file:

```python
conn = sqlite3.connect("path_to_your_database.db")


# Replace "path_to_your_database.db" with the actual path to optimism.db on your machine, for example:

conn = sqlite3.connect("C:/path/to/optimism.db")

# Running the Script
Navigate to the directory containing the script and execute:

python daoPoints-OP-Forum.py

# Ensure you replace daoPointsAlgorithm.py with the actual name of your script file.

# Viewing the Database Entries

To view the contents of the optimism.db database, you can install SQLite for VSCode along with the SQLiteViewer extension. Alternatively, you can use the online tool at sqliteviewer.app to upload and view the database file.

# Contributing

Your contributions are welcome! Please fork the repository, make your changes, and submit a pull request with your improvements.

# License

This project is open-source and available under the MIT License.

# Contact

For any questions or further information, feel free to reach out to me on Twitter: @JarisJames.


This README provides a comprehensive guide to your project, including how to get it running, prerequisites, and where to get additional resources like the database file. Remember to adjust paths and other specifics as necessary to match your project's actual setup.