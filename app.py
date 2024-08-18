from flask import Flask, render_template, request, redirect, url_for
import csv
import subprocess

app = Flask(__name__)

ITEMS_PER_PAGE = 10  # Number of headlines per page


@app.route('/')
def index():
    # Get the page number from the URL, default to 1
    page = int(request.args.get('page', 1))
    headlines = []

    # Read and filter headlines labeled as 'stocks'
    with open('./headlines/result_file.csv', 'r', encoding='utf-8') as file:
        reader = csv.reader(file)
        next(reader)  # Skip the header
        for row in reader:
            if row[3] == 'stocks':  # Only include headlines labeled as 'stocks'
                headlines.append(row)

    # Calculate the start and end index for pagination
    start_index = (page - 1) * ITEMS_PER_PAGE
    end_index = start_index + ITEMS_PER_PAGE

    # Slice the headlines for the current page
    paginated_headlines = headlines[start_index:end_index]

    total_pages = (len(headlines) + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE

    return render_template('index.html', headlines=paginated_headlines, page=page, total_pages=total_pages)


@app.route('/run_script', methods=['POST'])
def run_script():
    print("Button clicked! Running the script...")
    try:
        subprocess.run(["python3", "./mainFile.py"], check=True)
        print("Main.py executed successfully!")
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while running Main.py: {e}")
    # Here you can execute any function or script you want

    # After running your script, redirect back to the homepage
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)
